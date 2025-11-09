#!/bin/bash

# EverCart Backend Setup Script
# This script sets up the Django backend for development

echo "======================================"
echo "EverCart Backend Setup"
echo "======================================"
echo ""

# Check if in correct directory
if [ ! -f "manage.py" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# Step 1: Create virtual environment (optional but recommended)
echo "Step 1: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Step 2: Activate virtual environment
echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Step 3: Install dependencies
echo ""
echo "Step 3: Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Step 4: Create media directory
echo ""
echo "Step 4: Creating media directories..."
mkdir -p media/products
echo "✓ Media directories created"

# Step 5: Run migrations
echo ""
echo "Step 5: Running database migrations..."
python manage.py makemigrations
python manage.py migrate
echo "✓ Database migrations completed"

# Step 6: Create superuser
echo ""
echo "Step 6: Create superuser account..."
echo "You'll be prompted to create an admin account:"
python manage.py createsuperuser

# Step 7: Load sample data (optional)
echo ""
echo "======================================"
echo "Setup Complete! 🎉"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "2. Access the admin panel:"
echo "   http://localhost:8000/admin/"
echo ""
echo "3. API endpoints are available at:"
echo "   http://localhost:8000/api/"
echo ""
echo "4. Check API_DOCUMENTATION.md for endpoint details"
echo ""
echo "5. To deactivate virtual environment:"
echo "   deactivate"
echo ""
