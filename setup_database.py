import sqlite3
from datetime import datetime, timedelta
import random

def setup_database():
    """
    Creates SQLite database with fraud_cases table and populates it with sample data.
    """
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect('fraud_cases.db')
    cursor = conn.cursor()

    # Create fraud_cases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            security_identifier TEXT NOT NULL,
            card_ending TEXT NOT NULL,
            transaction_amount REAL NOT NULL,
            transaction_name TEXT NOT NULL,
            transaction_time TEXT NOT NULL,
            transaction_category TEXT NOT NULL,
            transaction_source TEXT NOT NULL,
            transaction_location TEXT NOT NULL,
            security_question TEXT NOT NULL,
            security_answer TEXT NOT NULL,
            status TEXT DEFAULT 'pending_review',
            outcome_note TEXT DEFAULT ''
        )
    ''')

    # Sample fraud cases with simple English names for voice recognition
    fraud_cases = [
        {
            'user_name': 'John Smith',
            'security_identifier': 'JS2847',
            'card_ending': '4242',
            'transaction_amount': 45999.50,
            'transaction_name': 'Electronics World Online',
            'transaction_time': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_category': 'Electronics',
            'transaction_source': 'electronicsworld.net',
            'transaction_location': 'Lagos, Nigeria',
            'security_question': 'What is your favorite color?',
            'security_answer': 'blue',
            'status': 'pending_review',
            'outcome_note': ''
        },
        {
            'user_name': 'Sarah Wilson',
            'security_identifier': 'SW1923',
            'card_ending': '7890',
            'transaction_amount': 89750.00,
            'transaction_name': 'Luxury Fashion Boutique',
            'transaction_time': (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_category': 'Fashion & Apparel',
            'transaction_source': 'luxuryfashion-outlet.com',
            'transaction_location': 'Shanghai, China',
            'security_question': 'What is your pet\'s name?',
            'security_answer': 'max',
            'status': 'pending_review',
            'outcome_note': ''
        },
        {
            'user_name': 'Mike Johnson',
            'security_identifier': 'MJ5612',
            'card_ending': '3456',
            'transaction_amount': 125000.00,
            'transaction_name': 'International Wire Transfer Service',
            'transaction_time': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_category': 'Money Transfer',
            'transaction_source': 'quickwire-transfer.biz',
            'transaction_location': 'Moscow, Russia',
            'security_question': 'What city were you born in?',
            'security_answer': 'london',
            'status': 'pending_review',
            'outcome_note': ''
        },
        {
            'user_name': 'Emma Davis',
            'security_identifier': 'ED8934',
            'card_ending': '6789',
            'transaction_amount': 32499.99,
            'transaction_name': 'Gaming Store Pro',
            'transaction_time': (datetime.now() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_category': 'Gaming & Entertainment',
            'transaction_source': 'gamingstorepro.online',
            'transaction_location': 'Bucharest, Romania',
            'security_question': 'What is your favorite food?',
            'security_answer': 'pizza',
            'status': 'pending_review',
            'outcome_note': ''
        },
        {
            'user_name': 'Tom Brown',
            'security_identifier': 'TB4521',
            'card_ending': '9012',
            'transaction_amount': 67800.00,
            'transaction_name': 'Premium Watches International',
            'transaction_time': (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_category': 'Jewelry & Accessories',
            'transaction_source': 'premiumwatches-intl.co',
            'transaction_location': 'Istanbul, Turkey',
            'security_question': 'What is your mother\'s name?',
            'security_answer': 'mary',
            'status': 'pending_review',
            'outcome_note': ''
        }
    ]

    # Insert sample data
    for case in fraud_cases:
        cursor.execute('''
            INSERT INTO fraud_cases (
                user_name, security_identifier, card_ending, transaction_amount,
                transaction_name, transaction_time, transaction_category,
                transaction_source, transaction_location, security_question,
                security_answer, status, outcome_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case['user_name'], case['security_identifier'], case['card_ending'],
            case['transaction_amount'], case['transaction_name'], case['transaction_time'],
            case['transaction_category'], case['transaction_source'], case['transaction_location'],
            case['security_question'], case['security_answer'], case['status'],
            case['outcome_note']
        ))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("✓ Database setup completed successfully!")
    print(f"✓ Created 'fraud_cases.db' with {len(fraud_cases)} sample fraud cases")
    print("✓ Table 'fraud_cases' created with all required columns")
    print("\nSample cases added for:")
    for case in fraud_cases:
        print(f"  - {case['user_name']} (Card ending: {case['card_ending']}, Amount: ₹{case['transaction_amount']:,.2f})")

if __name__ == '__main__':
    setup_database()
