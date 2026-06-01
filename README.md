# Django Mini E-commerce API

A backend-only Mini E-commerce REST API built with Django REST Framework and JWT Authentication.

This project simulates the core backend features of an e-commerce system, including product management, shopping cart, checkout, order workflow, product reviews, and admin reports.

## Features

### Authentication

* User registration
* JWT login and token refresh
* Role-based access using normal users and admin/staff users

### Product Management

* Category CRUD
* Product CRUD
* Public users can view active products
* Admin users can create, update, delete, and manage all products
* Product filtering and searching:

  * Search by product name
  * Filter by category
  * Filter by minimum price
  * Filter by maximum price

### Shopping Cart

* Each user has one cart
* Add products to cart
* Update cart item quantity
* Remove products from cart
* Automatically increase quantity if the same product is added again
* Validate stock before adding products to cart
* Calculate item subtotal and cart total amount

### Checkout and Orders

* Checkout cart into an order
* Create order items from cart items
* Store product name, price, quantity, and subtotal at checkout time
* Calculate total order amount
* Reduce product stock after checkout
* Clear cart after checkout
* Users can view only their own orders
* Admin users can view all orders

### Order Workflow

* Cancel pending orders
* Restore product stock when an order is cancelled
* Admin users can update order status
* Supported order statuses:

  * pending
  * paid
  * shipping
  * completed
  * cancelled
* Prevent updating completed or cancelled orders

### Product Reviews

* Public users can view reviews
* Authenticated users can create reviews
* Users can only review products they have purchased and completed
* Each user can review a product only once
* Review owners can update or delete their own reviews
* Admin users can manage all reviews
* Rating validation from 1 to 5 stars

### Admin Reports

* Admin-only summary report API
* Total orders
* Total revenue from completed orders
* Total products
* Low-stock products
* Total reviews

## Tech Stack

* Python
* Django
* Django REST Framework
* Simple JWT
* SQLite
* Postman
* Git / GitHub

## Main Concepts Practiced

* Django models and migrations
* Relational database design
* ForeignKey and OneToOneField relationships
* Django ORM queries
* Reverse relationships with `related_name`
* Django REST Framework serializers
* ModelViewSet and ViewSet
* Custom actions with `@action`
* JWT authentication
* Role-based permissions
* Object-level permissions
* Business validation
* Query params filtering
* Aggregation with `Sum`
* API testing with Postman
* Git workflow with small feature-based commits

## Database Design / ERD

The ERD image is stored in the `docs` folder.

```markdown
![Mini E-commerce ERD](docs/erd.png)
```

If the image is available in the repository, it will be displayed below:

![Mini E-commerce ERD](docs/erd.png)

## Project Structure

```text
django-mini-ecommerce-api/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│
├── shop/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│
├── docs/
│   └── erd.png
│
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Database Models

### Category

Represents product categories.

Main fields:

* name
* description
* is_active
* created_at

Relationship:

* One category has many products

### Product

Represents products in the shop.

Main fields:

* category
* name
* description
* price
* stock
* is_active
* created_at
* updated_at

Relationship:

* One product belongs to one category
* One product can appear in many cart items
* One product can appear in many order items
* One product can have many reviews

### Cart

Represents the current shopping cart of a user.

Main fields:

* user
* created_at
* updated_at

Relationship:

* One user has one cart
* One cart has many cart items

### CartItem

Represents each product line inside a cart.

Main fields:

* cart
* product
* quantity

Relationship:

* One cart item belongs to one cart
* One cart item refers to one product

### Order

Represents a confirmed order after checkout.

Main fields:

* user
* status
* total_amount
* shipping_address
* phone_number
* note
* created_at
* updated_at

Relationship:

* One user can have many orders
* One order has many order items

### OrderItem

Represents each product line inside an order.

Main fields:

* order
* product
* product_name
* price
* quantity
* subtotal

Important note:

`OrderItem` stores `product_name`, `price`, `quantity`, and `subtotal` separately to preserve purchase history even if product information changes later.

### Review

Represents product reviews.

Main fields:

* user
* product
* rating
* comment
* created_at

Business rules:

* Rating must be from 1 to 5
* A user can review a product only once
* A user can only review products they have purchased and completed

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd django-mini-ecommerce-api
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

On Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

### 7. Run development server

```bash
python manage.py runserver
```

Server will run at:

```text
http://127.0.0.1:8000/
```

## Authentication

### Register

```http
POST /api/register/
```

Example body:

```json
{
  "username": "user1",
  "password": "user1123456"
}
```

### Login

```http
POST /api/token/
```

Example body:

```json
{
  "username": "user1",
  "password": "user1123456"
}
```

Example response:

```json
{
  "refresh": "your_refresh_token",
  "access": "your_access_token"
}
```

Use the access token for protected APIs:

```http
Authorization: Bearer <access_token>
```

### Refresh Token

```http
POST /api/token/refresh/
```

Example body:

```json
{
  "refresh": "your_refresh_token"
}
```

## API Endpoints

### Auth

```http
POST /api/register/
POST /api/token/
POST /api/token/refresh/
```

### Categories

```http
GET    /api/categories/
POST   /api/categories/
GET    /api/categories/{id}/
PATCH  /api/categories/{id}/
DELETE /api/categories/{id}/
```

Permission rules:

* Anyone can view categories
* Only admin/staff users can create, update, or delete categories

### Products

```http
GET    /api/products/
POST   /api/products/
GET    /api/products/{id}/
PATCH  /api/products/{id}/
DELETE /api/products/{id}/
```

Permission rules:

* Anyone can view active products
* Admin/staff users can manage all products
* Normal users cannot create, update, or delete products

Product filters:

```http
GET /api/products/?search=macbook
GET /api/products/?category=1
GET /api/products/?min_price=10000000
GET /api/products/?max_price=30000000
GET /api/products/?category=1&min_price=10000000&max_price=35000000
```

### Cart

```http
GET /api/cart/my-cart/
```

Cart item APIs:

```http
POST   /api/cart/items/
PATCH  /api/cart/items/{id}/
DELETE /api/cart/items/{id}/
```

Example add item to cart:

```json
{
  "product": 1,
  "quantity": 2
}
```

Business rules:

* User must be authenticated
* Each user has one cart
* If the same product already exists in the cart, quantity is increased
* Quantity cannot exceed product stock
* Quantity must be greater than 0

### Orders

```http
GET  /api/orders/
GET  /api/orders/{id}/
POST /api/orders/checkout/
```

Example checkout body:

```json
{
  "shipping_address": "Hanoi, Vietnam",
  "phone_number": "0123456789",
  "note": "Deliver in the evening"
}
```

Business rules:

* User must be authenticated
* User can only view their own orders
* Admin/staff users can view all orders
* Cart must not be empty
* Product stock is checked before checkout
* Product stock is reduced after checkout
* Cart items are cleared after checkout
* Orders are created with `pending` status by default

### Order Status

Cancel order:

```http
PATCH /api/orders/{id}/cancel/
```

Business rules:

* Users can cancel only their own orders
* Only pending orders can be cancelled
* Product stock is restored when an order is cancelled

Admin update order status:

```http
PATCH /api/orders/{id}/update-status/
```

Example body:

```json
{
  "status": "shipping"
}
```

Permission rules:

* Only admin/staff users can update order status

Valid statuses:

```text
pending
paid
shipping
completed
cancelled
```

### Reviews

```http
GET    /api/reviews/
POST   /api/reviews/
GET    /api/reviews/{id}/
PATCH  /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

Filter reviews by product:

```http
GET /api/reviews/?product=1
```

Example create review:

```json
{
  "product": 1,
  "rating": 5,
  "comment": "Good product"
}
```

Business rules:

* Anyone can view reviews
* Only authenticated users can create reviews
* Users can only review products they have purchased and completed
* Each user can review a product only once
* Review owners can update or delete their own reviews
* Admin/staff users can update or delete all reviews

### Reports

Admin report summary:

```http
GET /api/reports/summary/
```

Example response:

```json
{
  "total_orders": 10,
  "total_revenue": "15000000.00",
  "total_products": 20,
  "low_stock_products": 3,
  "total_reviews": 8
}
```

Permission rules:

* Only admin/staff users can access report APIs

## Example Workflow

### 1. Admin creates category

```http
POST /api/categories/
```

```json
{
  "name": "Laptop",
  "description": "Laptop products",
  "is_active": true
}
```

### 2. Admin creates product

```http
POST /api/products/
```

```json
{
  "category": 1,
  "name": "MacBook Pro M2",
  "description": "Apple laptop with M2 chip",
  "price": "30000000.00",
  "stock": 5,
  "is_active": true
}
```

### 3. User adds product to cart

```http
POST /api/cart/items/
```

```json
{
  "product": 1,
  "quantity": 1
}
```

### 4. User checks out

```http
POST /api/orders/checkout/
```

```json
{
  "shipping_address": "Hanoi, Vietnam",
  "phone_number": "0123456789",
  "note": "Deliver in the evening"
}
```

### 5. Admin updates order to completed

```http
PATCH /api/orders/1/update-status/
```

```json
{
  "status": "completed"
}
```

### 6. User reviews purchased product

```http
POST /api/reviews/
```

```json
{
  "product": 1,
  "rating": 5,
  "comment": "Good product"
}
```

### 7. Admin views report

```http
GET /api/reports/summary/
```

## Business Rules Summary

* Users can only manage their own cart
* Users can only view their own orders
* Admin users can manage categories and products
* Admin users can view all orders
* Admin users can update order status
* Product stock is validated before adding to cart and before checkout
* Product stock is reduced after successful checkout
* Product stock is restored when a pending order is cancelled
* Users can only review completed purchased products
* Each user can review a product only once
* Completed or cancelled orders cannot be updated again

## Git Workflow

This project was developed using small feature-based commits, such as:

```text
Setup Django mini ecommerce API project with JWT
Add ecommerce models
Add serializers for ecommerce API
Add category and product APIs
Add cart APIs with stock validation
Add checkout and order APIs
Add order cancellation API
Add admin order status update API
Add product review APIs
Add review permissions and validation
Add admin report summary API
Add README documentation
```

## Future Improvements

* Add pagination
* Add product image upload
* Add payment simulation
* Add order history filters
* Add monthly revenue report
* Add PostgreSQL support
* Add Docker configuration
* Add deployment
* Add automated tests
* Add API documentation with Swagger or drf-spectacular

## CV Description

Mini E-commerce API — Django REST Framework

* Built a backend-only Mini E-commerce REST API using Django REST Framework and JWT Authentication.
* Designed relational models for categories, products, carts, cart items, orders, order items, and reviews.
* Implemented product management, shopping cart, checkout workflow, order status management, product reviews, and admin reports.
* Added role-based permissions for normal users and admin users.
* Implemented business validations such as stock checking, order cancellation rules, purchase-based reviews, and one-review-per-product rule.
* Used Django ORM for filtering, relationship queries, and aggregation reports.
* Tested all APIs with Postman and managed source code using Git/GitHub.
