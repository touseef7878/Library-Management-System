# 📚 BookHub - Library Management System

A modern, full-featured web application for managing library operations, built with Flask and SQLite. This system provides efficient management of books, members, loans, and book reviews through a clean and intuitive interface.

## ✨ Features

### 📖 Book Management
- Add, update, and delete books
- Search books by title, author, or genre
- Track book ratings and reviews
- Display average ratings for each book
- Real-time availability status (Available/On Loan)
- Book statistics dashboard with rating distribution
- Export books to CSV

### 👥 Member Management
- Register new library members
- Update member information
- Track member registration dates
- Email validation and duplicate prevention
- Member activity dashboard showing loan history and reviews
- Export members to CSV

### 📋 Loan Management
- Create and track book loans
- Automatic overdue loan detection
- Visual status indicators (Active/Overdue/Returned)
- Prevent duplicate loans for the same book
- Late fee calculator ($1 per day overdue)
- Complete loan history with all transactions
- Export loans to CSV

### ⭐ Review System
- Members can rate books (1-5 stars)
- Write detailed reviews
- Automatic average rating calculation
- One review per member per book
- View all reviews for each book

### 🔥 New Advanced Features

#### 1. Export to CSV
- Export books, members, and loans data to CSV format
- Easy data backup and analysis
- Accessible from each section's page

#### 2. Book Availability Status
- Real-time availability indicator on book listings
- Visual badges showing if book is available or on loan
- Prevents booking unavailable books

#### 3. Popular Books Page
- Top 10 books based on reviews and ratings
- Shows review count and average rating
- Quick access to book reviews and statistics

#### 4. Member Activity Dashboard
- Complete member profile with statistics
- View all loans (active and returned)
- See all reviews written by member
- Track total late fees
- Quick overview of member engagement

#### 5. Late Fee Calculator
- Automatic calculation of late fees ($1/day)
- Real-time fee display on loan listings
- Helps track overdue penalties
- Shows fees in member activity dashboard

#### 6. Book Statistics Page
- Detailed book analytics
- Rating distribution chart
- Total loan count
- Current availability status
- Visual progress bars for ratings

#### 7. Complete Loan History
- View all loans (active and returned)
- Filter between active loans and complete history
- Track book return status
- Historical data for reporting

### 🎨 Modern UI
- Responsive Bootstrap design
- Custom color scheme with purple theme
- Emoji icons for better visual appeal
- Card-based layouts for forms
- Dashboard with statistics
- Progress bars and visual indicators
- Hover effects and smooth transitions

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Library-Management-System
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python create_db.py
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 📦 Dependencies

- Flask 3.0.3 - Web framework
- Flask-SQLAlchemy 3.1.1 - Database ORM
- gunicorn 23.0.0 - Production server

## 🗂️ Project Structure

```
Library-Management-System/
├── app.py                 # Main application file with all routes
├── create_db.py          # Database initialization
├── requirements.txt      # Python dependencies
├── database/
│   └── library.db       # SQLite database
├── static/
│   ├── css/            # Bootstrap CSS
│   └── js/             # Bootstrap JavaScript
└── templates/          # HTML templates
    ├── base.html       # Base template with navigation
    ├── index.html      # Dashboard with statistics
    ├── books.html      # Book listing with search
    ├── add_book.html   # Add book form
    ├── update_book.html # Update book form
    ├── book_reviews.html # Book reviews page
    ├── book_stats.html  # Book statistics dashboard
    ├── popular_books.html # Top rated books
    ├── members.html    # Member listing
    ├── add_member.html # Add member form
    ├── update_member.html # Update member form
    ├── member_activity.html # Member activity dashboard
    ├── loans.html      # Active loan listing
    ├── add_loan.html   # Add loan form
    └── loan_history.html # Complete loan history
```

## 🎯 Key Endpoints

### Books
- `GET /books` - List all books with search
- `GET /books/add` - Add new book form
- `POST /books/add` - Create new book
- `GET /books/update/<id>` - Update book form
- `POST /books/update/<id>` - Update book
- `POST /books/delete/<id>` - Delete book
- `GET /books/<id>/reviews` - View/add reviews
- `GET /books/<id>/stats` - Book statistics
- `GET /books/popular` - Popular books
- `GET /export/books` - Export books to CSV

### Members
- `GET /members` - List all members
- `GET /members/add` - Add new member form
- `POST /members/add` - Create new member
- `GET /members/update/<id>` - Update member form
- `POST /members/update/<id>` - Update member
- `POST /members/delete/<id>` - Delete member
- `GET /members/<id>/activity` - Member activity dashboard
- `GET /export/members` - Export members to CSV

### Loans
- `GET /loans` - List active loans
- `GET /loans/add` - Add new loan form
- `POST /loans/add` - Create new loan
- `POST /loans/delete/<id>` - Return book (mark as returned)
- `GET /loans/history` - Complete loan history
- `GET /export/loans` - Export loans to CSV

### Dashboard
- `GET /` - Home page with statistics

## 💡 Usage

### Dashboard
The home page displays key statistics:
- Total number of books
- Total number of members
- Active loans count
- Total reviews

### Managing Books
1. Navigate to "Books" from the navigation menu
2. Use the search bar to find specific books
3. Click "Add New Book" to register a new book
4. Click "Stats" to view detailed book statistics
5. Click "Edit" to update book information
6. Click "Reviews" to see or add reviews
7. Click "Delete" to remove a book
8. Click "Export CSV" to download books data
9. Click "Popular Books" to see top-rated books

### Managing Members
1. Navigate to "Members" from the navigation menu
2. Click "Add New Member" to register a new member
3. Email addresses must be unique
4. Click "Activity" to view member's complete activity
5. Click "Edit" to update member information
6. Click "Delete" to remove a member
7. Click "Export CSV" to download members data

### Managing Loans
1. Navigate to "Loans" from the navigation menu (shows active loans)
2. Click "Add New Loan" to create a new loan
3. Select a member and an available book
4. Set loan and return dates
5. Overdue loans are highlighted in red with late fees
6. Click "Return Book" to mark a loan as returned
7. Click "View History" to see all loans (including returned)
8. Click "Export CSV" to download loans data

### Adding Reviews
1. Go to the Books page
2. Click "Reviews" on any book
3. Select your name from the member list
4. Choose a rating (1-5 stars)
5. Write your review (optional)
6. Submit the review

### Viewing Statistics
1. Click "Stats" on any book to see:
   - Average rating
   - Total reviews
   - Total loans
   - Availability status
   - Rating distribution chart

### Member Activity
1. Click "Activity" on any member to see:
   - Total loans and active loans
   - Complete loan history
   - All reviews written
   - Total late fees accumulated

### Popular Books
1. Navigate to "Popular" from the navigation menu
2. View top 10 books based on reviews and ratings
3. Quick access to reviews and statistics

## 🔒 Security Features

- Email validation for members
- Duplicate email prevention
- Date validation for loans
- One review per member per book
- SQL injection protection via SQLAlchemy ORM
- Form validation on both client and server side
- Confirmation dialogs for destructive actions

## 📊 Database Schema

### Book
- id (Primary Key)
- title
- author
- genre
- year_published
- average_rating

### Member
- id (Primary Key)
- name
- email (Unique)
- contact
- member_since

### Loan
- id (Primary Key)
- member_id (Foreign Key)
- book_id (Foreign Key)
- loan_date
- return_date
- returned (Boolean)
- late_fee

### Review
- id (Primary Key)
- book_id (Foreign Key)
- member_id (Foreign Key)
- rating (1-5)
- comment
- date_posted

## 🎨 Color Scheme

- Primary: #6B4E71 (Purple)
- Secondary: #8E7C93 (Light Purple)
- Accent: #B6A6BB (Pale Purple)
- Background: #F5F0F6 (Very Light Purple)

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👨‍💻 Development

To run in development mode:
```bash
python app.py
```

For production deployment, use gunicorn:
```bash
gunicorn app:app
```

---

Made with ❤️ using Flask and Bootstrap
