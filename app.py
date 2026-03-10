from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Configure the SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'library.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'hitec_university_library_secret_key_2024'

db = SQLAlchemy(app)

ITEMS_PER_PAGE = 12
LOAN_DURATION_DAYS = 15
LATE_FEE_PER_DAY = 50  # PKR per day

def get_utc_now():
    """Get current UTC datetime (naive)"""
    return datetime.utcnow()

# ==================== DATABASE MODELS ====================

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    genre = db.Column(db.String(50))
    year_published = db.Column(db.Integer)
    publisher = db.Column(db.String(150))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    cover_image = db.Column(db.String(500))
    description = db.Column(db.Text)
    average_rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    loans = db.relationship('Loan', backref='book', lazy=True)
    reviews = db.relationship('Review', backref='book', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    department = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    library_card_number = db.Column(db.String(50), unique=True, nullable=False)
    card_status = db.Column(db.String(20), default='active')  # active, suspended, expired
    total_fines = db.Column(db.Float, default=0.0)
    registered_at = db.Column(db.DateTime, default=get_utc_now)
    
    loans = db.relationship('Loan', backref='student', lazy=True)
    reviews = db.relationship('Review', backref='student', lazy=True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=get_utc_now)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    is_returned = db.Column(db.Boolean, default=False)
    fine_amount = db.Column(db.Float, default=0.0)
    
    def calculate_fine(self):
        """Calculate fine for overdue books"""
        if not self.is_returned:
            now = get_utc_now()
            if now > self.due_date:
                days_overdue = (now - self.due_date).days
                self.fine_amount = days_overdue * LATE_FEE_PER_DAY
        return self.fine_amount
    
    def is_overdue(self):
        """Check if loan is overdue"""
        if not self.is_returned:
            return get_utc_now() > self.due_date
        return False
    
    def days_remaining(self):
        """Get days remaining to return book"""
        if not self.is_returned:
            remaining = (self.due_date - get_utc_now()).days
            return max(0, remaining)
        return 0

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_utc_now)

class LibrarySettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    library_name = db.Column(db.String(200), default='HiTec University Library')
    library_address = db.Column(db.String(500))
    library_phone = db.Column(db.String(20))
    library_email = db.Column(db.String(100))
    opening_hours = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

# ==================== AUTHENTICATION ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ==================== ADMIN DASHBOARD ====================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    total_books = Book.query.count()
    total_students = Student.query.count()
    active_loans = Loan.query.filter_by(is_returned=False).count()
    overdue_loans = Loan.query.filter(
        Loan.is_returned == False,
        Loan.due_date < get_utc_now()
    ).count()
    total_fines = db.session.query(db.func.sum(Student.total_fines)).scalar() or 0
    
    recent_loans = Loan.query.order_by(Loan.loan_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_books=total_books,
                         total_students=total_students,
                         active_loans=active_loans,
                         overdue_loans=overdue_loans,
                         total_fines=total_fines,
                         recent_loans=recent_loans)

# ==================== ADMIN BOOKS ====================

@app.route('/admin/books')
@login_required
def admin_books():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Book.query
    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%')
            )
        )
    
    books = query.paginate(page=page, per_page=ITEMS_PER_PAGE)
    return render_template('admin/books.html', books=books, search=search)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
def admin_add_book():
    if request.method == 'POST':
        try:
            book = Book(
                title=request.form.get('title'),
                author=request.form.get('author'),
                isbn=request.form.get('isbn'),
                genre=request.form.get('genre'),
                year_published=request.form.get('year_published', type=int),
                publisher=request.form.get('publisher'),
                total_copies=request.form.get('total_copies', 1, type=int),
                available_copies=request.form.get('total_copies', 1, type=int),
                description=request.form.get('description'),
                cover_image=request.form.get('cover_image', '')
            )
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('admin_books'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding book: {str(e)}', 'danger')
    
    return render_template('admin/add_book.html')

@app.route('/admin/books/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_book(id):
    book = Book.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            book.title = request.form.get('title')
            book.author = request.form.get('author')
            book.isbn = request.form.get('isbn')
            book.genre = request.form.get('genre')
            book.year_published = request.form.get('year_published', type=int)
            book.publisher = request.form.get('publisher')
            book.description = request.form.get('description')
            book.cover_image = request.form.get('cover_image', '')
            
            db.session.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('admin_books'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating book: {str(e)}', 'danger')
    
    return render_template('admin/edit_book.html', book=book)

@app.route('/admin/books/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_book(id):
    book = Book.query.get_or_404(id)
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting book: {str(e)}', 'danger')
    
    return redirect(url_for('admin_books'))

# ==================== ADMIN STUDENTS ====================

@app.route('/admin/students')
@login_required
def admin_students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Student.query
    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(f'%{search}%'),
                Student.roll_number.ilike(f'%{search}%'),
                Student.library_card_number.ilike(f'%{search}%')
            )
        )
    
    students = query.paginate(page=page, per_page=ITEMS_PER_PAGE)
    return render_template('admin/students.html', students=students, search=search)

@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required
def admin_add_student():
    if request.method == 'POST':
        try:
            # Generate library card number
            card_number = f"HU{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            student = Student(
                name=request.form.get('name'),
                email=request.form.get('email'),
                roll_number=request.form.get('roll_number'),
                phone=request.form.get('phone'),
                department=request.form.get('department'),
                semester=request.form.get('semester', type=int),
                library_card_number=card_number
            )
            db.session.add(student)
            db.session.commit()
            flash(f'Student added successfully! Card Number: {card_number}', 'success')
            return redirect(url_for('admin_students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'danger')
    
    return render_template('admin/add_student.html')

@app.route('/admin/students/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_student(id):
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            student.name = request.form.get('name')
            student.email = request.form.get('email')
            student.phone = request.form.get('phone')
            student.department = request.form.get('department')
            student.semester = request.form.get('semester', type=int)
            student.card_status = request.form.get('card_status')
            
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin_students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')
    
    return render_template('admin/edit_student.html', student=student)

@app.route('/admin/students/<int:id>')
@login_required
def admin_student_detail(id):
    student = Student.query.get_or_404(id)
    loans = Loan.query.filter_by(student_id=id).order_by(Loan.loan_date.desc()).all()
    
    for loan in loans:
        loan.calculate_fine()
    
    return render_template('admin/student_detail.html', student=student, loans=loans)

# ==================== ADMIN LOANS ====================

@app.route('/admin/loans')
@login_required
def admin_loans():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'active')
    
    query = Loan.query
    
    if status == 'active':
        query = query.filter_by(is_returned=False)
    elif status == 'overdue':
        query = query.filter(
            Loan.is_returned == False,
            Loan.due_date < get_utc_now()
        )
    elif status == 'returned':
        query = query.filter_by(is_returned=True)
    
    loans = query.order_by(Loan.loan_date.desc()).paginate(page=page, per_page=ITEMS_PER_PAGE)
    
    for loan in loans.items:
        loan.calculate_fine()
    
    return render_template('admin/loans.html', loans=loans, status=status)

@app.route('/admin/loans/create', methods=['GET', 'POST'])
@login_required
def admin_create_loan():
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id', type=int)
            book_id = request.form.get('book_id', type=int)
            
            student = Student.query.get_or_404(student_id)
            book = Book.query.get_or_404(book_id)
            
            # Validations
            if student.card_status != 'active':
                flash('Student card is not active', 'danger')
                return redirect(url_for('admin_create_loan'))
            
            if book.available_copies <= 0:
                flash('Book is not available', 'danger')
                return redirect(url_for('admin_create_loan'))
            
            existing_loan = Loan.query.filter_by(
                student_id=student_id,
                book_id=book_id,
                is_returned=False
            ).first()
            
            if existing_loan:
                flash('Student already has an active loan for this book', 'danger')
                return redirect(url_for('admin_create_loan'))
            
            # Create loan
            loan = Loan(
                student_id=student_id,
                book_id=book_id,
                due_date=get_utc_now() + timedelta(days=LOAN_DURATION_DAYS)
            )
            
            book.available_copies -= 1
            
            db.session.add(loan)
            db.session.commit()
            
            flash('Loan created successfully!', 'success')
            return redirect(url_for('admin_loans'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating loan: {str(e)}', 'danger')
    
    students = Student.query.filter_by(card_status='active').all()
    books = Book.query.filter(Book.available_copies > 0).all()
    
    return render_template('admin/create_loan.html', students=students, books=books)

@app.route('/admin/loans/<int:id>/return', methods=['POST'])
@login_required
def admin_return_loan(id):
    loan = Loan.query.get_or_404(id)
    
    try:
        loan.is_returned = True
        loan.return_date = get_utc_now()
        loan.calculate_fine()
        
        loan.student.total_fines += loan.fine_amount
        loan.book.available_copies += 1
        
        db.session.commit()
        flash('Book returned successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error returning book: {str(e)}', 'danger')
    
    return redirect(url_for('admin_loans'))

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Public homepage"""
    # Get featured books with ratings, ordered by average rating
    featured_books = Book.query.order_by(Book.average_rating.desc()).limit(6).all()
    total_books = Book.query.count()
    total_students = Student.query.count()
    
    return render_template('public/index.html',
                         featured_books=featured_books,
                         total_books=total_books,
                         total_students=total_students)

@app.route('/books')
def public_books():
    """Public book catalog"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    genre = request.args.get('genre', '')
    
    query = Book.query
    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%')
            )
        )
    if genre:
        query = query.filter_by(genre=genre)
    
    books = query.paginate(page=page, per_page=ITEMS_PER_PAGE)
    genres = db.session.query(Book.genre).distinct().filter(Book.genre != None).all()
    genres = [g[0] for g in genres]
    
    return render_template('public/books.html', books=books, search=search, genre=genre, genres=genres)

@app.route('/books/<int:id>')
def book_detail(id):
    """Book detail page"""
    book = Book.query.get_or_404(id)
    reviews = Review.query.filter_by(book_id=id).order_by(Review.created_at.desc()).all()
    
    return render_template('public/book_detail.html', book=book, reviews=reviews)

@app.route('/about')
def about():
    """About library page with map"""
    settings = LibrarySettings.query.first()
    if not settings:
        settings = LibrarySettings(
            library_name='HITEC University Library',
            library_address='HITEC University, Taxila, Pakistan',
            library_phone='+92-51-9048-5000',
            library_email='library@hitec.edu.pk',
            opening_hours='Mon-Fri: 8:00 AM - 10:00 PM | Sat: 9:00 AM - 5:00 PM | Sun: Closed',
            latitude=33.7265,
            longitude=72.8194
        )
        db.session.add(settings)
        db.session.commit()
    
    return render_template('public/about.html', settings=settings)

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('public/contact.html')

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database with default data"""
    db.create_all()
    
    # Create default admin if not exists
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', email='admin@hitec.edu.pk')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    # Create library settings if not exists
    if not LibrarySettings.query.first():
        settings = LibrarySettings(
            library_name='HITEC University Library',
            library_address='HITEC University, Taxila, Pakistan',
            library_phone='+92-51-9048-5000',
            library_email='library@hitec.edu.pk',
            opening_hours='Mon-Fri: 8:00 AM - 10:00 PM | Sat: 9:00 AM - 5:00 PM | Sun: Closed',
            latitude=33.7265,
            longitude=72.8194
        )
        db.session.add(settings)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    
    app.run(debug=True)
