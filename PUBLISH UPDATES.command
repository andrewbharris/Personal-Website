#!/bin/bash
# ============================================================
#  PUBLISH UPDATES
#  Double-click this file to push your latest website changes
#  live to andrewbharrismd.com
# ============================================================

cd "$(dirname "$0")" || exit 1

echo ""
echo "=============================================="
echo "  Publishing andrewbharrismd.com"
echo "=============================================="
echo ""

if [ ! -d ".git" ]; then
  echo "  This folder is not connected to GitHub yet."
  echo "  See HOW TO PUBLISH.md for the one-time setup."
  echo ""
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi

# --- 1. Save any edits made on this computer ---
if [ -n "$(git status --porcelain)" ]; then
  echo "  Files changed on this computer:"
  echo ""
  git status --short | sed 's/^/    /'
  echo ""
  read -r -p "  Publish these changes? (y/n) " REPLY
  echo ""
  if [ "$REPLY" != "y" ] && [ "$REPLY" != "Y" ]; then
    echo "  Cancelled. Nothing was published."
    echo ""
    read -n 1 -s -r -p "Press any key to close..."
    exit 0
  fi
  git add -A
  git commit -q -m "Website update - $(date '+%B %-d, %Y at %-I:%M %p')"
  echo "  Saved."
  echo ""
else
  echo "  No new edits on this computer."
  echo ""
fi

# --- 2. Check whether anything still needs uploading ---
echo "  Checking GitHub..."
if ! git fetch -q 2>/dev/null; then
  echo ""
  echo "  Could not reach GitHub. Check your internet connection."
  echo "  Your work is saved safely on this computer."
  echo ""
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi

BRANCH=$(git branch --show-current)
AHEAD=$(git rev-list --count origin/"$BRANCH"..HEAD 2>/dev/null || echo 0)
BEHIND=$(git rev-list --count HEAD..origin/"$BRANCH" 2>/dev/null || echo 0)

if [ "$AHEAD" = "0" ] && [ "$BEHIND" = "0" ]; then
  echo ""
  echo "  Everything is already published. The live site is up to date."
  echo ""
  read -n 1 -s -r -p "Press any key to close..."
  exit 0
fi

# --- 3. Bring down anything changed on GitHub's side ---
#     (GitHub itself makes commits when you change Pages settings)
if [ "$BEHIND" != "0" ]; then
  echo "  GitHub has $BEHIND change(s) this computer doesn't have. Merging..."
  if ! git pull --rebase -q; then
    echo ""
    echo "  The two copies conflict and need a person to sort out."
    echo "  Nothing was lost. Open GitHub Desktop, or ask Claude for help."
    echo ""
    read -n 1 -s -r -p "Press any key to close..."
    exit 1
  fi
  echo "  Merged."
  echo ""
fi

# --- 4. Upload ---
echo "  Uploading to GitHub..."
if git push -q; then
  echo ""
  echo "  =========================================="
  echo "   Published successfully."
  echo ""
  echo "   Your changes will appear at"
  echo "   https://andrewbharrismd.com"
  echo "   within about a minute. Refresh with"
  echo "   Cmd+Shift+R to see them."
  echo "  =========================================="
else
  echo ""
  echo "  Upload failed."
  echo ""
  echo "  If it asked for a username and password: GitHub no longer"
  echo "  accepts your account password here. Open GitHub Desktop and"
  echo "  click Push origin instead, which signs you in securely."
  echo ""
  echo "  Your work is saved on this computer. Nothing was lost."
fi

echo ""
read -n 1 -s -r -p "Press any key to close..."
