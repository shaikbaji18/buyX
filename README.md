buyX - Mobile E-Commerce Platform
buyX is a full-featured Django-based e-commerce platform specifically designed for selling mobile phones online. It supports two user types: customers and distributors, with separate interfaces and functionalities.

🛠 Technology Stack
Backend: Django 6.0.2 (Python)
Database: SQLite3
Frontend: HTML5, CSS3, JavaScript
Email: Gmail SMTP
SMS: Twilio API integration
✨ Key Features
For Customers:
📱 Product Browsing: Browse mobile phones with brand filtering and search
🛒 Shopping Cart: Add multiple products, update quantities, manage cart
💳 Checkout: Complete with delivery details and live location coordinates
💰 Payment: Cash on Delivery (COD) option
📦 Order Tracking: Track orders with unique order IDs
⭐ Reviews & Ratings: Rate and review products
🛍️ Buy Now: Direct purchase for single products
📧 Email Notifications: Welcome emails and order confirmations
For Distributors:
📊 Dashboard: View products, orders, and sales statistics
➕ Product Management: Add, edit, and delete mobile products
📝 Product Details: Brand selection, multiple images (up to 4), pricing with discount, technical specifications, stock management
📦 Order Management: View and update order status
🏗️ Project Structure

buyX/
├── Mobiles/          # Django project settings
├── user/             # Customer app (models, views, urls)
├── distibutor/       # Distributor app (models, views, urls)
├── templates/        # HTML templates (user & distributor)
├── static/          # CSS and JavaScript files
└── media/           # Product images
📱 Supported Brands
Apple, Samsung, OnePlus, Xiaomi, Realme, Vivo, Oppo, Motorola, Nokia

🔧 Configuration
Email notification via Gmail SMTP
Twilio SMS integration for order updates
Custom user model with phone-based authentication
Session-based "Buy Now" functionality
JSONField for product specifications
