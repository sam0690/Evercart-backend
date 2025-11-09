"""
Seed script to populate the database with dummy data
Run with: python manage.py shell < seed_data.py
Or create a management command
"""
import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductImage
from orders.models import CartItem, Order, OrderItem
from payments.models import Payment

User = get_user_model()

def clear_data():
    """Clear existing data"""
    print("Clearing existing data...")
    Payment.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    CartItem.objects.all().delete()
    ProductImage.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    print("✓ Data cleared")

def create_users():
    """Create dummy users"""
    print("\nCreating users...")
    users = []
    
    # Create customers
    customers_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'bob_johnson', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Johnson'},
        {'username': 'alice_williams', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Williams'},
        {'username': 'charlie_brown', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Brown'},
        {'username': 'diana_prince', 'email': 'diana@example.com', 'first_name': 'Diana', 'last_name': 'Prince'},
        {'username': 'evan_davis', 'email': 'evan@example.com', 'first_name': 'Evan', 'last_name': 'Davis'},
        {'username': 'fiona_miller', 'email': 'fiona@example.com', 'first_name': 'Fiona', 'last_name': 'Miller'},
    ]
    
    for data in customers_data:
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password='password123',
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_customer=True,
            is_admin=False
        )
        users.append(user)
        print(f"  ✓ Created customer: {user.username}")
    
    # Create staff member
    staff = User.objects.create_user(
        username='staff_user',
        email='staff@example.com',
        password='password123',
        first_name='Staff',
        last_name='Member',
        is_customer=False,
        is_admin=False,
        is_staff=True
    )
    users.append(staff)
    print(f"  ✓ Created staff: {staff.username}")
    
    return users

def create_categories():
    """Create product categories"""
    print("\nCreating categories...")
    categories_data = [
        {'name': 'Electronics', 'slug': 'electronics'},
        {'name': 'Clothing', 'slug': 'clothing'},
        {'name': 'Books', 'slug': 'books'},
        {'name': 'Home & Garden', 'slug': 'home-garden'},
        {'name': 'Sports & Outdoors', 'slug': 'sports-outdoors'},
        {'name': 'Toys & Games', 'slug': 'toys-games'},
        {'name': 'Health & Beauty', 'slug': 'health-beauty'},
        {'name': 'Food & Beverages', 'slug': 'food-beverages'},
    ]
    
    categories = []
    for data in categories_data:
        category = Category.objects.create(**data)
        categories.append(category)
        print(f"  ✓ Created category: {category.name}")
    
    return categories

def create_products(categories):
    """Create dummy products with images"""
    print("\nCreating products...")
    
    products_data = [
        # Electronics
        {'title': 'Wireless Bluetooth Headphones', 'category': 'Electronics', 'price': 4500, 'inventory': 50, 'image': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500'},
        {'title': 'Smart Watch Pro', 'category': 'Electronics', 'price': 12000, 'inventory': 30, 'image': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500'},
        {'title': 'USB-C Fast Charger', 'category': 'Electronics', 'price': 1500, 'inventory': 100, 'image': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500'},
        {'title': 'Portable Power Bank 20000mAh', 'category': 'Electronics', 'price': 3200, 'inventory': 75, 'image': 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500'},
        {'title': 'Wireless Mouse', 'category': 'Electronics', 'price': 800, 'inventory': 60, 'image': 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=500'},
        {'title': 'Mechanical Keyboard RGB', 'category': 'Electronics', 'price': 5500, 'inventory': 40, 'image': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500'},
        {'title': 'HD Webcam 1080p', 'category': 'Electronics', 'price': 3500, 'inventory': 35, 'image': 'https://images.unsplash.com/photo-1565105077481-5876641c8db3?w=500'},
        {'title': 'Bluetooth Speaker', 'category': 'Electronics', 'price': 2800, 'inventory': 55, 'image': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500'},
        
        # Clothing
        {'title': 'Cotton T-Shirt (Black)', 'category': 'Clothing', 'price': 800, 'inventory': 120, 'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500'},
        {'title': 'Denim Jeans Classic Fit', 'category': 'Clothing', 'price': 2500, 'inventory': 80, 'image': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500'},
        {'title': 'Running Shoes Sport Edition', 'category': 'Clothing', 'price': 4200, 'inventory': 45, 'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500'},
        {'title': 'Hooded Sweatshirt', 'category': 'Clothing', 'price': 1800, 'inventory': 65, 'image': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500'},
        {'title': 'Casual Sneakers', 'category': 'Clothing', 'price': 3500, 'inventory': 50, 'image': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=500'},
        {'title': 'Winter Jacket Warm', 'category': 'Clothing', 'price': 6500, 'inventory': 30, 'image': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500'},
        {'title': 'Sports Shorts', 'category': 'Clothing', 'price': 900, 'inventory': 90, 'image': 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500'},
        
        # Books
        {'title': 'The Art of Programming', 'category': 'Books', 'price': 1200, 'inventory': 40, 'image': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=500'},
        {'title': 'Python for Beginners', 'category': 'Books', 'price': 950, 'inventory': 55, 'image': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=500'},
        {'title': 'Web Development Guide', 'category': 'Books', 'price': 1500, 'inventory': 35, 'image': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500'},
        {'title': 'Data Science Handbook', 'category': 'Books', 'price': 1800, 'inventory': 25, 'image': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=500'},
        {'title': 'Fiction Novel Collection', 'category': 'Books', 'price': 800, 'inventory': 70, 'image': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500'},
        
        # Home & Garden
        {'title': 'LED Desk Lamp Adjustable', 'category': 'Home & Garden', 'price': 1500, 'inventory': 45, 'image': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500'},
        {'title': 'Coffee Maker Machine', 'category': 'Home & Garden', 'price': 5500, 'inventory': 20, 'image': 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500'},
        {'title': 'Air Purifier HEPA Filter', 'category': 'Home & Garden', 'price': 8500, 'inventory': 15, 'image': 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500'},
        {'title': 'Kitchen Knife Set', 'category': 'Home & Garden', 'price': 3200, 'inventory': 30, 'image': 'https://images.unsplash.com/photo-1593618998160-e34014e67546?w=500'},
        {'title': 'Indoor Plant Pot Set', 'category': 'Home & Garden', 'price': 1200, 'inventory': 60, 'image': 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=500'},
        
        # Sports & Outdoors
        {'title': 'Yoga Mat Premium', 'category': 'Sports & Outdoors', 'price': 1800, 'inventory': 50, 'image': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500'},
        {'title': 'Dumbbell Set 20kg', 'category': 'Sports & Outdoors', 'price': 4500, 'inventory': 25, 'image': 'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=500'},
        {'title': 'Resistance Bands Kit', 'category': 'Sports & Outdoors', 'price': 1200, 'inventory': 70, 'image': 'https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=500'},
        {'title': 'Camping Tent 4-Person', 'category': 'Sports & Outdoors', 'price': 12000, 'inventory': 10, 'image': 'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=500'},
        {'title': 'Water Bottle Insulated', 'category': 'Sports & Outdoors', 'price': 800, 'inventory': 100, 'image': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500'},
        
        # Toys & Games
        {'title': 'Board Game Classic Edition', 'category': 'Toys & Games', 'price': 2500, 'inventory': 35, 'image': 'https://images.unsplash.com/photo-1632501641765-e568d28b0015?w=500'},
        {'title': 'Puzzle 1000 Pieces', 'category': 'Toys & Games', 'price': 1200, 'inventory': 45, 'image': 'https://images.unsplash.com/photo-1587334206039-022cbc7c2b3c?w=500'},
        {'title': 'Remote Control Car', 'category': 'Toys & Games', 'price': 3500, 'inventory': 20, 'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500'},
        {'title': 'Building Blocks Set', 'category': 'Toys & Games', 'price': 1800, 'inventory': 55, 'image': 'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=500'},
        
        # Health & Beauty
        {'title': 'Face Cream Moisturizer', 'category': 'Health & Beauty', 'price': 1500, 'inventory': 60, 'image': 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=500'},
        {'title': 'Hair Dryer Professional', 'category': 'Health & Beauty', 'price': 3200, 'inventory': 30, 'image': 'https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=500'},
        {'title': 'Electric Toothbrush', 'category': 'Health & Beauty', 'price': 2800, 'inventory': 40, 'image': 'https://images.unsplash.com/photo-1607613009820-a29f7bb81c04?w=500'},
        {'title': 'Vitamin C Serum', 'category': 'Health & Beauty', 'price': 1800, 'inventory': 50, 'image': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500'},
        
        # Food & Beverages
        {'title': 'Organic Green Tea 100g', 'category': 'Food & Beverages', 'price': 450, 'inventory': 150, 'image': 'https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=500'},
        {'title': 'Dark Chocolate Bar Pack', 'category': 'Food & Beverages', 'price': 600, 'inventory': 120, 'image': 'https://images.unsplash.com/photo-1511381939415-e44015466834?w=500'},
        {'title': 'Honey Pure Natural 500g', 'category': 'Food & Beverages', 'price': 800, 'inventory': 80, 'image': 'https://images.unsplash.com/photo-1587049352846-4a222e784773?w=500'},
        {'title': 'Protein Powder 1kg', 'category': 'Food & Beverages', 'price': 3500, 'inventory': 40, 'image': 'https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=500'},
    ]
    
    products = []
    category_map = {cat.name: cat for cat in categories}
    
    descriptions = [
        "High-quality product with excellent features and durability.",
        "Premium grade item perfect for daily use.",
        "Best seller with outstanding customer reviews.",
        "Eco-friendly and sustainable choice.",
        "Latest model with advanced technology.",
        "Affordable yet reliable product.",
        "Imported quality with warranty included.",
        "Popular choice among customers."
    ]
    
    for data in products_data:
        category = category_map[data['category']]
        product = Product.objects.create(
            title=data['title'],
            slug=data['title'].lower().replace(' ', '-').replace('(', '').replace(')', ''),
            description=random.choice(descriptions),
            price=Decimal(str(data['price'])),
            inventory=data['inventory'],
            category=category
        )
        
        # Create ProductImage with the image URL
        ProductImage.objects.create(
            product=product,
            image=data['image'],
            alt_text=data['title'],
            is_primary=True
        )
        
        products.append(product)
        print(f"  ✓ Created product: {product.title} (with image)")
    
    return products

def create_orders(users, products):
    """Create dummy orders"""
    print("\nCreating orders...")
    
    orders = []
    statuses = ['pending', 'paid', 'shipped']
    
    # Create 20 orders
    for i in range(20):
        user = random.choice([u for u in users if u.is_customer])
        status = random.choice(statuses)
        
        order = Order.objects.create(
            user=user,
            status=status,
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        
        # Add 1-5 items to each order
        num_items = random.randint(1, 5)
        order_total = Decimal('0')
        
        selected_products = random.sample(products, num_items)
        for product in selected_products:
            quantity = random.randint(1, 3)
            price = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
            order_total += price * quantity
        
        order.total = order_total
        order.save()
        orders.append(order)
        
        print(f"  ✓ Created order #{order.id} for {user.username} - Total: NPR {order_total}")
    
    return orders

def create_payments(orders):
    """Create payment records for orders"""
    print("\nCreating payments...")
    
    gateways = ['esewa', 'khalti', 'fonepay']
    
    for order in orders:
        if order.status in ['paid', 'shipped']:
            gateway = random.choice(gateways)
            payment = Payment.objects.create(
                user=order.user,
                order=order,
                amount=order.total,
                method=gateway,
                status='success',
                ref_id=f"TXN{random.randint(100000, 999999)}"
            )
            print(f"  ✓ Created payment for Order #{order.id} via {gateway}")

def create_cart_items(users, products):
    """Create cart items for some users"""
    print("\nCreating cart items...")
    
    # Create cart items for 5 random customers
    cart_users = random.sample([u for u in users if u.is_customer], min(5, len([u for u in users if u.is_customer])))
    
    for user in cart_users:
        # Add 1-3 products to cart
        num_items = random.randint(1, 3)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            quantity = random.randint(1, 2)
            CartItem.objects.create(
                user=user,
                product=product,
                quantity=quantity
            )
        
        print(f"  ✓ Created cart items for {user.username}")

def main():
    """Main seed function"""
    print("=" * 50)
    print("SEEDING DATABASE WITH DUMMY DATA")
    print("=" * 50)
    
    clear_data()
    users = create_users()
    categories = create_categories()
    products = create_products(categories)
    orders = create_orders(users, products)
    create_payments(orders)
    create_cart_items(users, products)
    
    print("\n" + "=" * 50)
    print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print(f"\n📊 Summary:")
    print(f"  • Users: {User.objects.count()}")
    print(f"  • Categories: {Category.objects.count()}")
    print(f"  • Products: {Product.objects.count()}")
    print(f"  • Orders: {Order.objects.count()}")
    print(f"  • Order Items: {OrderItem.objects.count()}")
    print(f"  • Payments: {Payment.objects.count()}")
    print(f"  • Cart Items: {CartItem.objects.count()}")
    print(f"\n✅ You can now login with:")
    print(f"  Username: john_doe (or any customer username)")
    print(f"  Password: password123")
    print(f"\n🔐 Admin account:")
    print(f"  Username: sam_0690")
    print(f"  Password: admin123")

if __name__ == '__main__':
    main()
