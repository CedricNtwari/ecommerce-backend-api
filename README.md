# eCommerce Backend API

**Slogan:** Empowering Digital Commerce with Scalable APIs

Welcome to the backend of TradeCorner, a robust and scalable eCommerce platform built with Django Rest Framework. This API serves as the foundation for product management, user authentication, order processing, and reviews, ensuring seamless and secure transactions.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Database Schema](#database-schema)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Test Covarage](#test-coverage)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Contact](#contact)

## Project Overview

**TradeCorner** provides an eCommerce backend built using Django Rest Framework (DRF). This API offers a modular structure allowing flexibility and scalability, making it ideal for building dynamic online stores.

Whether you are managing user profiles, handling orders, or managing product inventory, this API ensures optimized performance and secure transactions.

## Features

- **User Authentication and Profile Management:** Secure user authentication using JWT with profile customization.
- **Product Management:** Add, update, and manage products, categories, and stock control.
- **Order Management:** Process orders with full support for order items and order history.
- **Review System:** Users can leave reviews and rate products.
- **Optimized API Endpoints:** Well-structured, secured, and optimized for performance.
- **Search and Filtering:** Advanced search and filter functionalities across orders and products.
- **Email Notifications:** Integrated email services for order confirmations and alerts.

## Technologies Used

- **Django:** Web framework for rapid development.
- **Django Rest Framework (DRF):** API development framework.
- **PostgreSQL:** Relational database management system.
- **JWT:** Token-based authentication for secure API calls.
- **Git & GitHub:** Version control and project management.

## Database Schema

Below is the Entity Relationship Diagram (ERD) that illustrates the database schema used in this eCommerce backend:

![Entity Relationship Diagram](/assets/erd_ecommerce.png)

This diagram shows the relationships and fields within our database, crucial for understanding how data is managed and maintained.

### Diagram Description

- **User:** Represents a user in the system. Each user has a unique profile and cart.
- **Profile:** Contains additional information about the user, such as their name, address, phone number, and profile picture.
- **Product:** Represents a product in the inventory. Each product has details such as name, description, price, stock quantity, and an image. It also includes an optional image filter for visual effects.
- **Order:** Represents an order placed by a user. Each order has a total price and status.
- **OrderItem:** Represents the individual items in an order. Each item is linked to an order and a product and includes the quantity and price of the product.
- **Review:** Represents a review for a product written by a user. Each review includes a rating and a comment.
- **Cart:** Represents a shopping cart belonging to a user. Each cart is unique to a user and contains multiple cart items.
- **CartItem:** Represents individual items in a cart. Each item is linked to a cart and a product and includes the quantity and price of the product.

## Getting Started

### Prerequisites

- Python 3.x
- pip (Python package installer)
- PostgreSQL
- Virtualenv (recommended)

### Installation

1. **Clone the repo**

   ```sh
   git clone https://github.com/CedricNtwari/ecommerce-backend-api.git
   cd ecommerce-backend
   ```

2. **Install the required packages**

   ```sh
   pip install -r requirements.txt
   ```

3. **Set up the PostgreSQL database**

   Create a new PostgreSQL database and user, then update the DATABASES setting in settings.py with your database credentials.

4. **Apply migrations**

   ```sh
   python manage.py migrate
   ```

5. **Create a superuser**

   ```sh
   python manage.py createsuperuser
   ```

6. **Running the Application**

   ```sh
   python manage.py runserver
   ```

## API Endpoints

### Authentication

- `POST /dj-rest-auth/login/`: Login a user
- `POST /dj-rest-auth/logout/`: Logout a user
- `POST /dj-rest-auth/password/reset/`: Reset user password
- `POST /dj-rest-auth/password/reset/confirm/`: Confirm password reset
- `POST /dj-rest-auth/password/change/`: Change user password
- `POST /dj-rest-auth/registration/verify-email/`: Email Verification
- `GET /dj-rest-auth/user/`: User Details

### Registration

- `POST /dj-rest-auth/registration/`: Register a new user
- `POST /dj-rest-auth/registration/verify-email/`: Verify user email

### User Profiles

- `GET /profiles/`: List all profiles
- `GET /profiles/:id/`: Retrieve a specific profile
- `PUT /profiles/:id/`: Update a profile
- `DELETE /profiles/:id/`: Delete a profile
- `DELETE /dj-rest-auth/user/`: Retrieve authenticated user details

### Contact Form Submission

- `POST /contact/`: Submit a contact form with name, email, and message. Sends an email to the administrator upon successful submission.

### Products Management

- `GET /products/`: List all products
- `GET /products/:id/`: Retrieve a specific product
- `POST /products/`: Create a new product
- `PUT /products/:id/`: Update a product
- `DELETE /products/:id/`: Delete a product

### Order Management

- `GET /orders/` : List all orders (admin only)
- `POST /orders/`: Create a new order
- `GET /orders/{id}/`: Retrieve an order by ID
- `PUT /orders/{id}/`: Update an order by ID
- `DELETE /orders/{id}/`: Delete an order by ID (admin only)
- `POST /orders/{id}/cancel/`: Cancel an order by ID
- `POST /orders/{id}/add_item/`: Add an item to an order
- `GET /order-items/` : to list all OrderItem objects
- `POST /order-items/` : to create a new OrderItem
- `PUT /order-items/<id>/` : to update an existing OrderItem
- `DELETE /order-items/<id>/` : to delete an OrderItem

### Order History

- `GET /order-history/`: List user personal orders

### Search and Filter Endpoints

- `GET /orders/?search={query}`: Search orders by order number, owner username, or status

  - Example: `GET /orders/?search=22861A5D5B2043A8B8E0`
  - Example: `GET /orders/?search=haydee`
  - Example: `GET /orders/?search=Pending`

- `GET /orders/?order_number={order_number}&owner__username={owner_username}&status={status}&total_price={total_price}`: Filter orders by order number, owner username, status, or total price
  - Example: `GET /orders/?order_number=22861A5D5B2043A8B8E0`
  - Example: `GET /orders/?owner__username=haydee`
  - Example: `GET /orders/?status=Pending`
  - Example: `GET /orders/?total_price=100.00`

### Cart Management

- `GET /carts/` : List all carts (admin only)
- `POST /carts/`: Create a new cart
- `GET /carts/{id}/`: Retrieve a cart by ID
- `PUT /carts/{id}/`: Update a cart by ID
- `DELETE /carts/{id}/`: Delete a cart by ID (admin only)
- `POST /carts/{id}/add_item/`: Add an item to a cart
- `POST /carts/{id}/remove_item/`: Remove an item from a cart
- `POST /carts/{id}/update_quantity/`: Update quantity of an item in a cart

### Reviews management

- `GET /reviews/`: List all reviews
- `GET /reviews/:id/`: Retrieve a specific review
- `POST /reviews/`: Create a new review
- `PUT /reviews/:id/`: Update a review
- `DELETE /reviews/:id/`: Delete a review

### Checkout session

- `POST /reviewsreate-checkout-session/`: Create a new checkout session with Stripe

## Test Coverage

To ensure the stability and reliability of the application. I use the `coverage` tool to measure how much of the codebase is covered by automated tests. This helps identify areas that may need more testing and ensures that our code is well-tested.

As of the latest run, our test coverage is as follows:

- **Overall Coverage**: 94%

![Overall Coverage](/assets/coverage-.png)
![Overall Coverage](/assets/coverage.png)

## Documentation

This section provides a brief introduction to the detailed document that outlines the application's current features and future plans.
Here: https://docs.google.com/document/d/1wJ9-2GjuKNl_PyEiLAbfdFzHOBG6qeboLvMXuAyu3TY/edit?usp=sharing

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (git checkout -b feature/AmazingFeature)
3. Commit your Changes (git commit -m 'Add some AmazingFeature')
4. Push to the Branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## Contact

Cedric Ntwari - @CedricNtwari - ntwaricedric@gmail.com

Project Link: "https://ecommerce-backend-api-1-abe8f24df824.herokuapp.com/".
