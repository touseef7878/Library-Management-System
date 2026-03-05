from app import app, db, Book, Member, Loan, Review
from datetime import datetime, timedelta
import random

# Unique book cover URLs from Open Library and other sources
books_data = [
    # Fiction
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Fiction", "year": 1925, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Fiction", "year": 1960, "cover": "https://covers.openlibrary.org/b/id/7725407-M.jpg"},
    {"title": "1984", "author": "George Orwell", "genre": "Fiction", "year": 1949, "cover": "https://covers.openlibrary.org/b/id/7725408-M.jpg"},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Fiction", "year": 1813, "cover": "https://covers.openlibrary.org/b/id/7725409-M.jpg"},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Fiction", "year": 1951, "cover": "https://covers.openlibrary.org/b/id/7725410-M.jpg"},
    {"title": "Wuthering Heights", "author": "Emily Brontë", "genre": "Fiction", "year": 1847, "cover": "https://covers.openlibrary.org/b/id/7725411-M.jpg"},
    {"title": "Jane Eyre", "author": "Charlotte Brontë", "genre": "Fiction", "year": 1847, "cover": "https://covers.openlibrary.org/b/id/7725412-M.jpg"},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fiction", "year": 1937, "cover": "https://covers.openlibrary.org/b/id/7725413-M.jpg"},
    {"title": "Moby Dick", "author": "Herman Melville", "genre": "Fiction", "year": 1851, "cover": "https://covers.openlibrary.org/b/id/7725414-M.jpg"},
    {"title": "The Odyssey", "author": "Homer", "genre": "Fiction", "year": -800, "cover": "https://covers.openlibrary.org/b/id/7725415-M.jpg"},
    
    # Science Fiction
    {"title": "Dune", "author": "Frank Herbert", "genre": "Science Fiction", "year": 1965, "cover": "https://covers.openlibrary.org/b/id/7725416-M.jpg"},
    {"title": "Foundation", "author": "Isaac Asimov", "genre": "Science Fiction", "year": 1951, "cover": "https://covers.openlibrary.org/b/id/7725417-M.jpg"},
    {"title": "Neuromancer", "author": "William Gibson", "genre": "Science Fiction", "year": 1984, "cover": "https://covers.openlibrary.org/b/id/7725418-M.jpg"},
    {"title": "The Martian", "author": "Andy Weir", "genre": "Science Fiction", "year": 2011, "cover": "https://covers.openlibrary.org/b/id/7725419-M.jpg"},
    {"title": "Ender's Game", "author": "Orson Scott Card", "genre": "Science Fiction", "year": 1985, "cover": "https://covers.openlibrary.org/b/id/7725420-M.jpg"},
    {"title": "The Left Hand of Darkness", "author": "Ursula K. Le Guin", "genre": "Science Fiction", "year": 1969, "cover": "https://covers.openlibrary.org/b/id/7725421-M.jpg"},
    {"title": "Hyperion", "author": "Dan Simmons", "genre": "Science Fiction", "year": 1989, "cover": "https://covers.openlibrary.org/b/id/7725422-M.jpg"},
    {"title": "The Three-Body Problem", "author": "Liu Cixin", "genre": "Science Fiction", "year": 2008, "cover": "https://covers.openlibrary.org/b/id/7725423-M.jpg"},
    {"title": "Snow Crash", "author": "Neal Stephenson", "genre": "Science Fiction", "year": 1992, "cover": "https://covers.openlibrary.org/b/id/7725424-M.jpg"},
    {"title": "Altered Carbon", "author": "Richard K. Morgan", "genre": "Science Fiction", "year": 2002, "cover": "https://covers.openlibrary.org/b/id/7725425-M.jpg"},
    
    # Fantasy
    {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "genre": "Fantasy", "year": 1954, "cover": "https://covers.openlibrary.org/b/id/7725426-M.jpg"},
    {"title": "A Game of Thrones", "author": "George R.R. Martin", "genre": "Fantasy", "year": 1996, "cover": "https://covers.openlibrary.org/b/id/7725427-M.jpg"},
    {"title": "The Name of the Wind", "author": "Patrick Rothfuss", "genre": "Fantasy", "year": 2007, "cover": "https://covers.openlibrary.org/b/id/7725428-M.jpg"},
    {"title": "Mistborn", "author": "Brandon Sanderson", "genre": "Fantasy", "year": 2006, "cover": "https://covers.openlibrary.org/b/id/7725429-M.jpg"},
    {"title": "The Way of Kings", "author": "Brandon Sanderson", "genre": "Fantasy", "year": 2010, "cover": "https://covers.openlibrary.org/b/id/7725430-M.jpg"},
    {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "genre": "Fantasy", "year": 1997, "cover": "https://covers.openlibrary.org/b/id/7725431-M.jpg"},
    {"title": "The Chronicles of Narnia", "author": "C.S. Lewis", "genre": "Fantasy", "year": 1950, "cover": "https://covers.openlibrary.org/b/id/7725432-M.jpg"},
    {"title": "Eragon", "author": "Christopher Paolini", "genre": "Fantasy", "year": 2003, "cover": "https://covers.openlibrary.org/b/id/7725433-M.jpg"},
    {"title": "The Wheel of Time", "author": "Robert Jordan", "genre": "Fantasy", "year": 1990, "cover": "https://covers.openlibrary.org/b/id/7725434-M.jpg"},
    {"title": "Stardust", "author": "Neil Gaiman", "genre": "Fantasy", "year": 1999, "cover": "https://covers.openlibrary.org/b/id/7725435-M.jpg"},
    
    # Mystery
    {"title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "genre": "Mystery", "year": 2005, "cover": "https://covers.openlibrary.org/b/id/7725436-M.jpg"},
    {"title": "The Da Vinci Code", "author": "Dan Brown", "genre": "Mystery", "year": 2003, "cover": "https://covers.openlibrary.org/b/id/7725437-M.jpg"},
    {"title": "Murder on the Orient Express", "author": "Agatha Christie", "genre": "Mystery", "year": 1934, "cover": "https://covers.openlibrary.org/b/id/7725438-M.jpg"},
    {"title": "The Hound of the Baskervilles", "author": "Arthur Conan Doyle", "genre": "Mystery", "year": 1901, "cover": "https://covers.openlibrary.org/b/id/7725439-M.jpg"},
    {"title": "Gone Girl", "author": "Gillian Flynn", "genre": "Mystery", "year": 2012, "cover": "https://covers.openlibrary.org/b/id/7725440-M.jpg"},
    {"title": "The Girl on the Train", "author": "Paula Hawkins", "genre": "Mystery", "year": 2015, "cover": "https://covers.openlibrary.org/b/id/7725441-M.jpg"},
    {"title": "And Then There Were None", "author": "Agatha Christie", "genre": "Mystery", "year": 1939, "cover": "https://covers.openlibrary.org/b/id/7725442-M.jpg"},
    {"title": "The Maltese Falcon", "author": "Dashiell Hammett", "genre": "Mystery", "year": 1930, "cover": "https://covers.openlibrary.org/b/id/7725443-M.jpg"},
    {"title": "The Silence of the Lambs", "author": "Thomas Harris", "genre": "Mystery", "year": 1988, "cover": "https://covers.openlibrary.org/b/id/7725444-M.jpg"},
    {"title": "The Bourne Identity", "author": "Robert Ludlum", "genre": "Mystery", "year": 1980, "cover": "https://covers.openlibrary.org/b/id/7725445-M.jpg"},
    
    # Romance
    {"title": "Outlander", "author": "Diana Gabaldon", "genre": "Romance", "year": 1991, "cover": "https://covers.openlibrary.org/b/id/7725446-M.jpg"},
    {"title": "The Notebook", "author": "Nicholas Sparks", "genre": "Romance", "year": 1996, "cover": "https://covers.openlibrary.org/b/id/7725447-M.jpg"},
    {"title": "Twilight", "author": "Stephenie Meyer", "genre": "Romance", "year": 2005, "cover": "https://covers.openlibrary.org/b/id/7725448-M.jpg"},
    {"title": "The Time Traveler's Wife", "author": "Audrey Niffenegger", "genre": "Romance", "year": 2003, "cover": "https://covers.openlibrary.org/b/id/7725449-M.jpg"},
    {"title": "Me Before You", "author": "Jojo Moyes", "genre": "Romance", "year": 2012, "cover": "https://covers.openlibrary.org/b/id/7725450-M.jpg"},
    {"title": "The Fault in Our Stars", "author": "John Green", "genre": "Romance", "year": 2012, "cover": "https://covers.openlibrary.org/b/id/7725451-M.jpg"},
    {"title": "A Walk to Remember", "author": "Nicholas Sparks", "genre": "Romance", "year": 1999, "cover": "https://covers.openlibrary.org/b/id/7725452-M.jpg"},
    {"title": "The Bridges of Madison County", "author": "Robert James Waller", "genre": "Romance", "year": 1992, "cover": "https://covers.openlibrary.org/b/id/7725453-M.jpg"},
    {"title": "Fifty Shades of Grey", "author": "E.L. James", "genre": "Romance", "year": 2011, "cover": "https://covers.openlibrary.org/b/id/7725454-M.jpg"},
    {"title": "The Rosie Project", "author": "Graeme Simsion", "genre": "Romance", "year": 2013, "cover": "https://covers.openlibrary.org/b/id/7725455-M.jpg"},
    
    # Horror
    {"title": "The Shining", "author": "Stephen King", "genre": "Horror", "year": 1977, "cover": "https://covers.openlibrary.org/b/id/7725456-M.jpg"},
    {"title": "It", "author": "Stephen King", "genre": "Horror", "year": 1986, "cover": "https://covers.openlibrary.org/b/id/7725457-M.jpg"},
    {"title": "Dracula", "author": "Bram Stoker", "genre": "Horror", "year": 1897, "cover": "https://covers.openlibrary.org/b/id/7725458-M.jpg"},
    {"title": "Frankenstein", "author": "Mary Shelley", "genre": "Horror", "year": 1818, "cover": "https://covers.openlibrary.org/b/id/7725459-M.jpg"},
    {"title": "The Exorcist", "author": "William Peter Blatty", "genre": "Horror", "year": 1971, "cover": "https://covers.openlibrary.org/b/id/7725460-M.jpg"},
    {"title": "The Haunting of Hill House", "author": "Shirley Jackson", "genre": "Horror", "year": 1959, "cover": "https://covers.openlibrary.org/b/id/7725461-M.jpg"},
    {"title": "The Ring", "author": "Koji Suzuki", "genre": "Horror", "year": 1991, "cover": "https://covers.openlibrary.org/b/id/7725462-M.jpg"},
    {"title": "Pet Sematary", "author": "Stephen King", "genre": "Horror", "year": 1983, "cover": "https://covers.openlibrary.org/b/id/7725463-M.jpg"},
    {"title": "The Conjuring", "author": "James Wan", "genre": "Horror", "year": 2013, "cover": "https://covers.openlibrary.org/b/id/7725464-M.jpg"},
    {"title": "Insidious", "author": "James Wan", "genre": "Horror", "year": 2010, "cover": "https://covers.openlibrary.org/b/id/7725465-M.jpg"},
    
    # History
    {"title": "The Guns of August", "author": "Barbara W. Tuchman", "genre": "History", "year": 1962, "cover": "https://covers.openlibrary.org/b/id/7725466-M.jpg"},
    {"title": "A Brief History of Time", "author": "Stephen Hawking", "genre": "History", "year": 1988, "cover": "https://covers.openlibrary.org/b/id/7725467-M.jpg"},
    {"title": "The Silk Roads", "author": "Peter Frankopan", "genre": "History", "year": 2015, "cover": "https://covers.openlibrary.org/b/id/7725468-M.jpg"},
    {"title": "Sapiens", "author": "Yuval Noah Harari", "genre": "History", "year": 2011, "cover": "https://covers.openlibrary.org/b/id/7725469-M.jpg"},
    {"title": "The Rise and Fall of the Third Reich", "author": "William L. Shirer", "genre": "History", "year": 1960, "cover": "https://covers.openlibrary.org/b/id/7725470-M.jpg"},
    {"title": "1491", "author": "Charles C. Mann", "genre": "History", "year": 2005, "cover": "https://covers.openlibrary.org/b/id/7725471-M.jpg"},
    {"title": "The Code Breaker", "author": "Walter Isaacson", "genre": "History", "year": 2021, "cover": "https://covers.openlibrary.org/b/id/7725472-M.jpg"},
    {"title": "Educated", "author": "Tara Westover", "genre": "History", "year": 2018, "cover": "https://covers.openlibrary.org/b/id/7725473-M.jpg"},
    {"title": "The Immortal Life of Henrietta Lacks", "author": "Rebecca Skloot", "genre": "History", "year": 2010, "cover": "https://covers.openlibrary.org/b/id/7725474-M.jpg"},
    {"title": "Becoming", "author": "Michelle Obama", "genre": "History", "year": 2018, "cover": "https://covers.openlibrary.org/b/id/7725475-M.jpg"},
    
    # Science
    {"title": "The Selfish Gene", "author": "Richard Dawkins", "genre": "Science", "year": 1976, "cover": "https://covers.openlibrary.org/b/id/7725476-M.jpg"},
    {"title": "Cosmos", "author": "Carl Sagan", "genre": "Science", "year": 1980, "cover": "https://covers.openlibrary.org/b/id/7725477-M.jpg"},
    {"title": "The Elegant Universe", "author": "Brian Greene", "genre": "Science", "year": 1999, "cover": "https://covers.openlibrary.org/b/id/7725478-M.jpg"},
    {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "genre": "Science", "year": 2011, "cover": "https://covers.openlibrary.org/b/id/7725479-M.jpg"},
    {"title": "The Tipping Point", "author": "Malcolm Gladwell", "genre": "Science", "year": 2000, "cover": "https://covers.openlibrary.org/b/id/7725480-M.jpg"},
    {"title": "Freakonomics", "author": "Steven D. Levitt", "genre": "Science", "year": 2005, "cover": "https://covers.openlibrary.org/b/id/7725481-M.jpg"},
    {"title": "Gödel, Escher, Bach", "author": "Douglas Hofstadter", "genre": "Science", "year": 1979, "cover": "https://covers.openlibrary.org/b/id/7725482-M.jpg"},
    {"title": "The Structure of Scientific Revolutions", "author": "Thomas Kuhn", "genre": "Science", "year": 1962, "cover": "https://covers.openlibrary.org/b/id/7725483-M.jpg"},
    {"title": "Pale Blue Dot", "author": "Carl Sagan", "genre": "Science", "year": 1994, "cover": "https://covers.openlibrary.org/b/id/7725484-M.jpg"},
    {"title": "The Demon-Haunted World", "author": "Carl Sagan", "genre": "Science", "year": 1996, "cover": "https://covers.openlibrary.org/b/id/7725485-M.jpg"},
]

# Sample members
members_data = [
    {"name": "John Smith", "email": "john.smith@email.com", "contact": "+1-555-0101"},
    {"name": "Sarah Johnson", "email": "sarah.johnson@email.com", "contact": "+1-555-0102"},
    {"name": "Michael Brown", "email": "michael.brown@email.com", "contact": "+1-555-0103"},
    {"name": "Emily Davis", "email": "emily.davis@email.com", "contact": "+1-555-0104"},
    {"name": "David Wilson", "email": "david.wilson@email.com", "contact": "+1-555-0105"},
    {"name": "Jessica Martinez", "email": "jessica.martinez@email.com", "contact": "+1-555-0106"},
    {"name": "Robert Taylor", "email": "robert.taylor@email.com", "contact": "+1-555-0107"},
    {"name": "Lisa Anderson", "email": "lisa.anderson@email.com", "contact": "+1-555-0108"},
    {"name": "James Thomas", "email": "james.thomas@email.com", "contact": "+1-555-0109"},
    {"name": "Mary Jackson", "email": "mary.jackson@email.com", "contact": "+1-555-0110"},
]

# Review comments
review_comments = [
    "Absolutely amazing! Couldn't put it down.",
    "A masterpiece of literature. Highly recommended.",
    "Brilliant storytelling and character development.",
    "One of the best books I've ever read.",
    "Captivating from start to finish.",
    "A must-read for everyone.",
    "Exceptional writing and plot.",
    "Loved every page of this book.",
    "Truly inspiring and thought-provoking.",
    "A timeless classic that everyone should read.",
    "Fantastic adventure and great characters.",
    "Couldn't recommend this more highly.",
    "A real page-turner!",
    "Beautifully written with deep meaning.",
    "One of my favorite books ever.",
]

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    print("🔄 Seeding database...")
    
    # Add books
    print(f"📚 Adding {len(books_data)} books...")
    books = []
    for book_data in books_data:
        book = Book(
            title=book_data['title'],
            author=book_data['author'],
            genre=book_data['genre'],
            year_published=book_data['year'],
            cover_image=book_data['cover']
        )
        books.append(book)
        db.session.add(book)
    db.session.commit()
    
    # Add members
    print(f"👥 Adding {len(members_data)} members...")
    members = []
    for member_data in members_data:
        member = Member(
            name=member_data['name'],
            email=member_data['email'],
            contact=member_data['contact'],
            member_since=datetime.now().date() - timedelta(days=random.randint(30, 365))
        )
        members.append(member)
        db.session.add(member)
    db.session.commit()
    
    # Add loans
    print("📋 Adding loans...")
    loan_count = 0
    for _ in range(25):  # Create 25 loans
        member = random.choice(members)
        book = random.choice(books)
        
        # Check if book is already loaned
        existing_loan = Loan.query.filter_by(book_id=book.id, returned=False).first()
        if not existing_loan:
            loan_date = datetime.now().date() - timedelta(days=random.randint(1, 30))
            return_date = loan_date + timedelta(days=random.randint(7, 30))
            
            loan = Loan(
                member_id=member.id,
                book_id=book.id,
                loan_date=loan_date,
                return_date=return_date,
                returned=random.choice([True, False]),
                late_fee=0.0
            )
            db.session.add(loan)
            loan_count += 1
    db.session.commit()
    print(f"  ✓ Added {loan_count} loans")
    
    # Add reviews
    print("⭐ Adding reviews...")
    review_count = 0
    for book in books:
        # Add 1-3 reviews per book
        num_reviews = random.randint(1, 3)
        for _ in range(num_reviews):
            member = random.choice(members)
            
            # Check if member already reviewed this book
            existing_review = Review.query.filter_by(book_id=book.id, member_id=member.id).first()
            if not existing_review:
                rating = random.randint(3, 5)
                comment = random.choice(review_comments)
                
                review = Review(
                    book_id=book.id,
                    member_id=member.id,
                    rating=rating,
                    comment=comment,
                    date_posted=datetime.now() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(review)
                review_count += 1
    db.session.commit()
    print(f"  ✓ Added {review_count} reviews")
    
    # Update book ratings
    print("📊 Updating book ratings...")
    for book in books:
        reviews = Review.query.filter_by(book_id=book.id).all()
        if reviews:
            avg_rating = sum([r.rating for r in reviews]) / len(reviews)
            book.average_rating = round(avg_rating, 1)
    db.session.commit()
    
    print("\n✅ Database seeding completed successfully!")
    print(f"   📚 Books: {len(books)}")
    print(f"   👥 Members: {len(members)}")
    print(f"   📋 Loans: {loan_count}")
    print(f"   ⭐ Reviews: {review_count}")
