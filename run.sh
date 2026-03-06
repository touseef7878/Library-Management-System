#!/bin/bash

# HiTec University Library - Quick Start Script

echo "🚀 HiTec University Library Management System"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Create database directory
mkdir -p database

echo ""
echo "✨ Starting HiTec University Library..."
echo "=============================================="
echo ""
echo "📍 Access the application at: http://localhost:5000"
echo "🔐 Admin Panel: http://localhost:5000/admin/login"
echo "👤 Default Admin: username=admin, password=admin123"
echo ""
echo "⚠️  Change the default password after first login!"
echo ""
echo "=============================================="
echo ""

# Run the application
python app.py
