# BlissMake - Flask Application

BlissMake is a sophisticated Flask-based web application designed to streamline user authentication, product management, and a dynamic shopping cart experience with integrated payment processing. Leveraging MongoDB for data storage, BlissMake provides a seamless and interactive online shopping experience.

## Features

- **User Authentication**: 
  - Register new users, log in, and manage user sessions with ease.
  
- **Product Listings**: 
  - Browse and display a variety of products fetched directly from MongoDB.
  
- **Shopping Cart**: 
  - Add, update, and remove items from your cart effortlessly.
  
- **Payment Processing**: 
  - Generate QR codes for payment transactions and handle payment confirmations smoothly.
  
- **Blueprint Architecture**: 
  - Maintain a clean and organized codebase using Flask Blueprints.
  
- **Environment Configuration**: 
  - Manage application settings and secrets with environment variables for secure and flexible configuration.

## Installation

### Prerequisites

- **Python**: Version 3.6 or higher
- **MongoDB**: Make sure you have MongoDB installed and running
- **Git**: For cloning the repository

### Setup

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/prasannabalajitp/BlissMake---Flask-Application.git
    cd blissmake
    ```

2. **Create and Activate a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables**:

    Create a `.env` file in the root directory and add your configuration variables. You can use the provided `.env.example` as a reference.

5. **Run the Application**:

    ```bash
    python app.py
    ```

6. **Access the Application**:

    Open your web browser and navigate to `http://localhost:5000` to start using the application.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.