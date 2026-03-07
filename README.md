# HiTec University Library Management System

A full-featured library management system for HiTec University, enabling efficient management of books, student library cards, loans with automatic fine calculation, and a complete web interface for administrators and students.

## Features

- **Student Management:** 300 students with unique library cards (LIB-XXXXXX) and roll numbers (YY-DEPT-NNN format)
- **Book Catalog:** 1000 real book titles across 10 genres with cover images, ISBN tracking, and availability management
- **Loan System:** 15-day loan duration with automatic late fee calculation (PKR 50/day) and overdue tracking
- **Review System:** Student ratings and reviews with automatic average calculation
- **Admin Panel:** Secure dashboard for managing books, students, loans, and fines
- **Interactive Map:** Leaflet.js integration showing library location with directions
- **Responsive Design:** Mobile-optimized Bootstrap 5 interface with professional Navy Blue & Cyan theme

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

# Seed database (creates admin, 300 students, 1000 books, 1000+ reviews)
python seed_database.py

# Run application
python app.py
```

Access at `http://127.0.0.1:5000`

### Default Admin Login
- Username: `admin`
- Password: `admin123`

⚠️ Change credentials in production!

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
    ├── admin/              # Admin panel (11 templates)
    ├── public/             # Public pages (5 templates)
    └── errors/             # Error pages (2 templates)
```

## API Endpoints

### Public Routes
- `/` - Homepage with featured books
- `/about` - Library information with map
- `/books` - Book catalog with search
- `/books/<id>` - Book details and reviews
- `/contact` - Contact information

### Admin Routes
- `/admin/login` - Admin authentication
- `/admin/dashboard` - Statistics overview
- `/admin/books` - Manage books
- `/admin/students` - Manage students
- `/admin/loans` - Manage loans and fines

## Database Schema

- **Admin:** Authentication and user management
- **Book:** Title, author, ISBN, genre, copies, ratings
- **Student:** Name, roll number, library card, department, fines
- **Loan:** Student-book relationship, dates, fines, return status
- **Review:** Student ratings and comments for books
- **LibrarySettings:** Location, contact info, operating hours

## Technical Details

### Book Genres (100 books each)
Computer Science, Mathematics, History, Physics, Economics, Engineering, Electrical Engineering, Mechanical Engineering, Civil Engineering, Software Engineering

### Security
- Password hashing (Werkzeug)
- SQL injection protection (SQLAlchemy ORM)
- Session-based authentication
- Form validation
- Secure admin routes

### Loan Policy
- Duration: 15 days
- Late fee: PKR 50/day
- Automatic fine calculation
- Overdue tracking

## Deployment

### Production with Gunicorn
```bash
gunicorn app:app --workers 4 --bind 0.0.0.0:8000
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
```

```bash
docker build -t hitec-library .
docker run -p 8000:8000 hitec-library
```

## Support

- Email: touseefurrehman5554@gmail.com
- Phone: +92-3476992071
- Location: HiTec University, Taxila, Pakistan

## License

Proprietary software for HiTec University. All rights reserved.

---

Made with ❤️ for HiTec University Library
