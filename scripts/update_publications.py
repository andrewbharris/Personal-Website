#!/usr/bin/env python3
"""
Regenerate the publication list in publications.html from Dr. Harris's
Google Scholar profile.

The publication list on the page lives between these two markers:

    <!-- PUBLICATIONS:START -->
    ...generated <ol class="pub-list"> here...
    <!-- PUBLICATIONS:END -->

This script fetches the Scholar profile, rebuilds that <ol>, and writes it
back in place. Everything else on the page is left untouched.

It is intentionally conservative: if Scholar returns too few results (which
usually means the request was blocked/rate-limited), the script exits WITHOUT
touching the file, so the existing hand-maintained list is preserved.

Run locally:   python scripts/update_publications.py
In CI:         see .github/workflows/update-publications.yml
"""

import html
import re
import sys
from pathlib import Path

SCHOLAR_ID = "HISx5XcAAAAJ"
PAGE = Path(__file__).resolve().parent.parent / "publications.html"
START = "<!-- PUBLICATIONS:START -->"
END = "<!-- PUBLICATIONS:END -->"
MIN_EXPECTED = 25  # safety floor; below this we assume the fetch was blocked

# Surname to bold in each citation (Dr. Harris)
HARRIS = re.compile(r"(Harris,?\s*A(?:\.?\s*B\.?)?)", re.IGNORECASE)


def format_authors(raw: str) -> str:
    """Turn Scholar's 'First Last and First Last' into 'Last FM, Last FM'."""
    out = []
    for name in [n.strip() for n in raw.split(" and ") if n.strip()]:
        parts = name.split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = "".join(p[0] for p in parts[:-1] if p[:1].isalpha())
            out.append(f"{last} {initials}".strip())
        else:
            out.append(name)
    return ", ".join(out)


def build_items():
    from scholarly import scholarly

    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["publications"])
    pubs = author.get("publications", [])

    rows = []
    for p in pubs:
        p = scholarly.fill(p)
        bib = p.get("bib", {})
        title = (bib.get("title") or "").strip()
        if not title:
            continue
        year = bib.get("pub_year") or "0"
        try:
            year_i = int(re.sub(r"\D", "", str(year)) or 0)
        except ValueError:
            year_i = 0
        authors = format_authors(bib.get("author", ""))
        venue = (bib.get("venue") or bib.get("journal") or "").strip()

        pieces = []
        if authors:
            pieces.append(authors + ".")
        pieces.append(title.rstrip(".") + ".")
        if venue:
            pieces.append(venue.rstrip(".") + ".")
        if year_i:
            pieces.append(str(year_i) + ".")
        citation = " ".join(pieces)

        esc = html.escape(citation)
        esc = HARRIS.sub(r"<strong>\1</strong>", esc, count=1)
        rows.append((year_i, title.lower(), f"      <li>{esc}</li>"))

    rows.sort(key=lambda r: (-r[0], r[1]))
    return [r[2] for r in rows]


def main():
    items = build_items()
    if len(items) < MIN_EXPECTED:
        print(
            f"Only {len(items)} publications returned (< {MIN_EXPECTED}); "
            "assuming a blocked/partial fetch and leaving the page unchanged.",
            file=sys.stderr,
        )
        return 1

    fragment = '<ol class="pub-list">\n' + "\n".join(items) + "\n    </ol>"

    text = PAGE.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("Could not find publication markers in publications.html", file=sys.stderr)
        return 1

    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        f"{START}\n    {fragment}\n    {END}",
        text,
        flags=re.DOTALL,
    )

    if new != text:
        PAGE.write_text(new, encoding="utf-8")
        print(f"Updated publications.html with {len(items)} publications.")
    else:
        print("No change; publications.html already current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
