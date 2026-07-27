#!/bin/bash
# ============================================================
#  PUBLISH UPDATES
#  Double-click this file to push your latest website changes
#  live to andrewbharrismd.com
#
#  It saves every change in this folder, uploads it to GitHub,
#  and GitHub Pages rebuilds the site (usually within a minute).
# ============================================================

cd "$(dirname "$0")" || exit 1

echo ""
echo "=============================================="
echo "  Publishing andrewbharrismd.com"
echo "=============================================="
echo ""

# --- Safety check: is this folder connected to GitHub yet? ---
if [ ! -d ".git" ]; then
  echo "  This folder is not connected to GitHub yet."
  echo "  Follow the one-time setup in HOW TO PUBLISH.md first."
  echo ""
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi

# --- Show what changed ---
CHANGES=$(git status --porcelain)
if [ -z "$CHANGES" ]; then
  echo "  No changes to publish. The live site is already up to date."
  echo ""
  read -n 1 -s -r -p "Press any key to close..."
  exit 0
fi

echo "  These files changed:"
echo ""
git status --short | sed 's/^/    /'
echo ""

# --- Confirm ---
read -r -p "  Publish these changes to the live site? (y/n) " REPLY
echo ""
if [ "$REPLY" != "y" ] && [ "$REPLY" != "Y" ]; then
  echo "  Cancelled. Nothing was published."
  echo ""
  read -n 1 -s -r -p "Press any key to close..."
  exit 0
fi

# --- Publish ---
STAMP=$(date "+%B %-d, %Y at %-I:%M %p")
git add -A
git commit -m "Website update - $STAMP"

echo ""
echo "  Uploading to GitHub..."
if git push; then
  echo ""
  echo "  =========================================="
  echo "   Published successfully."
  echo ""
  echo "   Your changes will appear at"
  echo "   https://andrewbharrismd.com"
  echo "   within about a minute. You may need to"
  echo "   refresh with Cmd+Shift+R to see them."
  echo "  =========================================="
else
  echo ""
  echo "  Upload failed. The most common reasons:"
  echo "    - No internet connection"
  echo "    - GitHub is asking you to sign in again"
  echo ""
  echo "  Your changes are saved locally and nothing was lost."
  echo "  Try again, or ask Claude for help."
fi

echo ""
read -n 1 -s -r -p "Press any key to close..."
