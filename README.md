# Piazza Data Puller

A simple Python application to pull data from Piazza (posts, users, feeds, statistics) and export them to JSON or CSV formats.

## Features

- 🔐 Secure authentication with Piazza
- 📝 Pull posts with full details (content, answers, follow-ups)
- 👥 Export user lists
- 📊 Get network statistics
- 📰 Retrieve feed data
- 💾 Export to JSON or CSV formats
- ⚙️ Configurable via command-line or config file

## Installation

**Note:** On macOS, use `python3` instead of `python`. All examples in this README use `python3`.

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install piazza-api
```

2. **Set up configuration (optional):**

Copy the example config file and fill in your credentials:

```bash
cp config.json.example config.json
```

Edit `config.json` with your Piazza credentials:

```json
{
  "email": "your_email@example.com",
  "password": "your_password",
  "network_id": "your_network_id_here"
}
```

**Note:** The network ID can be found in your Piazza class URL:
- URL format: `https://piazza.com/class/{network_id}`

## Usage

### Interactive Mode

Run without arguments for interactive mode:

```bash
python3 piazza_puller.py
```

The script will prompt you for:
- Email and password (if not in config)
- Network ID (if not in config)
- What data to pull

### Command-Line Mode

#### Pull Posts

```bash
# Pull all posts and export to JSON
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull posts

# Pull limited number of posts
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull posts --limit 50

# Export to CSV
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull posts --format csv

# Export to both JSON and CSV
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull posts --format both
```

#### Pull Users

```bash
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull users --format csv
```

#### Pull Feed

```bash
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull feed --limit 100
```

#### Pull Statistics

```bash
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull stats
```

#### Pull Course Materials

```bash
# Pull course materials (posts with attachments, links, or instructor notes)
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull materials --format both
```

#### Pull Everything

```bash
python3 piazza_puller.py --email your@email.com --network-id abc123 --pull all --format both
```

### Command-Line Options

```
--email EMAIL              Piazza email address
--password PASSWORD        Piazza password
--network-id, --nid NID    Network ID (class ID)
--config PATH              Config file path (default: config.json)
--pull {posts,users,feed,stats,materials,all}
                          What to pull (default: posts)
--limit N                 Limit number of posts to pull
--format {json,csv,both}  Export format (default: json)
--output-dir DIR           Output directory (default: output)
--sleep SECONDS           Sleep time between requests (default: 1.0)
```

### Using Config File

If you have a `config.json` file, you can omit credentials:

```bash
python3 piazza_puller.py --pull posts
```

## Output

All exported files are saved in the `output/` directory (created automatically) with timestamps:

- `posts_YYYYMMDD_HHMMSS.json` - Posts in JSON format
- `posts_YYYYMMDD_HHMMSS.csv` - Posts in CSV format
- `users_YYYYMMDD_HHMMSS.json` - Users in JSON format
- `users_YYYYMMDD_HHMMSS.csv` - Users in CSV format
- `feed_YYYYMMDD_HHMMSS.json` - Feed data
- `statistics_YYYYMMDD_HHMMSS.json` - Network statistics
- `course_materials_YYYYMMDD_HHMMSS.json` - Course materials (JSON)
- `course_materials_YYYYMMDD_HHMMSS.csv` - Course materials (CSV)

### Post Data Structure

Each post includes:
- `id` - Post ID
- `subject` - Post subject/title
- `content` - Post content
- `type` - Post type (question, note, etc.)
- `created` - Creation timestamp
- `updated` - Last update timestamp
- `author` - Author user ID
- `author_name` - Author name
- `num_followups` - Number of follow-ups
- `instructor_answers` - List of instructor answers
- `tags` - Post tags
- `folders` - Folders the post belongs to
- `status` - Post status
- `is_pinned` - Whether post is pinned
- `is_resolved` - Whether post is resolved

### User Data Structure

Each user includes:
- `id` - User ID
- `name` - User name
- `email` - User email
- `role` - User role (student, instructor, etc.)

### Course Materials Data Structure

Course materials include posts that contain:
- `id` - Post ID
- `subject` - Post subject/title
- `type` - Post type
- `created` - Creation timestamp
- `folders` - Folders the post belongs to
- `is_instructor_note` - Whether it's an instructor note
- `is_pinned` - Whether post is pinned
- `author_name` - Author name
- `attachments` - List of attachments/files (if any)
- `links` - List of URLs found in the post (if any)
- `content_preview` - Preview of post content

## Examples

### Example 1: Quick Post Export

```bash
python3 piazza_puller.py --email student@university.edu --network-id hl5qm84dl4t3x2 --pull posts --limit 20 --format csv
```

### Example 2: Full Data Export

```bash
python3 piazza_puller.py --pull all --format both --output-dir my_data
```

### Example 3: Using Config File

1. Create `config.json`:
```json
{
  "email": "student@university.edu",
  "password": "mypassword",
  "network_id": "hl5qm84dl4t3x2"
}
```

2. Run:
```bash
python3 piazza_puller.py --pull posts --format both
```

## Rate Limiting

To avoid being rate-limited by Piazza, the script includes a `--sleep` parameter that adds a delay between requests. The default is 1 second, but you can adjust it:

```bash
python3 piazza_puller.py --pull posts --sleep 2.0  # 2 seconds between requests
```

For large datasets, it's recommended to use at least 1 second delay.

## Error Handling

The application handles common errors:
- Authentication failures
- Network connection issues
- Invalid network IDs
- Missing permissions

If an error occurs, the script will display a clear error message and exit gracefully.

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit `config.json`** - It contains your credentials. It's already in `.gitignore`.
2. **Use environment variables** for production deployments
3. **Keep your credentials secure** - Don't share your config file
4. **Use read-only operations** - This tool only pulls data, it doesn't modify Piazza

## Troubleshooting

### Authentication Errors

If you get authentication errors:
- Verify your email and password are correct
- Check if your account has 2FA enabled (may need to use app-specific password)
- Try logging in manually on Piazza website first

### Network ID Not Found

- Make sure you're using the correct network ID from the class URL
- Verify you have access to the class
- Check that you're enrolled in the class

### Rate Limiting

If you get rate-limited:
- Increase the `--sleep` parameter (e.g., `--sleep 2.0`)
- Pull smaller batches using `--limit`
- Wait a few minutes before retrying

## License

This project uses the Piazza API library which is licensed under MIT License.

## Disclaimer

This is an unofficial tool. It is not affiliated with Piazza Technologies Inc. Use at your own risk and be respectful of Piazza's terms of service.

