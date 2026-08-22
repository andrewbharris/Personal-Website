#!/usr/bin/env python3
"""
Regenerate the publication list in publications.html.

Data flow
---------
1. ORCID public API  ->  the list of works on Dr. Harris's ORCID record,
   which is where the DOIs come from.
2. Crossref public API  ->  full metadata for each DOI: complete author list,
   journal, year, volume, pages.

Both APIs are free, need no key, and do not block automated traffic the way
Google Scholar does. This replaces an earlier scholarly/Google Scholar version
that never completed a single successful run (it hung for the full 6-hour
GitHub Actions timeout on 2026-08-01).

The publication list on the page lives between these two markers:

    <!-- PUBLICATIONS:START -->
    ...generated <ol class="pub-list"> here...
    <!-- PUBLICATIONS:END -->

Everything else on the page is left untouched.

Safety behaviour
----------------
The script is deliberately conservative. It writes NOTHING and exits non-zero if:
  - ORCID or Crossref cannot be reached
  - fewer than MIN_EXPECTED publications come back (assume a partial fetch)
  - the markers are missing from publications.html
  - the result would shrink the list by more than SHRINK_TOLERANCE, which
    normally means the ORCID record is behind the CV (--allow-shrink overrides)
The existing list is never destroyed by a bad fetch.

Note: CI runs with --allow-shrink, because ORCID is the source of truth and the
site is meant to mirror it in both directions. The MIN_EXPECTED floor still
applies there, so a broken or partial API response cannot empty the page.

Run locally:   python3 scripts/update_publications.py
               python3 scripts/update_publications.py --dry-run
               python3 scripts/update_publications.py --allow-shrink
In CI:         see .github/workflows/update-publications.yml
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ORCID_ID = "0000-0002-8158-4364"
PAGE = Path(__file__).resolve().parent.parent / "publications.html"
START = "<!-- PUBLICATIONS:START -->"
END = "<!-- PUBLICATIONS:END -->"

MIN_EXPECTED = 25          # safety floor; below this we assume a partial fetch
SHRINK_TOLERANCE = 0.10    # refuse a sync that drops >10% of the existing list
TIMEOUT = 30               # seconds per HTTP request
CROSSREF_BATCH = 25        # DOIs per Crossref query
USER_AGENT = (
    "andrewbharrismd.com publication list updater "
    "(+https://andrewbharrismd.com)"
)

# Match Dr. Harris in a formatted author string: "Harris AB", "Harris A"
HARRIS = re.compile(r"\bHarris,? A(?:B)?\b")


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def get_json(url):
    """GET a URL and parse JSON. Raises on any failure."""
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


# --------------------------------------------------------------------------
# ORCID
# --------------------------------------------------------------------------

def orcid_works():
    """
    Return a list of dicts, one per work on the ORCID record:
        {doi, title, journal, year}
    doi may be None. Duplicate DOIs are collapsed.
    """
    url = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
    data = get_json(url)

    works = []
    seen_dois = set()

    for group in data.get("group", []):
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        s = summaries[0]  # the preferred record for this work

        doi = None
        for ext in (group.get("external-ids") or {}).get("external-id", []):
            if (ext.get("external-id-type") or "").lower() == "doi":
                doi = (ext.get("external-id-value") or "").strip().lower()
                break

        if doi:
            if doi in seen_dois:
                continue
            seen_dois.add(doi)

        title = ""
        t = s.get("title") or {}
        if t.get("title"):
            title = (t["title"].get("value") or "").strip()

        journal = ""
        j = s.get("journal-title") or {}
        if j:
            journal = (j.get("value") or "").strip()

        year = 0
        pd = s.get("publication-date") or {}
        if pd and pd.get("year"):
            try:
                year = int(re.sub(r"\D", "", str(pd["year"].get("value") or "")) or 0)
            except ValueError:
                year = 0

        if not title:
            continue

        works.append({"doi": doi, "title": title, "journal": journal, "year": year})

    return works


# --------------------------------------------------------------------------
# Crossref
# --------------------------------------------------------------------------

def crossref_metadata(dois):
    """
    Look DOIs up at Crossref in batches. Returns {doi: crossref_item}.
    Failures for individual batches are skipped, not fatal.
    """
    out = {}
    for i in range(0, len(dois), CROSSREF_BATCH):
        batch = dois[i:i + CROSSREF_BATCH]
        filt = ",".join("doi:" + d for d in batch)
        url = (
            "https://api.crossref.org/works?"
            + urllib.parse.urlencode({"filter": filt, "rows": len(batch)})
        )
        try:
            data = get_json(url)
        except (urllib.error.URLError, urllib.error.HTTPError,
                json.JSONDecodeError, TimeoutError) as exc:
            print(f"  Crossref batch {i // CROSSREF_BATCH + 1} failed: {exc}",
                  file=sys.stderr)
            continue

        for item in data.get("message", {}).get("items", []):
            doi = (item.get("DOI") or "").strip().lower()
            if doi:
                out[doi] = item
        time.sleep(0.5)  # be polite to a free public API
    return out


def format_authors(item):
    """Crossref author objects -> 'Last FM, Last FM, Last FM'."""
    names = []
    for a in item.get("author") or []:
        family = (a.get("family") or "").strip()
        given = (a.get("given") or "").strip()
        if not family:
            name = (a.get("name") or "").strip()
            if name:
                names.append(name)
            continue
        initials = "".join(p[0].upper() for p in re.split(r"[\s.\-]+", given) if p[:1].isalpha())
        names.append(f"{family} {initials}".strip())
    return ", ".join(names)


def citation_from_crossref(item, fallback):
    """
    Build a citation in the house style:
        Authors. Title. Journal. Year;Volume:Pages. doi:10.xxxx/yyy
    Missing pieces are simply omitted.
    """
    authors = format_authors(item)

    title = ""
    if item.get("title"):
        title = (item["title"][0] or "").strip()
    if not title:
        title = fallback.get("title", "")

    journal = ""
    for key in ("short-container-title", "container-title"):
        vals = item.get(key) or []
        if vals and vals[0]:
            journal = vals[0].strip()
            break
    if not journal:
        journal = fallback.get("journal", "")

    year = 0
    for key in ("published-print", "published-online", "published", "issued"):
        parts = (item.get(key) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            year = int(parts[0][0])
            break
    if not year:
        year = fallback.get("year", 0)

    volume = (item.get("volume") or "").strip()
    pages = (item.get("page") or "").strip()
    doi = (item.get("DOI") or "").strip()

    pieces = []
    if authors:
        pieces.append(authors + ".")
    if title:
        pieces.append(title.rstrip(".") + ".")
    if journal:
        pieces.append(journal.rstrip(".") + ".")

    # Year;Volume:Pages
    locator = ""
    if year:
        locator = str(year)
        if volume:
            locator += ";" + volume
            if pages:
                locator += ":" + pages
        locator += "."
    if locator:
        pieces.append(locator)

    if doi:
        pieces.append("doi:" + doi)

    return " ".join(pieces).strip(), year, title


def citation_from_orcid_only(work):
    """Fallback when a work has no DOI or Crossref has no record for it."""
    pieces = []
    if work["title"]:
        pieces.append(work["title"].rstrip(".") + ".")
    if work["journal"]:
        pieces.append(work["journal"].rstrip(".") + ".")
    if work["year"]:
        pieces.append(str(work["year"]) + ".")
    return " ".join(pieces).strip(), work["year"], work["title"]


# --------------------------------------------------------------------------
# Build + write
# --------------------------------------------------------------------------

def build_items():
    print(f"Fetching ORCID record {ORCID_ID} ...")
    works = orcid_works()
    print(f"  {len(works)} works on the ORCID record")

    dois = [w["doi"] for w in works if w["doi"]]
    print(f"  {len(dois)} of them carry a DOI; looking those up at Crossref ...")
    meta = crossref_metadata(dois) if dois else {}
    print(f"  Crossref returned metadata for {len(meta)}")

    rows = []
    for w in works:
        item = meta.get(w["doi"]) if w["doi"] else None
        if item:
            citation, year, title = citation_from_crossref(item, w)
        else:
            citation, year, title = citation_from_orcid_only(w)

        if not citation:
            continue

        esc = html.escape(citation)
        esc = HARRIS.sub(lambda m: f"<strong>{m.group(0)}</strong>", esc, count=1)
        rows.append((year, (title or "").lower(), f"      <li>{esc}</li>"))

    rows.sort(key=lambda r: (-r[0], r[1]))
    return [r[2] for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would change without writing the file")
    ap.add_argument("--allow-shrink", action="store_true",
                    help="permit a sync that removes more than "
                         "10%% of the current list (use only when ORCID is known good)")
    args = ap.parse_args()

    try:
        items = build_items()
    except (urllib.error.URLError, urllib.error.HTTPError,
            json.JSONDecodeError, TimeoutError) as exc:
        print(f"Could not reach ORCID/Crossref ({exc}); "
              "leaving publications.html unchanged.", file=sys.stderr)
        return 1

    if len(items) < MIN_EXPECTED:
        print(f"Only {len(items)} publications returned (< {MIN_EXPECTED}); "
              "assuming a blocked or partial fetch and leaving the page unchanged.",
              file=sys.stderr)
        return 1

    fragment = '<ol class="pub-list">\n' + "\n".join(items) + "\n    </ol>"

    text = PAGE.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("Could not find the publication markers in publications.html",
              file=sys.stderr)
        return 1

    existing = re.search(re.escape(START) + r"(.*?)" + re.escape(END), text, re.DOTALL)
    existing_count = len(re.findall(r"<li", existing.group(1))) if existing else 0

    # Would this sync shrink the list materially? The ORCID record is the source
    # of truth here, but it can lag the CV: on 2026-08-22 it held 115 works
    # against 143 on the page, so a straight sync would have quietly dropped 28
    # publications.
    lost = existing_count - len(items)
    shrinking = bool(
        existing_count and len(items) < existing_count * (1 - SHRINK_TOLERANCE)
    )

    # --dry-run is purely informational and always exits 0, so it can report a
    # shrink rather than failing on it.
    if args.dry_run:
        print(f"DRY RUN: would write {len(items)} publications "
              f"(page currently has {existing_count}).")
        if shrinking:
            print(f"  WARNING: that is {lost} fewer. A real run would refuse "
                  f"this unless given --allow-shrink.")
        print("First three entries:")
        for line in items[:3]:
            print("  " + re.sub(r"<[^>]+>", "", line).strip()[:160])
        return 0

    # Refuse any real run that would remove more than SHRINK_TOLERANCE of the
    # list. Override with --allow-shrink once ORCID is correct and the smaller
    # number is genuinely the right one.
    if shrinking and not args.allow_shrink:
        print(
            f"REFUSING TO WRITE: this would cut the list from {existing_count} to "
            f"{len(items)} publications, dropping {lost}.\n"
            f"That almost always means the ORCID record is behind the CV rather "
            f"than that the papers went away.\n"
            f"Fix: add the missing works at orcid.org (Works -> Add works -> "
            f"Search & link) and run this again.\n"
            f"If the smaller number really is correct, re-run with --allow-shrink.",
            file=sys.stderr,
        )
        return 1

    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _m: f"{START}\n    {fragment}\n    {END}",
        text,
        flags=re.DOTALL,
    )

    if new != text:
        PAGE.write_text(new, encoding="utf-8")
        print(f"Updated publications.html: {existing_count} -> {len(items)} publications.")
    else:
        print("No change; publications.html is already current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
