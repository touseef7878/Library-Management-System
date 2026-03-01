from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
import csv
from io import StringIO

app = Flask(__name__)
# Configure the SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'library.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'different_secret_key_here' 

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    year_published = db.Column(db.Integer)
    average_rating = db.Column(db.Float, default=0.0)  # New field
    reviews = db.relationship('Review', backref='book', lazy=True)  # New relationship

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
    if search:
        books = Book.query.filter(
            (Book.title.contains(search)) | 
            (Book.author.contains(search)) | 
            (Book.genre.contains(search))
        ).all()
    else:
        books = Book.query.all()
    
    # Check availability for each book
    book_availability = {}
    for book in books:
        active_loan = Loan.query.filter_by(book_id=book.id, returned=False).first()
        book_availability[book.id] = active_loan is None
    
    return render_template('books.html', books=books, search=search, book_availability=book_availability)

@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        year_published = request.form['year_published']

        new_book = Book(title=title, author=author, genre=genre, year_published=year_published)
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
    members = Member.query.all()
    return render_template('members.html', members=members)

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
    loans = db.session.query(Loan, Member, Book).join(Member).join(Book).filter(Loan.returned == False).all()
    overdue_loans = []
    for loan, member, book in loans:
        if loan.return_date and loan.return_date < datetime.utcnow().date():
            overdue_loans.append(loan.id)
            # Calculate late fee: $1 per day
            days_overdue = (datetime.utcnow().date() - loan.return_date).days
            loan.late_fee = days_overdue * 1.0
    db.session.commit()
    return render_template('loans.html', loans=loans, overdue_loans=overdue_loans)

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
    total_reviews = Review.query.count()
    return render_template('index.html', 
                         total_books=total_books,
                         total_members=total_members,
                         active_loans=active_loans,
                         total_reviews=total_reviews)

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
    loans = db.session.query(Loan, Member, Book).join(Member).join(Book).order_by(Loan.loan_date.desc()).all()
    return render_template('loan_history.html', loans=loans)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(debug=True)