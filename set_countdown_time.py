#!/usr/bin/env python3
"""
Script to set the countdown to a specific time.
Usage: python set_countdown_time.py "12:05" "Round 1 finishes at"
"""

import requests
import sys
import json

def set_countdown_time(target_time, text="Round finishes at"):
    """Set countdown to target time"""
    url = "http://localhost:8000/api/countdown"
    
    data = {
        "target_time": target_time,
        "text": text
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Countdown set successfully!")
                print(f"   Target time: {result.get('target_time')}")
                print(f"   Text: {result.get('text')}")
                print(f"   Duration: {result.get('duration')} seconds")
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server.py is running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python set_countdown_time.py <time> [text]")
        print("Example: python set_countdown_time.py \"12:05\" \"Round 1 finishes at\"")
        print("Time format: HH:MM (24-hour format)")
        return
    
    target_time = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "Round finishes at"
    
    set_countdown_time(target_time, text)

if __name__ == "__main__":
    main()
