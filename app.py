#!/usr/bin/env python3
"""
Piazza Data Puller - Web UI
Simple Flask web application for pulling data from Piazza
"""

import os
import json
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename

from piazza_puller import PiazzaPuller

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'json'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Store puller instances in session (in production, use Redis or database)
puller_instances = {}


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate with Piazza"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        network_id = data.get('network_id')  # Optional network ID from login
        
        # DEMO MODE: Allow fake admin login for testing UI
        DEMO_MODE = True  # Set to False to disable demo mode
        DEMO_EMAIL = "admin@demo.com"
        DEMO_PASSWORD = "demo123"
        
        if DEMO_MODE and email == DEMO_EMAIL and password == DEMO_PASSWORD:
            # Create a mock puller instance for demo
            class MockPuller:
                def __init__(self):
                    self.network = None
                    self.network_id = network_id
                    self.authenticated = True
                    self.p = type('obj', (object,), {
                        'get_user_profile': lambda: {'name': 'Demo Admin', 'email': DEMO_EMAIL},
                        'get_user_classes': lambda: [
                            {'name': 'Demo Class 1', 'term': 'Fall 2024', 'nid': 'demo_class_1', 'is_ta': False},
                            {'name': 'Demo Class 2', 'term': 'Spring 2024', 'nid': 'demo_class_2', 'is_ta': True}
                        ]
                    })()
                
                def set_network(self, nid):
                    self.network_id = nid
                    self.network = type('obj', (object,), {'_nid': nid})()
                    return True
                
                def get_all_posts(self, limit=None, sleep=0):
                    return [{'id': 1, 'subject': 'Demo Post 1', 'content': 'This is a demo post'}]
                
                def get_users(self):
                    return [{'id': '1', 'name': 'Demo User', 'email': 'user@demo.com', 'role': 'student'}]
                
                def get_feed(self, limit=100, offset=0):
                    return {'feed': [{'id': 1, 'subject': 'Demo Feed Post'}]}
                
                def get_statistics(self):
                    return {'total_posts': 10, 'total_users': 5}
                
                def get_course_materials(self, limit=None, sleep=0):
                    return [{'id': 1, 'subject': 'Demo Material', 'attachments': []}]
                
                def search_feed(self, query):
                    return {'feed': [{'id': 1, 'subject': f'Search result for: {query}'}]}
                
                def export_to_json(self, data, filename):
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    return True
                
                def export_posts_to_csv(self, posts, filename):
                    if not posts:
                        return False
                    with open(filename, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=posts[0].keys() if posts else [])
                        writer.writeheader()
                        writer.writerows(posts)
                    return True
                
                def export_users_to_csv(self, users, filename):
                    if not users:
                        return False
                    with open(filename, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'email', 'role'])
                        writer.writeheader()
                        writer.writerows(users)
                    return True
            
            puller = MockPuller()
            session_id = os.urandom(16).hex()
            puller_instances[session_id] = puller
            session['session_id'] = session_id
            
            response_data = {
                'success': True,
                'message': 'Demo mode: Authentication successful',
                'user': {
                    'name': 'Demo Admin',
                    'email': DEMO_EMAIL
                },
                'demo_mode': True
            }
            
            if network_id:
                if puller.set_network(network_id):
                    response_data['network_set'] = True
                    response_data['network_id'] = network_id
            
            return jsonify(response_data)
        
        # Real authentication
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        # Create puller instance
        puller = PiazzaPuller(email=email, password=password, network_id=network_id)
        
        # Authenticate
        if puller.authenticate():
            # Store in session
            session_id = os.urandom(16).hex()
            puller_instances[session_id] = puller
            session['session_id'] = session_id
            
            # Get user profile
            profile = puller.p.get_user_profile()
            
            response_data = {
                'success': True,
                'message': 'Authentication successful',
                'user': {
                    'name': profile.get('name', 'Unknown'),
                    'email': email
                }
            }
            
            # If network ID was provided and set successfully, include it in response
            if network_id:
                if puller.set_network(network_id):
                    response_data['network_set'] = True
                    response_data['network_id'] = network_id
            
            return jsonify(response_data)
        else:
            return jsonify({'success': False, 'error': 'Authentication failed'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/set-network', methods=['POST'])
def set_network():
    """Set the network (class) to pull data from"""
    try:
        data = request.json
        network_id = data.get('network_id')
        
        if not network_id:
            return jsonify({'success': False, 'error': 'Network ID is required'}), 400
        
        session_id = session.get('session_id')
        if not session_id or session_id not in puller_instances:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        puller = puller_instances[session_id]
        
        if puller.set_network(network_id):
            return jsonify({
                'success': True,
                'message': f'Connected to network: {network_id}'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to set network'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pull-data', methods=['POST'])
def pull_data():
    """Pull data from Piazza"""
    try:
        data = request.json
        data_type = data.get('type', 'posts')  # posts, users, feed, stats, materials
        limit = data.get('limit')
        format_type = data.get('format', 'json')  # json, csv, both
        
        session_id = session.get('session_id')
        if not session_id or session_id not in puller_instances:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        puller = puller_instances[session_id]
        
        if not puller.network:
            return jsonify({'success': False, 'error': 'Network not set'}), 400
        
        # Pull data based on type
        result_data = None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if data_type == 'posts':
            result_data = puller.get_all_posts(limit=limit, sleep=0.5)
            filename_base = f'posts_{timestamp}'
        elif data_type == 'users':
            result_data = puller.get_users()
            filename_base = f'users_{timestamp}'
        elif data_type == 'feed':
            result_data = puller.get_feed(limit=limit or 100, offset=0)
            filename_base = f'feed_{timestamp}'
        elif data_type == 'stats':
            result_data = puller.get_statistics()
            filename_base = f'statistics_{timestamp}'
        elif data_type == 'materials':
            result_data = puller.get_course_materials(limit=limit, sleep=0.5)
            filename_base = f'course_materials_{timestamp}'
        elif data_type == 'search':
            query = data.get('query')
            if not query:
                return jsonify({'success': False, 'error': 'Search query is required'}), 400
            result_data = puller.search_feed(query)
            filename_base = f'search_{query.replace(" ", "_")[:30]}_{timestamp}'
        else:
            return jsonify({'success': False, 'error': 'Invalid data type'}), 400
        
        if not result_data:
            return jsonify({'success': False, 'error': 'No data retrieved'}), 400
        
        # Export data
        files_created = []
        
        if format_type in ['json', 'both']:
            json_filename = os.path.join(OUTPUT_FOLDER, f'{filename_base}.json')
            if puller.export_to_json(result_data, json_filename):
                files_created.append(f'{filename_base}.json')
        
        if format_type in ['csv', 'both']:
            if data_type in ['posts', 'materials']:
                csv_filename = os.path.join(OUTPUT_FOLDER, f'{filename_base}.csv')
                if puller.export_posts_to_csv(result_data, csv_filename):
                    files_created.append(f'{filename_base}.csv')
            elif data_type == 'users':
                csv_filename = os.path.join(OUTPUT_FOLDER, f'{filename_base}.csv')
                if puller.export_users_to_csv(result_data, csv_filename):
                    files_created.append(f'{filename_base}.csv')
            elif data_type == 'search':
                # Search results are in feed format, convert to list for CSV export
                if 'feed' in result_data:
                    feed_posts = result_data['feed']
                    csv_filename = os.path.join(OUTPUT_FOLDER, f'{filename_base}.csv')
                    if puller.export_posts_to_csv(feed_posts, csv_filename):
                        files_created.append(f'{filename_base}.csv')
        
        # Get data summary
        if isinstance(result_data, list):
            count = len(result_data)
        elif isinstance(result_data, dict):
            if 'feed' in result_data:
                count = len(result_data['feed'])
            else:
                count = 1
        else:
            count = 1
        
        return jsonify({
            'success': True,
            'message': f'Successfully pulled {count} items',
            'count': count,
            'files': files_created,
            'preview': result_data[:5] if isinstance(result_data, list) else result_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download exported file"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user-classes', methods=['GET'])
def get_user_classes():
    """Get list of user's classes"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in puller_instances:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        puller = puller_instances[session_id]
        
        # Check if it's a mock puller (demo mode)
        if hasattr(puller, 'p') and hasattr(puller.p, 'get_user_classes'):
            classes = puller.p.get_user_classes()
        else:
            classes = puller.p.get_user_classes()
        
        return jsonify({
            'success': True,
            'classes': classes
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout and clear session"""
    session_id = session.get('session_id')
    if session_id and session_id in puller_instances:
        del puller_instances[session_id]
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


if __name__ == '__main__':
    print("=" * 50)
    print("Piazza Data Puller - Web UI")
    print("=" * 50)
    print("Starting server on http://localhost:5001")
    print("Open your browser and navigate to the URL above")
    print("=" * 50)
    print()
    app.run(debug=True, host='0.0.0.0', port=5001)

