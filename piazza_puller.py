#!/usr/bin/env python3
"""
Piazza Data Puller - A simple application to pull data from Piazza
"""

import json
import csv
import os
import sys
import argparse
import re
from datetime import datetime
from typing import Dict, List, Optional

try:
    from piazza_api import Piazza
    from piazza_api.exceptions import AuthenticationError, NotAuthenticatedError, RequestError
except ImportError:
    print("Error: piazza-api is not installed. Please run: pip install piazza-api")
    sys.exit(1)


class PiazzaPuller:
    """Main class for pulling data from Piazza"""
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None, 
                 network_id: Optional[str] = None):
        self.p = Piazza()
        self.network = None
        self.email = email
        self.password = password
        self.network_id = network_id
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with Piazza"""
        try:
            if self.email and self.password:
                print("Authenticating with Piazza...")
                self.p.user_login(email=self.email, password=self.password)
            else:
                print("Please enter your Piazza credentials:")
                self.p.user_login()
            
            # Test authentication by getting profile
            profile = self.p.get_user_profile()
            print(f"✓ Successfully authenticated as: {profile.get('name', 'Unknown')}")
            self.authenticated = True
            return True
            
        except AuthenticationError as e:
            print(f"✗ Authentication failed: {e}")
            return False
        except Exception as e:
            print(f"✗ Error during authentication: {e}")
            return False
    
    def set_network(self, network_id: Optional[str] = None) -> bool:
        """Set the network (class) to pull data from"""
        try:
            if not self.authenticated:
                print("✗ Please authenticate first")
                return False
            
            network_id = network_id or self.network_id
            if not network_id:
                print("✗ Network ID is required")
                return False
            
            self.network = self.p.network(network_id)
            self.network_id = network_id
            print(f"✓ Connected to network: {network_id}")
            return True
            
        except Exception as e:
            print(f"✗ Error setting network: {e}")
            return False
    
    def get_all_posts(self, limit: Optional[int] = None, sleep: float = 1.0) -> List[Dict]:
        """Pull all posts from the network"""
        if not self.network:
            print("✗ Network not set. Please set network first.")
            return []
        
        print(f"Pulling posts from network {self.network_id}...")
        posts = []
        
        try:
            for i, post in enumerate(self.network.iter_all_posts(limit=limit, sleep=sleep)):
                post_data = {
                    'id': post.get('id'),
                    'subject': post.get('subject', ''),
                    'content': post.get('content', ''),
                    'type': post.get('type', ''),
                    'created': post.get('created', ''),
                    'updated': post.get('updated', ''),
                    'num_followups': len(post.get('children', [])),
                    'tags': post.get('tags', []),
                    'folders': post.get('folders', []),
                    'status': post.get('status', ''),
                    'is_pinned': post.get('is_pinned', False),
                    'is_resolved': post.get('is_resolved', False),
                }
                
                # Extract author information
                if 'history' in post and len(post['history']) > 0:
                    author = post['history'][0]
                    post_data['author'] = author.get('uid', '')
                    post_data['author_name'] = author.get('name', 'Unknown')
                
                # Extract answer information
                if 'children' in post:
                    answers = []
                    for child in post['children']:
                        if child.get('type') == 'i_answer':
                            answers.append({
                                'content': child.get('subject', ''),
                                'revision': child.get('revision', 0)
                            })
                    post_data['instructor_answers'] = answers
                
                # Extract attachments and course materials
                attachments = []
                if 'data' in post:
                    data = post.get('data', {})
                    # Check for embed_links (deprecated but might still have data)
                    if 'embed_links' in data:
                        attachments.extend(data.get('embed_links', []))
                
                # Check for attachments in history
                if 'history' in post:
                    for hist_item in post['history']:
                        if 'data' in hist_item:
                            hist_data = hist_item.get('data', {})
                            if 'attachments' in hist_data:
                                attachments.extend(hist_data.get('attachments', []))
                            if 'embed_links' in hist_data:
                                attachments.extend(hist_data.get('embed_links', []))
                
                # Extract links from content (basic URL extraction)
                content = post_data.get('content', '')
                urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content)
                if urls:
                    post_data['links'] = urls
                
                if attachments:
                    post_data['attachments'] = attachments
                
                posts.append(post_data)
                
                if limit and (i + 1) >= limit:
                    break
                    
                if (i + 1) % 10 == 0:
                    print(f"  Pulled {i + 1} posts...")
            
            print(f"✓ Successfully pulled {len(posts)} posts")
            return posts
            
        except RequestError as e:
            print(f"✗ Error pulling posts: {e}")
            return posts
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return posts
    
    def get_feed(self, limit: int = 100, offset: int = 0) -> Dict:
        """Get feed from the network"""
        if not self.network:
            print("✗ Network not set. Please set network first.")
            return {}
        
        try:
            print(f"Getting feed (limit={limit}, offset={offset})...")
            feed = self.network.get_feed(limit=limit, offset=offset)
            print(f"✓ Retrieved feed with {len(feed.get('feed', []))} posts")
            return feed
        except Exception as e:
            print(f"✗ Error getting feed: {e}")
            return {}
    
    def get_users(self) -> List[Dict]:
        """Get all users from the network"""
        if not self.network:
            print("✗ Network not set. Please set network first.")
            return []
        
        try:
            print("Pulling user list...")
            users = self.network.get_all_users()
            
            user_data = []
            for user in users:
                user_data.append({
                    'id': user.get('id', ''),
                    'name': user.get('name', ''),
                    'email': user.get('email', ''),
                    'role': user.get('role', ''),
                })
            
            print(f"✓ Retrieved {len(user_data)} users")
            return user_data
            
        except Exception as e:
            print(f"✗ Error getting users: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get network statistics"""
        if not self.network:
            print("✗ Network not set. Please set network first.")
            return {}
        
        try:
            print("Getting network statistics...")
            stats = self.network.get_statistics()
            print("✓ Retrieved statistics")
            return stats
        except Exception as e:
            print(f"✗ Error getting statistics: {e}")
            return {}
    
    def search_feed(self, query: str) -> Dict:
        """Search for posts with query"""
        if not self.network:
            print("✗ Network not set. Please set network first.")
            return {}
        
        try:
            print(f"Searching for: '{query}'...")
            results = self.network.search_feed(query)
            count = len(results.get('feed', []))
            print(f"✓ Found {count} posts matching '{query}'")
            return results
        except Exception as e:
            print(f"✗ Error searching feed: {e}")
            return {}
    
    def get_course_materials(self, limit: Optional[int] = None, sleep: float = 1.0) -> List[Dict]:
        """Extract course materials (posts with attachments, links, or instructor notes)"""
        if not self.network:
            print("✗ Network not set. Please set network first.")
            return []
        
        print("Extracting course materials from posts...")
        materials = []
        
        try:
            for i, post in enumerate(self.network.iter_all_posts(limit=limit, sleep=sleep)):
                # Check if post contains course materials
                has_attachments = False
                has_links = False
                is_instructor_note = False
                
                # Check for attachments
                if 'data' in post:
                    data = post.get('data', {})
                    if data.get('embed_links') or data.get('attachments'):
                        has_attachments = True
                
                # Check if it's an instructor note
                tags = post.get('tags', [])
                if 'instructor-note' in tags or post.get('type') == 'note':
                    is_instructor_note = True
                
                # Extract links from content
                content = post.get('content', '') or post.get('subject', '')
                urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content)
                if urls:
                    has_links = True
                
                # Include if it has materials or is an instructor note
                if has_attachments or has_links or is_instructor_note:
                    material = {
                        'id': post.get('id'),
                        'subject': post.get('subject', ''),
                        'type': post.get('type', ''),
                        'created': post.get('created', ''),
                        'folders': post.get('folders', []),
                        'is_instructor_note': is_instructor_note,
                        'is_pinned': post.get('is_pinned', False),
                    }
                    
                    # Extract author
                    if 'history' in post and len(post['history']) > 0:
                        author = post['history'][0]
                        material['author_name'] = author.get('name', 'Unknown')
                    
                    # Extract attachments
                    attachments = []
                    if 'data' in post:
                        data = post.get('data', {})
                        if 'embed_links' in data:
                            attachments.extend(data.get('embed_links', []))
                        if 'attachments' in data:
                            attachments.extend(data.get('attachments', []))
                    
                    if attachments:
                        material['attachments'] = attachments
                    
                    # Extract links
                    if urls:
                        material['links'] = urls
                    
                    # Include content snippet
                    content_preview = (post.get('content', '') or post.get('subject', ''))[:200]
                    material['content_preview'] = content_preview
                    
                    materials.append(material)
                
                if limit and (i + 1) >= limit:
                    break
                    
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1} posts, found {len(materials)} materials...")
            
            print(f"✓ Found {len(materials)} course materials")
            return materials
            
        except Exception as e:
            print(f"✗ Error extracting course materials: {e}")
            return materials
    
    def export_to_json(self, data: any, filename: str) -> bool:
        """Export data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print(f"✓ Exported data to {filename}")
            return True
        except Exception as e:
            print(f"✗ Error exporting to JSON: {e}")
            return False
    
    def export_posts_to_csv(self, posts: List[Dict], filename: str) -> bool:
        """Export posts to CSV file"""
        if not posts:
            print("✗ No posts to export")
            return False
        
        try:
            # Get all unique keys from posts
            fieldnames = set()
            for post in posts:
                fieldnames.update(post.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for post in posts:
                    # Convert lists/dicts to strings for CSV
                    row = {}
                    for key, value in post.items():
                        if isinstance(value, (list, dict)):
                            row[key] = json.dumps(value)
                        else:
                            row[key] = value
                    writer.writerow(row)
            
            print(f"✓ Exported {len(posts)} posts to {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error exporting to CSV: {e}")
            return False
    
    def export_users_to_csv(self, users: List[Dict], filename: str) -> bool:
        """Export users to CSV file"""
        if not users:
            print("✗ No users to export")
            return False
        
        try:
            fieldnames = ['id', 'name', 'email', 'role']
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(users)
            
            print(f"✓ Exported {len(users)} users to {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error exporting users to CSV: {e}")
            return False


def load_config(config_file: str = 'config.json') -> Dict:
    """Load configuration from JSON file"""
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    return {}


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Piazza Data Puller - Pull data from Piazza',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python piazza_puller.py
  
  # Pull posts with credentials
  python piazza_puller.py --email user@example.com --network-id abc123 --pull posts
  
  # Pull users and export to CSV
  python piazza_puller.py --email user@example.com --network-id abc123 --pull users --format csv
        """
    )
    
    parser.add_argument('--email', help='Piazza email')
    parser.add_argument('--password', help='Piazza password')
    parser.add_argument('--network-id', '--nid', dest='network_id', help='Network ID (class ID)')
    parser.add_argument('--config', default='config.json', help='Config file path (default: config.json)')
    parser.add_argument('--pull', choices=['posts', 'users', 'feed', 'stats', 'materials', 'all'], 
                       default='posts', help='What to pull (default: posts)')
    parser.add_argument('--limit', type=int, help='Limit number of posts to pull')
    parser.add_argument('--format', choices=['json', 'csv', 'both'], default='json',
                       help='Export format (default: json)')
    parser.add_argument('--output-dir', default='output', help='Output directory (default: output)')
    parser.add_argument('--sleep', type=float, default=1.0, 
                       help='Sleep time between requests in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    email = args.email or config.get('email')
    password = args.password or config.get('password')
    network_id = args.network_id or config.get('network_id')
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize puller
    puller = PiazzaPuller(email=email, password=password, network_id=network_id)
    
    # Authenticate
    if not puller.authenticate():
        sys.exit(1)
    
    # Set network
    if not puller.set_network():
        if not network_id:
            network_id = input("Enter Network ID: ").strip()
            if not puller.set_network(network_id):
                sys.exit(1)
        else:
            sys.exit(1)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Pull data based on argument
    if args.pull in ['posts', 'all']:
        posts = puller.get_all_posts(limit=args.limit, sleep=args.sleep)
        if posts:
            if args.format in ['json', 'both']:
                filename = os.path.join(args.output_dir, f'posts_{timestamp}.json')
                puller.export_to_json(posts, filename)
            if args.format in ['csv', 'both']:
                filename = os.path.join(args.output_dir, f'posts_{timestamp}.csv')
                puller.export_posts_to_csv(posts, filename)
    
    if args.pull in ['users', 'all']:
        users = puller.get_users()
        if users:
            if args.format in ['json', 'both']:
                filename = os.path.join(args.output_dir, f'users_{timestamp}.json')
                puller.export_to_json(users, filename)
            if args.format in ['csv', 'both']:
                filename = os.path.join(args.output_dir, f'users_{timestamp}.csv')
                puller.export_users_to_csv(users, filename)
    
    if args.pull in ['feed', 'all']:
        feed = puller.get_feed(limit=args.limit or 100)
        if feed:
            filename = os.path.join(args.output_dir, f'feed_{timestamp}.json')
            puller.export_to_json(feed, filename)
    
    if args.pull in ['stats', 'all']:
        stats = puller.get_statistics()
        if stats:
            filename = os.path.join(args.output_dir, f'statistics_{timestamp}.json')
            puller.export_to_json(stats, filename)
    
    if args.pull in ['materials', 'all']:
        materials = puller.get_course_materials(limit=args.limit, sleep=args.sleep)
        if materials:
            if args.format in ['json', 'both']:
                filename = os.path.join(args.output_dir, f'course_materials_{timestamp}.json')
                puller.export_to_json(materials, filename)
            if args.format in ['csv', 'both']:
                filename = os.path.join(args.output_dir, f'course_materials_{timestamp}.csv')
                puller.export_posts_to_csv(materials, filename)
    
    print("\n✓ Data pull completed!")


if __name__ == '__main__':
    main()

