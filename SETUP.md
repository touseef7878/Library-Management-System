# Complete Setup Guide

## 🚀 Fresh Installation (First Time Setup)

Follow these steps in order:

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Database with Sample Data
```bash
python seed_database.py
```
This will:
- Create the database (`database/library.db`)
- Add 1 admin account
- Add 300 students
- Add 50 books
- Add sample loans, reviews, and rental requests
- Create `static/books/` directory with placeholder files

### Step 3: Download Real Book Content (Optional but Recommended)
```bash
python setup_book_content.py
```
This will:
- Read all books from the database
- Download public domain books from Project Gutenberg
- Map content to each book ID
- Update OnlineBook records

**Note:** This step requires internet connection and takes 2-3 minutes.

### Step 4: Run the Application
```bash
python app.py
```
Or use the startup script:
```bash
bash run.sh          # Linux/Mac
./run.sh             # Linux/Mac
python app.py        # Windows
```

Access at: `http://127.0.0.1:5000`

---

## 🔄 Reset Database (Start Fresh)

If you want to delete everything and start over:

### Option 1: Quick Reset (Recommended)
```bash
# Delete database
rm database/library.db              # Linux/Mac
del database\library.db             # Windows

# Delete book files (optional)
rm -rf static/books/*               # Linux/Mac
del /Q static\books\*               # Windows

# Recreate everything
python seed_database.py
python setup_book_content.py
python app.py
```

### Option 2: Use Reset Script (if available)
```bash
python reset_database.py
```

---

## 📋 Default Credentials

### Admin Login
- **URL:** `http://127.0.0.1:5000/admin/login`
- **Username:** `admin`
- **Password:** `admin123`

### Student Login
- **URL:** `http://127.0.0.1:5000/login`
- **Library Card:** Any from the 300 generated (e.g., `22-CS-051`, `23-EE-123`)
- **Password:** Any password (card must be active)

To see all student cards:
```bash
python -c "from app import app, db, Student; app.app_context().push(); students = Student.query.limit(10).all(); [print(f'{s.roll_number} - {s.name}') for s in students]"
```

---

## 🛠️ Troubleshooting

### Database Locked Error
```bash
# Close all connections and delete
rm database/library.db
python seed_database.py
```

### Book Content Not Loading
```bash
# Re-download book content
python setup_book_content.py
```

### Port Already in Use
```bash
# Change port in app.py (last line)
app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## 📁 What Gets Created

After running `seed_database.py`:
```
database/
└── library.db              # SQLite database

static/books/
├── book_1_sample.txt       # Placeholder files
├── book_2_sample.txt
└── ... (50 files)
```

After running `setup_book_content.py`:
```
static/books/
├── book_1_sample.txt       # Real book content (Frankenstein)
├── book_2_sample.txt       # Real book content (Pride & Prejudice)
└── ... (50 files with real content)
```

---

## ⚙️ Configuration

### Change Loan Duration
Edit `app.py`:
```python
LOAN_DURATION_DAYS = 15  # Change to desired days
```

### Change Late Fee
Edit `app.py`:
```python
LATE_FEE_PER_DAY = 50  # Change to desired amount (PKR)
```

### Change Max Active Loans
Edit `app.py`:
```python
MAX_ACTIVE_LOANS = 3  # Change to desired number
```

---

## 🔐 Security Notes

**Before deploying to production:**

1. Change admin password:
```python
# In seed_database.py, line ~200
admin = Admin(username='admin', password='YOUR_SECURE_PASSWORD')
```

2. Set Flask secret key:
```python
# In app.py
app.config['SECRET_KEY'] = 'your-very-secure-random-secret-key'
```

3. Disable debug mode:
```python
# In app.py, last line
app.run(debug=False)
```

---

## 📊 Database Statistics

After seeding, you'll have:
- ✅ 1 Admin account
- ✅ 300 Students (across 10 departments)
- ✅ 50 Books (5 genres)
- ✅ ~20 Active loans
- ✅ ~15 Rental requests
- ✅ ~30 Reviews
- ✅ 50 Online book records

---

## 🆘 Need Help?

1. Check if database exists: `ls database/library.db`
2. Check if books exist: `ls static/books/`
3. Check Python version: `python --version` (need 3.7+)
4. Check dependencies: `pip list`

For more help, contact: library@hitecuni.edu.pk
