# HiTec University Library Management System

A full-featured library management system for HiTec University, enabling efficient management of books, student library cards, loans with automatic fine calculation, and a complete web interface for administrators and students.

## Features

- **Student Management:** 300 students with unique library cards and roll numbers
- **Book Catalog:** 50 real books fetched from Open Library API with WebP cover images
- **Loan System:** 15-day loan duration with automatic late fee calculation (PKR 50/day)
- **Review System:** Student ratings and reviews with automatic average calculation
- **Admin Panel:** Secure dashboard for managing books, students, and loans
- **Responsive Design:** Mobile-optimized Bootstrap 5 interface

## Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation

```bash
# Clone and navigate
git clone <repository-url>
cd Library-Management-System

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed database
python seed_database.py

# Run application
python app.py
```

Access at `http://127.0.0.1:5000`

### Default Admin Login
- Username: `admin`
- Password: `admin123`

## Project Structure

```
Library-Management-System/
├── app.py                    # Main Flask application
├── seed_database.py          # Database seeding script
├── requirements.txt          # Dependencies
├── database/
│   └── library.db           # SQLite database
├── static/                  # CSS, JS, images
└── templates/
    ├── admin/              # Admin panel templates
    ├── public/             # Public pages
    └── errors/             # Error pages
```

## API Endpoints

### Public Routes
- `/` - Homepage
- `/about` - Library information
- `/books` - Book catalog with search
- `/books/<id>` - Book details
- `/contact` - Contact information

### Admin Routes
- `/admin/login` - Admin authentication
- `/admin/dashboard` - Statistics overview
- `/admin/books` - Manage books
- `/admin/students` - Manage students
- `/admin/loans` - Manage loans

## Database Schema

- **Admin:** Authentication
- **Book:** Title, author, ISBN, genre, copies, ratings
- **Student:** Name, roll number, library card, department
- **Loan:** Student-book relationship, dates, fines
- **Review:** Student ratings and comments
- **LibrarySettings:** Location, contact info

## Loan Policy

- Duration: 15 days
- Late fee: PKR 50/day
- Automatic fine calculation
- Overdue tracking

## Deployment

### Production with Gunicorn
```bash
gunicorn app:app --workers 4 --bind 0.0.0.0:8000
```

## Support

- Email: library@hitec.edu.pk
- Phone: +92-51-9048-5000
- Location: HiTec University, Taxila, Pakistan

## License

Proprietary software for HiTec University. All rights reserved.
