import sqlite3

conn = sqlite3.connect('fraud_cases.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('SELECT user_name, card_ending, transaction_amount, status, outcome_note FROM fraud_cases')

print("\n" + "="*70)
print("🏦 SECUREBANK FRAUD CASES DATABASE")
print("="*70)

for row in cursor.fetchall():
    status_emoji = "✅" if row['status'] == 'confirmed_safe' else "🚨" if row['status'] == 'confirmed_fraud' else "⏳"
    print(f"\n{status_emoji} {row['user_name']}")
    print(f"   Card: ****{row['card_ending']} | Amount: ₹{row['transaction_amount']:,.2f}")
    print(f"   Status: {row['status']}")
    if row['outcome_note']:
        print(f"   Note: {row['outcome_note']}")

print("\n" + "="*70 + "\n")
conn.close()