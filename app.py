from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta, timezone
import csv
from io import StringIO
from math import ceil

app = Flask(__name__)
# Configure the SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'library.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'different_secret_key_here' 

db = SQLAlchemy(app)

ITEMS_PER_PAGE = 10

def get_utc_now():
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    year_published = db.Column(db.Integer)
    average_rating = db.Column(db.Float, default=0.0)
    cover_image = db.Column(db.String(500))  # New field for book cover URL
    reviews = db.relationship('Review', backref='book', lazy=True)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact = db.Column(db.String(15))
    member_since = db.Column(db.Date, default=datetime.utcnow)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    returned = db.Column(db.Boolean, default=False)
    late_fee = db.Column(db.Float, default=0.0)
    member = db.relationship('Member', backref='loans', lazy=True)
    book = db.relationship('Book', backref='loans', lazy=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    member = db.relationship('Member', backref='reviews', lazy=True)


@app.route('/books')
def list_books():
    search = request.args.get('search', '')
    genre = request.args.get('genre', '')
    year_from = request.args.get('year_from', '')
    year_to = request.args.get('year_to', '')
    min_rating = request.args.get('min_rating', '')
    available_only = request.args.get('available_only', '')
    page = request.args.get('page', 1, type=int)
    
    query = Book.query
    
    if search:
        query = query.filter(
            (Book.title.contains(search)) | 
            (Book.author.contains(search)) | 
            (Book.genre.contains(search))
        )
    
    if genre:
        query = query.filter_by(genre=genre)
    
    if year_from:
        query = query.filter(Book.year_published >= int(year_from))
    
    if year_to:
        query = query.filter(Book.year_published <= int(year_to))
    
    if min_rating:
        query = query.filter(Book.average_rating >= float(min_rating))
    
    if available_only:
        available_book_ids = [loan.book_id for loan in Loan.query.filter_by(returned=False).all()]
        query = query.filter(~Book.id.in_(available_book_ids))
    
    total_books = query.count()
    total_pages = ceil(total_books / ITEMS_PER_PAGE)
    books = query.offset((page - 1) * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE).all()
    
    # Check availability for each book
    book_availability = {}
    for book in books:
        active_loan = Loan.query.filter_by(book_id=book.id, returned=False).first()
        book_availability[book.id] = active_loan is None
    
    # Get all genres for filter dropdown
    genres = db.session.query(Book.genre).distinct().filter(Book.genre != None).all()
    genres = [g[0] for g in genres]
    
    return render_template('books.html', 
                         books=books, 
                         search=search, 
                         genre=genre,
                         year_from=year_from,
                         year_to=year_to,
                         min_rating=min_rating,
                         available_only=available_only,
                         book_availability=book_availability,
                         genres=genres,
                         page=page,
                         total_pages=total_pages)

@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        year_published = request.form['year_published']
        cover_image = request.form.get('cover_image', '')

        new_book = Book(title=title, author=author, genre=genre, year_published=year_published, cover_image=cover_image)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('list_books'))

    return render_template('add_book.html')

@app.route('/books/update/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.genre = request.form['genre']
        book.year_published = request.form['year_published']
        book.cover_image = request.form.get('cover_image', '')

        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('list_books'))

    return render_template('update_book.html', book=book)

@app.route('/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'danger')
    return redirect(url_for('list_books'))


@app.route('/books/<int:id>/reviews', methods=['GET', 'POST'])
def book_reviews(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')
        
        
        member = Member.query.get(member_id)
        if not member:
            flash('Invalid member ID!', 'danger')
            return redirect(url_for('book_reviews', id=id))
        
       
        existing_review = Review.query.filter_by(book_id=id, member_id=member_id).first()
        if existing_review:
            flash('You have already reviewed this book!', 'danger')
            return redirect(url_for('book_reviews', id=id))
        
        if not 1 <= rating <= 5:
            flash('Rating must be between 1 and 5!', 'danger')
            return redirect(url_for('book_reviews', id=id))
        
        new_review = Review(book_id=id, member_id=member_id, rating=rating, comment=comment)
        db.session.add(new_review)
        
        
        book_reviews = Review.query.filter_by(book_id=id).all()
        total_rating = sum([review.rating for review in book_reviews]) + rating
        book.average_rating = total_rating / (len(book_reviews) + 1)
        
        db.session.commit()
        flash('Review added successfully!', 'success')
        return redirect(url_for('book_reviews', id=id))
    
    reviews = Review.query.filter_by(book_id=id).order_by(Review.date_posted.desc()).all()
    members = Member.query.all()
    return render_template('book_reviews.html', book=book, reviews=reviews, members=members)

@app.route('/members')
def list_members():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'name')
    page = request.args.get('page', 1, type=int)
    
    query = Member.query
    
    if search:
        query = query.filter(
            (Member.name.contains(search)) | 
            (Member.email.contains(search))
        )
    
    if sort == 'recent':
        query = query.order_by(Member.member_since.desc())
    elif sort == 'active':
        # Sort by number of loans (most active first)
        query = query.outerjoin(Loan).group_by(Member.id).order_by(db.func.count(Loan.id).desc())
    else:
        query = query.order_by(Member.name)
    
    total_members = query.count()
    total_pages = ceil(total_members / ITEMS_PER_PAGE)
    members = query.offset((page - 1) * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE).all()
    
    return render_template('members.html', 
                         members=members, 
                         search=search,
                         sort=sort,
                         page=page,
                         total_pages=total_pages)

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']

        if not name or not email:
            flash('Name and Email are required!', 'danger')
            return redirect(url_for('add_member'))

        if '@' not in email or '.' not in email:
            flash('Invalid email format!', 'danger')
            return redirect(url_for('add_member'))

        existing_member = Member.query.filter_by(email=email).first()
        if existing_member:
            flash('A member with this email already exists!', 'danger')
            return redirect(url_for('add_member'))

        new_member = Member(name=name, email=email, contact=contact)
        db.session.add(new_member)
        db.session.commit()
        flash('Member added successfully!', 'success')
        return redirect(url_for('list_members'))

    return render_template('add_member.html')

@app.route('/members/update/<int:id>', methods=['GET', 'POST'])
def update_member(id):
    member = Member.query.get_or_404(id)
    if request.method == 'POST':
        member.name = request.form['name']
        member.email = request.form['email']
        member.contact = request.form['contact']

        db.session.commit()
        flash('Member updated successfully!', 'success')
        return redirect(url_for('list_members'))

    return render_template('update_member.html', member=member)

@app.route('/members/delete/<int:id>', methods=['POST'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted successfully!', 'danger')
    return redirect(url_for('list_members'))

@app.route('/loans')
def list_loans():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'recent')
    page = request.args.get('page', 1, type=int)
    
    loans_query = db.session.query(Loan, Member, Book).join(Member).join(Book).filter(Loan.returned == False)
    
    if search:
        loans_query = loans_query.filter(
            (Member.name.contains(search)) | 
            (Book.title.contains(search))
        )
    
    # Calculate overdue and due soon
    overdue_loans = []
    due_soon_loans = []
    now = get_utc_now()
    
    for loan, member, book in loans_query.all():
        if loan.return_date and loan.return_date < now.date():
            overdue_loans.append(loan.id)
            days_overdue = (now.date() - loan.return_date).days
            loan.late_fee = days_overdue * 1.0
        elif loan.return_date and (loan.return_date - now.date()).days <= 7:
            due_soon_loans.append(loan.id)
    
    db.session.commit()
    
    # Filter by status
    if status == 'overdue':
        loans_query = loans_query.filter(Loan.id.in_(overdue_loans))
    elif status == 'active':
        loans_query = loans_query.filter(~Loan.id.in_(overdue_loans))
    
    # Sort
    if sort == 'due_soon':
        loans_query = loans_query.order_by(Loan.return_date.asc())
    elif sort == 'overdue':
        loans_query = loans_query.order_by(Loan.return_date.asc())
    else:
        loans_query = loans_query.order_by(Loan.loan_date.desc())
    
    total_loans = loans_query.count()
    total_pages = ceil(total_loans / ITEMS_PER_PAGE)
    loans = loans_query.offset((page - 1) * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE).all()
    
    return render_template('loans.html', 
                         loans=loans, 
                         search=search,
                         status=status,
                         sort=sort,
                         overdue_loans=overdue_loans,
                         due_soon_loans=due_soon_loans,
                         overdue_count=len(overdue_loans),
                         due_soon_count=len(due_soon_loans),
                         page=page,
                         total_pages=total_pages,
                         now=now)

@app.route('/loans/add', methods=['GET', 'POST'])
def add_loan():
    members = Member.query.all()
    books = Book.query.filter(~Book.id.in_([loan.book_id for loan in Loan.query.filter_by(returned=False).all()])).all()

    if request.method == 'POST':
        member_id = request.form['member']
        book_id = request.form['book']
        loan_date = request.form['loan_date']
        return_date = request.form['return_date']

        if not loan_date or not return_date:
            flash('Loan Date and Return Date are required!', 'danger')
            return redirect(url_for('add_loan'))

        loan_date_obj = datetime.strptime(loan_date, '%Y-%m-%d')
        return_date_obj = datetime.strptime(return_date, '%Y-%m-%d')
        if return_date_obj <= loan_date_obj:
            flash('Return Date must be after Loan Date!', 'danger')
            return redirect(url_for('add_loan'))

        new_loan = Loan(member_id=member_id, book_id=book_id, loan_date=loan_date_obj, return_date=return_date_obj, returned=False)
        db.session.add(new_loan)
        db.session.commit()
        flash('Loan added successfully!', 'success')
        return redirect(url_for('list_loans'))

    return render_template('add_loan.html', members=members, books=books)

@app.route('/loans/delete/<int:id>', methods=['POST'])
def delete_loan(id):
    loan = Loan.query.get_or_404(id)
    loan.returned = True
    db.session.commit()
    flash('Book returned successfully!', 'success')
    return redirect(url_for('list_loans'))

@app.route('/')
def index():
    total_books = Book.query.count()
    total_members = Member.query.count()
    active_loans = Loan.query.filter_by(returned=False).count()
    returned_loans = Loan.query.filter_by(returned=True).count()
    total_reviews = Review.query.count()
    
    # Calculate overdue loans
    now = get_utc_now().date()
    overdue_loans = Loan.query.filter(
        (Loan.returned == False) & 
        (Loan.return_date < now)
    ).count()
    
    # Genre distribution
    genre_data = {}
    genres = db.session.query(Book.genre, db.func.count(Book.id)).group_by(Book.genre).all()
    for genre, count in genres:
        if genre:
            genre_data[genre] = count
    
    # Recent books (last 5)
    recent_books = Book.query.order_by(Book.id.desc()).limit(5).all()
    
    # Top rated books (last 5)
    top_rated_books = Book.query.filter(Book.average_rating > 0).order_by(Book.average_rating.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_books=total_books,
                         total_members=total_members,
                         active_loans=active_loans,
                         returned_loans=returned_loans,
                         total_reviews=total_reviews,
                         overdue_loans=overdue_loans,
                         genre_data=genre_data,
                         recent_books=recent_books,
                         top_rated_books=top_rated_books)

# Feature 1: Export to CSV
@app.route('/export/books')
def export_books():
    books = Book.query.all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Title', 'Author', 'Genre', 'Year Published', 'Average Rating'])
    for book in books:
        writer.writerow([book.id, book.title, book.author, book.genre, book.year_published, book.average_rating])
    
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=books.csv"}
    )

@app.route('/export/members')
def export_members():
    members = Member.query.all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Name', 'Email', 'Contact', 'Member Since'])
    for member in members:
        writer.writerow([member.id, member.name, member.email, member.contact, member.member_since])
    
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=members.csv"}
    )

@app.route('/export/loans')
def export_loans():
    loans = db.session.query(Loan, Member, Book).join(Member).join(Book).all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Loan ID', 'Member Name', 'Book Title', 'Loan Date', 'Return Date', 'Status', 'Late Fee'])
    for loan, member, book in loans:
        status = 'Returned' if loan.returned else 'Active'
        writer.writerow([loan.id, member.name, book.title, loan.loan_date, loan.return_date, status, loan.late_fee])
    
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=loans.csv"}
    )

# Feature 2: Popular Books
@app.route('/books/popular')
def popular_books():
    # Get books with most reviews and highest ratings
    books_with_stats = db.session.query(
        Book,
        db.func.count(Review.id).label('review_count'),
        db.func.avg(Review.rating).label('avg_rating')
    ).outerjoin(Review).group_by(Book.id).order_by(
        db.desc('review_count'),
        db.desc('avg_rating')
    ).limit(10).all()
    
    return render_template('popular_books.html', books_with_stats=books_with_stats)

# Feature 3: Member Activity Dashboard
@app.route('/members/<int:id>/activity')
def member_activity(id):
    member = Member.query.get_or_404(id)
    loans = db.session.query(Loan, Book).join(Book).filter(Loan.member_id == id).order_by(Loan.loan_date.desc()).all()
    reviews = db.session.query(Review, Book).join(Book).filter(Review.member_id == id).order_by(Review.date_posted.desc()).all()
    
    total_loans = len(loans)
    active_loans = sum(1 for loan, book in loans if not loan.returned)
    total_reviews = len(reviews)
    total_late_fees = sum(loan.late_fee for loan, book in loans)
    
    return render_template('member_activity.html', 
                         member=member, 
                         loans=loans, 
                         reviews=reviews,
                         total_loans=total_loans,
                         active_loans=active_loans,
                         total_reviews=total_reviews,
                         total_late_fees=total_late_fees)

# Feature 4: Book Statistics
@app.route('/books/<int:id>/stats')
def book_stats(id):
    book = Book.query.get_or_404(id)
    reviews = Review.query.filter_by(book_id=id).all()
    loans = Loan.query.filter_by(book_id=id).all()
    
    total_loans = len(loans)
    current_loan = Loan.query.filter_by(book_id=id, returned=False).first()
    is_available = current_loan is None
    
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_distribution[review.rating] += 1
    
    return render_template('book_stats.html', 
                         book=book, 
                         reviews=reviews,
                         total_loans=total_loans,
                         is_available=is_available,
                         rating_distribution=rating_distribution)

# Feature 5: Loan History (All loans including returned)
@app.route('/loans/history')
def loan_history():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    loans_query = db.session.query(Loan, Member, Book).join(Member).join(Book).order_by(Loan.loan_date.desc())
    
    if search:
        loans_query = loans_query.filter(
            (Member.name.contains(search)) | 
            (Book.title.contains(search))
        )
    
    now = get_utc_now()
    
    if status == 'returned':
        loans_query = loans_query.filter(Loan.returned == True)
    elif status == 'active':
        loans_query = loans_query.filter(Loan.returned == False)
    elif status == 'overdue':
        loans_query = loans_query.filter(
            (Loan.returned == False) & 
            (Loan.return_date < now.date())
        )
    
    loans = loans_query.all()
    
    return render_template('loan_history.html', loans=loans, search=search, status=status, now=now)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message='Page Not Found'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500, error_message='Internal Server Error'), 500

if __name__ == '__main__':
    app.run(debug=True)