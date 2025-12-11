#!/usr/bin/env python3
"""
Example usage of PiazzaPuller class programmatically
"""

from piazza_puller import PiazzaPuller
import json

def example_pull_posts():
    """Example: Pull posts from Piazza"""
    print("=" * 50)
    print("Example: Pulling Posts")
    print("=" * 50)
    
    # Initialize puller
    puller = PiazzaPuller()
    
    # Authenticate (will prompt for credentials)
    if not puller.authenticate():
        print("Authentication failed")
        return
    
    # Set network (will prompt if not provided)
    network_id = input("Enter Network ID: ").strip()
    if not puller.set_network(network_id):
        print("Failed to set network")
        return
    
    # Pull posts (limit to 5 for example)
    posts = puller.get_all_posts(limit=5, sleep=1.0)
    
    # Display results
    print(f"\nPulled {len(posts)} posts:")
    for post in posts:
        print(f"  - [{post['id']}] {post['subject'][:50]}...")
        print(f"    Author: {post.get('author_name', 'Unknown')}")
        print(f"    Follow-ups: {post['num_followups']}")
    
    # Export to JSON
    puller.export_to_json(posts, 'example_posts.json')
    print("\n✓ Exported to example_posts.json")


def example_pull_users():
    """Example: Pull users from Piazza"""
    print("=" * 50)
    print("Example: Pulling Users")
    print("=" * 50)
    
    # Initialize with credentials (or use config)
    puller = PiazzaPuller()
    
    if not puller.authenticate():
        return
    
    network_id = input("Enter Network ID: ").strip()
    if not puller.set_network(network_id):
        return
    
    # Pull users
    users = puller.get_users()
    
    # Display results
    print(f"\nFound {len(users)} users:")
    for user in users[:10]:  # Show first 10
        print(f"  - {user['name']} ({user['email']}) - {user['role']}")
    
    # Export to CSV
    puller.export_users_to_csv(users, 'example_users.csv')
    print("\n✓ Exported to example_users.csv")


def example_with_config():
    """Example: Using config file"""
    print("=" * 50)
    print("Example: Using Config File")
    print("=" * 50)
    
    import os
    
    if not os.path.exists('config.json'):
        print("✗ config.json not found. Please create it first.")
        print("  Copy config.json.example to config.json and fill in your credentials.")
        return
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize with config
    puller = PiazzaPuller(
        email=config.get('email'),
        password=config.get('password'),
        network_id=config.get('network_id')
    )
    
    if not puller.authenticate():
        return
    
    if not puller.set_network():
        return
    
    # Pull feed
    feed = puller.get_feed(limit=10)
    if feed:
        print(f"\nRetrieved feed with {len(feed.get('feed', []))} posts")
        puller.export_to_json(feed, 'example_feed.json')
        print("✓ Exported to example_feed.json")


if __name__ == '__main__':
    print("\nPiazza Data Puller - Example Usage\n")
    print("Choose an example to run:")
    print("1. Pull Posts")
    print("2. Pull Users")
    print("3. Use Config File (requires config.json)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        example_pull_posts()
    elif choice == '2':
        example_pull_users()
    elif choice == '3':
        example_with_config()
    else:
        print("Invalid choice")

