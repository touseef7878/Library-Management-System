# ⚡ HiTec University Library - Quick Reference Guide

## 🚀 Getting Started (30 seconds)

### Windows
```bash
run.bat
```

### Linux/Mac
```bash
bash run.sh
```

### Manual
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Access:** http://localhost:5000

---

## 🔐 Default Credentials

```
Username: admin
Password: admin123
```

⚠️ **Change after first login!**

---

## 📍 Key URLs

| Page | URL |
|------|-----|
| Homepage | http://localhost:5000 |
| Books Catalog | http://localhost:5000/books |
| Library Map | http://localhost:5000/library-map |
| About | http://localhost:5000/about |
| Contact | http://localhost:5000/contact |
| Admin Login | http://localhost:5000/admin/login |
| Admin Dashboard | http://localhost:5000/admin/dashboard |
| Books Management | http://localhost:5000/admin/books |
| Students Management | http://localhost:5000/admin/students |
| Loans Management | http://localhost:5000/admin/loans |

---

## 📚 Admin Tasks

### Add a Book
1. Go to Admin Dashboard
2. Click "Add New Book"
3. Fill in details
4. Click "Add Book"

### Register a Student
1. Go to Admin Dashboard
2. Click "Register Student"
3. Fill in information
4. Click "Register Student"
5. System generates library card number

### Create a Loan
1. Go to Admin Dashboard
2. Click "Create Loan"
3. Select student and book
4. Click "Create Loan"
5. System sets 15-day due date

### Return a Book
1. Go to Loans Management
2. Find the loan
3. Click "Return" button
4. System calculates fine if overdue

### View Student Profile
1. Go to Students Management
2. Click student name
3. View all loans and fines

---

## 🔧 Configuration

### Change Loan Duration
Edit `app.py`:
```python
LOAN_DURATION_DAYS = 15
```

### Change Late Fee
Edit `app.py`:
```python
LATE_FEE_PER_DAY = 50  # PKR
```

### Change Items Per Page
Edit `app.py`:
```python
ITEMS_PER_PAGE = 12
```

---

## 🗄️ Database

### Location
```
database/library.db
```

### Backup
```bash
cp database/library.db database/library_backup.db
```

### Reset
```bash
rm database/library.db
python app.py
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | `python app.py --port 5001` |
| Module not found | `pip install -r requirements.txt` |
| Database locked | `rm database/library.db` |
| Admin login fails | Delete database and restart |
| CSS not loading | Check you're in correct directory |

---

## 📊 System Requirements

- Python 3.7+
- 512MB RAM
- 100MB disk space
- Modern browser

---

## 🎨 Color Scheme

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #001f3f | Headers, buttons |
| Secondary | #0074D9 | Links, accents |
| Accent | #39CCCC | Highlights |
| Success | #2ECC40 | Available, success |
| Danger | #FF4136 | Overdue, errors |
| Warning | #FF851B | Fines, warnings |

---

## 📱 Responsive Breakpoints

- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

---

## 🔐 Security Checklist

- [ ] Change admin password
- [ ] Update secret key
- [ ] Enable HTTPS
- [ ] Set debug=False
- [ ] Use environment variables
- [ ] Regular backups
- [ ] Monitor logs

---

## 📈 Performance Tips

1. Use pagination (12 items/page)
2. Index frequently searched fields
3. Regular database maintenance
4. Monitor server resources
5. Use CDN for static files
6. Enable caching

---

## 🚀 Deployment

### Gunicorn
```bash
gunicorn app:app --workers 4 --bind 0.0.0.0:8000
```

### Docker
```bash
docker-compose up -d
```

### Heroku
```bash
heroku create app-name
git push heroku main
```

---

## 📞 Quick Help

**Can't login?**
- Check username/password
- Delete database and restart

**Book not showing?**
- Check availability
- Refresh page

**Fine not calculating?**
- Return book to trigger calculation
- Check due date

**Student card not working?**
- Check card status (must be Active)
- Verify student exists

---

## 📚 Documentation Files

- `README.md` - Full documentation
- `INSTALLATION.md` - Setup guide
- `SETUP_GUIDE.md` - Configuration
- `FEATURES.md` - All features
- `PROJECT_SUMMARY.md` - Overview
- `QUICK_REFERENCE.md` - This file

---

## 🎯 Common Workflows

### New Library Setup
1. Run application
2. Change admin password
3. Update library info
4. Add books
5. Register students
6. Create sample loans

### Daily Operations
1. Check dashboard
2. View overdue loans
3. Process returns
4. Register new students
5. Add new books

### Month-End
1. Generate reports
2. Collect fines
3. Archive old loans
4. Backup database
5. Review statistics

---

## 💡 Tips & Tricks

- Use search to find books quickly
- Filter by genre to browse
- Check student profiles for history
- View overdue loans regularly
- Monitor total fines
- Backup database weekly

---

## 🔗 Useful Links

- [Flask Docs](https://flask.palletsprojects.com/)
- [Bootstrap Docs](https://getbootstrap.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Leaflet Docs](https://leafletjs.com/)

---

## ✅ Pre-Launch Checklist

- [ ] Application runs without errors
- [ ] Can access all pages
- [ ] Admin login works
- [ ] Can add books
- [ ] Can register students
- [ ] Can create loans
- [ ] Can return books
- [ ] Fines calculate correctly
- [ ] Map displays correctly
- [ ] Responsive on mobile

---

## 🎉 You're All Set!

Your HiTec University Library is ready to go!

**Questions?** Check the documentation files.  
**Issues?** See troubleshooting section.  
**Support?** Email library@hitec.edu.pk

---

**Happy Library Managing!** 📚✨
