from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime, timedelta, timezone
import json
import secrets
import re

app = Flask(__name__)

# Configure the SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'library.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

db = SQLAlchemy(app)

ITEMS_PER_PAGE = 12
LOAN_DURATION_DAYS = 15
LATE_FEE_PER_DAY = 50  # PKR per day
MAX_ACTIVE_LOANS = 5  # Maximum books a student can borrow at once
MAX_OVERDUE_FINES = 5000  # PKR - Maximum fine before account suspension

def get_utc_now():
    """Get current UTC datetime (timezone-aware)"""
    return datetime.now(timezone.utc).replace(tzinfo=None)

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
    password_hash = db.Column(db.String(255), nullable=True)  # For student authentication
    card_status = db.Column(db.String(20), default='active')  # active, suspended, expired
    total_fines = db.Column(db.Float, default=0.0)
    registered_at = db.Column(db.DateTime, default=get_utc_now)
    profile_image = db.Column(db.String(500), default='https://ui-avatars.com/api/?name={}&background=random'.format('Student'))
    last_login = db.Column(db.DateTime, nullable=True)
    
    loans = db.relationship('Loan', backref='student', lazy=True)
    reviews = db.relationship('Review', backref='student', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return True  # Backward compatibility for students without passwords
        return check_password_hash(self.password_hash, password)
    
    def can_borrow(self):
        """Check if student can borrow more books"""
        active_loans = Loan.query.filter_by(student_id=self.id, is_returned=False).count()
        return active_loans < MAX_ACTIVE_LOANS and self.total_fines < MAX_OVERDUE_FINES and self.card_status == 'active'

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
    library_name = db.Column(db.String(200), default='HITEC University Taxila Library')
    library_address = db.Column(db.String(500))
    library_phone = db.Column(db.String(20))
    library_email = db.Column(db.String(100))
    opening_hours = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

class BookRentalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=get_utc_now)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    approval_date = db.Column(db.DateTime, nullable=True)
    loan_start_date = db.Column(db.DateTime, nullable=True)
    loan_end_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    student = db.relationship('Student', backref='rental_requests')
    book = db.relationship('Book', backref='rental_requests')
    admin = db.relationship('Admin', backref='approved_requests')

class OnlineBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, epub, mobi
    upload_date = db.Column(db.DateTime, default=get_utc_now)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    
    book = db.relationship('Book', backref='online_books')
    admin = db.relationship('Admin', backref='uploaded_books')

class FinePayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='cash')  # cash, card, online
    payment_date = db.Column(db.DateTime, default=get_utc_now)
    received_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    student = db.relationship('Student', backref='fine_payments')
    admin = db.relationship('Admin', backref='received_payments')

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # admin, student
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=True)  # book, student, loan, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=get_utc_now)

class BookReservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    reservation_date = db.Column(db.DateTime, default=get_utc_now)
    expiry_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, fulfilled, expired, cancelled
    notified = db.Column(db.Boolean, default=False)
    
    student = db.relationship('Student', backref='reservations')
    book = db.relationship('Book', backref='reservations')

# ==================== AUTHENTICATION ====================

def log_audit(user_id, user_type, action, entity_type=None, entity_id=None, details=None):
    """Log user actions for audit trail"""
    try:
        log = AuditLog(
            user_id=user_id,
            user_type=user_type,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Audit log error: {str(e)}")

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?[\d\s-]{10,15}$'
    return re.match(pattern, phone) is not None

def validate_isbn(isbn):
    """Validate ISBN format"""
    isbn = isbn.replace('-', '').replace(' ', '')
    return len(isbn) in [10, 13] and isbn.isdigit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def student_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# UNIFIED LOGIN ROUTE
# ============================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Unified login for both admin and students with role-based redirection"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username/Library Card and password are required', 'danger')
            return render_template('login.html')
        
        # Try admin login first
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session.permanent = True
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            log_audit(admin.id, 'admin', 'login', details='Successful login')
            flash('Welcome back, Administrator!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Try student login
        student = Student.query.filter_by(library_card_number=username).first()
        if student:
            # Check password
            if student.password_hash and not student.check_password(password):
                flash('Invalid password', 'danger')
                log_audit(student.id, 'student', 'failed_login', details='Invalid password')
                return render_template('login.html')
            
            # Check card status
            if student.card_status != 'active':
                flash(f'Your library card is {student.card_status}. Please contact the library.', 'danger')
                return render_template('login.html')
            
            # Check fines
            if student.total_fines >= MAX_OVERDUE_FINES:
                flash(f'Your account is suspended due to outstanding fines (PKR {student.total_fines:.2f}). Please pay your fines.', 'danger')
                return render_template('login.html')
            
            # Login successful
            session.permanent = True
            session['student_id'] = student.id
            session['student_name'] = student.name
            session['student_card'] = student.library_card_number
            session['student_department'] = student.department
            session['student_semester'] = student.semester
            
            student.last_login = get_utc_now()
            db.session.commit()
            
            log_audit(student.id, 'student', 'login', details='Successful login')
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student_dashboard'))
        
        # Neither admin nor student found
        log_audit(0, 'unknown', 'failed_login', details=f'Invalid credentials for: {username}')
        flash('Invalid username/library card or password', 'danger')
    
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('admin/login.html')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session.permanent = True
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            log_audit(admin.id, 'admin', 'login', details='Successful login')
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            log_audit(0, 'admin', 'failed_login', details=f'Invalid credentials for: {username}')
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        library_card = request.form.get('library_card', '').strip()
        password = request.form.get('password', '')
        
        if not library_card:
            flash('Library card number is required', 'danger')
            return render_template('student/login.html')
        
        student = Student.query.filter_by(library_card_number=library_card).first()
        
        if not student:
            flash('Invalid library card number', 'danger')
            log_audit(0, 'student', 'failed_login', details=f'Invalid card: {library_card}')
            return render_template('student/login.html')
        
        # Check password if student has one set
        if student.password_hash and not student.check_password(password):
            flash('Invalid password', 'danger')
            log_audit(student.id, 'student', 'failed_login', details='Invalid password')
            return render_template('student/login.html')
        
        if student.card_status != 'active':
            flash(f'Your library card is {student.card_status}. Please contact the library.', 'danger')
            return render_template('student/login.html')
        
        # Check if account is suspended due to fines
        if student.total_fines >= MAX_OVERDUE_FINES:
            flash(f'Your account is suspended due to outstanding fines (PKR {student.total_fines:.2f}). Please pay your fines.', 'danger')
            return render_template('student/login.html')
        
        session.permanent = True
        session['student_id'] = student.id
        session['student_name'] = student.name
        session['student_card'] = student.library_card_number
        session['student_department'] = student.department
        session['student_semester'] = student.semester
        
        student.last_login = get_utc_now()
        db.session.commit()
        
        log_audit(student.id, 'student', 'login', details=f'Successful login')
        flash(f'Welcome back, {student.name}!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('student/login.html')

@app.route('/student/logout')
def student_logout():
    student_id = session.get('student_id')
    if student_id:
        log_audit(student_id, 'student', 'logout', details='User logged out')
    session.pop('student_id', None)
    session.pop('student_name', None)
    session.pop('student_card', None)
    session.pop('student_department', None)
    session.pop('student_semester', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/student/dashboard')
@student_login_required
def student_dashboard():
    """Student dashboard with profile and requests"""
    student = Student.query.get_or_404(session['student_id'])
    
    # Get all rental requests (pending, approved, rejected)
    rental_requests = BookRentalRequest.query.filter_by(student_id=student.id).order_by(BookRentalRequest.request_date.desc()).all()
    
    # Get active loans
    active_loans = Loan.query.filter_by(student_id=student.id, is_returned=False).all()
    for loan in active_loans:
        loan.calculate_fine()
    
    # Count by status
    pending_count = BookRentalRequest.query.filter_by(student_id=student.id, status='pending').count()
    approved_count = BookRentalRequest.query.filter_by(student_id=student.id, status='approved').count()
    rejected_count = BookRentalRequest.query.filter_by(student_id=student.id, status='rejected').count()
    
    # Get active reservations
    active_reservations = BookReservation.query.filter_by(
        student_id=student.id, 
        status='active'
    ).filter(BookReservation.expiry_date > get_utc_now()).all()
    
    return render_template('student/dashboard.html',
                         student=student,
                         rental_requests=rental_requests,
                         active_loans=active_loans,
                         pending_count=pending_count,
                         approved_count=approved_count,
                         rejected_count=rejected_count,
                         active_reservations=active_reservations)

@app.route('/student/profile', methods=['GET', 'POST'])
@student_login_required
def student_profile():
    """Student profile management"""
    student = Student.query.get_or_404(session['student_id'])
    
    if request.method == 'POST':
        try:
            # Update profile information
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validate email
            if email and not validate_email(email):
                flash('Invalid email format', 'danger')
                return render_template('student/profile.html', student=student)
            
            # Validate phone
            if phone and not validate_phone(phone):
                flash('Invalid phone number format', 'danger')
                return render_template('student/profile.html', student=student)
            
            # Update basic info
            if phone:
                student.phone = phone
            if email and email != student.email:
                # Check if email already exists
                existing = Student.query.filter_by(email=email).first()
                if existing and existing.id != student.id:
                    flash('Email already in use', 'danger')
                    return render_template('student/profile.html', student=student)
                student.email = email
            
            # Update password if provided
            if new_password:
                if not current_password:
                    flash('Current password is required to set a new password', 'danger')
                    return render_template('student/profile.html', student=student)
                
                if student.password_hash and not student.check_password(current_password):
                    flash('Current password is incorrect', 'danger')
                    return render_template('student/profile.html', student=student)
                
                if new_password != confirm_password:
                    flash('New passwords do not match', 'danger')
                    return render_template('student/profile.html', student=student)
                
                if len(new_password) < 6:
                    flash('Password must be at least 6 characters', 'danger')
                    return render_template('student/profile.html', student=student)
                
                student.set_password(new_password)
                flash('Password updated successfully', 'success')
            
            db.session.commit()
            log_audit(student.id, 'student', 'profile_update', 'student', student.id, 'Profile updated')
            flash('Profile updated successfully', 'success')
            return redirect(url_for('student_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('student/profile.html', student=student)

@app.route('/admin/logout')
def admin_logout():
    admin_id = session.get('admin_id')
    if admin_id:
        log_audit(admin_id, 'admin', 'logout', details='Admin logged out')
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
    pending_requests = BookRentalRequest.query.filter_by(status='pending').count()
    active_reservations = BookReservation.query.filter_by(status='active').filter(
        BookReservation.expiry_date > get_utc_now()
    ).count()
    
    recent_loans = Loan.query.order_by(Loan.loan_date.desc()).limit(5).all()
    recent_requests = BookRentalRequest.query.order_by(BookRentalRequest.request_date.desc()).limit(5).all()
    
    # Top borrowed books
    top_books = db.session.query(
        Book, db.func.count(Loan.id).label('loan_count')
    ).join(Loan).group_by(Book.id).order_by(db.desc('loan_count')).limit(5).all()
    
    # Students with most loans
    top_students = db.session.query(
        Student, db.func.count(Loan.id).label('loan_count')
    ).join(Loan).group_by(Student.id).order_by(db.desc('loan_count')).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_books=total_books,
                         total_students=total_students,
                         active_loans=active_loans,
                         overdue_loans=overdue_loans,
                         total_fines=total_fines,
                         pending_requests=pending_requests,
                         active_reservations=active_reservations,
                         recent_loans=recent_loans,
                         recent_requests=recent_requests,
                         top_books=top_books,
                         top_students=top_students)

@app.route('/admin/reports')
@login_required
def admin_reports():
    """Admin reports and analytics"""
    # Date range filter
    days = request.args.get('days', 30, type=int)
    start_date = get_utc_now() - timedelta(days=days)
    
    # Loan statistics
    total_loans = Loan.query.filter(Loan.loan_date >= start_date).count()
    returned_loans = Loan.query.filter(
        Loan.loan_date >= start_date,
        Loan.is_returned == True
    ).count()
    overdue_loans = Loan.query.filter(
        Loan.loan_date >= start_date,
        Loan.is_returned == False,
        Loan.due_date < get_utc_now()
    ).count()
    
    # Fine statistics
    total_fines_collected = db.session.query(
        db.func.sum(FinePayment.amount)
    ).filter(FinePayment.payment_date >= start_date).scalar() or 0
    
    outstanding_fines = db.session.query(
        db.func.sum(Student.total_fines)
    ).scalar() or 0
    
    # Popular books
    popular_books = db.session.query(
        Book, db.func.count(Loan.id).label('loan_count')
    ).join(Loan).filter(Loan.loan_date >= start_date).group_by(
        Book.id
    ).order_by(db.desc('loan_count')).limit(10).all()
    
    # Popular genres
    popular_genres = db.session.query(
        Book.genre, db.func.count(Loan.id).label('loan_count')
    ).join(Loan).filter(
        Loan.loan_date >= start_date,
        Book.genre != None
    ).group_by(Book.genre).order_by(db.desc('loan_count')).limit(10).all()
    
    # Department statistics
    dept_stats = db.session.query(
        Student.department, 
        db.func.count(Loan.id).label('loan_count')
    ).join(Loan).filter(
        Loan.loan_date >= start_date,
        Student.department != None
    ).group_by(Student.department).order_by(db.desc('loan_count')).all()
    
    return render_template('admin/reports.html',
                         days=days,
                         total_loans=total_loans,
                         returned_loans=returned_loans,
                         overdue_loans=overdue_loans,
                         total_fines_collected=total_fines_collected,
                         outstanding_fines=outstanding_fines,
                         popular_books=popular_books,
                         popular_genres=popular_genres,
                         dept_stats=dept_stats)

@app.route('/admin/audit-logs')
@login_required
def admin_audit_logs():
    """View audit logs"""
    page = request.args.get('page', 1, type=int)
    user_type = request.args.get('user_type', '')
    action = request.args.get('action', '')
    
    query = AuditLog.query
    
    if user_type:
        query = query.filter_by(user_type=user_type)
    if action:
        query = query.filter(AuditLog.action.ilike(f'%{action}%'))
    
    logs = query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=50
    )
    
    return render_template('admin/audit_logs.html', logs=logs, 
                         user_type=user_type, action=action)

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
            title = request.form.get('title', '').strip()
            author = request.form.get('author', '').strip()
            isbn = request.form.get('isbn', '').strip()
            genre = request.form.get('genre', '').strip()
            year_published = request.form.get('year_published', type=int)
            publisher = request.form.get('publisher', '').strip()
            total_copies = request.form.get('total_copies', 1, type=int)
            description = request.form.get('description', '').strip()
            cover_image = request.form.get('cover_image', '').strip()
            
            # Validation
            if not title or not author:
                flash('Title and author are required', 'danger')
                return render_template('admin/add_book.html')
            
            if isbn and not validate_isbn(isbn):
                flash('Invalid ISBN format', 'danger')
                return render_template('admin/add_book.html')
            
            if isbn:
                existing = Book.query.filter_by(isbn=isbn).first()
                if existing:
                    flash('A book with this ISBN already exists', 'danger')
                    return render_template('admin/add_book.html')
            
            if total_copies < 1:
                flash('Total copies must be at least 1', 'danger')
                return render_template('admin/add_book.html')
            
            if year_published and (year_published < 1000 or year_published > datetime.now().year):
                flash('Invalid publication year', 'danger')
                return render_template('admin/add_book.html')
            
            book = Book(
                title=title,
                author=author,
                isbn=isbn if isbn else None,
                genre=genre if genre else None,
                year_published=year_published,
                publisher=publisher if publisher else None,
                total_copies=total_copies,
                available_copies=total_copies,
                description=description if description else None,
                cover_image=cover_image if cover_image else None
            )
            db.session.add(book)
            db.session.commit()
            
            log_audit(session['admin_id'], 'admin', 'book_add', 'book', book.id, 
                     f'Added book: {book.title}')
            
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
            title = request.form.get('title', '').strip()
            author = request.form.get('author', '').strip()
            isbn = request.form.get('isbn', '').strip()
            
            # Validation
            if not title or not author:
                flash('Title and author are required', 'danger')
                return render_template('admin/edit_book.html', book=book)
            
            if isbn and not validate_isbn(isbn):
                flash('Invalid ISBN format', 'danger')
                return render_template('admin/edit_book.html', book=book)
            
            if isbn and isbn != book.isbn:
                existing = Book.query.filter_by(isbn=isbn).first()
                if existing:
                    flash('A book with this ISBN already exists', 'danger')
                    return render_template('admin/edit_book.html', book=book)
            
            year_published = request.form.get('year_published', type=int)
            if year_published and (year_published < 1000 or year_published > datetime.now().year):
                flash('Invalid publication year', 'danger')
                return render_template('admin/edit_book.html', book=book)
            
            book.title = title
            book.author = author
            book.isbn = isbn if isbn else None
            book.genre = request.form.get('genre', '').strip() or None
            book.year_published = year_published
            book.publisher = request.form.get('publisher', '').strip() or None
            book.description = request.form.get('description', '').strip() or None
            book.cover_image = request.form.get('cover_image', '').strip() or None
            
            db.session.commit()
            
            log_audit(session['admin_id'], 'admin', 'book_edit', 'book', book.id, 
                     f'Edited book: {book.title}')
            
            flash('Book updated successfully!', 'success')
            return redirect(url_for('admin_books'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating book: {str(e)}', 'danger')
    
    return render_template('admin/edit_book.html', book=book)

@app.route('/admin/books/<int:id>/copies', methods=['POST'])
@login_required
def admin_update_copies(id):
    """Update book copy counts"""
    book = Book.query.get_or_404(id)
    
    try:
        action = request.form.get('action')
        quantity = int(request.form.get('quantity', 1))
        
        if quantity < 1:
            flash('Quantity must be at least 1', 'danger')
            return redirect(url_for('admin_books'))
        
        if action == 'add':
            book.total_copies += quantity
            book.available_copies += quantity
            log_audit(session['admin_id'], 'admin', 'book_copies_add', 'book', book.id, 
                     f'Added {quantity} copies')
            flash(f'Added {quantity} copies successfully', 'success')
        elif action == 'remove':
            if quantity > book.available_copies:
                flash(f'Cannot remove {quantity} copies. Only {book.available_copies} available.', 'danger')
                return redirect(url_for('admin_books'))
            book.total_copies -= quantity
            book.available_copies -= quantity
            log_audit(session['admin_id'], 'admin', 'book_copies_remove', 'book', book.id, 
                     f'Removed {quantity} copies')
            flash(f'Removed {quantity} copies successfully', 'success')
        else:
            flash('Invalid action', 'danger')
            return redirect(url_for('admin_books'))
        
        db.session.commit()
    except ValueError:
        flash('Invalid quantity', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating copies: {str(e)}', 'danger')
    
    return redirect(url_for('admin_books'))

@app.route('/admin/books/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_book(id):
    book = Book.query.get_or_404(id)
    
    # Check if book has active loans
    active_loans = Loan.query.filter_by(book_id=id, is_returned=False).count()
    if active_loans > 0:
        flash(f'Cannot delete book. It has {active_loans} active loan(s).', 'danger')
        return redirect(url_for('admin_books'))
    
    try:
        book_title = book.title
        db.session.delete(book)
        db.session.commit()
        
        log_audit(session['admin_id'], 'admin', 'book_delete', 'book', id, 
                 f'Deleted book: {book_title}')
        
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
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            roll_number = request.form.get('roll_number', '').strip()
            phone = request.form.get('phone', '').strip()
            department = request.form.get('department', '').strip()
            semester = request.form.get('semester', type=int)
            
            # Validation
            if not name or not email or not roll_number:
                flash('Name, email, and roll number are required', 'danger')
                return render_template('admin/add_student.html')
            
            if not validate_email(email):
                flash('Invalid email format', 'danger')
                return render_template('admin/add_student.html')
            
            if phone and not validate_phone(phone):
                flash('Invalid phone number format', 'danger')
                return render_template('admin/add_student.html')
            
            # Check for duplicates
            if Student.query.filter_by(email=email).first():
                flash('A student with this email already exists', 'danger')
                return render_template('admin/add_student.html')
            
            if Student.query.filter_by(roll_number=roll_number).first():
                flash('A student with this roll number already exists', 'danger')
                return render_template('admin/add_student.html')
            
            # Generate library card number
            card_number = f"HU{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            student = Student(
                name=name,
                email=email,
                roll_number=roll_number,
                phone=phone if phone else None,
                department=department if department else None,
                semester=semester,
                library_card_number=card_number
            )
            
            # Set default password as roll number
            student.set_password(roll_number)
            
            db.session.add(student)
            db.session.commit()
            
            log_audit(session['admin_id'], 'admin', 'student_add', 'student', student.id, 
                     f'Added student: {student.name}')
            
            flash(f'Student added successfully! Card Number: {card_number} | Default Password: {roll_number}', 'success')
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
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            
            # Validation
            if not name or not email:
                flash('Name and email are required', 'danger')
                return render_template('admin/edit_student.html', student=student)
            
            if not validate_email(email):
                flash('Invalid email format', 'danger')
                return render_template('admin/edit_student.html', student=student)
            
            if phone and not validate_phone(phone):
                flash('Invalid phone number format', 'danger')
                return render_template('admin/edit_student.html', student=student)
            
            # Check email uniqueness
            if email != student.email:
                existing = Student.query.filter_by(email=email).first()
                if existing:
                    flash('A student with this email already exists', 'danger')
                    return render_template('admin/edit_student.html', student=student)
            
            student.name = name
            student.email = email
            student.phone = phone if phone else None
            student.department = request.form.get('department', '').strip() or None
            student.semester = request.form.get('semester', type=int)
            student.card_status = request.form.get('card_status')
            
            db.session.commit()
            
            log_audit(session['admin_id'], 'admin', 'student_edit', 'student', student.id, 
                     f'Edited student: {student.name}')
            
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin_students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')
    
    return render_template('admin/edit_student.html', student=student)

@app.route('/admin/students/<int:id>/reset-password', methods=['POST'])
@login_required
def admin_reset_student_password(id):
    """Reset student password to their roll number"""
    student = Student.query.get_or_404(id)
    
    try:
        student.set_password(student.roll_number)
        db.session.commit()
        
        log_audit(session['admin_id'], 'admin', 'password_reset', 'student', student.id, 
                 f'Reset password for: {student.name}')
        
        flash(f'Password reset successfully. New password: {student.roll_number}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting password: {str(e)}', 'danger')
    
    return redirect(url_for('admin_student_detail', id=id))

@app.route('/admin/students/bulk-action', methods=['POST'])
@login_required
def admin_bulk_student_action():
    """Perform bulk actions on students"""
    try:
        action = request.form.get('action')
        student_ids = request.form.getlist('student_ids[]')
        
        if not student_ids:
            flash('No students selected', 'warning')
            return redirect(url_for('admin_students'))
        
        student_ids = [int(id) for id in student_ids]
        students = Student.query.filter(Student.id.in_(student_ids)).all()
        
        if action == 'activate':
            for student in students:
                student.card_status = 'active'
            db.session.commit()
            log_audit(session['admin_id'], 'admin', 'bulk_activate', 'student', None, 
                     f'Activated {len(students)} students')
            flash(f'Activated {len(students)} student(s)', 'success')
        elif action == 'suspend':
            for student in students:
                student.card_status = 'suspended'
            db.session.commit()
            log_audit(session['admin_id'], 'admin', 'bulk_suspend', 'student', None, 
                     f'Suspended {len(students)} students')
            flash(f'Suspended {len(students)} student(s)', 'success')
        elif action == 'delete':
            # Check for active loans
            active_loans = Loan.query.filter(
                Loan.student_id.in_(student_ids),
                Loan.is_returned == False
            ).count()
            
            if active_loans > 0:
                flash(f'Cannot delete students with active loans', 'danger')
                return redirect(url_for('admin_students'))
            
            for student in students:
                db.session.delete(student)
            db.session.commit()
            log_audit(session['admin_id'], 'admin', 'bulk_delete', 'student', None, 
                     f'Deleted {len(students)} students')
            flash(f'Deleted {len(students)} student(s)', 'success')
        else:
            flash('Invalid action', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error performing bulk action: {str(e)}', 'danger')
    
    return redirect(url_for('admin_students'))

@app.route('/admin/students/<int:id>')
@login_required
def admin_student_detail(id):
    student = Student.query.get_or_404(id)
    loans = Loan.query.filter_by(student_id=id).order_by(Loan.loan_date.desc()).all()
    rental_requests = BookRentalRequest.query.filter_by(student_id=id).order_by(BookRentalRequest.request_date.desc()).all()
    fine_payments = FinePayment.query.filter_by(student_id=id).order_by(FinePayment.payment_date.desc()).all()
    
    for loan in loans:
        loan.calculate_fine()
    
    return render_template('admin/student_detail.html', 
                         student=student, 
                         loans=loans, 
                         rental_requests=rental_requests,
                         fine_payments=fine_payments)

@app.route('/admin/students/<int:id>/pay-fine', methods=['POST'])
@login_required
def admin_pay_fine(id):
    """Admin records a fine payment"""
    student = Student.query.get_or_404(id)
    
    try:
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method', 'cash')
        notes = request.form.get('notes', '')
        
        if amount <= 0:
            flash('Payment amount must be greater than zero', 'danger')
            return redirect(url_for('admin_student_detail', id=id))
        
        if amount > student.total_fines:
            flash(f'Payment amount cannot exceed outstanding fines (PKR {student.total_fines:.2f})', 'danger')
            return redirect(url_for('admin_student_detail', id=id))
        
        # Create payment record
        payment = FinePayment(
            student_id=student.id,
            amount=amount,
            payment_method=payment_method,
            received_by=session['admin_id'],
            notes=notes
        )
        
        # Update student's total fines
        student.total_fines -= amount
        
        # Reactivate card if fines are below threshold
        if student.total_fines < MAX_OVERDUE_FINES and student.card_status == 'suspended':
            student.card_status = 'active'
            flash('Student card reactivated', 'success')
        
        db.session.add(payment)
        db.session.commit()
        
        log_audit(session['admin_id'], 'admin', 'fine_payment', 'student', student.id, 
                 f'Recorded payment of PKR {amount:.2f}')
        
        flash(f'Fine payment of PKR {amount:.2f} recorded successfully', 'success')
    except ValueError:
        flash('Invalid payment amount', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error recording payment: {str(e)}', 'danger')
    
    return redirect(url_for('admin_student_detail', id=id))

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
            
            if not student_id or not book_id:
                flash('Student and book are required', 'danger')
                return redirect(url_for('admin_create_loan'))
            
            student = Student.query.get_or_404(student_id)
            book = Book.query.get_or_404(book_id)
            
            # Validations
            if not student.can_borrow():
                if student.card_status != 'active':
                    flash('Student card is not active', 'danger')
                elif student.total_fines >= MAX_OVERDUE_FINES:
                    flash(f'Student has excessive fines (PKR {student.total_fines:.2f})', 'danger')
                else:
                    flash(f'Student has reached maximum active loans ({MAX_ACTIVE_LOANS})', 'danger')
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
            
            # Check for reservations and fulfill if exists
            reservation = BookReservation.query.filter_by(
                student_id=student_id,
                book_id=book_id,
                status='active'
            ).first()
            
            if reservation:
                reservation.status = 'fulfilled'
            
            db.session.add(loan)
            db.session.commit()
            
            log_audit(session['admin_id'], 'admin', 'loan_create', 'loan', loan.id, 
                     f'Created loan for {student.name} - {book.title}')
            
            flash('Loan created successfully!', 'success')
            return redirect(url_for('admin_loans'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating loan: {str(e)}', 'danger')
    
    students = Student.query.filter_by(card_status='active').order_by(Student.name).all()
    books = Book.query.filter(Book.available_copies > 0).order_by(Book.title).all()
    
    return render_template('admin/create_loan.html', students=students, books=books)

@app.route('/admin/loans/<int:id>/return', methods=['POST'])
@login_required
def admin_return_loan(id):
    loan = Loan.query.get_or_404(id)
    
    if loan.is_returned:
        flash('This loan has already been returned', 'warning')
        return redirect(url_for('admin_loans'))
    
    try:
        loan.is_returned = True
        loan.return_date = get_utc_now()
        loan.calculate_fine()
        
        loan.student.total_fines += loan.fine_amount
        loan.book.available_copies += 1
        
        # Check for pending reservations
        next_reservation = BookReservation.query.filter_by(
            book_id=loan.book_id,
            status='active'
        ).filter(BookReservation.expiry_date > get_utc_now()).order_by(
            BookReservation.reservation_date
        ).first()
        
        if next_reservation:
            next_reservation.notified = True
            flash(f'Book returned. Next reservation: {next_reservation.student.name}', 'info')
        
        db.session.commit()
        
        log_audit(session['admin_id'], 'admin', 'loan_return', 'loan', loan.id, 
                 f'Returned loan - Fine: PKR {loan.fine_amount:.2f}')
        
        if loan.fine_amount > 0:
            flash(f'Book returned successfully! Fine: PKR {loan.fine_amount:.2f}', 'warning')
        else:
            flash('Book returned successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error returning book: {str(e)}', 'danger')
    
    return redirect(url_for('admin_loans'))

@app.route('/admin/loans/<int:id>/extend', methods=['POST'])
@login_required
def admin_extend_loan(id):
    """Extend loan due date"""
    loan = Loan.query.get_or_404(id)
    
    if loan.is_returned:
        flash('Cannot extend a returned loan', 'warning')
        return redirect(url_for('admin_loans'))
    
    try:
        days = int(request.form.get('days', 7))
        if days < 1 or days > 30:
            flash('Extension must be between 1 and 30 days', 'danger')
            return redirect(url_for('admin_loans'))
        
        loan.due_date = loan.due_date + timedelta(days=days)
        db.session.commit()
        
        log_audit(session['admin_id'], 'admin', 'loan_extend', 'loan', loan.id, 
                 f'Extended loan by {days} days')
        
        flash(f'Loan extended by {days} days', 'success')
    except ValueError:
        flash('Invalid number of days', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error extending loan: {str(e)}', 'danger')
    
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
    
    # Check if user has active loan
    has_active_loan = False
    if 'student_id' in session:
        has_active_loan = Loan.query.filter_by(
            student_id=session['student_id'],
            book_id=id,
            is_returned=False
        ).first() is not None
    
    # Check if user has pending rental request
    has_pending_request = False
    if 'student_id' in session:
        has_pending_request = BookRentalRequest.query.filter_by(
            student_id=session['student_id'],
            book_id=id,
            status='pending'
        ).first() is not None
    
    return render_template('public/book_detail.html', 
                         book=book, 
                         reviews=reviews,
                         has_active_loan=has_active_loan,
                         has_pending_request=has_pending_request)

@app.route('/about')
def about():
    """About library page with map"""
    settings = LibrarySettings.query.first()
    if not settings:
        settings = LibrarySettings(
            library_name='HITEC University Taxila Library',
            library_address='HITEC University Taxila, Pakistan',
            library_phone='+92-51-9048-5000',
            library_email='library@hitecuni.edu.pk',
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

# ==================== STUDENT RENTAL REQUESTS ====================

@app.route('/student/rental/request/<int:book_id>', methods=['POST'])
@student_login_required
def student_rental_request(book_id):
    """Student requests to rent a book"""
    student = Student.query.get_or_404(session['student_id'])
    book = Book.query.get_or_404(book_id)
    
    # Check if student can borrow
    if not student.can_borrow():
        if student.card_status != 'active':
            flash('Your library card is not active', 'danger')
        elif student.total_fines >= MAX_OVERDUE_FINES:
            flash(f'You have excessive fines (PKR {student.total_fines:.2f}). Please pay your fines.', 'danger')
        else:
            flash(f'You have reached the maximum number of active loans ({MAX_ACTIVE_LOANS})', 'danger')
        return redirect(url_for('book_detail', id=book_id))
    
    # Check if already has an active loan
    existing_loan = Loan.query.filter_by(
        student_id=student.id,
        book_id=book_id,
        is_returned=False
    ).first()
    
    if existing_loan:
        flash('You already have an active loan for this book', 'danger')
        return redirect(url_for('book_detail', id=book_id))
    
    # Check if already has a pending request
    existing_request = BookRentalRequest.query.filter_by(
        student_id=student.id,
        book_id=book_id,
        status='pending'
    ).first()
    
    if existing_request:
        flash('You already have a pending request for this book', 'warning')
        return redirect(url_for('book_detail', id=book_id))
    
    # Create rental request
    request_obj = BookRentalRequest(
        student_id=student.id,
        book_id=book_id
    )
    db.session.add(request_obj)
    db.session.commit()
    
    log_audit(student.id, 'student', 'rental_request', 'book', book_id, 
             f'Requested: {book.title}')
    
    flash('Book rental request submitted successfully!', 'success')
    return redirect(url_for('book_detail', id=book_id))

@app.route('/student/book/<int:book_id>/reserve', methods=['POST'])
@student_login_required
def student_reserve_book(book_id):
    """Student reserves a book when it's unavailable"""
    student = Student.query.get_or_404(session['student_id'])
    book = Book.query.get_or_404(book_id)
    
    if book.available_copies > 0:
        flash('This book is available. Please request to rent it instead.', 'info')
        return redirect(url_for('book_detail', id=book_id))
    
    # Check for existing active reservation
    existing = BookReservation.query.filter_by(
        student_id=student.id,
        book_id=book_id,
        status='active'
    ).filter(BookReservation.expiry_date > get_utc_now()).first()
    
    if existing:
        flash('You already have an active reservation for this book', 'warning')
        return redirect(url_for('book_detail', id=book_id))
    
    try:
        reservation = BookReservation(
            student_id=student.id,
            book_id=book_id,
            expiry_date=get_utc_now() + timedelta(days=7)  # 7 days to claim
        )
        db.session.add(reservation)
        db.session.commit()
        
        log_audit(student.id, 'student', 'book_reserve', 'book', book_id, 
                 f'Reserved: {book.title}')
        
        flash('Book reserved successfully! You will be notified when it becomes available.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating reservation: {str(e)}', 'danger')
    
    return redirect(url_for('book_detail', id=book_id))

@app.route('/student/reservations')
@student_login_required
def student_reservations():
    """View student's book reservations"""
    student = Student.query.get_or_404(session['student_id'])
    
    # Get active reservations
    active_reservations = BookReservation.query.filter_by(
        student_id=student.id,
        status='active'
    ).filter(BookReservation.expiry_date > get_utc_now()).order_by(
        BookReservation.reservation_date
    ).all()
    
    # Get expired/fulfilled reservations
    past_reservations = BookReservation.query.filter_by(
        student_id=student.id
    ).filter(
        db.or_(
            BookReservation.status != 'active',
            BookReservation.expiry_date <= get_utc_now()
        )
    ).order_by(BookReservation.reservation_date.desc()).limit(10).all()
    
    return render_template('student/reservations.html', 
                         active_reservations=active_reservations,
                         past_reservations=past_reservations)

@app.route('/student/reservation/<int:id>/cancel', methods=['POST'])
@student_login_required
def student_cancel_reservation(id):
    """Cancel a book reservation"""
    reservation = BookReservation.query.get_or_404(id)
    
    if reservation.student_id != session['student_id']:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('student_reservations'))
    
    try:
        reservation.status = 'cancelled'
        db.session.commit()
        
        log_audit(session['student_id'], 'student', 'reservation_cancel', 'reservation', id, 
                 f'Cancelled reservation for: {reservation.book.title}')
        
        flash('Reservation cancelled successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling reservation: {str(e)}', 'danger')
    
    return redirect(url_for('student_reservations'))

@app.route('/student/rental/requests')
@student_login_required
def student_rental_requests():
    """View student's rental requests"""
    student = Student.query.get_or_404(session['student_id'])
    requests = BookRentalRequest.query.filter_by(student_id=student.id).order_by(BookRentalRequest.request_date.desc()).all()
    
    return render_template('student/rental_requests.html', requests=requests)

@app.route('/student/loans')
@student_login_required
def student_loans():
    """View student's active loans"""
    student = Student.query.get_or_404(session['student_id'])
    loans = Loan.query.filter_by(student_id=student.id, is_returned=False).order_by(Loan.loan_date.desc()).all()
    
    for loan in loans:
        loan.calculate_fine()
    
    return render_template('student/loans.html', loans=loans)

@app.route('/student/loan/<int:loan_id>/read')
def student_read_book(loan_id):
    """Read book online"""
    if 'student_id' not in session:
        flash('Please login to read the book', 'warning')
        return redirect(url_for('student_login'))
    
    loan = Loan.query.get_or_404(loan_id)
    
    # Check if loan belongs to current student
    if loan.student_id != session['student_id']:
        flash('You do not have permission to read this book', 'danger')
        return redirect(url_for('student_loans'))
    
    # Check if book has online version
    online_book = OnlineBook.query.filter_by(book_id=loan.book_id).first()
    
    if not online_book:
        flash('This book is not available for online reading', 'warning')
        return redirect(url_for('student_loans'))
    
    # Read book content
    book_content = ''
    try:
        with open(online_book.file_path, 'r', encoding='utf-8') as f:
            book_content = f.read()
    except Exception as e:
        book_content = 'Unable to load book content.'
    
    return render_template('student/read_book.html', loan=loan, online_book=online_book, book_content=book_content)

@app.route('/student/loan/<int:loan_id>/return', methods=['POST'])
def student_return_book(loan_id):
    """Student returns a book"""
    if 'student_id' not in session:
        flash('Please login to return a book', 'warning')
        return redirect(url_for('student_login'))
    
    loan = Loan.query.get_or_404(loan_id)
    
    # Check if loan belongs to current student
    if loan.student_id != session['student_id']:
        flash('You do not have permission to return this book', 'danger')
        return redirect(url_for('student_loans'))
    
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
    
    return redirect(url_for('student_loans'))

# ==================== ADMIN RENTAL REQUESTS ====================

@app.route('/admin/rental-requests')
@login_required
def admin_rental_requests():
    """Admin views all rental requests"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')
    
    query = BookRentalRequest.query
    
    if status == 'pending':
        query = query.filter_by(status='pending')
    elif status == 'approved':
        query = query.filter_by(status='approved')
    elif status == 'rejected':
        query = query.filter_by(status='rejected')
    
    requests = query.order_by(BookRentalRequest.request_date.desc()).paginate(page=page, per_page=ITEMS_PER_PAGE)
    
    return render_template('admin/rental_requests.html', requests=requests, status=status)

@app.route('/admin/rental-requests/<int:request_id>/approve', methods=['POST'])
@login_required
def admin_approve_request(request_id):
    """Admin approves a rental request"""
    rental_request = BookRentalRequest.query.get_or_404(request_id)
    
    if rental_request.status != 'pending':
        flash('This request has already been processed', 'warning')
        return redirect(url_for('admin_rental_requests'))
    
    book = Book.query.get_or_404(rental_request.book_id)
    student = Student.query.get_or_404(rental_request.student_id)
    
    # Check if student can borrow
    if not student.can_borrow():
        rental_request.status = 'rejected'
        if student.card_status != 'active':
            rental_request.notes = 'Student card is not active'
        elif student.total_fines >= MAX_OVERDUE_FINES:
            rental_request.notes = f'Student has excessive fines (PKR {student.total_fines:.2f})'
        else:
            rental_request.notes = f'Student has reached maximum active loans ({MAX_ACTIVE_LOANS})'
        db.session.commit()
        flash(rental_request.notes, 'danger')
        return redirect(url_for('admin_rental_requests'))
    
    # Check if book is available
    if book.available_copies <= 0:
        rental_request.status = 'rejected'
        rental_request.notes = 'Book is not available'
        db.session.commit()
        flash('Book is not available for loan', 'danger')
        return redirect(url_for('admin_rental_requests'))
    
    # Check if student already has an active loan for this book
    existing_loan = Loan.query.filter_by(
        student_id=student.id,
        book_id=book.id,
        is_returned=False
    ).first()
    
    if existing_loan:
        rental_request.status = 'rejected'
        rental_request.notes = 'Student already has an active loan for this book'
        db.session.commit()
        flash('Student already has an active loan for this book', 'danger')
        return redirect(url_for('admin_rental_requests'))
    
    try:
        # Create loan
        loan = Loan(
            student_id=student.id,
            book_id=book.id,
            loan_date=get_utc_now(),
            due_date=get_utc_now() + timedelta(days=LOAN_DURATION_DAYS)
        )
        
        book.available_copies -= 1
        
        # Update rental request
        rental_request.status = 'approved'
        rental_request.approved_by = session['admin_id']
        rental_request.approval_date = get_utc_now()
        rental_request.loan_start_date = get_utc_now()
        rental_request.loan_end_date = get_utc_now() + timedelta(days=LOAN_DURATION_DAYS)
        
        db.session.add(loan)
        db.session.commit()
        
        log_audit(session['admin_id'], 'admin', 'rental_approve', 'rental_request', request_id, 
                 f'Approved request for {student.name} - {book.title}')
        
        flash('Rental request approved and loan created!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving request: {str(e)}', 'danger')
    
    return redirect(url_for('admin_rental_requests'))

@app.route('/admin/rental-requests/<int:request_id>/reject', methods=['POST'])
@login_required
def admin_reject_request(request_id):
    """Admin rejects a rental request"""
    rental_request = BookRentalRequest.query.get_or_404(request_id)
    
    if rental_request.status != 'pending':
        flash('This request has already been processed', 'warning')
        return redirect(url_for('admin_rental_requests'))
    
    try:
        rental_request.status = 'rejected'
        rental_request.approved_by = session['admin_id']
        rental_request.approval_date = get_utc_now()
        rental_request.notes = request.form.get('notes', 'Request rejected')
        
        db.session.commit()
        
        log_audit(session['admin_id'], 'admin', 'rental_reject', 'rental_request', request_id, 
                 f'Rejected request - Reason: {rental_request.notes}')
        
        flash('Rental request rejected', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting request: {str(e)}', 'danger')
    
    return redirect(url_for('admin_rental_requests'))

# ==================== ADMIN ONLINE BOOKS ====================

@app.route('/admin/books/<int:book_id>/upload', methods=['GET', 'POST'])
@login_required
def admin_upload_book(book_id):
    """Admin uploads an online version of a book"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        if 'book_file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('admin_upload_book', book_id=book_id))
        
        file = request.files['book_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('admin_upload_book', book_id=book_id))
        
        # Validate file type
        allowed_extensions = {'pdf', 'epub', 'mobi'}
        if '.' in file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            if ext not in allowed_extensions:
                flash('Invalid file type. Allowed: PDF, EPUB, MOBI', 'danger')
                return redirect(url_for('admin_upload_book', book_id=book_id))
        else:
            flash('Invalid file name', 'danger')
            return redirect(url_for('admin_upload_book', book_id=book_id))
        
        # Save file
        filename = f"book_{book.id}_{file.filename}"
        file_path = os.path.join('static', 'books', filename)
        file.save(file_path)
        
        # Create online book record
        online_book = OnlineBook(
            book_id=book.id,
            file_path=file_path,
            file_type=ext,
            created_by=session['admin_id']
        )
        db.session.add(online_book)
        db.session.commit()
        
        flash('Book uploaded successfully!', 'success')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/upload_book.html', book=book)

@app.route('/admin/books/<int:book_id>/online')
@login_required
def admin_view_online_books(book_id):
    """Admin views uploaded online books for a book"""
    book = Book.query.get_or_404(book_id)
    online_books = OnlineBook.query.filter_by(book_id=book_id).all()
    
    return render_template('admin/online_books.html', book=book, online_books=online_books)

@app.route('/admin/books/<int:book_id>/online/<int:online_book_id>/delete', methods=['POST'])
@login_required
def admin_delete_online_book(book_id, online_book_id):
    """Admin deletes an online book"""
    online_book = OnlineBook.query.get_or_404(online_book_id)
    
    try:
        # Delete file
        if os.path.exists(online_book.file_path):
            os.remove(online_book.file_path)
        
        db.session.delete(online_book)
        db.session.commit()
        flash('Online book deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting online book: {str(e)}', 'danger')
    
    return redirect(url_for('admin_view_online_books', book_id=book_id))

# ==================== PUBLIC ONLINE BOOKS ====================

@app.route('/books/<int:book_id>/read')
def public_read_book(book_id):
    """Public page to read book online (requires active loan)"""
    book = Book.query.get_or_404(book_id)
    
    # Check if user has an active loan for this book
    if 'student_id' not in session:
        flash('Please login to read this book', 'warning')
        return redirect(url_for('book_detail', id=book_id))
    
    student = Student.query.get_or_404(session['student_id'])
    
    loan = Loan.query.filter_by(
        student_id=student.id,
        book_id=book_id,
        is_returned=False
    ).first()
    
    if not loan:
        flash('You need an active loan to read this book', 'danger')
        return redirect(url_for('book_detail', id=book_id))
    
    # Check if book has online version
    online_book = OnlineBook.query.filter_by(book_id=book_id).first()
    
    if not online_book:
        flash('This book is not available for online reading', 'warning')
        return redirect(url_for('book_detail', id=book_id))
    
    return render_template('public/read_book.html', book=book, online_book=online_book, loan=loan)

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
        admin = Admin(username='admin', email='admin@hitecuni.edu.pk')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    # Create library settings if not exists
    if not LibrarySettings.query.first():
        settings = LibrarySettings(
            library_name='HITEC University Taxila Library',
            library_address='HITEC University Taxila, Pakistan',
            library_phone='+92-51-9048-5000',
            library_email='library@hitecuni.edu.pk',
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
