"""
Reset and Seed Database Script
Cleans the database and populates it with fresh data:
- 1 Admin account
- 300 Students with proper roll numbers (YY-DEPT-NNN)
- 1000 Books with real titles and cover images
- Reviews from students
"""

from app import app, db, Admin, Student, Book, Review
from datetime import datetime, timedelta, timezone
import random
import string

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

# Real book titles by genre (50 per genre = 500 total, will be duplicated to reach 1000)
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
    'Economics': [
        'The Wealth of Nations', 'Capital', 'The General Theory of Employment', 'Capitalism and Socialism', 'The Road to Serfdom',
        'Free to Choose', 'Freakonomics', 'Thinking, Fast and Slow', 'Misbehaving', 'Predictably Irrational',
        'The Black Swan', 'Antifragile', 'Capital in the Twenty-First Century', 'The Second Machine Age', 'Rise of the Robots',
        'The Lean Startup', 'Good to Great', 'Built to Last', 'The Innovators Dilemma', 'Crossing the Chasm',
        'The Tipping Point', 'Outliers', 'David and Goliath', 'Blink', 'What the Dog Saw',
        'Talking to Strangers', 'The Undercover Economist', 'Superfreakonomics', 'Think Like a Freak', 'Naked Economics',
        'Economics Rules', 'The Meritocracy Trap', 'Bowling Alone', 'Strangers in Their Own Land', 'Deaths of Despair',
        'The New Geography of Jobs', 'The Rise and Fall of American Growth', 'The Great Risk Shift', 'The Precariat', 'Bullshit Jobs',
        'The Utopia of Rules', 'Debt: The First 5000 Years', 'The Price of Inequality', 'The Great Transformation', 'Development Economics',
        'International Economics', 'Monetary Economics', 'Public Finance', 'Labor Economics', 'Environmental Economics'
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
    'Electrical Engineering': [
        'Electrical Engineering Fundamentals', 'Circuit Theory', 'Network Analysis', 'Electromagnetic Theory', 'Electromagnetics',
        'Antenna Theory', 'Microwave Engineering', 'RF Circuit Design', 'Digital Electronics', 'Analog Electronics',
        'Power Electronics', 'Semiconductor Devices', 'Integrated Circuits', 'VLSI Design', 'Digital Signal Processing',
        'Signal Processing', 'Communication Systems', 'Digital Communications', 'Wireless Communications', 'Optical Communications',
        'Fiber Optics', 'Photonics', 'Laser Engineering', 'Optoelectronics', 'Power Systems',
        'Power Generation', 'Power Transmission', 'Power Distribution', 'Electrical Machines', 'DC Machines',
        'AC Machines', 'Transformers', 'Induction Motors', 'Synchronous Machines', 'Control Systems',
        'Automatic Control', 'Process Control', 'Industrial Automation', 'Robotics Control', 'Power Quality',
        'Harmonic Analysis', 'Transient Analysis', 'Fault Analysis', 'Protection Systems', 'Switchgear',
        'Electrical Safety', 'High Voltage Engineering', 'Electric Drives', 'Renewable Energy Systems', 'Smart Grids'
    ],
    'Mechanical Engineering': [
        'Engineering Mechanics', 'Statics and Dynamics', 'Mechanics of Materials', 'Strength of Materials', 'Thermodynamics',
        'Heat Transfer', 'Fluid Mechanics', 'Hydraulics and Pneumatics', 'Machine Design', 'Mechanical Design',
        'Design of Machine Elements', 'Bearings and Lubrication', 'Gears and Gear Trains', 'Belts and Chains', 'Clutches and Brakes',
        'Vibration Analysis', 'Mechanical Vibrations', 'Dynamics of Machinery', 'Kinematics of Machinery', 'Mechanisms',
        'Manufacturing Processes', 'Metal Cutting', 'Machining', 'Casting', 'Welding',
        'Forging', 'Sheet Metal Work', 'Powder Metallurgy', 'Composite Materials', 'Materials Science',
        'Material Properties', 'Metallurgy', 'Non-Destructive Testing', 'Quality Control', 'Metrology',
        'Precision Engineering', 'CAD/CAM', 'CNC Machining', 'Robotics', 'Automation',
        'Industrial Engineering', 'Production Planning', 'Inventory Management', 'Supply Chain Management', 'Lean Manufacturing',
        'Six Sigma', 'Total Quality Management', 'Maintenance Engineering', 'Reliability Engineering', 'Tribology'
    ],
    'Civil Engineering': [
        'Structural Analysis', 'Structural Design', 'Reinforced Concrete Design', 'Steel Structures', 'Foundation Engineering',
        'Soil Mechanics', 'Geotechnical Engineering', 'Rock Mechanics', 'Tunneling', 'Underground Construction',
        'Dams and Reservoirs', 'Water Resources Engineering', 'Hydraulics', 'Hydrology', 'Flood Management',
        'Irrigation Engineering', 'Drainage Engineering', 'Water Supply Engineering', 'Wastewater Treatment', 'Environmental Engineering',
        'Air Pollution Control', 'Noise Control', 'Solid Waste Management', 'Hazardous Waste Management', 'Transportation Engineering',
        'Highway Engineering', 'Railway Engineering', 'Airport Engineering', 'Port Engineering', 'Bridge Engineering',
        'Tunnel Engineering', 'Pavement Design', 'Traffic Engineering', 'Urban Planning', 'City Planning',
        'Sustainable Development', 'Green Building', 'Building Information Modeling', 'Construction Management', 'Project Management',
        'Quantity Surveying', 'Estimation and Costing', 'Contracts and Specifications', 'Building Codes', 'Earthquake Engineering',
        'Wind Engineering', 'Coastal Engineering', 'River Engineering', 'Surveying', 'Remote Sensing'
    ],
    'Software Engineering': [
        'Software Engineering Principles', 'Software Design', 'Software Architecture', 'Design Patterns', 'Refactoring',
        'Code Quality', 'Testing and Debugging', 'Unit Testing', 'Integration Testing', 'System Testing',
        'Performance Testing', 'Security Testing', 'Test Automation', 'Continuous Integration', 'Continuous Delivery',
        'DevOps', 'Agile Development', 'Scrum', 'Kanban', 'Lean Software Development',
        'Extreme Programming', 'Requirements Engineering', 'Software Specification', 'Use Cases', 'User Stories',
        'Software Modeling', 'UML', 'Domain-Driven Design', 'Microservices Architecture', 'Monolithic Architecture',
        'Service-Oriented Architecture', 'Event-Driven Architecture', 'API Design', 'REST APIs', 'GraphQL',
        'Web Services', 'Cloud Computing', 'Containerization', 'Docker', 'Kubernetes',
        'Serverless Computing', 'Database Design', 'SQL', 'NoSQL', 'Data Warehousing',
        'Big Data', 'Software Maintenance', 'Legacy Systems', 'Software Evolution', 'Software Metrics'
    ]
}

# Authors by genre
AUTHORS = {
    'Computer Science': ['Donald Knuth', 'Thomas Cormen', 'Robert Martin', 'Steve McConnell', 'Martin Fowler'],
    'Mathematics': ['Carl Gauss', 'Leonhard Euler', 'Isaac Newton', 'Euclid', 'David Hilbert'],
    'History': ['Yuval Harari', 'Will Durant', 'Barbara Tuchman', 'Eric Hobsbawm', 'Christopher Clark'],
    'Physics': ['Albert Einstein', 'Stephen Hawking', 'Richard Feynman', 'Carl Sagan', 'Brian Greene'],
    'Economics': ['Adam Smith', 'John Keynes', 'Milton Friedman', 'Thomas Piketty', 'Paul Krugman'],
    'Engineering': ['Gustave Eiffel', 'Nikola Tesla', 'George Stephenson', 'Thomas Edison', 'Henry Ford'],
    'Electrical Engineering': ['James Maxwell', 'Michael Faraday', 'Georg Ohm', 'Alessandro Volta', 'Oliver Heaviside'],
    'Mechanical Engineering': ['James Watt', 'Rudolf Diesel', 'Charles Babbage', 'Joseph Bramah', 'John Smeaton'],
    'Civil Engineering': ['Gustave Eiffel', 'Isambard Brunel', 'John Roebling', 'Joseph Bazalgette', 'Thomas Telford'],
    'Software Engineering': ['Fred Brooks', 'Barry Boehm', 'Grady Booch', 'Kent Beck', 'Martin Fowler']
}

PUBLISHERS = ['Addison-Wesley', 'O\'Reilly', 'Pearson', 'MIT Press', 'Springer', 'Cambridge', 'Oxford', 'Dover', 'Princeton', 'Penguin', 'McGraw-Hill', 'Elsevier', 'Wiley', 'IEEE Press']

COVER_IMAGES = [
    'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=300&h=400&fit=crop',
    'https://images.unsplash.com/photo-1516979187457-635ffe35ff15?w=300&h=400&fit=crop',
    'https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop',
    'https://images.unsplash.com/photo-1509228627152-72ae67a42c27?w=300&h=400&fit=crop',
    'https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=300&h=400&fit=crop',
    'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=300&h=400&fit=crop',
    'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=300&h=400&fit=crop',
    'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300&h=400&fit=crop',
]

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

def generate_library_card():
    return f"LIB{random.randint(100000, 999999)}"

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
        admin = Admin(username='admin', email='admin@hitec.edu.pk')
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
        for i in range(300):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            department = random.choice(list(DEPARTMENTS.keys()))
            dept_code = DEPARTMENTS[department]
            batch_year = random.randint(20, 24)
            
            student = Student(
                name=name,
                email=f"student{i+1}@hitec.edu.pk",
                roll_number=generate_roll_number(dept_code, batch_year, used_rolls),
                phone=f"+92-{random.randint(300, 345)}-{random.randint(1000000, 9999999)}",
                department=department,
                semester=random.randint(1, 8),
                library_card_number=generate_library_card(),
                card_status='active'
            )
            db.session.add(student)
            
            if (i + 1) % 50 == 0:
                db.session.commit()
                print(f"   Added {i + 1}/300 students")
        
        db.session.commit()
        print("   ✓ 300 students created")
        
        # Seed Books
        print("\n5. Creating 1000 books...")
        book_count = 0
        for genre, titles in BOOK_TITLES.items():
            for i in range(100):  # 100 books per genre
                title = titles[i % len(titles)]
                author = random.choice(AUTHORS[genre])
                
                book = Book(
                    title=title,
                    author=author,
                    isbn=generate_isbn(),
                    genre=genre,
                    year_published=random.randint(2000, 2024),
                    publisher=random.choice(PUBLISHERS),
                    total_copies=random.randint(2, 10),
                    available_copies=random.randint(1, 10),
                    cover_image=random.choice(COVER_IMAGES),
                    description=f"A comprehensive guide to {genre}. This book covers essential concepts and practical applications.",
                    average_rating=0.0
                )
                db.session.add(book)
                book_count += 1
                
                if book_count % 100 == 0:
                    db.session.commit()
                    print(f"   Added {book_count}/1000 books")
        
        db.session.commit()
        print("   ✓ 1000 books created")
        
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
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))
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
