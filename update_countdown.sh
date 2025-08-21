#!/bin/bash
# Simple script to update countdown via curl
# Usage: ./update_countdown.sh "Round 2 finishes in" 600

PORT=8000
URL="http://localhost:${PORT}/api/countdown"

if [ $# -eq 0 ]; then
    echo "Usage:"
    echo "  ./update_countdown.sh 'Round 2 finishes in' 600"
    echo "  ./update_countdown.sh 'Final round ends in' 300"
    echo "  ./update_countdown.sh 'Break time ends in' 900"
    echo ""
    echo "Current countdown settings:"
    curl -s ${URL} | python3 -m json.tool
    exit 1
fi

TEXT="$1"
DURATION="$2"

# Build JSON payload
if [ -n "$TEXT" ] && [ -n "$DURATION" ]; then
    JSON="{\"text\":\"$TEXT\",\"duration\":$DURATION}"
elif [ -n "$TEXT" ]; then
    JSON="{\"text\":\"$TEXT\"}"
elif [ -n "$DURATION" ]; then
    JSON="{\"duration\":$DURATION}"
else
    echo "Error: No valid parameters provided"
    exit 1
fi

echo "Updating countdown..."
echo "Text: $TEXT"
echo "Duration: $DURATION seconds"

curl -X POST \
     -H "Content-Type: application/json" \
     -d "$JSON" \
     ${URL}

echo ""
echo "Update complete!"
