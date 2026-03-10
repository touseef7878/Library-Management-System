"""
Reset and Seed Database Script
Cleans the database and populates it with fresh data:
- 1 Admin account
- 300 Students with proper roll numbers (YY-DEPT-NNN)
- 50 Real books from Open Library API with readable links
- Reviews from students
"""

from app import app, db, Admin, Student, Book, Review, BookRentalRequest, OnlineBook
from datetime import datetime, timedelta, timezone
import random
import string
import requests
import time
import os

def get_utc_now():
    """Get current UTC datetime (timezone-aware)"""
    return datetime.now(timezone.utc).replace(tzinfo=None)

# Department codes
DEPARTMENTS = {
    'Computer Science': 'CS',
    'Electrical Engineering': 'EE',
    'Mechanical Engineering': 'ME',
    'Civil Engineering': 'CE',
    'Software Engineering': 'SE',
    'Mathematics': 'MT',
    'Physics': 'PH',
    'Chemistry': 'CH',
    'Biology': 'BL',
    'Business Administration': 'BA'
}

# Real book titles by genre (50 per genre = 50 total)
BOOK_TITLES = {
    'Computer Science': [
        'The Art of Computer Programming', 'Introduction to Algorithms', 'Design Patterns', 'Clean Code', 'Code Complete',
        'The Pragmatic Programmer', 'Refactoring', 'The C Programming Language', 'Algorithms Unlocked', 'Cracking the Coding Interview',
        'System Design Interview', 'Database Design Manual', 'Artificial Intelligence', 'Machine Learning Basics', 'Deep Learning',
        'Cloud Computing Essentials', 'Microservices Architecture', 'DevOps Handbook', 'Docker in Action', 'Kubernetes in Action',
        'Python Cookbook', 'JavaScript: The Good Parts', 'React in Action', 'Vue.js in Action', 'Angular in Action',
        'TypeScript Handbook', 'GraphQL in Action', 'REST API Design Rulebook', 'Web Performance in Action', 'Designing Data-Intensive Applications',
        'Go Programming Language', 'Rust Programming Language', 'Node.js Design Patterns', 'Express.js Guide', 'You Don\'t Know JS',
        'Eloquent JavaScript', 'Big Data Analytics', 'Data Science Handbook', 'Natural Language Processing', 'Computer Vision Fundamentals',
        'Neural Networks and Deep Learning', 'Site Reliability Engineering', 'The Phoenix Project', 'Continuous Delivery', 'Infrastructure as Code',
        'Software Architecture Patterns', 'Domain-Driven Design', 'Test-Driven Development', 'Agile Software Development', 'Scrum Guide'
    ],
    'Mathematics': [
        'Calculus', 'Linear Algebra Done Right', 'Abstract Algebra', 'Real Analysis', 'Complex Analysis',
        'Functional Analysis', 'Topology', 'Differential Geometry', 'Number Theory', 'Combinatorics',
        'Graph Theory', 'Discrete Mathematics', 'Probability and Statistics', 'Mathematical Statistics', 'Stochastic Processes',
        'Numerical Analysis', 'Partial Differential Equations', 'Ordinary Differential Equations', 'Mathematical Methods', 'Applied Mathematics',
        'Optimization Theory', 'Game Theory', 'Mathematical Logic', 'Set Theory', 'Category Theory',
        'Algebraic Topology', 'Differential Topology', 'Riemannian Geometry', 'Algebraic Geometry', 'Commutative Algebra',
        'Representation Theory', 'Lie Groups and Lie Algebras', 'Harmonic Analysis', 'Fourier Analysis', 'Measure Theory',
        'Integration Theory', 'Functional Equations', 'Inequalities', 'Convex Analysis', 'Variational Methods',
        'Calculus of Variations', 'Mathematical Physics', 'Quantum Mechanics Mathematics', 'General Relativity Mathematics', 'Tensor Analysis',
        'Vector Calculus', 'Multivariable Calculus', 'Advanced Calculus', 'Mathematical Modeling', 'Computational Mathematics'
    ],
    'Physics': [
        'A Brief History of Time', 'The Universe in a Nutshell', 'Cosmos', 'Astrophysics for People in a Hurry', 'The Elegant Universe',
        'Parallel Worlds', 'The Fabric of the Cosmos', 'Something Deeply Hidden', 'Quantum Mechanics: The Theoretical Minimum', 'Classical Mechanics',
        'Thermodynamics', 'Electromagnetism', 'Optics', 'Waves and Oscillations', 'Fluid Mechanics',
        'Heat Transfer', 'Nuclear Physics', 'Particle Physics', 'Quantum Field Theory', 'General Relativity',
        'Special Relativity', 'Black Holes and Time Warps', 'The First Three Minutes', 'The Big Bang', 'Dark Matter and Dark Energy',
        'Gravitational Waves', 'String Theory', 'Quantum Gravity', 'Cosmology', 'Stellar Physics',
        'Planetary Science', 'Atmospheric Physics', 'Plasma Physics', 'Condensed Matter Physics', 'Solid State Physics',
        'Superconductivity', 'Superfluidity', 'Quantum Computing', 'Quantum Information', 'Quantum Entanglement',
        'Statistical Mechanics', 'Kinetic Theory', 'Molecular Physics', 'Atomic Physics', 'Laser Physics',
        'Photonics', 'Semiconductor Physics', 'Nanophysics', 'Biophysics', 'Medical Physics'
    ],
    'Engineering': [
        'Engineering Mechanics', 'Strength of Materials', 'Theory of Structures', 'Structural Analysis', 'Reinforced Concrete Design',
        'Steel Structures', 'Foundation Engineering', 'Soil Mechanics', 'Geotechnical Engineering', 'Water Resources Engineering',
        'Hydraulics', 'Fluid Mechanics', 'Thermodynamics', 'Heat Transfer', 'Mass Transfer',
        'Chemical Engineering Principles', 'Process Engineering', 'Unit Operations', 'Reaction Engineering', 'Biomedical Engineering',
        'Biomechanics', 'Medical Device Design', 'Environmental Engineering', 'Air Pollution Control', 'Water Treatment',
        'Waste Management', 'Renewable Energy', 'Solar Energy', 'Wind Energy', 'Hydroelectric Power',
        'Geothermal Energy', 'Biomass Energy', 'Energy Efficiency', 'Smart Grid Technology', 'Power Systems',
        'Electrical Machines', 'Power Electronics', 'Control Systems', 'Automation', 'Robotics',
        'Manufacturing Engineering', 'Production Management', 'Quality Engineering', 'Industrial Safety', 'Project Management',
        'Engineering Economics', 'Engineering Ethics', 'Sustainable Engineering', 'Green Engineering', 'Innovation Engineering'
    ],
    'History': [
        'Sapiens', 'Homo Deus', 'The Story of Civilization', 'A Brief History of Time', 'The Rise and Fall of the Third Reich',
        'The Cold War', 'World War II History', 'The American Civil War', 'The French Revolution', 'The Russian Revolution',
        'The Ottoman Empire', 'The British Empire', 'The Roman Empire', 'Ancient Egypt', 'Medieval History',
        'Renaissance History', 'Age of Enlightenment', 'Industrial Revolution', 'The Great Depression', 'The Vietnam War',
        'The Korean War', 'Islamic History', 'History of Science', 'History of Technology', 'History of Medicine',
        'History of Art', 'History of Music', 'History of Literature', 'History of Philosophy', 'History of Religion',
        'History of Economics', 'History of Politics', 'History of Law', 'History of Education', 'History of Sports',
        'History of Food', 'History of Fashion', 'History of Architecture', 'History of Transportation', 'History of Communication',
        'History of Exploration', 'History of Trade', 'History of Warfare', 'History of Diplomacy', 'Ancient Greece',
        'Ancient Rome', 'Byzantine Empire', 'Medieval Europe', 'Colonial America', 'Modern Europe'
    ]
}

# Authors by genre
AUTHORS = {
    'Computer Science': ['Donald Knuth', 'Thomas Cormen', 'Robert Martin', 'Steve McConnell', 'Martin Fowler'],
    'Mathematics': ['Carl Gauss', 'Leonhard Euler', 'Isaac Newton', 'Euclid', 'David Hilbert'],
    'Physics': ['Albert Einstein', 'Stephen Hawking', 'Richard Feynman', 'Carl Sagan', 'Brian Greene'],
    'Engineering': ['Gustave Eiffel', 'Nikola Tesla', 'George Stephenson', 'Thomas Edison', 'Henry Ford'],
    'History': ['Yuval Harari', 'Will Durant', 'Barbara Tuchman', 'Eric Hobsbawm', 'Christopher Clark']
}

PUBLISHERS = ['Addison-Wesley', 'O\'Reilly', 'Pearson', 'MIT Press', 'Springer', 'Cambridge', 'Oxford', 'Dover', 'Princeton', 'Penguin', 'McGraw-Hill', 'Elsevier', 'Wiley', 'IEEE Press']

# Cover images with WebP format - using reliable Unsplash URLs
COVER_IMAGES = [
    'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=300&h=400&fit=crop&fm=webp&q=80',
    'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop&fm=webp&q=80',
    'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop&fm=webp&q=80',
    'https://images.unsplash.com/photo-1509228627152-72ae67a42c27?w=300&h=400&fit=crop&fm=webp&q=80',
    'https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=300&h=400&fit=crop&fm=webp&q=80',
    'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=300&h=400&fit=crop&fm=webp&q=80',
    'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=300&h=400&fit=crop&fm=webp&q=80',
    'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300&h=400&fit=crop&fm=webp&q=80',
]

# Genre-specific covers for better visual representation
GENRE_COVERS = {
    'Computer Science': [
        'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop&fm=webp&q=80',
    ],
    'Mathematics': [
        'https://images.unsplash.com/photo-1509228627152-72ae67a42c27?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=300&h=400&fit=crop&fm=webp&q=80',
    ],
    'Physics': [
        'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=300&h=400&fit=crop&fm=webp&q=80',
    ],
    'Engineering': [
        'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1509228627152-72ae67a42c27?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=300&h=400&fit=crop&fm=webp&q=80',
    ],
    'History': [
        'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300&h=400&fit=crop&fm=webp&q=80',
        'https://images.unsplash.com/photo-1495446815901-a7297e3ffe02?w=300&h=400&fit=crop&fm=webp&q=80',
    ]
}

REVIEW_COMMENTS = [
    'Excellent book, highly recommended!', 'Very informative and well-written.', 'Great resource for learning.',
    'Comprehensive coverage of the topic.', 'Easy to understand with good examples.', 'A must-read for this field.',
    'Well-organized and clearly explained.', 'Provides deep insights.', 'Perfect for beginners and experts.',
    'Outstanding work by the author.', 'Helped me understand complex concepts.', 'Highly valuable for studies.',
    'Excellent reference material.', 'Engaging and informative.', 'Thoroughly enjoyed reading this.',
    'Great addition to any library.', 'Practical and theoretical knowledge.', 'Highly detailed and accurate.',
    'Recommended for all students.', 'Exceptional quality and content.'
]

def generate_isbn():
    return ''.join(random.choices(string.digits, k=13))

def generate_roll_number(dept_code, batch_year, used_rolls):
    while True:
        roll_num = random.randint(1, 999)
        new_roll = f"{batch_year}-{dept_code}-{roll_num:03d}"
        if new_roll not in used_rolls:
            used_rolls.add(new_roll)
            return new_roll

def generate_library_card(used_cards):
    while True:
        card_num = random.randint(100000, 999999)
        card = f"LIB{card_num}"
        if card not in used_cards:
            used_cards.add(card)
            return card

def fetch_books_from_openlibrary(genre, count=10):
    """Fetch real books from Open Library API"""
    books = []
    subjects = {
        'Computer Science': ['computer science', 'programming', 'algorithms'],
        'Mathematics': ['mathematics', 'algebra', 'calculus'],
        'Physics': ['physics', 'quantum mechanics', 'relativity'],
        'Engineering': ['engineering', 'mechanical engineering', 'electrical engineering'],
        'History': ['history', 'world history', 'modern history']
    }
    
    subject_list = subjects.get(genre, ['books'])
    
    for subject in subject_list:
        if len(books) >= count:
            break
            
        try:
            url = f"https://openlibrary.org/search.json?q={subject}&limit=50"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get('docs', [])
                
                for doc in docs:
                    if len(books) >= count:
                        break
                    
                    # Check for required fields
                    if 'title' not in doc or 'author_name' not in doc or 'cover_i' not in doc:
                        continue
                    
                    title = doc.get('title', '')[:200]
                    authors = doc.get('author_name', [])
                    author = authors[0] if authors else 'Unknown'
                    author = author[:150]
                    
                    cover_id = doc.get('cover_i')
                    # Use Open Library cover API - they serve WebP by default for modern browsers
                    cover_image = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                    
                    year = doc.get('first_publish_year', random.randint(2000, 2024))
                    
                    # Get ISBN if available
                    isbn = doc.get('isbn', [generate_isbn()])[0] if doc.get('isbn') else generate_isbn()
                    
                    books.append({
                        'title': title,
                        'author': author,
                        'isbn': isbn,
                        'year': year,
                        'cover': cover_image,
                        'publisher': 'Open Library'
                    })
                    
        except Exception as e:
            continue
    
    return books[:count]

print("=" * 60)
print("DATABASE RESET AND SEED")
print("=" * 60)

with app.app_context():
    try:
        # Drop all tables
        print("\n1. Dropping all tables...")
        db.drop_all()
        print("   ✓ All tables dropped")
        
        # Create all tables
        print("\n2. Creating all tables...")
        db.create_all()
        print("   ✓ All tables created")
        
        # Seed Admin
        print("\n3. Creating admin account...")
        admin = Admin(username='admin', email='admin@hitecuni.edu.pk')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("   ✓ Admin created (admin / admin123)")
        
        # Seed Students
        print("\n4. Creating 300 students...")
        first_names = ['Ahmed', 'Ali', 'Hassan', 'Muhammad', 'Fatima', 'Aisha', 'Zainab', 'Hana', 'Omar', 'Sara',
                      'Khalid', 'Layla', 'Noor', 'Rayan', 'Dina', 'Karim', 'Leila', 'Tariq', 'Yasmin', 'Amira']
        last_names = ['Khan', 'Ahmed', 'Hassan', 'Ali', 'Ibrahim', 'Abdullah', 'Rahman', 'Malik', 'Hussain', 'Iqbal',
                     'Siddiqui', 'Mirza', 'Baig', 'Qureshi', 'Shaikh', 'Rizvi', 'Naqvi', 'Haider', 'Raza', 'Farooq']
        
        used_rolls = set()
        used_cards = set()
        for i in range(300):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            department = random.choice(list(DEPARTMENTS.keys()))
            dept_code = DEPARTMENTS[department]
            batch_year = random.randint(20, 24)
            roll_number = generate_roll_number(dept_code, batch_year, used_rolls)
            
            student = Student(
                name=name,
                email=f"student{i+1}@hitecuni.edu.pk",
                roll_number=roll_number,
                phone=f"+92-{random.randint(300, 345)}-{random.randint(1000000, 9999999)}",
                department=department,
                semester=random.randint(1, 8),
                library_card_number=generate_library_card(used_cards),
                card_status='active'
            )
            # Set default password as roll number
            student.set_password(roll_number)
            db.session.add(student)
            
            if (i + 1) % 50 == 0:
                db.session.commit()
                print(f"   Added {i + 1}/300 students")
        
        db.session.commit()
        print("   ✓ 300 students created with default passwords (roll number)")
        
        # Seed Books - Fetch real books from Open Library API
        print("\n5. Creating 50 real books from Open Library API...")
        book_count = 0
        used_isbns = set()
        
        # Get 10 books from each genre
        genres_to_seed = ['Computer Science', 'Mathematics', 'Physics', 'Engineering', 'History']
        
        for genre in genres_to_seed:
            print(f"   Fetching books for {genre}...")
            genre_books = fetch_books_from_openlibrary(genre, count=10)
            
            # If not enough books from API, use local titles as fallback
            if len(genre_books) < 10:
                local_titles = BOOK_TITLES.get(genre, [])[:10 - len(genre_books)]
                for title in local_titles:
                    author = random.choice(AUTHORS.get(genre, ['Unknown Author']))
                    genre_books.append({
                        'title': title,
                        'author': author,
                        'isbn': generate_isbn(),
                        'year': random.randint(2000, 2024),
                        'cover': random.choice(GENRE_COVERS.get(genre, COVER_IMAGES)),
                        'publisher': random.choice(PUBLISHERS)
                    })
            
            for book_data in genre_books:
                if book_count >= 50:
                    break
                
                # Ensure unique ISBN
                if book_data['isbn'] in used_isbns:
                    book_data['isbn'] = generate_isbn()
                used_isbns.add(book_data['isbn'])
                
                book = Book(
                    title=book_data['title'],
                    author=book_data['author'],
                    isbn=book_data['isbn'],
                    genre=genre,
                    year_published=book_data['year'],
                    publisher=book_data['publisher'],
                    total_copies=random.randint(2, 5),
                    available_copies=random.randint(1, 5),
                    cover_image=book_data['cover'],
                    description=f"A comprehensive guide to {genre.lower()}. Published in {book_data['year']}.",
                    average_rating=0.0
                )
                db.session.add(book)
                book_count += 1
                
                if book_count % 10 == 0:
                    db.session.commit()
                    print(f"   Added {book_count}/50 books")
            
            if book_count >= 50:
                break
        
        db.session.commit()
        print(f"   ✓ {book_count} real books created")
        
        # Create online books directory
        os.makedirs('static/books', exist_ok=True)
        
        # Seed Online Books - Create sample PDF files for online reading
        print("\n6. Creating online books for reading...")
        online_books_count = 0
        
        # Create sample online books for first 10 books
        sample_books = Book.query.limit(10).all()
        
        for book in sample_books:
            # Create a simple text file as sample content
            filename = f"book_{book.id}_sample.txt"
            file_path = os.path.join('static', 'books', filename)
            
            # Create sample content
            content = f"""{book.title}
by {book.author}

This is a sample chapter from the book "{book.title}".
This is a demonstration of the online reading feature.

Chapter 1: Introduction

Welcome to this sample chapter. In a real library system,
this would contain the actual book content in PDF format.

The library management system allows students to:
- Request book rentals
- View their rental requests
- Read books online after approval
- Return books when finished

Thank you for using the HITEC University Taxila Library System!
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create online book record
            online_book = OnlineBook(
                book_id=book.id,
                file_path=file_path,
                file_type='txt',
                created_by=1  # Admin ID
            )
            db.session.add(online_book)
            online_books_count += 1
        
        db.session.commit()
        print(f"   ✓ {online_books_count} online books created")
        
        # Seed Reviews
        print("\n7. Creating reviews...")
        
        # Seed Reviews
        print("\n6. Creating reviews...")
        students = Student.query.all()
        books = Book.query.all()
        
        reviews_added = 0
        for student in students:
            num_reviews = random.randint(2, 5)
            reviewed_books = random.sample(books, min(num_reviews, len(books)))
            
            for book in reviewed_books:
                review = Review(
                    book_id=book.id,
                    student_id=student.id,
                    rating=random.randint(3, 5),
                    comment=random.choice(REVIEW_COMMENTS),
                    created_at=get_utc_now() - timedelta(days=random.randint(1, 365))
                )
                db.session.add(review)
                reviews_added += 1
            
            if reviews_added % 100 == 0:
                db.session.commit()
                print(f"   Added {reviews_added} reviews")
        
        db.session.commit()
        
        # Update book ratings
        print("\n7. Updating book ratings...")
        for book in books:
            reviews = Review.query.filter_by(book_id=book.id).all()
            if reviews:
                avg_rating = sum(r.rating for r in reviews) / len(reviews)
                book.average_rating = round(avg_rating, 1)
        
        db.session.commit()
        print(f"   ✓ {reviews_added} reviews created and ratings updated")
        
        print("\n" + "=" * 60)
        print("✓ DATABASE RESET AND SEED COMPLETED!")
        print("=" * 60)
        
        print("\nFinal Statistics:")
        print(f"  Admins: {Admin.query.count()}")
        print(f"  Students: {Student.query.count()}")
        print(f"  Books: {Book.query.count()}")
        print(f"  Reviews: {Review.query.count()}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        db.session.rollback()
        raise
