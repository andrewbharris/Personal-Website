#!/bin/bash
# Double-click this file to open the visual website editor.
# It starts a small local server and opens the editor in Google Chrome.
# Keep the Terminal window that opens; close it when you're finished editing.

cd "$(dirname "$0")" || exit 1

PORT=8123
echo "======================================================"
echo "  Andrew B. Harris, MD — Website Editor"
echo "======================================================"
echo ""
echo "Opening the editor in Google Chrome..."
echo "Keep THIS window open while you edit. Close it when done."
echo ""

# Start a local server in the background (ignore error if the port is already in use)
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!

sleep 1

# Open the editor in Chrome (falls back to default browser if Chrome isn't found)
if open -a "Google Chrome" "http://127.0.0.1:$PORT/USE%20THIS%20TO%20HAND-EDIT%20CONTENT.html" 2>/dev/null; then
  :
else
  open "http://127.0.0.1:$PORT/USE%20THIS%20TO%20HAND-EDIT%20CONTENT.html"
fi

# Keep running so the server stays alive until you close this window
wait "$SERVER_PID"
