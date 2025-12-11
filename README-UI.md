# Piazza Data Puller - Web UI

A simple web-based user interface for pulling data from Piazza. This provides an easy-to-use browser interface instead of using the command line.

## Features

- 🌐 **Web-based UI** - No command line needed
- 🔐 **Secure Authentication** - Login with your Piazza credentials
- 📋 **Class Selection** - View and select from your enrolled classes
- 📊 **Multiple Data Types** - Pull posts, users, feed, statistics, and course materials
- 💾 **Export Options** - Export to JSON, CSV, or both formats
- 📥 **Direct Downloads** - Download exported files directly from the browser

## Installation

1. **Install dependencies:**

```bash
pip3 install -r requirements.txt
```

2. **Make sure you have the piazza-api library:**

```bash
pip3 install piazza-api
```

## Running the Web UI

1. **Start the server:**

```bash
cd pull-test
python3 app.py
```

2. **Open your browser:**

Navigate to: `http://localhost:5000`

You should see the login page.

## Usage

### Step 1: Login

1. Enter your Piazza email and password
2. Click "Login"
3. Wait for authentication (you'll see your name appear)

### Step 2: Set Network (Class)

1. **Option A:** Enter the network ID manually in the text field
2. **Option B:** Click "Load My Classes" to see all your enrolled classes
   - Click on a class to select it
   - The network ID will be filled automatically

3. Click "Set Network" to connect

### Step 3: Select Data Type

Click on one of the data type cards:
- **📝 Posts** - All posts with full content
- **👥 Users** - All users in the class
- **📰 Feed** - Feed summaries
- **📊 Statistics** - Class statistics
- **📚 Materials** - Course materials (attachments, links, instructor notes)

### Step 4: Configure Options

- **Limit (optional):** Enter a number to limit results (leave empty for all)
- **Export Format:** Choose JSON, CSV, or Both

### Step 5: Pull Data

1. Click "Pull Data"
2. Wait for the process to complete (you'll see a loading spinner)
3. Download the exported files using the download links

## Screenshots

### Login Page
- Clean login interface with email and password fields

### Main Dashboard
- User info display
- Network selection
- Data type selection cards
- Export options
- Results with download links

## Features in Detail

### Authentication
- Secure session management
- User profile display
- Logout functionality

### Class Management
- View all enrolled classes
- Quick selection from class list
- Manual network ID entry

### Data Pulling
- Real-time progress indication
- Error handling and display
- Success notifications
- File download links

### Export Options
- JSON format (full data structure)
- CSV format (spreadsheet-friendly)
- Both formats simultaneously

## Troubleshooting

### Server Won't Start

**Error: Port 5000 already in use**

Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Authentication Fails

- Verify your email and password are correct
- Check if your account has 2FA enabled
- Try logging in manually on Piazza website first

### Network ID Not Found

- Make sure you're using the correct network ID
- Verify you have access to the class
- Try loading your classes using "Load My Classes" button

### Files Not Downloading

- Check that the `output/` directory exists
- Verify file permissions
- Check browser download settings

## Security Notes

⚠️ **Important:**

1. **Local Development Only** - This is designed for local use. For production:
   - Use proper session management (Redis, database)
   - Implement HTTPS
   - Add rate limiting
   - Secure credential storage

2. **Credentials** - Your credentials are stored in session memory only during your session

3. **Files** - Exported files are stored in the `output/` directory on your local machine

## API Endpoints

The web UI uses these API endpoints:

- `POST /api/login` - Authenticate with Piazza
- `POST /api/set-network` - Set the network/class
- `POST /api/pull-data` - Pull data from Piazza
- `GET /api/user-classes` - Get user's enrolled classes
- `GET /api/download/<filename>` - Download exported file
- `POST /api/logout` - Logout and clear session

## Development

### File Structure

```
pull-test/
├── app.py              # Flask web application
├── templates/
│   └── index.html      # Web UI frontend
├── piazza_puller.py    # Core pulling logic
├── output/             # Exported files directory
└── uploads/            # Upload directory (if needed)
```

### Customization

You can customize the UI by editing:
- `templates/index.html` - Frontend HTML/CSS/JavaScript
- `app.py` - Backend Flask routes and logic

### Adding Features

To add new features:
1. Add new route in `app.py`
2. Update frontend in `templates/index.html`
3. Test thoroughly

## Comparison: Web UI vs Command Line

| Feature | Web UI | Command Line |
|---------|--------|--------------|
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Speed | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Automation | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Visual Feedback | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Batch Processing | ⭐⭐ | ⭐⭐⭐⭐⭐ |

**Use Web UI when:**
- You want a visual interface
- You're pulling data occasionally
- You want to see results immediately

**Use Command Line when:**
- You need automation/scripting
- You're pulling large amounts of data
- You want to integrate with other tools

## License

Same as the main project - MIT License

## Support

For issues or questions:
1. Check the main README.md
2. Review error messages in the browser console
3. Check server logs in the terminal

