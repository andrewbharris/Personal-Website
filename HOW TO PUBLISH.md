# How to Publish Your Website

Everything you need to get **andrewbharrismd.com** live and keep it updated.

There are two parts: a **one-time setup** you do once, and then **making updates**, which becomes a single double-click every time after that.

---

## How this works (the short version)

- This folder (`Working Version`) **is** your website. The files here are the live site.
- GitHub stores a copy and serves it to the world, free, forever.
- When you change something here and publish, the live site updates in about a minute.
- Every publish is saved permanently, so you can always go back to how it was before.

---

# PART 1 — One-time setup

You only do this once. Budget about 20 minutes.

## Step 1. Install GitHub Desktop

This is the easiest way to connect your folder to GitHub without using the command line.

1. Go to **https://desktop.github.com**
2. Download and install it.
3. Open it and sign in with your GitHub account (`andrewbharris`).

## Step 2. Connect this folder to GitHub

1. In GitHub Desktop, go to **File → Add Local Repository**
2. Click **Choose...** and select this folder:
   `Documents/Personal Website/Working Version`
3. It will say *"This directory does not appear to be a Git repository."*
   Click the **create a repository** link in that message.
4. Fill in:
   - **Name:** `Personal-Website`
   - **Description:** leave blank
   - **Git ignore:** None (you already have one)
   - **License:** None
5. Click **Create Repository**.

## Step 3. Push it to GitHub

1. Click the **Publish repository** button at the top.
2. **Uncheck** "Keep this code private" — GitHub Pages needs it public on a free account.
3. Confirm the name is `Personal-Website`.
4. Click **Publish Repository**.

Your files are now on GitHub.

## Step 4. Turn on GitHub Pages

1. Go to **https://github.com/andrewbharris/Personal-Website**
2. Click **Settings** (top right of the repo).
3. In the left sidebar, click **Pages**.
4. Under **Build and deployment → Source**, choose **Deploy from a branch**.
5. Under **Branch**, choose **main**, folder **/ (root)**, then click **Save**.
6. Wait about a minute, then refresh. It will show a live link like
   `https://andrewbharris.github.io/Personal-Website/`

Click it and confirm your site loads. **If it works here, the hard part is done.**

## Step 5. Point your domain at it

Your domain is registered at Namecheap but still points at your old SiteGround hosting. This is what moves it.

### 5a. Tell GitHub about the domain

The `CNAME` file in this folder already contains `andrewbharrismd.com`, so GitHub will pick it up automatically. In the same **Settings → Pages** screen, confirm the **Custom domain** box shows `andrewbharrismd.com`. If it's empty, type it in and click **Save**.

> **Important:** do this step *before* the Namecheap step below. GitHub warns that changing DNS first, without claiming the domain on GitHub, briefly leaves an opening for someone else to host a site on your domain.

### 5b. Change the DNS at Namecheap

1. Sign in at **https://namecheap.com**
2. **Domain List → Manage** next to `andrewbharrismd.com`
3. Set **Nameservers** to **Namecheap BasicDNS** (this is what moves you off SiteGround).
4. Go to the **Advanced DNS** tab.
5. Delete any existing `A`, `CNAME`, or `URL Redirect` records for `@` and `www`.
6. Add these **five** records:

   | Type       | Host | Value                     | TTL       |
   |------------|------|---------------------------|-----------|
   | A Record   | `@`  | `185.199.108.153`         | Automatic |
   | A Record   | `@`  | `185.199.109.153`         | Automatic |
   | A Record   | `@`  | `185.199.110.153`         | Automatic |
   | A Record   | `@`  | `185.199.111.153`         | Automatic |
   | CNAME      | `www`| `andrewbharris.github.io.` | Automatic |

   *(The four A records are GitHub's servers. The trailing dot on the CNAME value matters.)*

7. Save.

### 5c. Wait, then turn on HTTPS

DNS changes take anywhere from 30 minutes to 24 hours to spread.

Once `andrewbharrismd.com` loads your site, go back to **GitHub → Settings → Pages** and tick **Enforce HTTPS**. (The checkbox stays greyed out until DNS has finished, so if you can't click it yet, just wait longer.)

**Setup is done.**

---

# PART 2 — Making updates from now on

This is the part you'll actually use.

### The routine

1. **Change something.** Either:
   - Double-click **`USE THIS TO HAND-EDIT CONTENT.command`** to edit text by clicking directly on the page, or
   - Ask Claude to make the change.
2. **Check it looks right.** Double-click `index.html` to preview it in your browser.
3. **Double-click `PUBLISH UPDATES.command`.**
   It shows you what changed, asks you to confirm with `y`, then publishes.
4. Wait about a minute, then visit **andrewbharrismd.com** and refresh with **Cmd+Shift+R**.

That's it. No other steps.

> **Note:** the first time you run `PUBLISH UPDATES.command`, macOS may warn that it's from an unidentified developer. Right-click the file → **Open** → **Open**. You only have to do that once.

---

## Keeping your folders straight

| Folder | What it's for |
|---|---|
| **Working Version** | **The live website.** Edit here. This is what gets published. |
| **Archived Versions** | Frozen snapshots (V1, V3, V5...). Never edit these — they exist so you can go back. |
| Photos, Logos, Brand Profiles | Source material. Not published. |
| Design Mockups | Design experiments. Not published. |

**Rule of thumb:** if you want it on the website, it goes in `Working Version`. Everything else is just your own reference.

---

## If something goes wrong

**The site didn't update.**
Hard-refresh with **Cmd+Shift+R** — browsers cache aggressively. If it's still stale, check GitHub Desktop shows no pending changes, then look at the **Actions** tab on GitHub for a red X.

**I broke something and want to undo it.**
Nothing is ever lost. In GitHub Desktop, click **History** to see every publish. Right-click any entry and choose **Revert changes in commit**. Or ask Claude to restore from an archived version.

**The publish script says it failed.**
Your changes are still saved locally. The usual causes are no internet, or GitHub wanting you to sign in again — open GitHub Desktop and it will prompt you.

**Someone submitted the contact form but I got nothing.**
Sign in at **https://formspree.io** and check the form's submissions. Confirm the destination email there is one you actually check. Free accounts get 50 submissions a month.

---

## Things worth doing eventually

- **Add real office phone numbers and addresses** to the Contact page and footer once you have them.
- **Swap in a practice email** on Formspree instead of a personal address.
- **Replace the headshot** with a higher-resolution photo when you have one — drop it in `assets/img/` named `headshot.jpg` and it updates everywhere at once.
- **Add the Endeavor Health affiliation back** when your employment starts. Archived version **V9** still has all of that wording ready to restore.
