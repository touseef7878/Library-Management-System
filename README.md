# HiTec University Library Management System

A modern, full-featured library management system built with Flask, featuring online book reading, rental requests, automatic fine calculation, and responsive design for both desktop and mobile.

## ✨ Features

### For Students
- 📚 Browse and search book catalog
- 📝 Request book rentals online
- 📖 Read books online with beautiful reader interface
- 📊 Track rental requests and active loans
- ⭐ Rate and review books
- 📱 Fully responsive mobile interface

### For Administrators
- 👥 Manage students and library cards
- 📚 Manage book inventory
- ✅ Approve/reject rental requests
- 💰 Automatic fine calculation (PKR 50/day overdue)
- 📊 Dashboard with statistics
- 📖 Upload books for online reading
- 📋 Audit logs and reports

### Technical Features
- 🎨 Modern, responsive UI with Bootstrap 5
- 📱 Mobile-optimized design
- 🔐 Secure authentication system
- 💾 SQLite database
- 📖 Online book reader with font controls and dark mode
- 🔍 Advanced search and filtering
- 📊 Real-time statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation & Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd Library-Management-System

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create database with sample data
python seed_database.py

# 4. Download real book content (optional, 2-3 min)
python setup_book_content.py

# 5. Run application
python app.py
```

**Access at:** `http://127.0.0.1:5000`

### Default Credentials

**Admin Login:**
- URL: `/admin/login`
- Username: `admin`
- Password: `admin123`

**Student Login:**
- URL: `/login`
- Library Card: `22-CS-051` (or any generated card)
- Password: Any password

### Reset Database

```bash
# Automated reset (deletes everything and recreates)
python reset_database.py

# Manual reset
rm database/library.db        # Delete database
python seed_database.py       # Recreate
python setup_book_content.py  # Download books
```
pip install -r requirements.txt

# Initialize database with sample data
python seed_database.py

# Run application
python app.py
```

Access at `http://127.0.0.1:5000`

### Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`

**Student Login:**
- Use any generated library card number (e.g., `22-CS-051`)
- Password: Any password (card must be active)

## 📁 Project Structure

```
Library-Management-System/
├── app.py                      # Main Flask application
├── seed_database.py            # Database initialization script
├── setup_book_content.py       # Book content fetcher (optional)
├── requirements.txt            # Python dependencies
├── run.sh                      # Startup script
├── database/
│   └── library.db             # SQLite database (auto-created)
├── static/
│   ├── books/                 # Book content files (txt, pdf, epub)
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── images/                # Images and assets
└── templates/
    ├── admin/                 # Admin panel templates
    ├── student/               # Student portal templates
    ├── public/                # Public pages
    ├── errors/                # Error pages
    └── base.html              # Base template
```

## 📖 Book Content Setup

The system includes a script to fetch public domain books from Project Gutenberg:

```bash
python setup_book_content.py
```

This will:
- Read all books from your database
- Download appropriate public domain content
- Map content to each book ID
- Update the database with file paths

**Note:** Modern textbooks are under copyright. The script uses classic literature as placeholders for educational purposes.

## 🔧 Configuration

### Database
- SQLite database stored in `database/library.db`
- Automatically created on first run
- Run `seed_database.py` to populate with sample data

### Loan Policy
- **Duration:** 15 days
- **Late Fee:** PKR 50 per day
- **Automatic Calculation:** Fines calculated on return

### File Uploads
- Book files stored in `static/books/`
- Supported formats: TXT, PDF, EPUB
- Maximum file size: Configurable in Flask

## 🌐 API Routes

### Public Routes
- `GET /` - Homepage
- `GET /books` - Book catalog
- `GET /books/<id>` - Book details
- `GET /about` - About page
- `GET /contact` - Contact page

### Student Routes
- `POST /login` - Student login
- `GET /student/dashboard` - Student dashboard
- `GET /student/loans` - Active loans
- `POST /student/rental/request/<book_id>` - Request book
- `GET /student/loan/<id>/read` - Read book online
- `POST /student/loan/<id>/return` - Return book

### Admin Routes
- `POST /admin/login` - Admin login
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/books` - Manage books
- `GET /admin/students` - Manage students
- `GET /admin/loans` - Manage loans
- `GET /admin/rental-requests` - Manage requests
- `POST /admin/rental-request/<id>/approve` - Approve request
- `POST /admin/rental-request/<id>/reject` - Reject request

## 📊 Database Schema

### Main Tables
- **Admin** - Administrator accounts
- **Student** - Student information and library cards
- **Book** - Book catalog with metadata
- **Loan** - Active and historical loans
- **BookRentalRequest** - Rental request workflow
- **OnlineBook** - Digital book files
- **Review** - Student ratings and reviews
- **LibrarySettings** - System configuration

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn app:app --workers 4 --bind 0.0.0.0:8000
```

### Using Docker (if Dockerfile exists)
```bash
docker build -t library-system .
docker run -p 5000:5000 library-system
```

## 🔒 Security Notes

- Change default admin password in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Regular database backups recommended
- Keep dependencies updated

## 📝 License

Proprietary software for HiTec University. All rights reserved.

## 📞 Support

- **Email:** library@hitec.edu.pk
- **Phone:** +92-51-9048-5000
- **Location:** HiTec University, Taxila, Pakistan
- **Hours:** Mon-Fri: 8:00 AM - 10:00 PM, Sat: 9:00 AM - 5:00 PM

## 🙏 Acknowledgments

- Book content from [Project Gutenberg](https://www.gutenberg.org/) (Public Domain)
- UI Framework: [Bootstrap 5](https://getbootstrap.com/)
- Icons: [Font Awesome](https://fontawesome.com/)

---

Made with ❤️ for HiTec University
