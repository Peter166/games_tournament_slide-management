#!/usr/bin/env python3
"""
Simple script to update the countdown text and duration via API
Usage examples:
  python3 update_countdown.py "Round 2 finishes in" 600
  python3 update_countdown.py "Final round ends in" 300
  python3 update_countdown.py "Break time ends in" 900
"""

import requests
import sys
import json

def update_countdown(text=None, duration=None, port=8000):
    """Update countdown via API"""
    url = f"http://localhost:{port}/api/countdown"
    
    data = {}
    if text:
        data['text'] = text
    if duration:
        data['duration'] = int(duration)
    
    if not data:
        print("No updates provided. Use: python3 update_countdown.py 'text' duration")
        return
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Countdown updated successfully!")
            print(f"   Text: {result['text']}")
            print(f"   Duration: {result['duration']} seconds ({result['duration']//60}:{result['duration']%60:02d})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Make sure the server is running: python3 server.py")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 update_countdown.py 'Round 2 finishes in' 600")
        print("  python3 update_countdown.py 'Final round ends in' 300")
        print("\nCurrent countdown settings:")
        
        # Show current settings
        try:
            response = requests.get("http://localhost:8000/api/countdown")
            if response.status_code == 200:
                data = response.json()
                print(f"  Text: {data['text']}")
                print(f"  Duration: {data['duration']} seconds ({data['duration']//60}:{data['duration']%60:02d})")
            else:
                print("  Could not fetch current settings")
        except:
            print("  Server not running or not accessible")
        sys.exit(1)
    
    text = sys.argv[1] if len(sys.argv) > 1 else None
    duration = sys.argv[2] if len(sys.argv) > 2 else None
    
    update_countdown(text, duration)
