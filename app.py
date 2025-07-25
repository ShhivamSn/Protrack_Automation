from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import threading
import os
from datetime import datetime
import sys
import io
from contextlib import redirect_stdout
from protrack_automation import run_automation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to track automation status
automation_running = False
automation_thread = None

class StatusCapture:
    def __init__(self):
        self.output = []
    
    def write(self, text):
        if text.strip():
            self.output.append(text.strip())
            socketio.emit('status_update', {'message': text.strip()})
    
    def flush(self):
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_automation', methods=['POST'])
def start_automation():
    global automation_running, automation_thread
    
    if automation_running:
        return jsonify({'status': 'error', 'message': 'Automation is already running'})
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not all([username, password, start_date, end_date]):
        return jsonify({'status': 'error', 'message': 'All fields are required'})
    
    # Validate date format
    try:
        datetime.strptime(start_date, '%m/%d/%Y')
        datetime.strptime(end_date, '%m/%d/%Y')
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid date format. Use MM/DD/YYYY'})
    
    # Start automation in a separate thread
    automation_thread = threading.Thread(
        target=run_automation_thread,
        args=(username, password, start_date, end_date)
    )
    automation_thread.daemon = True
    automation_running = True
    automation_thread.start()
    
    return jsonify({'status': 'success', 'message': 'Automation started successfully'})

def run_automation_thread(username, password, start_date, end_date):
    global automation_running
    
    try:
        # Capture stdout to send status updates
        status_capture = StatusCapture()
        
        # Redirect stdout to our custom capture
        old_stdout = sys.stdout
        sys.stdout = status_capture
        
        socketio.emit('status_update', {'message': 'Starting ProTrack automation...'})
        
        # Run the automation
        run_automation(username, password, start_date, end_date)
        
        socketio.emit('status_update', {'message': 'Automation completed successfully!'})
        socketio.emit('automation_complete', {'status': 'success'})
        
    except Exception as e:
        error_msg = f"Automation failed: {str(e)}"
        socketio.emit('status_update', {'message': error_msg})
        socketio.emit('automation_complete', {'status': 'error', 'message': error_msg})
    
    finally:
        # Restore stdout
        sys.stdout = old_stdout
        automation_running = False

@app.route('/stop_automation', methods=['POST'])
def stop_automation():
    global automation_running
    
    if not automation_running:
        return jsonify({'status': 'error', 'message': 'No automation is currently running'})
    
    automation_running = False
    socketio.emit('status_update', {'message': 'Automation stopped by user'})
    
    return jsonify({'status': 'success', 'message': 'Automation stopped'})

@app.route('/status')
def get_status():
    return jsonify({'running': automation_running})

@socketio.on('connect')
def handle_connect():
    emit('status_update', {'message': 'Connected to ProTrack Automation'})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('downloads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)