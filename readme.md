# LibraSphere – Smart Library Management System

LibraSphere is a web-based library management system built using Flask and MySQL. It supports role-based access control (RBAC) with three types of users: Super Admin, Admin, and User. Each role comes with its own set of permissions to manage books, users, and borrowing records.

## Features

LibraSphere allows Super Admins to manage both Admin and User accounts, as well as the book inventory. Admins can manage books and view user data, while regular Users can browse available books and borrow them. The system includes secure registration and login, user profile management, and real-time book borrowing with return tracking. An admin dashboard is also integrated using Flask-Admin for convenient backend management.

## Tech Stack

- Python (Flask)
- SQLAlchemy (ORM)
- MySQL (via PyMySQL)
- Flask-Login (Authentication)
- Flask-Bcrypt (Password hashing)
- Flask-Admin (Admin dashboard)
- HTML, CSS, Jinja2 (Frontend templating)
- Flask-Migrate (Database migrations)
- python-dotenv (Environment configuration)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- MySQL or MariaDB installed

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ap-bhattacharya/LibraSphere.git
   cd LibraSphere
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your configuration:

   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://username:password@localhost/database_name
   ```

5. Initialize the database:

   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:

   ```bash
   flask run
   ```

## License

This project is licensed under the MIT License.

## Repository

GitHub: [https://github.com/ap-bhattacharya/LibraSphere](https://github.com/ap-bhattacharya/LibraSphere)
