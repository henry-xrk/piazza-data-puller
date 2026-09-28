# Piazza Data Puller

A web-based application to pull data from Piazza (posts, users, feeds, statistics, course materials) and export them to JSON or CSV formats. Features a modern, easy-to-use browser interface.

## Features

- 🌐 **Web-based UI** - No command line needed, works entirely in your browser
- 🔐 Secure authentication with Piazza
- 📝 Pull posts with full details (content, answers, follow-ups)
- 👥 Export user lists
- 📊 Get network statistics
- 📰 Retrieve feed data
- 📚 Extract course materials (attachments, links, instructor notes)
- 🔍 Search feed functionality
- 💾 Export to JSON or CSV formats
- 📋 Class selection from enrolled classes
- 📥 Direct file downloads from the browser
- 🖨️ Save live posts as PDF, including images and formatting

## Installation

**Note:** On macOS, use `python3` instead of `python`. All examples in this README use `python3`.

1. **Install dependencies:**

```bash
pip install -r requirements.txt
python3 -m playwright install chromium
```

`playwright install chromium` is only needed for PDF export. The web UI does not use it.

Or install the API client directly:

```bash
pip install piazza-api
```

## Usage

### Starting the Application

1. **Start the web server:**

```bash
python3 app.py
```

2. **Open your browser:**

Navigate to: `http://127.0.0.1:5001`

You should see the login page.

### Using the Web Interface

#### Step 1: Login

1. Enter your Piazza email and password
2. Optionally enter a network ID (class ID) if you know it
3. Click "Login"
4. Wait for authentication (you'll see your name appear)

**Note:** Demo mode is off by default. To try the UI without Piazza credentials, start the server with `PIAZZA_DEMO_MODE=1` and log in as `admin@demo.com` / `demo123`. Demo mode returns sample data only.

#### Step 2: Set Network (Class)

1. **Option A:** Enter the network ID manually in the text field
2. **Option B:** Click "Load My Classes" to see all your enrolled classes
   - Click on a class to select it
   - The network ID will be filled automatically
3. Click "Set Network" to connect

**Note:** The network ID can be found in your Piazza class URL:
- URL format: `https://piazza.com/class/{network_id}`

#### Step 3: Select Data Type

Click on one of the data type cards:
- **📝 Posts** - All posts with full content
- **👥 Users** - All users in the class
- **📰 Feed** - Feed summaries
- **📊 Statistics** - Class statistics
- **📚 Materials** - Course materials (attachments, links, instructor notes)
- **🔍 Search** - Search for posts in the feed

#### Step 4: Configure Options

- **Limit (optional):** Enter a number to limit results (leave empty for all)
- **Export Format:** Choose JSON, CSV, or Both

#### Step 5: Pull Data

1. Click "Pull Data"
2. Wait for the process to complete (you'll see a loading spinner)
3. Download the exported files using the download links

For more details about the web UI, see [README-UI.md](README-UI.md).

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
  - Attachment objects may contain: `id`, `name`, `url`, `size`, `type`
  - **Note:** Attachment URLs may require Piazza authentication to access
- `links` - List of URLs found in the post content (if any)
  - **Note:** These are external links extracted from post text - can be clicked directly
- `content_preview` - Preview of post content

### Accessing Links and Attachments

**Links (from `links` array):**
- These are URLs extracted from the post content text
- Usually external URLs (e.g., `https://example.com/resource`)
- Can be clicked directly - no special handling needed
- Open in a new tab/window when clicked

**Attachments (from `attachments` array):**
- These are files uploaded to Piazza
- Attachment URLs are included in the exported data
- **May require Piazza authentication** - you may need to:
  1. Be logged into Piazza in your browser
  2. Click the link while authenticated
  3. Or access through the original Piazza post
- If an attachment URL doesn't work, access it through the Piazza website using the post ID

## Programmatic Usage

The `PiazzaPuller` class can also be used programmatically in your own Python scripts:

```python
from piazza_puller import PiazzaPuller

# Initialize
puller = PiazzaPuller(email="your@email.com", password="password", network_id="abc123")

# Authenticate
if puller.authenticate():
    # Set network
    puller.set_network()
    
    # Pull data
    posts = puller.get_all_posts(limit=10)
    users = puller.get_users()
    feed = puller.get_feed(limit=100)
    stats = puller.get_statistics()
    materials = puller.get_course_materials(limit=50)
    search_results = puller.search_feed("your search query")
    
    # Export
    puller.export_to_json(posts, 'posts.json')
    puller.export_posts_to_csv(posts, 'posts.csv')
```

## Export Posts as PDF

`piazza_pdf_converter.py` opens the live Piazza page and saves each post as a PDF, so images and formatting stay intact. It collapses the class feed before printing. PDFs are written to `pdfs/` and are gitignored.

```bash
python3 piazza_pdf_converter.py \
  --config config.json \
  --class-id your_class_id \
  --start 1 \
  --end 10
```

The class ID is the value in `https://piazza.com/class/{class_id}`. Add `--no-headless` to watch the browser. Credentials can also be passed with `--email` and `--password`.

## Examples

### Example 1: Basic Usage

1. Start the server:
```bash
python3 app.py
```

2. Open browser to `http://127.0.0.1:5001`
3. Login with your Piazza credentials
4. Select a class and pull data

### Example 2: Using Demo Mode

1. Start the server with demo mode enabled:
```bash
PIAZZA_DEMO_MODE=1 python3 app.py
```

2. Open browser to `http://127.0.0.1:5001`
3. Login with demo credentials: `admin@demo.com` / `demo123`
4. Test the interface without real Piazza credentials. The button only appears when demo mode is on.

## Rate Limiting

To avoid being rate-limited by Piazza, the application includes automatic delays between requests. For large datasets, the web UI will automatically add appropriate delays to prevent rate limiting.

## Error Handling

The application handles common errors:
- Authentication failures
- Network connection issues
- Invalid network IDs
- Missing permissions

If an error occurs, the script will display a clear error message and exit gracefully.

## Project Structure

```
piazza-data-puller/
├── app.py                  # Flask web application (main entry point)
├── piazza_puller.py        # Core PiazzaPuller class (library)
├── piazza_pdf_converter.py # Save live posts as PDF
├── config.json.example     # Example configuration file (optional)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Web UI frontend template
├── output/                 # Exported files directory (created automatically)
├── pdfs/                   # PDF exports (created by piazza_pdf_converter.py)
├── uploads/                # Upload directory (created automatically)
├── LICENSE                 # MIT License
├── README.md               # This file
└── README-UI.md            # Detailed web UI documentation
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit `config.json`** - It contains your credentials. It's already in `.gitignore`.
2. **Use environment variables** for production deployments
3. **Keep your credentials secure** - Don't share your config file
4. **Use read-only operations** - This tool only pulls data, it doesn't modify Piazza
5. **Web UI Security** - The server listens on `127.0.0.1` and runs with the debugger off unless you set `FLASK_DEBUG=1`. Do not expose it on a public host. For anything beyond local use:
   - Use proper session management (Redis, database)
   - Implement HTTPS
   - Add rate limiting
   - Secure credential storage
6. **Exported data** - Pulls can include classmates' names and emails, plus course content. Do not commit or publish files from `output/`, `downloads/`, `downloaded_pdfs/`, or `pdfs/`.

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
- Pull smaller batches using the limit option
- Wait a few minutes before retrying
- The application automatically includes delays between requests

## Dependencies

The project requires the following Python packages (see `requirements.txt`):

- `piazza-api` - Official Piazza API library
- `requests` - HTTP library
- `six` - Python 2/3 compatibility
- `flask` - Web framework (for Web UI)
- `werkzeug` - WSGI utilities (for Web UI)
- `playwright` - Browser automation for PDF export

Install all dependencies, then download the Chromium build used by the PDF exporter:

```bash
pip install -r requirements.txt
python3 -m playwright install chromium
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

The `piazza-api` library it depends on is a separate project, also MIT licensed: https://github.com/hfaran/piazza-api

## Disclaimer

This is an unofficial tool. It is not affiliated with Piazza Technologies Inc. Use at your own risk and be respectful of Piazza's terms of service.

## Additional Resources

- [README-UI.md](README-UI.md) - Detailed documentation for the Web UI
- [piazza-api-usage-guide.md](piazza-api-usage-guide.md) - Guide for using the Piazza API library

