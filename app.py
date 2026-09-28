#!/usr/bin/env python3
"""
Piazza Data Puller - Web UI
Simple Flask web application for pulling data from Piazza
"""

import os
import json
import csv
import io
import zipfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, Response
from werkzeug.utils import secure_filename

from piazza_puller import PiazzaPuller

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'json'}
DEMO_MODE = os.environ.get('PIAZZA_DEMO_MODE', '').lower() in ('1', 'true', 'yes')
DEMO_EMAIL = 'admin@demo.com'
DEMO_PASSWORD = 'demo123'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Store puller instances in session (in production, use Redis or database)
puller_instances = {}


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', demo_mode=DEMO_MODE)


@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate with Piazza"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        network_id = data.get('network_id')  # Optional network ID from login
        
        if DEMO_MODE and email == DEMO_EMAIL and password == DEMO_PASSWORD:
            # Create a mock puller instance for demo
            class MockPuller:
                def __init__(self):
                    class DemoApi:
                        def get_user_profile(_self):
                            return {'name': 'Demo Admin', 'email': DEMO_EMAIL}

                        def get_user_classes(_self):
                            return [
                                {'name': 'Demo Class 1', 'term': 'Fall 2024', 'nid': 'demo_class_1', 'is_ta': False},
                                {'name': 'Demo Class 2', 'term': 'Spring 2024', 'nid': 'demo_class_2', 'is_ta': True},
                            ]

                    self.network = None
                    self.network_id = network_id
                    self.authenticated = True
                    self.p = DemoApi()
                
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


def export_to_json_memory(data):
    """Export data to JSON in memory"""
    output = io.StringIO()
    json.dump(data, output, indent=2, ensure_ascii=False, default=str)
    return output.getvalue().encode('utf-8')

def export_posts_to_csv_memory(posts):
    """Export posts to CSV in memory"""
    if not posts:
        return None
    
    output = io.StringIO()
    fieldnames = set()
    for post in posts:
        fieldnames.update(post.keys())
    fieldnames = sorted(list(fieldnames))
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for post in posts:
        row = {}
        for key, value in post.items():
            if isinstance(value, (list, dict)):
                row[key] = json.dumps(value)
            else:
                row[key] = value
        writer.writerow(row)
    
    return output.getvalue().encode('utf-8')

def export_users_to_csv_memory(users):
    """Export users to CSV in memory"""
    if not users:
        return None
    
    output = io.StringIO()
    fieldnames = ['id', 'name', 'email', 'role']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(users)
    
    return output.getvalue().encode('utf-8')

@app.route('/api/pull-data', methods=['POST'])
def pull_data():
    """Pull data from Piazza and return as direct download"""
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
        
        # Generate files in memory
        files_data = {}
        
        if format_type in ['json', 'both']:
            json_data = export_to_json_memory(result_data)
            files_data[f'{filename_base}.json'] = json_data
        
        if format_type in ['csv', 'both']:
            if data_type in ['posts', 'materials']:
                csv_data = export_posts_to_csv_memory(result_data)
                if csv_data:
                    files_data[f'{filename_base}.csv'] = csv_data
            elif data_type == 'users':
                csv_data = export_users_to_csv_memory(result_data)
                if csv_data:
                    files_data[f'{filename_base}.csv'] = csv_data
            elif data_type in ['feed', 'search']:
                # Feed and search results are in feed format, convert to list for CSV export
                if 'feed' in result_data:
                    feed_posts = result_data['feed']
                    csv_data = export_posts_to_csv_memory(feed_posts)
                    if csv_data:
                        files_data[f'{filename_base}.csv'] = csv_data
        
        # If only one file, return it directly
        if len(files_data) == 1:
            filename, file_data = next(iter(files_data.items()))
            return Response(
                file_data,
                mimetype='application/json' if filename.endswith('.json') else 'text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Length': str(len(file_data))
                }
            )
        
        # If multiple files, zip them
        elif len(files_data) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for filename, file_data in files_data.items():
                    zip_file.writestr(filename, file_data)
            zip_buffer.seek(0)
            
            zip_filename = f'{filename_base}.zip'
            return Response(
                zip_buffer.getvalue(),
                mimetype='application/zip',
                headers={
                    'Content-Disposition': f'attachment; filename="{zip_filename}"',
                    'Content-Length': str(len(zip_buffer.getvalue()))
                }
            )
        else:
            return jsonify({'success': False, 'error': 'No files generated'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download an exported file from the current session"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in puller_instances:
            return jsonify({'error': 'Not authenticated'}), 401

        safe_name = secure_filename(filename)
        if not safe_name:
            return jsonify({'error': 'Invalid filename'}), 400

        output_dir = os.path.abspath(OUTPUT_FOLDER)
        file_path = os.path.abspath(os.path.join(output_dir, safe_name))
        if os.path.commonpath([output_dir, file_path]) != output_dir:
            return jsonify({'error': 'Invalid filename'}), 400

        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True)
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
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    host = os.environ.get('PIAZZA_PULLER_HOST', '127.0.0.1')
    port = int(os.environ.get('PIAZZA_PULLER_PORT', '5001'))
    print("=" * 50)
    print("Piazza Data Puller - Web UI")
    print("=" * 50)
    print(f"Starting server on http://{host}:{port}")
    if DEMO_MODE:
        print("Demo mode is ON (PIAZZA_DEMO_MODE). Login: admin@demo.com / demo123")
    print("Open your browser and navigate to the URL above")
    print("=" * 50)
    print()
    app.run(debug=debug, host=host, port=port)

