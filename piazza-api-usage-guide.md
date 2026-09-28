# Piazza API Usage Guide

This guide documents [`piazza-api`](https://github.com/hfaran/piazza-api), a third-party client for Piazza's internal API. It is not the API of this repository. This project only reads data through `PiazzaPuller`. Examples below that create, edit, or delete posts, or that add and remove users, are capabilities of `piazza-api`, not of this tool.

Network IDs and the demo login token in the examples are the public samples from the `piazza-api` documentation.

## Table of Contents

1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Basic Usage](#basic-usage)
4. [Network Operations](#network-operations)
5. [Post Operations](#post-operations)
6. [User Operations](#user-operations)
7. [Feed Operations](#feed-operations)
8. [Advanced Features](#advanced-features)
9. [Error Handling](#error-handling)
10. [Examples](#examples)

---

## Installation

### Using pip (Recommended)

```bash
pip install piazza-api
```

### From Source

```bash
git clone https://github.com/hfaran/piazza-api
cd piazza-api
python setup.py develop
```

### Dependencies

- `requests` - For HTTP requests
- `six` - For Python 2/3 compatibility

---

## Authentication

The API requires authentication before you can access any Piazza data. There are two main ways to authenticate:

### 1. User Login (Email/Password)

```python
from piazza_api import Piazza

p = Piazza()
p.user_login(email="your_email@example.com", password="your_password")
```

**Interactive Login:**
If you don't provide email and password, the API will prompt you:

```python
p = Piazza()
p.user_login()  # Will prompt for Email and Password
```

### 2. Demo Login (Share Your Class URL)

For accessing public/demo classes without credentials:

```python
p = Piazza()
# Option 1: Provide full URL
p.demo_login(url="https://piazza.com/demo_login?nid=hbj11a1gcvl1s6&auth=06c111b")

# Option 2: Provide just the auth token
p.demo_login(auth="06c111b")
```

### 3. Cookie-based Authentication

You can also save and reuse session cookies:

```python
from piazza_api.rpc import PiazzaRPC

# After initial login, save cookies
rpc = PiazzaRPC()
rpc.user_login(email="your_email@example.com", password="your_password")
cookies = rpc.get_cookies()

# Later, restore cookies
rpc2 = PiazzaRPC()
rpc2.set_cookies(cookies)
```

---

## Basic Usage

### Getting User Profile

```python
from piazza_api import Piazza

p = Piazza()
p.user_login(email="your_email@example.com", password="your_password")

# Get your profile
profile = p.get_user_profile()
print(profile)

# Get your status (includes all enrolled classes)
status = p.get_user_status()
print(status)

# Get list of your classes
classes = p.get_user_classes()
for cls in classes:
    print(f"{cls['name']} - {cls['term']} (Network ID: {cls['nid']})")
```

### Accessing a Network (Class)

To interact with a specific class, you need the network ID (nid). You can find this in the URL when viewing a class on Piazza:
- URL format: `https://piazza.com/class/{network_id}`

```python
# Get a network instance
network = p.network("hl5qm84dl4t3x2")  # Replace with your network ID
```

---

## Network Operations

### Getting Posts

#### Get a Single Post

```python
network = p.network("hl5qm84dl4t3x2")
post = network.get_post(100)  # Post ID (cid)
print(post)
```

#### Get All Posts

```python
# Iterate through all posts
posts = network.iter_all_posts(limit=10)  # Limit to 10 posts
for post in posts:
    print(f"Post {post['id']}: {post['subject']}")

# Get all posts with delay to avoid rate limiting
posts = network.iter_all_posts(limit=None, sleep=1)  # 1 second delay between requests
```

### Creating Posts

#### Create a Question or Note

```python
# Create a question
result = network.create_post(
    post_type="question",  # or "note"
    post_folders="homework",  # Folder name
    post_subject="How do I solve this problem?",
    post_content="<p>I'm having trouble with problem 3...</p>",  # HTML or plain text
    is_announcement=0,  # 0 for regular post, 1 for announcement
    bypass_email=0,  # 0 to send emails, 1 to bypass
    anonymous=False,  # Post anonymously
    is_private=False  # Private to instructors only
)

print(f"Created post with ID: {result['id']}")
```

#### Create a Follow-up

```python
post = network.get_post(100)  # Get existing post
followup = network.create_followup(
    post=post,  # Can also pass post ID directly
    content="This is a follow-up question",
    anonymous=False,
    instructor=False  # True if posting as instructor
)
```

#### Create an Instructor Answer

```python
post = network.get_post(100)
answer = network.create_instructor_answer(
    post=post,
    content="<p>Here's the solution...</p>",
    revision=0,  # 0 for first answer, increment for edits
    anonymous=False
)
```

#### Create a Reply to Follow-up

```python
followup_post = network.get_post(101)  # Follow-up post ID
reply = network.create_reply(
    post=followup_post,
    content="Thanks for the clarification!",
    anonymous=False
)
```

### Updating Posts

```python
post = network.get_post(100)
updated = network.update_post(
    post=post,  # Can also pass post ID
    content="<p>Updated content here</p>"
)
```

### Post Management

#### Mark as Duplicate

```python
network.mark_as_duplicate(
    duplicated_cid=200,  # Post to mark as duplicate
    master_cid=100,  # Original post to keep
    msg="This question was already asked"  # Optional message
)
```

#### Resolve Post

```python
post = network.get_post(100)
network.resolve_post(post)  # Mark as resolved
```

#### Pin/Unpin Post

```python
post = network.get_post(100)
network.pin_post(post)  # Pin the post
network.pin_post(post, unpin=True)  # Unpin the post
```

#### Delete Post

```python
post = network.get_post(100)
network.delete_post(post)  # Delete the post
```

#### Add/Remove Feedback (Good Note)

```python
post = network.get_post(100)
network.add_feedback(post)  # Mark as good note
network.remove_feedback(post)  # Unmark as good note
```

---

## User Operations

### Get Users

#### Get All Users in Network

```python
all_users = network.get_all_users()
for user in all_users:
    print(f"{user['name']} ({user['email']})")
```

#### Get Specific Users

```python
user_ids = ["user_id_1", "user_id_2"]
users = network.get_users(user_ids)
```

#### Iterate Through Users

```python
# Iterate all users
for user in network.iter_all_users():
    print(user['name'])

# Iterate specific users
for user in network.iter_users(["user_id_1", "user_id_2"]):
    print(user['name'])
```

### Manage Users

#### Add Students

```python
student_emails = ["student1@example.com", "student2@example.com"]
result = network.add_students(student_emails)
# Piazza will email these students with activation instructions
```

#### Remove Users

```python
user_ids = ["user_id_1", "user_id_2"]
remaining_users = network.remove_users(user_ids)
```

---

## Feed Operations

### Get Feed

```python
# Get feed with pagination
feed = network.get_feed(limit=100, offset=0)
for post in feed["feed"]:
    print(f"Post {post['id']}: {post['subject']}")

# Get more posts (pagination)
feed_page2 = network.get_feed(limit=100, offset=100)
```

### Filter Feed

The API provides several feed filters:

```python
# Get unread posts
unread_feed = network.get_filtered_feed(network.feed_filters.unread())

# Get posts you're following
following_feed = network.get_filtered_feed(network.feed_filters.following())

# Get posts in a specific folder
folder_feed = network.get_filtered_feed(
    network.feed_filters.folder("homework")
)
```

### Search Feed

```python
# Search for posts
results = network.search_feed("homework assignment")
for post in results["feed"]:
    print(f"Found: {post['subject']}")
```

### Get Statistics

```python
stats = network.get_statistics()
print(stats)  # Class statistics (viewable on Statistics page)
```

---

## Advanced Features

### Using PiazzaRPC Directly

For more direct access to Piazza's API:

```python
from piazza_api.rpc import PiazzaRPC

rpc = PiazzaRPC("hl5qm84dl4t3x2")  # Network ID
rpc.user_login(email="your_email@example.com", password="your_password")

# Direct API calls
post = rpc.content_get(cid=100)
users = rpc.get_all_users()
feed = rpc.get_my_feed(limit=50, offset=0)
```

### Custom Requests

You can make custom requests using the `request` method:

```python
from piazza_api.rpc import PiazzaRPC

rpc = PiazzaRPC("hl5qm84dl4t3x2")
rpc.user_login(email="your_email@example.com", password="your_password")

# Custom API call
result = rpc.request(
    method="content.get",
    data={"cid": 100, "student_view": None}
)
```

---

## Error Handling

The API raises specific exceptions for different error conditions:

```python
from piazza_api import Piazza
from piazza_api.exceptions import (
    AuthenticationError,
    NotAuthenticatedError,
    RequestError
)

p = Piazza()

try:
    p.user_login(email="wrong@email.com", password="wrong")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")

try:
    # Try to access network without logging in
    network = p.network("hl5qm84dl4t3x2")
except NotAuthenticatedError as e:
    print(f"Not authenticated: {e}")

try:
    post = network.get_post(99999)  # Non-existent post
except RequestError as e:
    print(f"Request failed: {e}")
```

---

## Examples

### Example 1: Get All Posts and Save to File

```python
from piazza_api import Piazza
import json

p = Piazza()
p.user_login(email="your_email@example.com", password="your_password")
network = p.network("hl5qm84dl4t3x2")

posts = []
for post in network.iter_all_posts(limit=50, sleep=1):
    posts.append({
        'id': post['id'],
        'subject': post['subject'],
        'content': post['content'],
        'created': post['created']
    })

with open('posts.json', 'w') as f:
    json.dump(posts, f, indent=2)
```

### Example 2: Monitor Unread Posts

```python
from piazza_api import Piazza

p = Piazza()
p.user_login(email="your_email@example.com", password="your_password")
network = p.network("hl5qm84dl4t3x2")

# Get unread posts
unread_feed = network.get_filtered_feed(network.feed_filters.unread())

print(f"Found {len(unread_feed['feed'])} unread posts:")
for post in unread_feed['feed']:
    print(f"  - {post['subject']} (ID: {post['id']})")
```

### Example 3: Create and Manage Posts

```python
from piazza_api import Piazza

p = Piazza()
p.user_login(email="your_email@example.com", password="your_password")
network = p.network("hl5qm84dl4t3x2")

# Create a new question
new_post = network.create_post(
    post_type="question",
    post_folders="general",
    post_subject="API Test Question",
    post_content="<p>This is a test question created via the API.</p>",
    anonymous=False
)

print(f"Created post: {new_post['id']}")

# Get the post back
post = network.get_post(new_post['id'])
print(f"Post subject: {post['subject']}")

# Pin it
network.pin_post(post)

# Add a follow-up
followup = network.create_followup(
    post=post,
    content="Additional information",
    anonymous=False
)
```

### Example 4: User Management

```python
from piazza_api import Piazza

p = Piazza()
p.user_login(email="your_email@example.com", password="your_password")
network = p.network("hl5qm84dl4t3x2")

# Get all users
all_users = network.get_all_users()
print(f"Total users: {len(all_users)}")

# Add new students
new_students = ["newstudent1@example.com", "newstudent2@example.com"]
network.add_students(new_students)
print("Added new students")

# Get updated user list
updated_users = network.get_all_users()
print(f"Total users after adding: {len(updated_users)}")
```

### Example 5: Search and Filter

```python
from piazza_api import Piazza

p = Piazza()
p.user_login(email="your_email@example.com", password="your_password")
network = p.network("hl5qm84dl4t3x2")

# Search for posts
search_results = network.search_feed("homework")
print(f"Found {len(search_results['feed'])} posts matching 'homework'")

# Get posts in specific folder
homework_posts = network.get_filtered_feed(
    network.feed_filters.folder("homework")
)
print(f"Found {len(homework_posts['feed'])} posts in homework folder")
```

---

## Important Notes

1. **Rate Limiting**: When iterating through many posts, use the `sleep` parameter to avoid being rate-limited or banned by Piazza.

2. **Network ID**: The network ID (nid) can be found in the URL when viewing a class on Piazza: `https://piazza.com/class/{network_id}`

3. **Content Format**: Posts with `<p>` tags are treated as HTML, otherwise as plain text.

4. **Authentication**: Session cookies are stored in the `PiazzaRPC` session object. You can save and reuse them to avoid repeated logins.

5. **Unofficial API**: This is an unofficial API client. Use at your own risk and be respectful of Piazza's terms of service.

6. **Permissions**: Some operations (like adding students, deleting posts) require appropriate permissions (e.g., instructor/TA access).

---

## Additional Resources

- **Source Code**: https://github.com/hfaran/piazza-api
- **Issue Tracker**: https://github.com/hfaran/piazza-api/issues
- **PyPI Package**: https://pypi.org/project/piazza-api/

---

## License

`piazza-api` is licensed under the MIT License. This repository is also MIT licensed; see [LICENSE](LICENSE).

## Disclaimer

`piazza-api` is not an official API. Its authors are not affiliated with Piazza Technologies Inc. Use it at your own risk.

