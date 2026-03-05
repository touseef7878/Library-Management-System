from app import app, db, Book

# Sample books data with real cover image URLs from Open Library
books_data = [
    # Fiction
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Fiction", "year": 1925, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Fiction", "year": 1960, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "1984", "author": "George Orwell", "genre": "Fiction", "year": 1949, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Fiction", "year": 1813, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Fiction", "year": 1951, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Wuthering Heights", "author": "Emily Brontë", "genre": "Fiction", "year": 1847, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Jane Eyre", "author": "Charlotte Brontë", "genre": "Fiction", "year": 1847, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fiction", "year": 1937, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Moby Dick", "author": "Herman Melville", "genre": "Fiction", "year": 1851, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Odyssey", "author": "Homer", "genre": "Fiction", "year": -800, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    
    # Science Fiction
    {"title": "Dune", "author": "Frank Herbert", "genre": "Science Fiction", "year": 1965, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Foundation", "author": "Isaac Asimov", "genre": "Science Fiction", "year": 1951, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Neuromancer", "author": "William Gibson", "genre": "Science Fiction", "year": 1984, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Martian", "author": "Andy Weir", "genre": "Science Fiction", "year": 2011, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Ender's Game", "author": "Orson Scott Card", "genre": "Science Fiction", "year": 1985, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Left Hand of Darkness", "author": "Ursula K. Le Guin", "genre": "Science Fiction", "year": 1969, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Hyperion", "author": "Dan Simmons", "genre": "Science Fiction", "year": 1989, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Three-Body Problem", "author": "Liu Cixin", "genre": "Science Fiction", "year": 2008, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Snow Crash", "author": "Neal Stephenson", "genre": "Science Fiction", "year": 1992, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Altered Carbon", "author": "Richard K. Morgan", "genre": "Science Fiction", "year": 2002, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    
    # Fantasy
    {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "genre": "Fantasy", "year": 1954, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "A Game of Thrones", "author": "George R.R. Martin", "genre": "Fantasy", "year": 1996, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Name of the Wind", "author": "Patrick Rothfuss", "genre": "Fantasy", "year": 2007, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Mistborn", "author": "Brandon Sanderson", "genre": "Fantasy", "year": 2006, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Way of Kings", "author": "Brandon Sanderson", "genre": "Fantasy", "year": 2010, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "genre": "Fantasy", "year": 1997, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Chronicles of Narnia", "author": "C.S. Lewis", "genre": "Fantasy", "year": 1950, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Eragon", "author": "Christopher Paolini", "genre": "Fantasy", "year": 2003, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Wheel of Time", "author": "Robert Jordan", "genre": "Fantasy", "year": 1990, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Stardust", "author": "Neil Gaiman", "genre": "Fantasy", "year": 1999, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    
    # Mystery/Thriller
    {"title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "genre": "Mystery", "year": 2005, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Da Vinci Code", "author": "Dan Brown", "genre": "Mystery", "year": 2003, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Murder on the Orient Express", "author": "Agatha Christie", "genre": "Mystery", "year": 1934, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Hound of the Baskervilles", "author": "Arthur Conan Doyle", "genre": "Mystery", "year": 1901, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Gone Girl", "author": "Gillian Flynn", "genre": "Mystery", "year": 2012, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Silence of the Lambs", "author": "Thomas Harris", "genre": "Thriller", "year": 1988, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Bourne Identity", "author": "Robert Ludlum", "genre": "Thriller", "year": 1980, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Girl on the Train", "author": "Paula Hawkins", "genre": "Mystery", "year": 2015, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "And Then There Were None", "author": "Agatha Christie", "genre": "Mystery", "year": 1939, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Maltese Falcon", "author": "Dashiell Hammett", "genre": "Mystery", "year": 1930, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    
    # Romance
    {"title": "Outlander", "author": "Diana Gabaldon", "genre": "Romance", "year": 1991, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Notebook", "author": "Nicholas Sparks", "genre": "Romance", "year": 1996, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Twilight", "author": "Stephenie Meyer", "genre": "Romance", "year": 2005, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Time Traveler's Wife", "author": "Audrey Niffenegger", "genre": "Romance", "year": 2003, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Me Before You", "author": "Jojo Moyes", "genre": "Romance", "year": 2012, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Fault in Our Stars", "author": "John Green", "genre": "Romance", "year": 2012, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "A Walk to Remember", "author": "Nicholas Sparks", "genre": "Romance", "year": 1999, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Bridges of Madison County", "author": "Robert James Waller", "genre": "Romance", "year": 1992, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Fifty Shades of Grey", "author": "E.L. James", "genre": "Romance", "year": 2011, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Rosie Project", "author": "Graeme Simsion", "genre": "Romance", "year": 2013, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    
    # Horror
    {"title": "The Shining", "author": "Stephen King", "genre": "Horror", "year": 1977, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "It", "author": "Stephen King", "genre": "Horror", "year": 1986, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Dracula", "author": "Bram Stoker", "genre": "Horror", "year": 1897, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Frankenstein", "author": "Mary Shelley", "genre": "Horror", "year": 1818, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Exorcist", "author": "William Peter Blatty", "genre": "Horror", "year": 1971, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Haunting of Hill House", "author": "Shirley Jackson", "genre": "Horror", "year": 1959, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Ring", "author": "Koji Suzuki", "genre": "Horror", "year": 1991, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Conjuring", "author": "James Wan", "genre": "Horror", "year": 2013, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Pet Sematary", "author": "Stephen King", "genre": "Horror", "year": 1983, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Silence of the Lambs", "author": "Thomas Harris", "genre": "Horror", "year": 1988, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    
    # History
    {"title": "The Guns of August", "author": "Barbara W. Tuchman", "genre": "History", "year": 1962, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "A Brief History of Time", "author": "Stephen Hawking", "genre": "History", "year": 1988, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Silk Roads", "author": "Peter Frankopan", "genre": "History", "year": 2015, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Sapiens", "author": "Yuval Noah Harari", "genre": "History", "year": 2011, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Rise and Fall of the Third Reich", "author": "William L. Shirer", "genre": "History", "year": 1960, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "1491", "author": "Charles C. Mann", "genre": "History", "year": 2005, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Code Breaker", "author": "Walter Isaacson", "genre": "History", "year": 2021, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Educated", "author": "Tara Westover", "genre": "History", "year": 2018, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Immortal Life of Henrietta Lacks", "author": "Rebecca Skloot", "genre": "History", "year": 2010, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Becoming", "author": "Michelle Obama", "genre": "History", "year": 2018, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    
    # Science
    {"title": "The Selfish Gene", "author": "Richard Dawkins", "genre": "Science", "year": 1976, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Cosmos", "author": "Carl Sagan", "genre": "Science", "year": 1980, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Elegant Universe", "author": "Brian Greene", "genre": "Science", "year": 1999, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "genre": "Science", "year": 2011, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Tipping Point", "author": "Malcolm Gladwell", "genre": "Science", "year": 2000, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Freakonomics", "author": "Steven D. Levitt", "genre": "Science", "year": 2005, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Immortal Life of Henrietta Lacks", "author": "Rebecca Skloot", "genre": "Science", "year": 2010, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Gödel, Escher, Bach", "author": "Douglas Hofstadter", "genre": "Science", "year": 1979, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "The Structure of Scientific Revolutions", "author": "Thomas Kuhn", "genre": "Science", "year": 1962, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
    {"title": "Pale Blue Dot", "author": "Carl Sagan", "genre": "Science", "year": 1994, "cover": "https://covers.openlibrary.org/b/id/7725406-M.jpg"},
]

with app.app_context():
    # Check if books already exist
    existing_count = Book.query.count()
    if existing_count > 1:
        print(f"Database already has {existing_count} books. Skipping seed.")
    else:
        for book_data in books_data:
            book = Book(
                title=book_data['title'],
                author=book_data['author'],
                genre=book_data['genre'],
                year_published=book_data['year'],
                cover_image=book_data['cover']
            )
            db.session.add(book)
        
        db.session.commit()
        print(f"Successfully added {len(books_data)} books to the database!")
