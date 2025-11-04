"""
Quick database checker - Run from command line
Usage: python quick_check.py [wallets|transactions|student ID]
"""
import sys
import database as db

def show_wallets():
    """Show all wallets"""
    print("\n" + "="*70)
    print("ALL WALLETS")
    print("="*70)
    wallets = db.get_all_wallets()
    for wallet in wallets:
        print(f"\n{wallet['student_id']}: {wallet['student_name']}")
        print(f"  Balance: {wallet['balance']} KES")
        print(f"  Wallet ID: {wallet['wallet_id']}")
        print(f"  Created: {wallet['created_at']}")
    print(f"\nTotal wallets: {len(wallets)}")
    print(f"Total balance: {sum(w['balance'] for w in wallets)} KES")

def show_transactions(limit=10):
    """Show recent transactions"""
    print("\n" + "="*70)
    print(f"RECENT {limit} TRANSACTIONS")
    print("="*70)
    transactions = db.get_all_transactions(limit)
    for txn in transactions:
        print(f"\n[{txn['id']}] {txn['type'].upper()}")
        print(f"  Amount: {txn['amount']} KES")
        print(f"  Status: {txn['status']}")
        if txn['student_id']:
            print(f"  Student: {txn['student_id']}")
        if txn['from_student'] and txn['to_student']:
            print(f"  Transfer: {txn['from_student']} -> {txn['to_student']}")
        print(f"  Time: {txn['timestamp']}")
        print(f"  Description: {txn['description']}")
    print(f"\nTotal transactions: {len(transactions)}")

def show_student(student_id):
    """Show specific student details"""
    wallet = db.get_wallet_by_student_id(student_id)
    if not wallet:
        print(f"No wallet found for student: {student_id}")
        return

    print("\n" + "="*70)
    print(f"STUDENT: {wallet['student_name']} ({student_id})")
    print("="*70)
    print(f"\nWallet ID: {wallet['wallet_id']}")
    print(f"Balance: {wallet['balance']} KES")
    print(f"Phone: {wallet['phone'] or 'Not set'}")
    print(f"Email: {wallet['email'] or 'Not set'}")
    print(f"Created: {wallet['created_at']}")
    print(f"Updated: {wallet['updated_at']}")

    # Show transactions
    print(f"\nRECENT TRANSACTIONS:")
    transactions = db.get_transactions_by_student(student_id, 10)
    if transactions:
        for txn in transactions:
            status_icon = "[OK]" if txn['status'] == 'completed' else "[...]"
            print(f"  {status_icon} {txn['type']}: {txn['amount']} KES - {txn['timestamp']}")
    else:
        print("  No transactions yet")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: show wallets
        show_wallets()
    elif sys.argv[1] == 'wallets':
        show_wallets()
    elif sys.argv[1] == 'transactions':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_transactions(limit)
    else:
        # Assume it's a student ID
        show_student(sys.argv[1])
