# University Wallet System

A complete digital wallet management system built with Flask and IntaSend API for managing student wallets, deposits, transfers, and M-Pesa payments.

## Features

- **Create Student Wallets**: Set up individual wallets for students
- **M-Pesa Integration**: Deposit money via M-Pesa STK Push
- **Balance Checking**: View real-time wallet balances
- **Wallet Transfers**: Transfer money between student wallets
- **Transaction History**: Track all wallet activities
- **Webhook Support**: Receive real-time payment notifications from IntaSend

## Quick Start

### Prerequisites

- Python 3.7+
- IntaSend API credentials (Publishable Key and Secret Key)
- M-Pesa account (for testing deposits)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd university_wallet_system
   ```

2. **Create a virtual environment** (if not already created)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your IntaSend API credentials:
     ```
     INTASEND_PUBLISHABLE_KEY=your_publishable_key_here
     INTASEND_SECRET_KEY=your_secret_key_here
     FLASK_SECRET_KEY=your_random_secret_key
     FLASK_PORT=5000
     ```

### Running the Application

**Option 1: Using the start script (Windows)**
```bash
start_server.bat
```

**Option 2: Using the start script (Linux/Mac)**
```bash
./start_server.sh
```

**Option 3: Manual start**
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Accessing the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Creating a Wallet

1. Go to the "Create Wallet" section
2. Enter Student ID (e.g., STU001)
3. Enter Student Name (e.g., John Doe)
4. Click "Create Wallet"

### Depositing Money

1. Go to the "Deposit Money" section
2. Enter Student ID
3. Enter Amount in KES
4. Enter M-Pesa Phone Number (format: 254712345678)
5. Click "Send STK Push"
6. Complete payment on your phone

### Checking Balance

1. Go to the "Check Balance" section
2. Enter Student ID
3. Click "Check Balance"

### Transferring Money

1. Go to the "Transfer Money" section
2. Enter sender's Student ID
3. Enter receiver's Student ID
4. Enter Amount
5. Click "Transfer"

## API Endpoints

- `GET /` - Web interface
- `GET /api` - API status and endpoint list
- `GET /health` - Health check
- `POST /create-wallet` - Create a new wallet
- `POST /deposit` - Deposit money via M-Pesa
- `GET /balance/<student_id>` - Get wallet balance
- `POST /transfer` - Transfer between wallets
- `GET /wallets` - List all wallets
- `GET /transactions` - List all transactions
- `POST /webhook/intasend` - IntaSend webhook endpoint

## Project Structure

```
university_wallet_system/
├── app.py                 # Main Flask application
├── database.py            # Database operations
├── wallet_manager.py      # IntaSend wallet management
├── index.html             # Web interface
├── wallet_system.db       # SQLite database
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment template
├── start_server.bat      # Windows start script
└── start_server.sh       # Linux/Mac start script
```

## Database Schema

### Wallets Table
- `student_id` - Unique student identifier
- `student_name` - Student's name
- `wallet_id` - IntaSend wallet ID
- `balance` - Current balance
- `phone` - Phone number (optional)
- `email` - Email (optional)
- `created_at` - Creation timestamp

### Transactions Table
- `id` - Transaction ID
- `type` - Transaction type (wallet_created, deposit, transfer, etc.)
- `amount` - Transaction amount
- `status` - Transaction status (pending, completed, failed)
- `student_id` - Associated student (for deposits/balance)
- `from_student` - Sender (for transfers)
- `to_student` - Receiver (for transfers)
- `description` - Transaction description
- `transaction_id` - External transaction ID
- `timestamp` - Transaction time

## Webhook Setup

To receive real-time payment notifications:

1. Expose your local server using ngrok:
   ```bash
   ngrok http 5000
   ```

2. Copy the ngrok URL (e.g., https://abc123.ngrok.io)

3. Set up webhook in IntaSend dashboard:
   - URL: `https://your-ngrok-url.ngrok.io/webhook/intasend`
   - Events: All payment events

## Troubleshooting

**Database issues:**
```bash
python view_database.py
```

**Port already in use:**
Change the port in `.env` file:
```
FLASK_PORT=5001
```

**M-Pesa not working:**
- Verify phone number format: 254XXXXXXXXX
- Ensure you have sufficient M-Pesa balance
- Check IntaSend API credentials

## Security Notes

- Never commit `.env` file to git
- Keep your IntaSend API keys secure
- Use strong `FLASK_SECRET_KEY` in production
- This is a development server - use a production WSGI server for deployment

## Technologies Used

- **Flask** - Web framework
- **IntaSend Python SDK** - Payment processing
- **SQLite** - Database
- **HTML/CSS/JavaScript** - Frontend

## License

MIT License

## Support

For issues or questions, please check the IntaSend documentation or create an issue in the project repository.
