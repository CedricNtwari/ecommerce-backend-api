# eCommerce Backend API

A scalable eCommerce backend API built with Django Rest Framework, providing robust APIs for product management, user authentication, order processing, and reviews. This backend is designed to be the foundation for a dynamic and user-friendly eCommerce platform.

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

This repository contains the backend for a scalable eCommerce application developed using Django Rest Framework. It includes comprehensive APIs for managing products, users, orders, and reviews. The backend is designed with modularity and scalability in mind, making it a solid foundation for building dynamic and user-friendly eCommerce platforms.

## Features

- User Authentication and Profile Management
- Product Management with Category and Stock Control
- Order Processing with Order Item Management
- Product Reviews and Ratings
- Secure and Optimized API Endpoints

## Technologies Used

- Django
- Django Rest Framework
- PostgreSQL
- Docker (optional for containerization)
- JWT for Authentication
- Git & GitHub for version control

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
   python manage.py runserver
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
