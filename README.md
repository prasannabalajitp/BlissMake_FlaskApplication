## Installation

### Prerequisites

- **Python**: Version 3.6 or higher
- **MongoDB**: Ensure MongoDB is installed and running
- **Git**: For cloning the repository

### Setup

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/your-username/blissmake.git
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

    Copy the `.env.example` file to `.env` and update it with your actual configuration values:

    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file with your MongoDB URI and other details:

    ```dotenv
    # MongoDB URI
    MONGO_URI=mongodb://<username>:<password>@<hostname>:<port>/<database>

    # Secret key for session management and other cryptographic operations
    SECRET_KEY=your_secret_key

    # UPI ID and payment details (if applicable)
    UPI_ID=your_upi_id
    PAYEE_NAME=your_payee_name
    ```

### Running the Application

- **To Run the Application**:

    ```bash
    flask --app app.py run
    ```

- **To Run the Application with Debug Enabled**:

    ```bash
    flask --app app.py --debug run
    ```

### Access the Application

Open your web browser and navigate to `http://localhost:5000/blissmake` to start using the application.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.