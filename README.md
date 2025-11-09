# EverCart Backend

Django REST Framework-based eCommerce backend with eSewa, Khalti, and Fonepay payment integrations.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Run the setup script:**

   ```bash
   cd backend
   ./setup.sh
   ```

2. **Or manually:**

   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Create media directory
   mkdir -p media/products

   # Run migrations
   python manage.py makemigrations
   python manage.py migrate

   # Create superuser
   python manage.py createsuperuser

   # Start server
   python manage.py runserver
   ```

3. **Access:**
   - Admin Panel: http://localhost:8000/admin/
   - API Root: http://localhost:8000/api/

## 📁 Project Structure

```
backend/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── setup.sh                     # Setup script
├── API_DOCUMENTATION.md         # API endpoint documentation
├── REVIEW_AND_FIXES.md         # Comprehensive review
├── ecommerce/                   # Main project folder
│   ├── settings.py             # Project settings
│   └── urls.py                 # Main URL configuration
├── users/                       # Authentication & user management
│   ├── models.py               # CustomUser model
│   ├── serializers.py          # User serializers
│   ├── views.py                # Auth views (register, login, etc.)
│   └── urls.py                 # User endpoints
├── products/                    # Product catalog
│   ├── models.py               # Product, Category, ProductImage
│   ├── serializers.py          # Product serializers
│   ├── views.py                # Product viewsets
│   └── urls.py                 # Product endpoints
├── orders/                      # Cart & order management
│   ├── models.py               # CartItem, Order, OrderItem
│   ├── serializers.py          # Order serializers
│   ├── views.py                # Cart & order views
│   └── urls.py                 # Order endpoints
└── payments/                    # Payment gateway integrations
    ├── models.py               # Payment model
    ├── serializers.py          # Payment serializers
    ├── views.py                # Payment initiation & verification
    ├── urls.py                 # Payment endpoints
    └── utils.py                # Payment verification helpers
```

## 🔧 Configuration

### Database

- **Development:** SQLite (default)
- **Location:** `db.sqlite3` in project root

### Authentication

- **Method:** JWT (JSON Web Tokens)
- **Library:** djangorestframework-simplejwt
- **Access Token:** 30 minutes
- **Refresh Token:** 7 days (stored in HttpOnly cookie)

### Media Files

- **Products:** `media/products/`
- **URL:** `/media/`

### CORS

Configured for Next.js frontend:

- http://localhost:3000
- http://127.0.0.1:3000

## 📡 API Endpoints

### Authentication

- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - Login
- `POST /api/users/refresh/` - Refresh access token
- `POST /api/users/logout/` - Logout

### Products

- `GET /api/products/products/` - List products
- `GET /api/products/products/{id}/` - Product detail
- `GET /api/products/categories/` - List categories
- `GET /api/products/categories/{id}/` - Category detail

### Orders

- `GET /api/orders/cart/` - View cart
- `POST /api/orders/cart/` - Add to cart
- `PUT /api/orders/cart/{id}/` - Update cart item
- `DELETE /api/orders/cart/{id}/` - Remove from cart
- `POST /api/orders/create-from-cart/` - Create order

### Payments

- `POST /api/payments/initiate/` - Initiate payment
- `GET /api/payments/esewa-verify/` - eSewa verification
- `POST /api/payments/khalti-verify/` - Khalti verification
- `GET /api/payments/fonepay-verify/` - Fonepay verification

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed usage.

## 💳 Payment Gateways

### eSewa

- **Environment:** Test/UAT
- **Merchant ID:** EPAYTEST
- **Verification:** Server-side callback

### Khalti

- **Environment:** Test
- **Integration:** Widget-based (frontend)
- **Verification:** Backend API call

### Fonepay

- **Environment:** Development
- **Security:** Checksum-based
- **Verification:** Server-side callback

## 🛠️ Development

### Add Sample Data

```bash
python manage.py shell
```

```python
from products.models import Category, Product
from django.contrib.auth import get_user_model

# Create category
cat = Category.objects.create(name="Electronics", slug="electronics")

# Create product
Product.objects.create(
    title="Smartphone X",
    slug="smartphone-x",
    description="Amazing phone",
    price=999.99,
    inventory=50,
    category=cat
)
```

### Run Tests

```bash
python manage.py test
```

### Make Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

## 📦 Dependencies

Key packages:

- Django 5.2.5
- djangorestframework 3.16.1
- djangorestframework-simplejwt 5.5.1
- django-cors-headers 4.7.0
- Pillow 11.0.0 (for image handling)
- requests 2.32.4 (for payment verification)

See [requirements.txt](./requirements.txt) for full list.

## 🔒 Security Notes

### Before Production:

1. Move `SECRET_KEY` to environment variable
2. Set `DEBUG = False`
3. Update `ALLOWED_HOSTS`
4. Enable HTTPS (set `CORS_ALLOW_CREDENTIALS` with `secure=True`)
5. Use production payment gateway credentials
6. Add rate limiting
7. Configure proper CSRF settings
8. Set up database backups

## 📝 Models Overview

### CustomUser (users)

- Extends Django's AbstractUser
- Unique email field
- Used for authentication

### Product (products)

- Title, slug, description
- Price (Decimal)
- Inventory tracking
- Category relationship
- Multiple images support

### Category (products)

- Name and slug
- Related to products

### CartItem (orders)

- User-specific cart
- Product reference
- Quantity
- Unique together: (user, product)

### Order (orders)

- User reference
- Total amount
- Status: pending/paid/shipped
- Contains OrderItems

### OrderItem (orders)

- Order reference
- Product snapshot
- Quantity and price at purchase

### Payment (payments)

- User and Order reference
- Payment method (esewa/khalti/fonepay)
- Amount and reference ID
- Status tracking

## 🤝 Contributing

1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

[Add your license here]

## 📞 Support

For issues or questions, please refer to:

- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- [REVIEW_AND_FIXES.md](./REVIEW_AND_FIXES.md)

---

**Built with Django REST Framework for EverCart** 🛒

# Evercart-backend