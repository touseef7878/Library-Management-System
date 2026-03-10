"""
Complete Database Reset Script
Deletes existing database and book files, then recreates everything
"""

import os
import shutil
import subprocess
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def confirm_reset():
    """Ask user to confirm reset"""
    print("⚠️  WARNING: This will DELETE all existing data!")
    print("   - Database will be deleted")
    print("   - All book content files will be deleted")
    print("   - All student records, loans, and reviews will be lost")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    return response in ['yes', 'y']

def delete_database():
    """Delete the database file"""
    db_path = os.path.join('database', 'library.db')
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✓ Deleted database: {db_path}")
            return True
        except Exception as e:
            print(f"✗ Error deleting database: {e}")
            return False
    else:
        print("ℹ Database file not found (already deleted or never created)")
        return True

def delete_book_files():
    """Delete all book content files"""
    books_dir = os.path.join('static', 'books')
    
    if os.path.exists(books_dir):
        try:
            # Delete all files in the directory
            for filename in os.listdir(books_dir):
                file_path = os.path.join(books_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"✓ Deleted all book files from: {books_dir}")
            return True
        except Exception as e:
            print(f"✗ Error deleting book files: {e}")
            return False
    else:
        print("ℹ Books directory not found")
        return True

def run_seed_database():
    """Run the seed_database.py script"""
    print("\nRunning seed_database.py...")
    print("-" * 70)
    
    try:
        result = subprocess.run([sys.executable, 'seed_database.py'], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("-" * 70)
            print("✓ Database seeded successfully")
            return True
        else:
            print("-" * 70)
            print("✗ Error seeding database")
            return False
    except Exception as e:
        print(f"✗ Error running seed_database.py: {e}")
        return False

def run_setup_book_content():
    """Run the setup_book_content.py script"""
    print("\nRunning setup_book_content.py...")
    print("-" * 70)
    
    try:
        result = subprocess.run([sys.executable, 'setup_book_content.py'], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("-" * 70)
            print("✓ Book content downloaded successfully")
            return True
        else:
            print("-" * 70)
            print("✗ Error downloading book content")
            return False
    except Exception as e:
        print(f"✗ Error running setup_book_content.py: {e}")
        return False

def main():
    """Main reset function"""
    print_header("HITEC Library - Complete Database Reset")
    
    # Confirm with user
    if not confirm_reset():
        print("\n❌ Reset cancelled by user")
        return
    
    print()
    print_header("Step 1: Deleting Existing Data")
    
    # Delete database
    db_success = delete_database()
    
    # Delete book files
    books_success = delete_book_files()
    
    if not (db_success and books_success):
        print("\n❌ Failed to delete existing data. Please check errors above.")
        return
    
    print("\n✅ All existing data deleted successfully!")
    
    # Seed database
    print_header("Step 2: Creating New Database")
    
    if not run_seed_database():
        print("\n❌ Failed to create database. Please run manually:")
        print("   python seed_database.py")
        return
    
    # Download book content
    print_header("Step 3: Downloading Book Content")
    
    print("This will download real book content from Project Gutenberg.")
    print("It requires internet connection and takes 2-3 minutes.")
    print()
    
    download = input("Download book content now? (yes/no): ").strip().lower()
    
    if download in ['yes', 'y']:
        if not run_setup_book_content():
            print("\n⚠️  Book content download failed. You can run it later:")
            print("   python setup_book_content.py")
    else:
        print("\n⚠️  Skipped book content download. Run later with:")
        print("   python setup_book_content.py")
    
    # Final summary
    print_header("Reset Complete!")
    
    print("✅ Database has been reset successfully!")
    print()
    print("📊 What was created:")
    print("   • 1 Admin account (username: admin, password: admin123)")
    print("   • 300 Students with library cards")
    print("   • 50 Books in the catalog")
    print("   • Sample loans, reviews, and rental requests")
    if download in ['yes', 'y']:
        print("   • 50 Book content files with real text")
    else:
        print("   • 50 Placeholder book files (run setup_book_content.py)")
    print()
    print("🚀 Start the application:")
    print("   python app.py")
    print()
    print("🌐 Access at: http://127.0.0.1:5000")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Reset cancelled by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
