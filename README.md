# PigeonSOCIAL

PigeonSOCIAL is a lightweight, modern, open-source social networking platform designed to connect people through a clean, responsive, and minimalist web interface.

## About the Project

PigeonSOCIAL is a full-stack social network built with Python, Flask, and SQLite. It aims to provide a fast, secure, and straightforward platform for online communities. The application includes interactive post feeds, private messaging, hashtag indexing, daily activity streak tracking, and built-in administrative moderation tools.

## Key Features

- Public Feed: Create posts, interact with comments, and use clickable hashtags.
- Special Post Types: Support for custom post classifications such as Pigeon Mail.
- Direct Messaging: One-on-one private chat system between registered users.
- User Profiles: Customizable bios, avatar selection, saved posts bookmarks, and posting streak counters.
- Hashtag Filtering: Easily discover and search posts by specific topic tags.
- Administrative Panel: Comprehensive moderation dashboard for reviewing user appeals and applying temporary or permanent account suspensions.
- Multilingual Support: Built-in internationalization supporting English and Portuguese.
- Account Privacy Settings: Options for users to control profile visibility and application settings.

## Technology Stack

- Backend: Python 3, Flask, Werkzeug Security
- Database: SQLite with Write-Ahead Logging (WAL) enabled for optimized concurrency
- Frontend: HTML5, CSS3 with native CSS variables for responsive styling
- Deployment Compatibility: Runs on local environments, cloud hosting services (such as PythonAnywhere), and mobile terminal setups (such as Termux)

## System Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/PigeonSOCIAL.git
   cd PigeonSOCIAL
   ```

2. Install the required dependencies:
   ```bash
   pip install flask werkzeug markupsafe
   ```

3. Initialize the database and run the application:
   ```bash
   python app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Project Structure

```
PigeonSOCIAL/
├── app.py              # Main application entry point
├── database.py         # Database initialization and connection helpers
├── routes.py           # Blueprint routes and core application logic
├── templates/          # HTML templates
│   ├── base.html       # Base layout template
│   ├── feed.html       # Public feed view
│   ├── profile.html    # User profile view
│   ├── chat.html       # Direct messaging view
│   ├── admin.html      # Administration panel
│   ├── login.html      # User authentication login
│   ├── register.html   # Account registration
│   ├── settings.html   # User settings and preferences
│   └── banned.html     # Account suspension screen
└── static/             # Static assets (CSS, JS, images)
```

## Contributing

Contributions are welcome. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add NewFeature'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request explaining your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
