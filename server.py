#!/usr/bin/env python3
"""
Simple HTTP server that provides a JSON API to list pictures in the pictures folder.
This allows the HTML page to dynamically discover available images.
"""

import http.server
import socketserver
import json
import os
from pathlib import Path
import urllib.parse
from datetime import datetime, timedelta
import re
import shutil
import tempfile

# Global variables to store countdown settings
countdown_text = "Round 1 finishes in"
countdown_duration = 5 * 60  # 5 minutes in seconds
countdown_target_time = None  # Will store target time as datetime object

def load_countdown_settings():
    """Load countdown settings from the times file"""
    global countdown_text, countdown_duration, countdown_target_time
    
    times_file = Path('times')
    if times_file.exists():
        try:
            with open(times_file, 'r') as f:
                data = json.load(f)
                countdown_text = data.get('text', countdown_text)
                countdown_duration = data.get('duration', countdown_duration)
                
                # Load target time if it exists
                if 'target_time' in data and data['target_time']:
                    countdown_target_time = datetime.fromisoformat(data['target_time'])
                    # Recalculate duration if target time is set
                    now = datetime.now()
                    remaining_seconds = int((countdown_target_time - now).total_seconds())
                    if remaining_seconds > 0:
                        countdown_duration = remaining_seconds
                    else:
                        countdown_duration = 0
                        
            print(f"Loaded countdown settings: {countdown_text}, duration: {countdown_duration}s")
        except Exception as e:
            print(f"Error loading countdown settings: {e}, using defaults")

def save_countdown_settings():
    """Save countdown settings to the times file"""
    global countdown_text, countdown_duration, countdown_target_time
    
    data = {
        'text': countdown_text,
        'duration': countdown_duration,
        'target_time': countdown_target_time.isoformat() if countdown_target_time else None
    }
    
    try:
        with open('times', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved countdown settings to times file")
    except Exception as e:
        print(f"Error saving countdown settings: {e}")

class PictureHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging for API requests and picture requests
        if args and len(args) > 0 and isinstance(args[0], str):
            request_path = args[0]
            if '/api/' in request_path or '/pictures/' in request_path or '/favicon.ico' in request_path:
                return
        super().log_message(format, *args)
    
    def do_GET(self):
        if self.path == '/api/countdown':
            self.send_countdown_json()
        elif self.path == '/api/pictures':
            self.send_pictures_json()
        elif self.path == '/admin':
            self.serve_admin_page()
        elif self.path == '/favicon.ico':
            self.send_favicon()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/countdown':
            self.update_countdown()
        elif self.path == '/api/upload':
            self.handle_file_upload()
        else:
            self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        if self.path.startswith('/api/delete/'):
            filename = urllib.parse.unquote(self.path[12:])  # Remove '/api/delete/'
            self.delete_picture(filename)
        else:
            self.send_error(404, "Not Found")
    
    def send_favicon(self):
        """Send empty favicon to prevent 404 errors"""
        self.send_response(204)  # No Content
        self.end_headers()
    
    def serve_admin_page(self):
        """Serve the admin HTML page"""
        try:
            admin_file = Path('admin.html')
            if admin_file.exists():
                with open(admin_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_error(404, "Admin page not found")
        except Exception as e:
            self.send_error(500, f"Error serving admin page: {e}")
    
    def send_pictures_json(self):
        """Send JSON list of available pictures"""
        pictures_dir = Path('pictures')
        picture_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        pictures = []
        if pictures_dir.exists():
            for file in pictures_dir.iterdir():
                if file.is_file() and file.suffix.lower() in picture_extensions:
                    pictures.append(f'pictures/{file.name}')
        
        # Sort pictures naturally
        pictures.sort()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps({
            'pictures': pictures,
            'count': len(pictures)
        })
        self.wfile.write(response.encode())
    
    def send_countdown_json(self):
        """Send current countdown settings"""
        global countdown_text, countdown_duration, countdown_target_time
        
        # If we have a target time, calculate remaining duration
        if countdown_target_time:
            now = datetime.now()
            remaining_seconds = int((countdown_target_time - now).total_seconds())
            
            # If target time has passed, show 0 instead of setting for next day
            if remaining_seconds <= 0:
                countdown_duration = 0
            else:
                countdown_duration = remaining_seconds
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps({
            'text': countdown_text,
            'duration': countdown_duration,
            'target_time': countdown_target_time.strftime('%H:%M') if countdown_target_time else None
        })
        self.wfile.write(response.encode())
    
    def update_countdown(self):
        """Update countdown settings"""
        global countdown_text, countdown_duration, countdown_target_time
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'text' in data:
                countdown_text = data['text']
            
            # Handle both duration and target_time
            if 'target_time' in data:
                # Parse time format like "12:05" or "23:30"
                time_str = data['target_time']
                time_match = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
                if time_match:
                    hours = int(time_match.group(1))
                    minutes = int(time_match.group(2))
                    
                    if 0 <= hours <= 23 and 0 <= minutes <= 59:
                        # Create target datetime for today
                        now = datetime.now()
                        target = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                        
                        # If target time has already passed today, set for tomorrow
                        if target <= now:
                            target = target + timedelta(days=1)
                        
                        countdown_target_time = target
                        countdown_duration = int((target - now).total_seconds())
                    else:
                        raise ValueError("Invalid time format: hours must be 0-23, minutes 0-59")
                else:
                    raise ValueError("Invalid time format. Use HH:MM format (e.g., '12:05')")
            
            elif 'duration' in data:
                # Traditional duration-based countdown
                countdown_duration = int(data['duration'])
                countdown_target_time = None
            
            # Save settings to file after updating
            save_countdown_settings()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                'success': True,
                'text': countdown_text,
                'duration': countdown_duration,
                'target_time': countdown_target_time.strftime('%H:%M') if countdown_target_time else None
            })
            self.wfile.write(response.encode())
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                'success': False,
                'error': str(e)
            })
            self.wfile.write(response.encode())
    
    def handle_file_upload(self):
        """Handle file upload for pictures"""
        try:
            # Ensure pictures directory exists
            pictures_dir = Path('pictures')
            pictures_dir.mkdir(exist_ok=True)
            
            # Parse the multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                raise ValueError("Invalid content type")
            
            # Get boundary
            boundary = content_type.split('boundary=')[1]
            if boundary.startswith('"') and boundary.endswith('"'):
                boundary = boundary[1:-1]
            
            # Read the content
            content_length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(content_length)
            
            # Simple multipart parsing
            parts = data.split(f'--{boundary}'.encode())
            
            uploaded_files = []
            for part in parts:
                if b'filename=' in part and b'Content-Type: image/' in part:
                    # Extract filename
                    lines = part.split(b'\r\n')
                    filename = None
                    file_data = None
                    
                    for i, line in enumerate(lines):
                        if b'filename=' in line:
                            # Extract filename from Content-Disposition header
                            line_str = line.decode('utf-8')
                            filename_start = line_str.find('filename="') + 10
                            filename_end = line_str.find('"', filename_start)
                            filename = line_str[filename_start:filename_end]
                            
                            # Find the empty line that separates headers from data
                            for j in range(i + 1, len(lines)):
                                if lines[j] == b'':
                                    # File data starts after the empty line
                                    file_data = b'\r\n'.join(lines[j + 1:])
                                    # Remove trailing boundary data
                                    if file_data.endswith(b'\r\n'):
                                        file_data = file_data[:-2]
                                    break
                            break
                    
                    if filename and file_data:
                        # Save the file
                        file_path = pictures_dir / filename
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        uploaded_files.append(filename)
            
            if uploaded_files:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = json.dumps({
                    'success': True,
                    'uploaded_files': uploaded_files,
                    'count': len(uploaded_files)
                })
                self.wfile.write(response.encode())
            else:
                raise ValueError("No valid image files found")
                
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                'success': False,
                'error': str(e)
            })
            self.wfile.write(response.encode())
    
    def delete_picture(self, filename):
        """Delete a picture file"""
        try:
            # Security check: ensure filename doesn't contain path traversal
            if '..' in filename or '/' in filename or '\\' in filename:
                raise ValueError("Invalid filename")
            
            file_path = Path('pictures') / filename
            
            if not file_path.exists():
                raise ValueError("File not found")
            
            if not file_path.is_file():
                raise ValueError("Not a file")
            
            # Delete the file
            file_path.unlink()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                'success': True,
                'message': f'File {filename} deleted successfully'
            })
            self.wfile.write(response.encode())
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                'success': False,
                'error': str(e)
            })
            self.wfile.write(response.encode())

if __name__ == "__main__":
    # Load countdown settings from file on startup
    load_countdown_settings()
    
    # Try multiple ports to find one that's available
    for PORT in range(8000, 8010):
        try:
            with socketserver.TCPServer(("", PORT), PictureHandler) as httpd:
                print(f"Starting server at http://localhost:{PORT}")
                print(f"📺 Slideshow: http://localhost:{PORT}")
                print(f"⚙️  Admin Panel: http://localhost:{PORT}/admin")
                print("Add pictures to the 'pictures' folder and they will appear automatically!")
                print("Press Ctrl+C to stop the server")
                httpd.serve_forever()
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"Port {PORT} is in use, trying next port...")
                continue
            else:
                raise
        break
    else:
        print("Could not find an available port between 8000-8009")
        print("Please close other applications using these ports or restart your computer")
