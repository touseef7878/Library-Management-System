"""
Database seeding script for HiTec University Library
Populates database with:
- 300 students with dummy data
- 1000 books across 10 genres (100 per genre)
- Reviews from students on books
"""

from app import app, db, Student, Book, Review, Admin
from datetime import datetime, timedelta, timezone
import random
import string

# Book genres and their details
GENRES = {
    'Computer Science': {
        'authors': ['Donald Knuth', 'Andrew Tanenbaum', 'Bjarne Stroustrup', 'Robert Martin', 'Steve McConnell',
                   'Eric Evans', 'Martin Fowler', 'Gang of Four', 'Kent Beck', 'Joel Spolsky'],
        'publishers': ['Addison-Wesley', 'O\'Reilly Media', 'Pearson', 'MIT Press', 'Springer'],
        'cover_images': [
            'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=300&h=400&fit=crop',
        ]
    },
    'Mathematics': {
        'authors': ['Carl Friedrich Gauss', 'Leonhard Euler', 'Isaac Newton', 'Euclid', 'David Hilbert',
                   'Emmy Noether', 'Georg Cantor', 'Bernhard Riemann', 'Henri Poincaré', 'Kurt Gödel'],
        'publishers': ['Springer', 'Cambridge University Press', 'Oxford University Press', 'Dover Publications', 'Princeton'],
        'cover_images': [
            'https://images.unsplash.com/photo-1509228627152-72ae67a42c27?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
        ]
    },
    'History': {
        'authors': ['Yuval Noah Harari', 'Will Durant', 'Barbara Tuchman', 'Eric Hobsbawm', 'Christopher Clark',
                   'Margaret MacMillan', 'David McCullough', 'Simon Schama', 'Niall Ferguson', 'Mary Beard'],
        'publishers': ['Penguin Books', 'Simon & Schuster', 'Knopf', 'Hachette', 'HarperCollins'],
        'cover_images': [
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
        ]
    },
    'Physics': {
        'authors': ['Albert Einstein', 'Stephen Hawking', 'Richard Feynman', 'Carl Sagan', 'Brian Greene',
                   'Neil deGrasse Tyson', 'Lisa Randall', 'Sean Carroll', 'Michio Kaku', 'Alan Lightman'],
        'publishers': ['Basic Books', 'W.W. Norton', 'Bantam', 'Doubleday', 'Penguin'],
        'cover_images': [
            'https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
        ]
    },
    'Economics': {
        'authors': ['Adam Smith', 'John Maynard Keynes', 'Milton Friedman', 'Thomas Piketty', 'Paul Krugman',
                   'Joseph Stiglitz', 'Daron Acemoglu', 'Daniel Kahneman', 'Richard Thaler', 'Nassim Taleb'],
        'publishers': ['Penguin Economics', 'Oxford University Press', 'Harvard Business Review', 'Wiley', 'Routledge'],
        'cover_images': [
            'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
        ]
    },
    'Engineering': {
        'authors': ['Gustave Eiffel', 'Nikola Tesla', 'George Stephenson', 'Isambard Brunel', 'Thomas Edison',
                   'Henry Ford', 'Wright Brothers', 'Elias Howe', 'Alexander Graham Bell', 'John Roebling'],
        'publishers': ['McGraw-Hill', 'Elsevier', 'Springer', 'CRC Press', 'IEEE Press'],
        'cover_images': [
            'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
        ]
    },
    'Electrical Engineering': {
        'authors': ['James Clerk Maxwell', 'Michael Faraday', 'Georg Ohm', 'Alessandro Volta', 'Charles Coulomb',
                   'Oliver Heaviside', 'Guglielmo Marconi', 'John Ambrose Fleming', 'Lee de Forest', 'Reginald Fessenden'],
        'publishers': ['IEEE Press', 'Springer', 'Elsevier', 'McGraw-Hill', 'Wiley'],
        'cover_images': [
            'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
        ]
    },
    'Mechanical Engineering': {
        'authors': ['James Watt', 'George Stephenson', 'Rudolf Diesel', 'Charles Babbage', 'Joseph Bramah',
                   'John Smeaton', 'Thomas Newcomen', 'James Hargreaves', 'Edmund Cartwright', 'Henry Maudslay'],
        'publishers': ['McGraw-Hill', 'Elsevier', 'Springer', 'CRC Press', 'ASME Press'],
        'cover_images': [
            'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
        ]
    },
    'Civil Engineering': {
        'authors': ['Gustave Eiffel', 'Isambard Brunel', 'John Roebling', 'Nikola Tesla', 'Joseph Bazalgette',
                   'Thomas Telford', 'John Smeaton', 'Marc Brunel', 'Robert Stephenson', 'Benjamin Baker'],
        'publishers': ['Springer', 'Elsevier', 'CRC Press', 'McGraw-Hill', 'ASCE Press'],
        'cover_images': [
            'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
        ]
    },
    'Software Engineering': {
        'authors': ['Fred Brooks', 'Barry Boehm', 'Grady Booch', 'Ivar Jacobson', 'James Rumbaugh',
                   'Kent Beck', 'Martin Fowler', 'Robert Martin', 'Steve McConnell', 'Andrew Hunt'],
        'publishers': ['Addison-Wesley', 'Pearson', 'O\'Reilly Media', 'Pragmatic Bookshelf', 'Apress'],
        'cover_images': [
            'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
            'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
        ]
    }
}

# Student departments
DEPARTMENTS = ['Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering',
               'Software Engineering', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Business Administration']

# Review comments
REVIEW_COMMENTS = [
    'Excellent book, highly recommended!',
    'Very informative and well-written.',
    'Great resource for learning.',
    'Comprehensive coverage of the topic.',
    'Easy to understand with good examples.',
    'A must-read for anyone interested in this field.',
    'Well-organized and clearly explained.',
    'Provides deep insights into the subject.',
    'Perfect for beginners and experts alike.',
    'Outstanding work by the author.',
    'Helped me understand complex concepts.',
    'Highly valuable for my studies.',
    'Excellent reference material.',
    'Engaging and informative.',
    'Thoroughly enjoyed reading this.',
    'Great addition to any library.',
    'Practical and theoretical knowledge combined.',
    'Highly detailed and accurate.',
    'Recommended for all students.',
    'Exceptional quality and content.',
]

def generate_isbn():
    """Generate a random ISBN"""
    return ''.join(random.choices(string.digits, k=13))

def generate_roll_number():
    """Generate a random roll number"""
    return f"HU{random.randint(10000, 99999)}"

def generate_library_card():
    """Generate a library card number"""
    return f"LIB{random.randint(100000, 999999)}"

def seed_admin():
    """Create admin user"""
    print("Creating admin user...")
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(
            username='admin',
            email='admin@hitec.edu.pk'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin created: admin / admin123")
    else:
        print("✓ Admin already exists")

def seed_students():
    """Create 300 students"""
    print("\nSeeding 300 students...")
    existing_count = Student.query.count()
    
    if existing_count >= 300:
        print(f"✓ Students already exist ({existing_count})")
        return
    
    students_to_add = 300 - existing_count
    first_names = ['Ahmed', 'Ali', 'Hassan', 'Muhammad', 'Fatima', 'Aisha', 'Zainab', 'Hana', 'Omar', 'Sara',
                   'Khalid', 'Layla', 'Noor', 'Rayan', 'Dina', 'Karim', 'Leila', 'Tariq', 'Yasmin', 'Amira']
    last_names = ['Khan', 'Ahmed', 'Hassan', 'Ali', 'Ibrahim', 'Abdullah', 'Rahman', 'Malik', 'Hussain', 'Iqbal',
                  'Siddiqui', 'Mirza', 'Baig', 'Qureshi', 'Shaikh', 'Rizvi', 'Naqvi', 'Haider', 'Raza', 'Farooq']
    
    for i in range(students_to_add):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        
        student = Student(
            name=name,
            email=f"student{existing_count + i + 1}@hitec.edu.pk",
            roll_number=generate_roll_number(),
            phone=f"+92-{random.randint(300, 345)}-{random.randint(1000000, 9999999)}",
            department=random.choice(DEPARTMENTS),
            semester=random.randint(1, 8),
            library_card_number=generate_library_card(),
            card_status='active'
        )
        db.session.add(student)
        
        if (i + 1) % 50 == 0:
            db.session.commit()
            print(f"  Added {i + 1}/{students_to_add} students")
    
    db.session.commit()
    print(f"✓ {students_to_add} students created")

def seed_books():
    """Create 1000 books across 10 genres"""
    print("\nSeeding 1000 books...")
    existing_count = Book.query.count()
    
    if existing_count >= 1000:
        print(f"✓ Books already exist ({existing_count})")
        return
    
    books_to_add = 1000 - existing_count
    books_per_genre = books_to_add // len(GENRES)
    
    book_counter = 0
    for genre_name, genre_data in GENRES.items():
        print(f"  Adding {books_per_genre} books for {genre_name}...")
        
        for i in range(books_per_genre):
            title = f"{genre_name} Book {existing_count + book_counter + i + 1}"
            author = random.choice(genre_data['authors'])
            publisher = random.choice(genre_data['publishers'])
            cover_image = random.choice(genre_data['cover_images'])
            
            book = Book(
                title=title,
                author=author,
                isbn=generate_isbn(),
                genre=genre_name,
                year_published=random.randint(2000, 2024),
                publisher=publisher,
                total_copies=random.randint(2, 10),
                available_copies=random.randint(1, 10),
                cover_image=cover_image,
                description=f"A comprehensive guide to {genre_name}. This book covers essential concepts and practical applications.",
                average_rating=0.0
            )
            db.session.add(book)
            book_counter += 1
            
            if book_counter % 100 == 0:
                db.session.commit()
                print(f"    Added {book_counter}/{books_to_add} books")
    
    db.session.commit()
    print(f"✓ {books_to_add} books created")

def seed_reviews():
    """Add reviews from students on books"""
    print("\nSeeding reviews...")
    existing_reviews = Review.query.count()
    
    if existing_reviews > 0:
        print(f"✓ Reviews already exist ({existing_reviews})")
        return
    
    students = Student.query.all()
    books = Book.query.all()
    
    if not students or not books:
        print("✗ No students or books found")
        return
    
    reviews_added = 0
    # Each student reviews 2-5 random books
    for student in students:
        num_reviews = random.randint(2, 5)
        reviewed_books = random.sample(books, min(num_reviews, len(books)))
        
        for book in reviewed_books:
            # Check if review already exists
            existing = Review.query.filter_by(
                book_id=book.id,
                student_id=student.id
            ).first()
            
            if not existing:
                review = Review(
                    book_id=book.id,
                    student_id=student.id,
                    rating=random.randint(3, 5),
                    comment=random.choice(REVIEW_COMMENTS),
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))
                )
                db.session.add(review)
                reviews_added += 1
        
        if reviews_added % 100 == 0:
            db.session.commit()
            print(f"  Added {reviews_added} reviews")
    
    db.session.commit()
    
    # Update book average ratings
    print("  Updating book ratings...")
    books = Book.query.all()
    for book in books:
        reviews = Review.query.filter_by(book_id=book.id).all()
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            book.average_rating = round(avg_rating, 1)
    
    db.session.commit()
    print(f"✓ {reviews_added} reviews created and ratings updated")

def main():
    """Run all seeding functions"""
    with app.app_context():
        print("=" * 50)
        print("HiTec University Library - Database Seeding")
        print("=" * 50)
        
        try:
            seed_admin()
            seed_students()
            seed_books()
            seed_reviews()
            
            print("\n" + "=" * 50)
            print("✓ Seeding completed successfully!")
            print("=" * 50)
            
            # Print statistics
            print("\nDatabase Statistics:")
            print(f"  Admins: {Admin.query.count()}")
            print(f"  Students: {Student.query.count()}")
            print(f"  Books: {Book.query.count()}")
            print(f"  Reviews: {Review.query.count()}")
            
        except Exception as e:
            print(f"\n✗ Error during seeding: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()
