🎓 Student Performance Management System
A full-stack web application built with Python (Flask) and MySQL to manage student records, calculate academic performance, and generate digital marksheets.

🚀 Features
CRUD Operations: Add, View, Update, and Delete student records.

Automated Grading: Automatically calculates Total Marks, Percentage, and Letter Grades (A+, A, B, etc.).

Search Functionality: Quickly find students by Name or Roll Number.

Relational Database: Uses a structured schema with Students, Classes, Subjects, and Marks tables.

Printable Marksheets: A dedicated, formally styled report card view for every student.

Cloud Ready: Configured for deployment on Render (Frontend) and Aiven (Database).

🛠️ Tech Stack
Backend: Python 3, Flask

Database: MySQL (Relational)

Frontend: HTML5, CSS3, Jinja2 Templates

Deployment: Render, Gunicorn

📂 Project Structure
Plaintext

├── app.py              # Main Flask application logic
├── requirements.txt    # Python dependencies for deployment
├── templates/          # HTML files
│   ├── index.html      # Main dashboard & registration
│   ├── edit.html       # Student record update page
│   └── marksheet.html  # Formal report card view
└── README.md           # Project documentation
⚙️ Installation & Setup
Clone the repository:

Bash

git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
Install Dependencies:

Bash

pip install -r requirements.txt
Database Setup:

Import the provided SQL script into your MySQL server.

Update the db_config in app.py with your credentials (or set environment variables).

Run the App:

Bash

python app.py
The app will be available at http://127.0.0.1:5000.

🌐 Deployment
This project is optimized for Render. Ensure the following Environment Variables are set in your Render dashboard:

DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

📄 License
This project is open-source and available under the MIT License.
