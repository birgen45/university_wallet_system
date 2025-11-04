
"""
Flask application with webhook endpoint for IntaSend events
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import json
from wallet_manager import UniversityWalletManager
import database as db

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS for frontend communication
CORS(app)

# Initialize wallet manager
wallet_manager = UniversityWalletManager()


@app.route('/')
def home():
    """Serve the main HTML interface"""
    from flask import send_file
    return send_file('index.html')

@app.route('/api')
def api_info():
    """API status and endpoints"""
    return jsonify({
        'status': 'online',
        'service': 'University Wallet System',
        'endpoints': {
            'webhook': '/webhook/intasend',
            'health': '/health',
            'create_wallet': '/create-wallet',
            'deposit': '/deposit',
            'balance': '/balance/<student_id>',
            'transfer': '/transfer',
            'wallets': '/wallets',
            'transactions': '/transactions'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })



@app.route('/create-wallet', methods=['POST'])
def create_wallet():
    
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        student_name = data.get('student_name')

        if not student_id or not student_name:
            return jsonify({'error': 'student_id and student_name are required'}), 400

        # Check if wallet already exists
        existing_wallet = db.get_wallet_by_student_id(student_id)
        if existing_wallet:
            return jsonify({'error': f'Wallet already exists for student {student_id}'}), 400

        # Create wallet via IntaSend
        wallet = wallet_manager.create_wallet(
            label=student_id,
            currency="KES",
            can_disburse=True
        )

        if wallet and 'wallet_id' in wallet:
            # Save to local database
            db.add_wallet(
                student_id=student_id,
                student_name=student_name,
                wallet_id=wallet['wallet_id'],
                phone=None,
                email=None
         )

            # Add transaction record
            db.add_transaction(
                transaction_type='wallet_created',
                amount=0,
                status='completed',
                student_id=student_id,
                description=f'Wallet created for {student_name}'
            )

            return jsonify({
                'success': True,
                'message': f'Wallet created successfully for {student_name}',
                'student_id': student_id,
                'wallet_id': wallet['wallet_id'],
                'balance': wallet.get('current_balance', 0)
            }), 201
        else:
            return jsonify({'error': 'Failed to create wallet with IntaSend'}), 500

    except Exception as e:
        print(f"Error creating wallet: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/deposit', methods=['POST'])
def deposit():
    
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        amount = data.get('amount')
        phone = data.get('phone')

        if not student_id or not amount or not phone:
            return jsonify({'error': 'student_id, amount, and phone are required'}), 400

        # Get wallet from database
        wallet = db.get_wallet_by_student_id(student_id)
        if not wallet:
            return jsonify({'error': f'No wallet found for student {student_id}'}), 404

        # Initiate M-Pesa STK push
        result = wallet_manager.fund_wallet(
            wallet_id=wallet['wallet_id'],
            amount=float(amount),
            phone_number=phone
        )

        # Add transaction record (pending)
        db.add_transaction(
            transaction_type='deposit',
            amount=float(amount),
            status='pending',
            student_id=student_id,
            description=f'M-Pesa deposit to {wallet["student_name"]}',
            metadata={'phone': phone, 'method': 'M-PESA'}
        )

        return jsonify({
            'success': True,
            'message': 'M-Pesa STK push sent. Check your phone to complete payment.',
            'student_id': student_id,
            'amount': amount,
            'phone': phone,
            'result': result
        }), 200

    except Exception as e:
        print(f"Error processing deposit: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/balance/<student_id>')
def get_balance(student_id):
   
    try:
        # Get wallet from database
        wallet = db.get_wallet_by_student_id(student_id)
        if not wallet:
            return jsonify({'error': f'No wallet found for student {student_id}'}), 404

        # Get live balance from IntaSend
        balance_info = wallet_manager.get_wallet_balance(wallet['wallet_id'])

        if balance_info:
            # Update local database with current balance
            current_balance = balance_info.get('current_balance', 0)
            db.update_wallet_balance(student_id, current_balance)

            return jsonify({
                'success': True,
                'student_id': student_id,
                'student_name': wallet['student_name'],
                'balance': current_balance,
                'currency': balance_info.get('currency', 'KES'),
                'wallet_id': wallet['wallet_id']
            }), 200
        else:
            return jsonify({'error': 'Failed to fetch balance from IntaSend'}), 500

    except Exception as e:
        print(f"Error fetching balance: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/transfer', methods=['POST'])
def transfer():
    
    try:
        data = request.get_json()
        from_student = data.get('from_student')
        to_student = data.get('to_student')
        amount = data.get('amount')

        if not from_student or not to_student or not amount:
            return jsonify({'error': 'from_student, to_student, and amount are required'}), 400

        # Get wallets from database
        from_wallet = db.get_wallet_by_student_id(from_student)
        to_wallet = db.get_wallet_by_student_id(to_student)

        if not from_wallet:
            return jsonify({'error': f'No wallet found for student {from_student}'}), 404
        if not to_wallet:
            return jsonify({'error': f'No wallet found for student {to_student}'}), 404

        # Get current balance from IntaSend to verify sufficient funds
        from_balance_info = wallet_manager.get_wallet_balance(from_wallet['wallet_id'])
        if not from_balance_info:
            return jsonify({'error': 'Unable to fetch sender wallet balance from IntaSend'}), 500

        available_balance = from_balance_info.get('available_balance', 0)
        if float(amount) > available_balance:
            return jsonify({
                'error': f'Insufficient balance. Available: {available_balance} KES, Required: {amount} KES',
                'available_balance': available_balance,
                'required_amount': float(amount)
            }), 400

        # Perform transfer via IntaSend
        result = wallet_manager.transfer_between_wallets(
            origin_wallet_id=from_wallet['wallet_id'],
            destination_wallet_id=to_wallet['wallet_id'],
            amount=float(amount),
            narrative=f"Transfer from {from_wallet['student_name']} to {to_wallet['student_name']}"
        )

        # Check if transfer was successful
        # First check if there's an explicit error in the response
        if result and 'error' in result:
            error_message = result.get('error', 'Transfer failed')

            # Check if it's an insufficient balance error based on the details
            if 'details' in result and 'origin' in result.get('details', {}):
                origin_balance = result['details']['origin'].get('available_balance', 0)
                if float(amount) > origin_balance:
                    error_message = f'Insufficient balance. Available: {origin_balance} KES, Required: {amount} KES'

            return jsonify({
                'error': error_message,
                'details': result
            }), 400

        # Then check for success indicators: tracking_id or details with valid balances
        if result and ('tracking_id' in result or ('details' in result and not 'error' in result)):
            # Add transaction record
            db.add_transaction(
                transaction_type='transfer',
                amount=float(amount),
                status='completed',
                from_student=from_student,
                to_student=to_student,
                description=f'Transfer: {from_wallet["student_name"]} -> {to_wallet["student_name"]}',
                transaction_id=result.get('tracking_id', 'N/A'),
                metadata=result
            )

            # Update wallet balances from the response
            if 'details' in result:
                if 'origin' in result['details']:
                    db.update_wallet_balance(from_student, result['details']['origin'].get('current_balance', 0))
                if 'destination' in result['details']:
                    db.update_wallet_balance(to_student, result['details']['destination'].get('current_balance', 0))

            return jsonify({
                'success': True,
                'message': f'Transfer successful: {amount} KES from {from_student} to {to_student}',
                'from_student': from_student,
                'to_student': to_student,
                'amount': amount,
                'tracking_id': result.get('tracking_id', 'N/A'),
                'details': result
            }), 200
        else:
            return jsonify({'error': 'Transfer failed', 'details': result}), 500

    except Exception as e:
        print(f"Error processing transfer: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/wallets')
def get_wallets():
    
    try:
        wallets = db.get_all_wallets()

        # Format wallets for frontend
        formatted_wallets = []
        for wallet in wallets:
            formatted_wallets.append({
                'student_id': wallet['student_id'],
                'student_name': wallet['student_name'],
                'wallet_id': wallet['wallet_id'],
                'balance': wallet['balance'],
                'phone': wallet.get('phone'),
                'email': wallet.get('email'),
                'created_at': wallet['created_at']
            })

        return jsonify({
            'success': True,
            'count': len(formatted_wallets),
            'wallets': formatted_wallets
        }), 200 

    except Exception as e:
        print(f"Error fetching wallets: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/transactions')
def get_transactions():
    
    try:
        limit = request.args.get('limit', 50, type=int)
        transactions = db.get_all_transactions(limit=limit)

        # Format transactions for frontend
        formatted_transactions = []
        for txn in transactions:
            formatted_transactions.append({
                'id': txn['id'],
                'type': txn['type'],
                'amount': txn['amount'],
                'status': txn['status'],
                'student_id': txn.get('student_id'),
                'from_student': txn.get('from_student'),
                'to_student': txn.get('to_student'),
                'description': txn.get('description'),
                'timestamp': txn['timestamp']
            })

        return jsonify({
            'success': True,
            'count': len(formatted_transactions),
            'transactions': formatted_transactions
        }), 200

    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500



# WEBHOOK ENDPOINTS


@app.route('/webhook/intasend', methods=['GET', 'POST'])
def intasend_webhook():

    # Handle GET requests (for webhook verification/testing)
    if request.method == 'GET':
        return jsonify({
            'status': 'online',
            'message': 'IntaSend webhook endpoint is ready',
            'endpoint': '/webhook/intasend',
            'methods': ['POST'],
            'timestamp': datetime.now().isoformat()
        }), 200

    # Handle POST requests (actual webhook events)
    try:
        # Get the webhook data
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Log the webhook event
        print("\n" + "="*60)
        print(f"[{datetime.now().isoformat()}] IntaSend Webhook Received")
        print("="*60)
        print(json.dumps(data, indent=2))
        print("="*60 + "\n")

        # Process different event types
        event_type = data.get('event')

        if event_type == 'COMPLETE':
            handle_payment_complete(data)
        elif event_type == 'FAILED':
            handle_payment_failed(data)
        elif event_type == 'wallet.topup':
            handle_wallet_topup(data)
        elif event_type == 'wallet.transfer':
            handle_wallet_transfer(data)
        else:
            print(f"[WARN] Unhandled event type: {event_type}")

        # Always return 200 to acknowledge receipt
        return jsonify({
            'status': 'success',
            'message': 'Webhook received',
            'event': event_type
        }), 200

    except Exception as e:
        print(f"[ERROR] Error processing webhook: {str(e)}")
        # Still return 200 to avoid retries for processing errors
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 200


def handle_payment_complete(data):
   
    print("\n[OK] Payment Completed Event")

    # Extract key information
    invoice_id = data.get('invoice_id')
    amount = data.get('value') or data.get('amount')
    currency = data.get('currency', 'KES')
    account = data.get('account')  # Phone number or email
    state = data.get('state')

    print(f"  Invoice ID: {invoice_id}")
    print(f"  Amount: {currency} {amount}")
    print(f"  Account: {account}")
    print(f"  State: {state}")

    # Save to database
    try:
        db.add_transaction(
            transaction_type='payment_complete',
            amount=float(amount) if amount else 0,
            status='completed',
            description=f'Payment completed for account {account}',
            transaction_id=invoice_id,
            metadata=data
        )
        print("  [OK] Transaction saved to database")
    except Exception as e:
        print(f"  [ERROR] Failed to save transaction: {str(e)}")

    return True


def handle_payment_failed(data):
    """Handle failed payment events"""
    print("\n[ERROR] Payment Failed Event")

    invoice_id = data.get('invoice_id')
    failed_reason = data.get('failed_reason')

    print(f"  Invoice ID: {invoice_id}")
    print(f"  Reason: {failed_reason}")

    # Save to database
    try:
        db.add_transaction(
            transaction_type='payment_failed',
            amount=0,
            status='failed',
            description=f'Payment failed: {failed_reason}',
            transaction_id=invoice_id,
            metadata=data
        )
        print("  [OK] Failed transaction logged to database")
    except Exception as e:
        print(f"  [ERROR] Failed to save transaction: {str(e)}")

    return True


def handle_wallet_topup(data):
    """Handle wallet top-up events"""
    print("\n[OK] Wallet Top-up Event")

    wallet_id = data.get('wallet_id')
    amount = data.get('amount')
    currency = data.get('currency', 'KES')
    status = data.get('status')

    print(f"  Wallet ID: {wallet_id}")
    print(f"  Amount: {currency} {amount}")
    print(f"  Status: {status}")

    # Save to database and update wallet balance
    try:
        # Find wallet by wallet_id
        wallet = db.get_wallet_by_wallet_id(wallet_id)
        if wallet:
            # Get updated balance from IntaSend
            balance_info = wallet_manager.get_wallet_balance(wallet_id)
            if balance_info:
                new_balance = balance_info.get('current_balance', 0)
                db.update_wallet_balance(wallet['student_id'], new_balance)
                print(f"  [OK] Updated balance for {wallet['student_name']}: {new_balance} KES")

            # Log transaction
            db.add_transaction(
                transaction_type='topup',
                amount=float(amount) if amount else 0,
                status=status or 'completed',
                student_id=wallet['student_id'],
                description=f'Wallet top-up for {wallet["student_name"]}',
                metadata=data
            )
            print("  [OK] Transaction saved to database")
        else:
            print(f"  [WARN] Wallet not found in local database: {wallet_id}")
    except Exception as e:
        print(f"  [ERROR] Failed to process top-up: {str(e)}")

    return True


def handle_wallet_transfer(data):
    
    print("\n[OK] Wallet Transfer Event")

    origin_wallet = data.get('origin_wallet_id')
    destination_wallet = data.get('destination_wallet_id')
    amount = data.get('amount')
    narrative = data.get('narrative')
    status = data.get('status')
    tracking_id = data.get('tracking_id')

    print(f"  From: {origin_wallet}")
    print(f"  To: {destination_wallet}")
    print(f"  Amount: KES {amount}")
    print(f"  Narrative: {narrative}")
    print(f"  Status: {status}")

    # Save to database and update wallet balances
    try:
        # Find both wallets
        from_wallet = db.get_wallet_by_wallet_id(origin_wallet)
        to_wallet = db.get_wallet_by_wallet_id(destination_wallet)

        if from_wallet and to_wallet:
            # Update balances for both wallets
            from_balance_info = wallet_manager.get_wallet_balance(origin_wallet)
            to_balance_info = wallet_manager.get_wallet_balance(destination_wallet)

            if from_balance_info:
                db.update_wallet_balance(from_wallet['student_id'], from_balance_info.get('current_balance', 0))
            if to_balance_info:
                db.update_wallet_balance(to_wallet['student_id'], to_balance_info.get('current_balance', 0))

            print(f"  [OK] Updated balances for both wallets")

            # Log transaction
            db.add_transaction(
                transaction_type='transfer',
                amount=float(amount) if amount else 0,
                status=status or 'completed',
                from_student=from_wallet['student_id'],
                to_student=to_wallet['student_id'],
                description=narrative or f'Transfer: {from_wallet["student_name"]} -> {to_wallet["student_name"]}',
                transaction_id=tracking_id,
                metadata=data
            )
            print("  [OK] Transaction saved to database")
        else:
            if not from_wallet:
                print(f"  [WARN] Origin wallet not found: {origin_wallet}")
            if not to_wallet:
                print(f"  [WARN] Destination wallet not found: {destination_wallet}")
    except Exception as e:
        print(f"  [ERROR] Failed to process transfer: {str(e)}")

    return True


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000)) 

    print("\n" + "="*60)
    print("University Wallet System - Webhook Server")
    print("="*60)
    print(f"Server running on port {port}")
    print("\nEndpoints:")
    print(f"  - Home: http://localhost:{port}/")
    print(f"  - Webhook: http://localhost:{port}/webhook/intasend")
    print(f"  - Health: http://localhost:{port}/health")
    print("\nTo expose via ngrok, run:")
    print(f"  ngrok http {port}")
    print("="*60 + "\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
