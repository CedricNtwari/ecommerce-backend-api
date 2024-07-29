# eCommerce Backend API

A scalable eCommerce backend API built with Django Rest Framework, providing robust APIs for product management, user authentication, order processing, and reviews. This backend is designed to be the foundation for a dynamic and user-friendly eCommerce platform.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
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

- `POST /api/auth/login/`: Login a user
- `POST /api/auth/register/`: Register a new user
- `POST /api/auth/logout/`: Logout a user

### User Profiles

- `GET /api/profiles/`: List all profiles
- `GET /api/profiles/:id/`: Retrieve a specific profile
- `PUT /api/profiles/:id/`: Update a profile
- `DELETE /api/profiles/:id/`: Delete a profile

### Products Management

- `GET /api/products/`: List all products
- `GET /api/products/:id/`: Retrieve a specific product
- `POST /api/products/`: Create a new product
- `PUT /api/products/:id/`: Update a product
- `DELETE /api/products/:id/`: Delete a product

### Order Management

- `GET /orders/` : List all orders (admin only)
- `POST /orders/`: Create a new order
- `GET /orders/{id}/`: Retrieve an order by ID
- `PUT /orders/{id}/`: Update an order by ID
- `DELETE /orders/{id}/`: Delete an order by ID (admin only)
- `POST /orders/{id}/cancel/`: Cancel an order by ID
- `POST /orders/{id}/add_item/`: Add an item to an order

### Order History

- `GET /order-history/`: List all reviews

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

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (git checkout -b feature/AmazingFeature)
3. Commit your Changes (git commit -m 'Add some AmazingFeature')
4. Push to the Branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## Contact

Cedric Ntwari - @CedricNtwari - ntwaricedric@gmail.com

Project Link: "...".
