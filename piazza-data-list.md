# Complete List of Data You Can Pull from Piazza

This document provides a comprehensive list of all data types and information you can pull from Piazza using the `piazza-api` library.

---

## 📋 Table of Contents

1. [User Information](#user-information)
2. [Post Data](#post-data)
3. [User/Student Data](#userstudent-data)
4. [Feed Data](#feed-data)
5. [Statistics](#statistics)
6. [Course Materials](#course-materials)

---

## 👤 User Information

### 1. User Profile
**Method:** `get_user_profile()`

**What you get:**
- User ID
- Name
- Email
- Profile information
- All classes the user is enrolled in
- User preferences and settings

**Example:**
```python
from piazza_api import Piazza
p = Piazza()
p.user_login(email="your@email.com", password="password")
profile = p.get_user_profile()
```

---

### 2. User Status
**Method:** `get_user_status()`

**What you get:**
- Global user status
- Relationship with all enrolled classes
- User ID
- Network memberships
- Role in each class (student, instructor, TA)

**Example:**
```python
status = p.get_user_status()
```

---

### 3. User Classes
**Method:** `get_user_classes()`

**What you get:**
- List of all classes the user is enrolled in
- For each class:
  - Class name
  - Term
  - Course number
  - Network ID (nid)
  - Whether user is TA/instructor

**Example:**
```python
classes = p.get_user_classes()
for cls in classes:
    print(f"{cls['name']} - {cls['term']} (ID: {cls['nid']})")
```

---

## 📝 Post Data

### 4. Single Post
**Method:** `network.get_post(cid)`

**What you get:**
- Complete post data including:
  - Post ID
  - Subject/title
  - Full content (HTML or text)
  - Post type (question, note, poll)
  - Creation and update timestamps
  - Author information
  - Tags and folders
  - Status (active, inactive, resolved, pinned)
  - Follow-ups and answers
  - Instructor answers
  - Student answers
  - Endorsements
  - View counts
  - Bookmark/favorite counts
  - Change history
  - Attachments (if any)
  - Links (if any)

**Example:**
```python
network = p.network("network_id")
post = network.get_post(100)  # Post ID
```

---

### 5. All Posts
**Method:** `network.iter_all_posts(limit=None, sleep=0)`

**What you get:**
- All posts visible to the current user
- Each post contains the same data as single post (see above)
- Can be limited with `limit` parameter
- Can add delay between requests with `sleep` parameter

**Example:**
```python
posts = network.iter_all_posts(limit=50, sleep=1.0)
for post in posts:
    print(post['subject'])
```

**Post Data Includes:**
- **Basic Info:**
  - `id` - Post ID
  - `subject` - Post title/subject
  - `content` - Post content (HTML or text)
  - `type` - Post type (question, note, poll)
  - `created` - Creation timestamp
  - `updated` - Last update timestamp
  - `status` - Post status (active, inactive)
  
- **Author Info:**
  - `author` - Author user ID
  - `author_name` - Author name
  - `uid` - User ID hash
  
- **Metadata:**
  - `tags` - List of tags (unanswered, instructor-note, pin, student)
  - `folders` - List of folders the post belongs to
  - `is_pinned` - Whether post is pinned
  - `is_resolved` - Whether post is resolved
  - `bucket_order` - Bucket assignment number
  - `bucket_name` - Bucket name (Today, Yesterday, etc.)
  
- **Interactions:**
  - `num_followups` - Number of follow-ups
  - `no_answer_followup` - Count of unresolved follow-ups
  - `unique_views` - Number of unique views
  - `bookmarked` - Number of bookmarks
  - `num_favorites` - Number of favorites
  - `my_favorite` - Whether you favorited it
  - `is_bookmarked` - Whether you bookmarked it
  
- **Content:**
  - `children` - List of follow-ups and answers
  - `instructor_answers` - List of instructor answers
  - `history` - Change history
  - `change_log` - List of changes
  - `tag_good` - List of endorsements
  - `attachments` - Files/attachments (if any)
  - `links` - URLs found in content (if any)

---

## 👥 User/Student Data

### 6. All Users
**Method:** `network.get_all_users()`

**What you get:**
- List of all users in the network/class
- For each user:
  - User ID
  - Name
  - Email
  - Role (student, instructor, TA)
  - Profile information
  - Enrollment status

**Example:**
```python
users = network.get_all_users()
for user in users:
    print(f"{user['name']} ({user['email']}) - {user['role']}")
```

---

### 7. Specific Users
**Method:** `network.get_users(user_ids)`

**What you get:**
- Data for specific users by their user IDs
- Same data structure as `get_all_users()`

**Example:**
```python
user_ids = ["user_id_1", "user_id_2"]
users = network.get_users(user_ids)
```

---

## 📰 Feed Data

### 8. Feed
**Method:** `network.get_feed(limit=100, offset=0)`

**What you get:**
- Feed metadata
- List of posts in feed format (partial/summary data)
- Post summaries (not full posts)
- Content snippets
- Pagination support via `limit` and `offset`

**Example:**
```python
feed = network.get_feed(limit=50, offset=0)
for post in feed["feed"]:
    print(post['subject'])
```

**Feed Post Data Includes:**
- Post ID
- Subject
- Content snippet (not full content)
- Author info
- Timestamps
- Tags
- Folders
- Status indicators

---

### 9. Filtered Feed - Unread Posts
**Method:** `network.get_filtered_feed(network.feed_filters.unread())`

**What you get:**
- Only posts with unread content
- Same structure as regular feed

**Example:**
```python
unread_feed = network.get_filtered_feed(network.feed_filters.unread())
```

---

### 10. Filtered Feed - Following Posts
**Method:** `network.get_filtered_feed(network.feed_filters.following())`

**What you get:**
- Only posts you are following
- Same structure as regular feed

**Example:**
```python
following_feed = network.get_filtered_feed(network.feed_filters.following())
```

---

### 11. Filtered Feed - Folder Posts
**Method:** `network.get_filtered_feed(network.feed_filters.folder("folder_name"))`

**What you get:**
- Only posts in a specific folder
- Same structure as regular feed

**Example:**
```python
homework_feed = network.get_filtered_feed(
    network.feed_filters.folder("homework")
)
```

---

### 12. Search Feed
**Method:** `network.search_feed(query)`

**What you get:**
- Search results matching the query
- Posts in feed format
- Search metadata

**Example:**
```python
results = network.search_feed("homework assignment")
for post in results["feed"]:
    print(post['subject'])
```

---

## 📊 Statistics

### 13. Network Statistics
**Method:** `network.get_statistics()`

**What you get:**
- Class statistics viewable on Statistics page
- Post views
- Participation by folders
- Thread statistics
- Live Q&A statistics
- Poll statistics
- Activity counts
- User engagement metrics

**Example:**
```python
stats = network.get_statistics()
print(stats)
```

---

## 📚 Course Materials

### 14. Course Materials (Custom Extraction)
**Method:** `get_course_materials()` (in piazza_puller.py)

**What you get:**
- Posts that contain course materials:
  - Posts with attachments/files
  - Posts with links/URLs
  - Instructor notes
  - Pinned posts (often contain important materials)

**For each material:**
- Post ID
- Subject
- Type
- Created date
- Folders
- Author name
- List of attachments (if any)
- List of links/URLs (if any)
- Content preview
- Whether it's an instructor note
- Whether it's pinned

**Example:**
```python
from piazza_puller import PiazzaPuller

puller = PiazzaPuller(email="your@email.com", password="password", network_id="network_id")
puller.authenticate()
puller.set_network()
materials = puller.get_course_materials()
```

---

## 📦 Data Export Formats

All data can be exported in:

1. **JSON Format** - Full data structure, preserves nested data
2. **CSV Format** - Spreadsheet-friendly (for posts and users)
3. **Both** - Export to both JSON and CSV

---

## 🔍 What's Included in Post Data

When you pull posts, each post contains:

### Basic Information
- Post ID, subject, content
- Type (question, note, poll)
- Creation and update timestamps
- Status (active, inactive, resolved, pinned)

### Author Information
- Author user ID
- Author name
- Anonymous status

### Content
- Full post content (HTML or text)
- Subject/title
- Attachments (if any)
- Links/URLs (if any)

### Thread Information
- Follow-ups (children)
- Instructor answers
- Student answers
- Replies to follow-ups
- Revision history

### Metadata
- Tags (unanswered, instructor-note, pin, student)
- Folders
- Bucket information (Today, Yesterday, etc.)
- Change log
- History

### Engagement Metrics
- View counts
- Bookmark counts
- Favorite counts
- Endorsement information
- Your interaction status (favorited, bookmarked, etc.)

### Status Flags
- Is pinned
- Is resolved
- Is bookmarked (by you)
- Is favorited (by you)
- Is endorsed (by you)

---

## 📋 Summary Table

| Data Type | Method | Format | Description |
|-----------|--------|--------|-------------|
| User Profile | `get_user_profile()` | JSON | Current user's profile |
| User Status | `get_user_status()` | JSON | User's global status |
| User Classes | `get_user_classes()` | JSON | List of enrolled classes |
| Single Post | `network.get_post(cid)` | JSON | Complete post data |
| All Posts | `network.iter_all_posts()` | JSON | All posts (iterator) |
| All Users | `network.get_all_users()` | JSON | All users in class |
| Specific Users | `network.get_users(ids)` | JSON | Specific users by ID |
| Feed | `network.get_feed()` | JSON | Feed with post summaries |
| Unread Feed | `network.get_filtered_feed(unread)` | JSON | Unread posts only |
| Following Feed | `network.get_filtered_feed(following)` | JSON | Posts you're following |
| Folder Feed | `network.get_filtered_feed(folder)` | JSON | Posts in specific folder |
| Search | `network.search_feed(query)` | JSON | Search results |
| Statistics | `network.get_statistics()` | JSON | Class statistics |
| Course Materials | `get_course_materials()` | JSON/CSV | Materials extraction |

---

## 🚀 Quick Reference

### Using the web UI

```bash
python3 app.py
```

Open `http://127.0.0.1:5001`, log in, and choose a data type. There is no command-line interface on `piazza_puller.py`.

### Using `PiazzaPuller`

```python
from piazza_puller import PiazzaPuller

puller = PiazzaPuller(email="your@email.com", password="password", network_id="network_id")
puller.authenticate()
puller.set_network()

posts = puller.get_all_posts(limit=50)
users = puller.get_users()
feed = puller.get_feed(limit=100)
stats = puller.get_statistics()
materials = puller.get_course_materials()
```

### Using the `piazza-api` library directly

```python
from piazza_api import Piazza

p = Piazza()
p.user_login(email="your@email.com", password="password")

# Get user info
profile = p.get_user_profile()
classes = p.get_user_classes()

# Get network
network = p.network("network_id")

# Get posts
post = network.get_post(100)
all_posts = network.iter_all_posts(limit=50)

# Get users
users = network.get_all_users()

# Get feed
feed = network.get_feed(limit=100)
unread = network.get_filtered_feed(network.feed_filters.unread())

# Search
results = network.search_feed("query")

# Statistics
stats = network.get_statistics()
```

---

## 📝 Notes

1. **Rate Limiting:** When pulling many posts, use `sleep` parameter to avoid being rate-limited
2. **Permissions:** Some data may require instructor/TA permissions
3. **Data Completeness:** Feed data contains summaries, not full posts. Use `get_post()` for complete data
4. **Attachments:** Attachments are included in post data but may need additional processing to download files
5. **Links:** URLs in posts are extracted from content, but actual file downloads require separate handling

---

## 🔗 Related Files

- `piazza_puller.py` - Application to pull and export data
- `piazza-api-usage-guide.md` - Detailed API usage guide
- `README.md` - Application documentation

