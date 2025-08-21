#!/bin/bash
# Script to set countdown time using curl
# Usage: ./set_countdown_time.sh "12:05" "Round 1 finishes at"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <time> [text]"
    echo "Example: $0 \"12:05\" \"Round 1 finishes at\""
    echo "Time format: HH:MM (24-hour format)"
    exit 1
fi

TARGET_TIME="$1"
TEXT="${2:-Round finishes at}"

echo "Setting countdown to $TARGET_TIME with text: $TEXT"

curl -X POST http://localhost:8000/api/countdown \
     -H "Content-Type: application/json" \
     -d "{\"target_time\": \"$TARGET_TIME\", \"text\": \"$TEXT\"}" \
     && echo ""
