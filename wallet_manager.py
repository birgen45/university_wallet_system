#intasend Api integration
import os
from intasend import APIService
from dotenv import load_dotenv

load_dotenv()


class UniversityWalletManager:


    def __init__(self):
        """Initialize IntaSend API service"""
        self.publishable_key = os.getenv('INTASEND_PUBLISHABLE_KEY')
        self.secret_key = os.getenv('INTASEND_SECRET_KEY')
        self.is_live = os.getenv('INTASEND_IS_LIVE', 'False').lower() == 'true'

        if not self.publishable_key or not self.secret_key:
            raise ValueError("IntaSend API keys not found. Please check your .env file")

        # Initialize IntaSend API service
        #  IntaSend SDK uses 'token' parameter for the secret key
        self.api = APIService(
            token=self.secret_key,
            publishable_key=self.publishable_key,
            test=not self.is_live
        )

        # Get wallets service
        self.wallet_service = self.api.wallets

    def create_wallet(self, label, currency="KES", can_disburse=True):
       
        try:
            # Create wallet with IntaSend
            response = self.wallet_service.create(
                currency=currency,
                label=label,
                can_disburse=can_disburse
            )

            print(f"[OK] Wallet created successfully")
            print(f"  Label: {label}")
            print(f"  Wallet ID: {response.get('wallet_id', 'N/A')}")
            print(f"  Balance: {currency} {response.get('current_balance', 0)}")

            return response

        except Exception as e:
            print(f"[ERROR] Error creating wallet: {str(e)}")
            raise

    def get_wallet_balance(self, wallet_id):
        
        try:
            response = self.wallet_service.retrieve(wallet_id=wallet_id)
            balance = response.get('current_balance', 0)

            print(f"[OK] Wallet {wallet_id} balance: KES {balance}")

            return response

        except Exception as e:
            print(f"[ERROR] Error retrieving wallet: {str(e)}")
            raise

    def list_wallets(self):
       
        try:
            response = self.wallet_service.list()
            wallets = response.get('results', [])

            print(f"[OK] Found {len(wallets)} wallet(s)")
            for wallet in wallets:
                label = wallet.get('label', 'N/A')
                balance = wallet.get('current_balance', 0)
                wallet_id = wallet.get('wallet_id', 'N/A')
                print(f"  - {label}: KES {balance} (ID: {wallet_id})")

            return wallets

        except Exception as e:
            print(f"[ERROR] Error listing wallets: {str(e)}")
            raise

    def fund_wallet(self, wallet_id, amount, phone_number, email=None):
        
        try:
            # Format phone number - remove + if present, ensure starts with 254
            phone_number = phone_number.replace('+', '').replace(' ', '')
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number

            # Use default email if none provided
            if not email:
                email = f"wallet-{wallet_id}@university.ac.ke"

            # Create checkout request for wallet funding
            response = self.api.collect.mpesa_stk_push(
                phone_number=phone_number,
                email=email,
                amount=amount,
                narrative=f"Wallet top-up for {wallet_id}",
                wallet_id=wallet_id
            )

            print(f"[OK] Funding request initiated for wallet {wallet_id}")
            print(f"  Amount: KES {amount}")
            print(f"  Phone: {phone_number}")
            print(f"  Please complete M-Pesa prompt on your phone")

            return response

        except Exception as e:
            print(f"[ERROR] Error funding wallet: {str(e)}")
            raise

    def transfer_between_wallets(self, origin_wallet_id, destination_wallet_id, amount, narrative="Canteen payment"):
        
        try:
            response = self.wallet_service.intra_transfer(
                origin_wallet_id,
                destination_wallet_id,
                amount,
                narrative
            )

            print(f"[OK] Transfer API response:")
            print(f"  Response: {response}")
            print(f"  From: {origin_wallet_id}")
            print(f"  To: {destination_wallet_id}")
            print(f"  Amount: KES {amount}")
            print(f"  Narrative: {narrative}")

            return response

        except Exception as e:
            print(f"[ERROR] Error transferring funds: {str(e)}")
            raise

    def get_wallet_transactions(self, wallet_id):
       
        try:
            response = self.wallet_service.transactions(wallet_id=wallet_id)
            transactions = response.get('results', [])

            print(f"[OK] Found {len(transactions)} transaction(s) for wallet {wallet_id}")
            for txn in transactions:
                print(f"  - {txn.get('created_at')}: {txn.get('narrative')} - "
                      f"KES {txn.get('value', 0)} ({txn.get('transaction_type')})")

            return transactions

        except Exception as e:
            print(f"[ERROR] Error retrieving transactions: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    manager = UniversityWalletManager()

    print("\n=== University Wallet System Demo ===\n")

    # List existing wallets
    print("1. Listing existing wallets...")
    manager.list_wallets()

