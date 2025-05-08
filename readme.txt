Book Manager Website

A web application for managing books, users, and borrowing records built with Flask, SQLAlchemy, and MySQL. The application features role-based access control with different user roles like Super Admin, Admin, and User.

Features

- Super Admin: Manage Admin and User accounts, as well as manage books.
- Admin: Manage books and see user data.
- User: View available books and borrow them.
- User Registration: Users can sign up and manage their own profiles.
- Role-based Access Control (RBAC): Different permissions for different user roles.
- Book Borrowing: Users can borrow books, with tracking for borrow and return dates.
- Admin & User Management: Admins can manage users, and Super Admins can manage all users and admins.

Technologies Used

- Flask: Web framework used to build the application.
- SQLAlchemy: ORM for database interactions.
- Flask-SQLAlchemy: Flask integration for SQLAlchemy.
- Flask-Migrate: Database migrations.
- PyMySQL: MySQL database connector.
- Flask-Login: User session management.
- Flask-Bcrypt: Password hashing and verification.
- Jinja2: Template engine for dynamic HTML rendering.
- python-dotenv: Environment variable management.
- Flask-Admin: Admin interface for managing users and books.

Prerequisites

- Python 3.8 or above
- MySQL or MariaDB database
- Virtual environment (optional but recommended)