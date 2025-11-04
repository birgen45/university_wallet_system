"""
Simple script to view database contents
Run: python view_database.py
"""
import database as db
from datetime import datetime

def print_separator(title=""):
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print('='*70)
    else:
        print('-'*70)

def view_wallets():
    """Display all wallets"""
    print_separator("WALLETS")
    wallets = db.get_all_wallets()

    if not wallets:
        print("No wallets found in database.")
        return

    print(f"\nTotal Wallets: {len(wallets)}\n")
    print(f"{'ID':<10} {'Student':<20} {'Balance':<12} {'Wallet ID':<12} {'Created':<20}")
    print_separator()

    for w in wallets:
        print(f"{w['student_id']:<10} {w['student_name']:<20} "
              f"{w['balance']:>8.2f} KES  {w['wallet_id']:<12} {w['created_at']:<20}")

def view_transactions():
    """Display all transactions"""
    print_separator("TRANSACTIONS")
    transactions = db.get_all_transactions()

    if not transactions:
        print("No transactions found in database.")
        return

    print(f"\nTotal Transactions: {len(transactions)}\n")
    print(f"{'Type':<15} {'Amount':<12} {'Status':<12} {'Student':<12} {'Timestamp':<20}")
    print_separator()

    for t in transactions[:50]:  # Show last 50
        student = t.get('student_id') or t.get('from_student') or '-'
        print(f"{t['type']:<15} {t['amount']:>8.2f} KES  {t['status']:<12} "
              f"{student:<12} {t['timestamp']:<20}")

    if len(transactions) > 50:
        print(f"\n... and {len(transactions) - 50} more transactions")

def view_student_details(student_id):
    """Display specific student details"""
    print_separator(f"STUDENT DETAILS: {student_id}")

    # Get wallet
    wallet = db.get_wallet_by_student_id(student_id)
    if not wallet:
        print(f"Student {student_id} not found.")
        return

    print(f"\nStudent ID:    {wallet['student_id']}")
    print(f"Student Name:  {wallet['student_name']}")
    print(f"Wallet ID:     {wallet['wallet_id']}")
    print(f"Balance:       {wallet['balance']:.2f} KES")
    print(f"Phone:         {wallet['phone'] or 'Not set'}")
    print(f"Email:         {wallet['email'] or 'Not set'}")
    print(f"Created:       {wallet['created_at']}")
    print(f"Last Updated:  {wallet['updated_at']}")

    # Get transactions
    transactions = db.get_all_transactions()
    student_trans = [t for t in transactions
                     if t.get('student_id') == student_id
                     or t.get('from_student') == student_id
                     or t.get('to_student') == student_id]

    if student_trans:
        print(f"\nTransactions: {len(student_trans)}")
        print_separator()
        for t in student_trans[-10:]:  # Last 10
            print(f"  {t['type']:<15} {t['amount']:>8.2f} KES  {t['status']:<12} {t['timestamp']}")

def main_menu():
    """Interactive menu"""
    while True:
        print_separator("WALLET DATABASE VIEWER")
        print("\n1. View All Wallets")
        print("2. View All Transactions")
        print("3. View Student Details")
        print("4. View Statistics")
        print("5. Exit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == '1':
            view_wallets()
        elif choice == '2':
            view_transactions()
        elif choice == '3':
            student_id = input("Enter Student ID: ").strip()
            view_student_details(student_id)
        elif choice == '4':
            view_statistics()
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")

def view_statistics():
    """Display database statistics"""
    print_separator("STATISTICS")

    wallets = db.get_all_wallets()
    transactions = db.get_all_transactions()

    total_balance = sum(w['balance'] for w in wallets)
    avg_balance = total_balance / len(wallets) if wallets else 0

    print(f"\nTotal Wallets:       {len(wallets)}")
    print(f"Total Transactions:  {len(transactions)}")
    print(f"Total Balance:       {total_balance:.2f} KES")
    print(f"Average Balance:     {avg_balance:.2f} KES")

    if wallets:
        richest = max(wallets, key=lambda w: w['balance'])
        print(f"\nRichest Student:     {richest['student_name']} ({richest['student_id']})")
        print(f"  Balance:           {richest['balance']:.2f} KES")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  UNIVERSITY WALLET SYSTEM - DATABASE VIEWER")
    print("="*70)

    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
