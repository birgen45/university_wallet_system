"""
Sync all wallet balances from IntaSend
Use this if webhooks are not working
"""
import sqlite3
from wallet_manager import UniversityWalletManager

def sync_all_balances():
    """Sync all wallet balances from IntaSend"""

    wm = UniversityWalletManager()

    # Connect to database
    conn = sqlite3.connect('wallet_system.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all wallets
    wallets = cur.execute('SELECT * FROM wallets').fetchall()

    print("="*60)
    print("Syncing wallet balances from IntaSend...")
    print("="*60)

    for wallet in wallets:
        student_id = wallet['student_id']
        wallet_id = wallet['wallet_id']
        old_balance = wallet['balance']

        # Get live balance from IntaSend
        balance_info = wm.get_wallet_balance(wallet_id)

        if balance_info:
            new_balance = balance_info.get('current_balance', 0)

            # Update database
            cur.execute(
                'UPDATE wallets SET balance = ? WHERE student_id = ?',
                (new_balance, student_id)
            )

            print(f"\n{wallet['student_name']} ({student_id}):")
            print(f"  Old balance: {old_balance} KES")
            print(f"  New balance: {new_balance} KES")

            if new_balance != old_balance:
                print(f"  [OK] Updated!")
            else:
                print(f"  [OK] No change")
        else:
            print(f"\n{wallet['student_name']} ({student_id}): ERROR fetching balance")

    # Commit changes
    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("Sync complete!")
    print("="*60)

if __name__ == "__main__":
    sync_all_balances()
