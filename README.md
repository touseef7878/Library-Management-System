# 📚 HiTec University Library Management System

A professional, full-featured library management system built for HiTec University. This system enables efficient management of books, student library cards, loans with automatic fine calculation, and provides a complete web interface for both administrators and students.

## ✨ Key Features

### 🎓 Student Library Card System
- Unique library card generation for each student
- Card status management (Active, Suspended, Expired)
- Student profile with department and semester information
- Complete loan history tracking

### 📖 Book Management
- Comprehensive book catalog with ISBN, genre, publisher, and year
- Book availability tracking (total copies vs available copies)
- Book cover images and descriptions
- Advanced search by title, author, or ISBN
- Genre-based filtering

### 📋 Loan Management
- 15-day loan duration (configurable)
- Automatic late fee calculation (PKR 50/day)
- Real-time overdue detection
- Loan status tracking (Active, Overdue, Returned)
- Complete loan history with fine calculations
- Prevent duplicate loans for same book

### ⭐ Review System
- Students can rate books (1-5 stars)
- Write detailed reviews
- Automatic average rating calculation
- View all reviews for each book

### 🗺️ Interactive Map
- Leaflet.js integration for library location
- Get directions to the library
- Library contact information and hours

### 🔐 Admin Panel
- Secure login system with password hashing
- Dashboard with key statistics
- Books management (Add, Edit, Delete)
- Students management (Register, Edit, View)
- Loans management (Create, Return, Track)
- Overdue tracking and fine management

### 🎨 Professional UI
- Modern Bootstrap 5 design
- Responsive layout for all devices
- Professional color scheme (Navy Blue & Cyan)
- Smooth animations and transitions
- Intuitive navigation

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd hitec-library-system
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python app.py
```

5. **Access the application:**
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 📝 Default Admin Credentials

```
Username: admin
Password: admin123
```

⚠️ **Important:** Change these credentials in production!

## 🗂️ Project Structure

```
hitec-library-system/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── database/
│   └── library.db                 # SQLite database
├── static/
│   ├── css/                       # Bootstrap CSS
│   ├── js/                        # Bootstrap JavaScript
│   └── images/
│       └── logo.png               # HiTec University logo
└── templates/
    ├── base.html                  # Base template with navbar/footer
    ├── admin/
    │   ├── login.html             # Admin login page
    │   ├── dashboard.html         # Admin dashboard
    │   ├── books.html             # Books management
    │   ├── add_book.html          # Add book form
    │   ├── edit_book.html         # Edit book form
    │   ├── students.html          # Students management
    │   ├── add_student.html       # Register student form
    │   ├── edit_student.html      # Edit student form
    │   ├── student_detail.html    # Student profile & loans
    │   ├── loans.html             # Loans management
    │   └── create_loan.html       # Create loan form
    ├── public/
    │   ├── index.html             # Public homepage
    │   ├── books.html             # Public book catalog
    │   ├── book_detail.html       # Book detail page
    │   ├── map.html               # Library location map
    │   ├── about.html             # About library
    │   └── contact.html           # Contact page
    └── errors/
        ├── 404.html               # Page not found
        └── 500.html               # Server error
```

## 🔑 Key Endpoints

### Public Routes
- `GET /` - Homepage with featured books
- `GET /books` - Book catalog with search and filters
- `GET /books/<id>` - Book detail page with reviews
- `GET /library-map` - Interactive map with location
- `GET /about` - About library page
- `GET /contact` - Contact information

### Admin Routes
- `GET /admin/login` - Admin login page
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/books` - Books management
- `POST /admin/books/add` - Add new book
- `POST /admin/books/<id>/edit` - Edit book
- `POST /admin/books/<id>/delete` - Delete book
- `GET /admin/students` - Students management
- `POST /admin/students/add` - Register student
- `POST /admin/students/<id>/edit` - Edit student
- `GET /admin/students/<id>` - Student profile
- `GET /admin/loans` - Loans management
- `POST /admin/loans/create` - Create loan
- `POST /admin/loans/<id>/return` - Return book

## 💾 Database Schema

### Admin
- id (Primary Key)
- username (Unique)
- password_hash
- email (Unique)
- created_at

### Book
- id (Primary Key)
- title
- author
- isbn (Unique)
- genre
- year_published
- publisher
- total_copies
- available_copies
- cover_image
- description
- average_rating
- created_at

### Student
- id (Primary Key)
- name
- email (Unique)
- roll_number (Unique)
- phone
- department
- semester
- library_card_number (Unique)
- card_status (active/suspended/expired)
- total_fines
- registered_at

### Loan
- id (Primary Key)
- student_id (Foreign Key)
- book_id (Foreign Key)
- loan_date
- due_date
- return_date
- is_returned (Boolean)
- fine_amount

### Review
- id (Primary Key)
- book_id (Foreign Key)
- student_id (Foreign Key)
- rating (1-5)
- comment
- created_at

### LibrarySettings
- id (Primary Key)
- library_name
- library_address
- library_phone
- library_email
- opening_hours
- latitude
- longitude

## 🎨 Color Scheme

- **Primary:** #001f3f (Navy Blue)
- **Secondary:** #0074D9 (Bright Blue)
- **Accent:** #39CCCC (Cyan)
- **Success:** #2ECC40 (Green)
- **Danger:** #FF4136 (Red)
- **Warning:** #FF851B (Orange)

## 🔒 Security Features

- Password hashing using Werkzeug
- SQL injection protection via SQLAlchemy ORM
- Session-based authentication for admin
- Form validation on both client and server
- CSRF protection ready (add Flask-WTF for production)
- Confirmation dialogs for destructive actions

## 📊 Loan Policy

- **Loan Duration:** 15 days
- **Late Fee:** PKR 50 per day
- **Maximum Books:** No limit (configurable)
- **Renewal:** Available if not requested by another student
- **Damage/Loss:** Student responsible for borrowed books

## 🚀 Deployment

### Using Gunicorn (Production)
```bash
gunicorn app:app --workers 4 --bind 0.0.0.0:8000
```

### Using Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t hitec-library .
docker run -p 8000:8000 hitec-library
```

## 📈 Future Enhancements

- Email notifications for overdue books
- SMS alerts for students
- Mobile app integration
- Advanced analytics and reporting
- Book reservation system
- Digital library integration
- QR code generation for library cards
- Integration with Supabase for cloud database
- Payment gateway for fine collection
- Multi-language support

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is proprietary software for HiTec University. All rights reserved.

## 👨‍💻 Support

For technical support or inquiries:
- Email: library@hitec.edu.pk
- Phone: +92-51-XXXX-XXXX
- Location: HiTec University, Taxila, Pakistan

---

**Made with ❤️ for HiTec University Library**

*Professional Library Management System - Empowering Academic Excellence*
