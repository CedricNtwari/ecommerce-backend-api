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

### Products

- `GET /api/products/`: List all products
- `GET /api/products/:id/`: Retrieve a specific product
- `POST /api/products/`: Create a new product
- `PUT /api/products/:id/`: Update a product
- `DELETE /api/products/:id/`: Delete a product

### Orders

- `GET /api/orders/`: List all orders
- `GET /api/orders/:id/`: Retrieve a specific order
- `POST /api/orders/`: Create a new order
- `PUT /api/orders/:id/`: Update an order
- `DELETE /api/orders/:id/`: Delete an order

### Reviews

- `GET /api/reviews/`: List all reviews
- `GET /api/reviews/:id/`: Retrieve a specific review
- `POST /api/reviews/`: Create a new review
- `PUT /api/reviews/:id/`: Update a review
- `DELETE /api/reviews/:id/`: Delete a review

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
