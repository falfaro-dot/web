#!/usr/bin/env python3
"""
Debug bank balance overwrite issue
"""

import requests
import json

BACKEND_URL = "https://cash-flow-mgr-1.preview.emergentagent.com/api"

def test_bank_balance_debug():
    session = requests.Session()
    
    # Login first
    login_data = {"username": "operaciones@ibsgroup.mx", "password": "Sistema2"}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    print(f"Login: {response.status_code} - {response.json()}")
    
    account_name = "MESUBAJ COMERCIALIZADORA SA DE CV"
    test_date = "2025-01-15"
    
    print(f"\n=== Testing Bank Balance Overwrite for {account_name} on {test_date} ===")
    
    # Step 1: Create initial balance
    print("\n1. Creating initial balance...")
    initial_data = {
        'fecha': test_date,
        'nombre_cuenta': account_name,
        'saldo': 50000.00,
        'ejecutivo': 'operaciones@ibsgroup.mx'
    }
    response = session.post(f"{BACKEND_URL}/bancos/create", data=initial_data)
    print(f"Initial creation: {response.status_code} - {response.json()}")
    
    # Step 2: Check what's in the database
    print("\n2. Checking bank accounts with balances...")
    response = session.get(f"{BACKEND_URL}/bank_accounts/saldos")
    if response.status_code == 200:
        accounts = response.json()
        for account in accounts:
            if account.get("nombre") == account_name:
                print(f"Found account: {account}")
                break
    
    # Step 3: Create second balance (should overwrite)
    print("\n3. Creating second balance (should overwrite)...")
    overwrite_data = {
        'fecha': test_date,
        'nombre_cuenta': account_name,
        'saldo': 75000.00,
        'ejecutivo': 'operaciones@ibsgroup.mx'
    }
    response = session.post(f"{BACKEND_URL}/bancos/create", data=overwrite_data)
    print(f"Overwrite attempt: {response.status_code} - {response.json()}")
    
    # Step 4: Check again
    print("\n4. Checking bank accounts with balances after overwrite...")
    response = session.get(f"{BACKEND_URL}/bank_accounts/saldos")
    if response.status_code == 200:
        accounts = response.json()
        for account in accounts:
            if account.get("nombre") == account_name:
                print(f"Found account after overwrite: {account}")
                break
    
    # Step 5: Check with specific date
    print(f"\n5. Checking bank accounts with specific date ({test_date})...")
    response = session.get(f"{BACKEND_URL}/bank_accounts/saldos?fecha={test_date}")
    if response.status_code == 200:
        accounts = response.json()
        for account in accounts:
            if account.get("nombre") == account_name:
                print(f"Found account with specific date: {account}")
                break

if __name__ == "__main__":
    test_bank_balance_debug()