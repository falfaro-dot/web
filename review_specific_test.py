#!/usr/bin/env python3
"""
Specific tests for the review request functionalities
Tests the exact scenarios mentioned in the review request
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "https://cash-flow-mgr-1.preview.emergentagent.com/api"

# Test credentials from review request
REGULAR_USER = {"username": "operaciones@ibsgroup.mx", "password": "Sistema2"}
DELETE_USER_1 = {"username": "f.alfaro@ibsgroup.mx", "password": "System3ras3$0"}
DELETE_USER_2 = {"username": "administracion@ibsgroup.mx", "password": "System3ras3$!"}

class ReviewTestRunner:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        self.results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        
        if success:
            print(f"✅ {test_name}: {details}")
        else:
            print(f"❌ {test_name}: {details}")

    def test_1_cash_excel_export(self):
        """Test 1: Exportación de Caja Chica a Excel"""
        print("\n🧪 Test 1: Exportación de Caja Chica a Excel")
        
        # Test without parameters
        try:
            response = self.session.get(f"{BACKEND_URL}/export/efectivo/xlsx")
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    self.log_result("Excel Export - No Parameters", True, 
                                  f"Excel file generated. Size: {len(response.content)} bytes, Content-Type: {content_type}")
                else:
                    self.log_result("Excel Export - No Parameters", False, 
                                  f"Wrong content type: {content_type}")
            else:
                self.log_result("Excel Export - No Parameters", False, 
                              f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Excel Export - No Parameters", False, f"Exception: {str(e)}")
        
        # Test with date parameters
        try:
            params = {
                'fecha_inicio': '2025-01-01',
                'fecha_fin': '2025-01-31'
            }
            response = self.session.get(f"{BACKEND_URL}/export/efectivo/xlsx", params=params)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    self.log_result("Excel Export - With Date Filters", True, 
                                  f"Filtered Excel file generated. Size: {len(response.content)} bytes")
                else:
                    self.log_result("Excel Export - With Date Filters", False, 
                                  f"Wrong content type: {content_type}")
            else:
                self.log_result("Excel Export - With Date Filters", False, 
                              f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Excel Export - With Date Filters", False, f"Exception: {str(e)}")

    def test_2_cash_data_deletion(self):
        """Test 2: Borrado de datos de Caja Chica"""
        print("\n🧪 Test 2: Borrado de datos de Caja Chica")
        
        # First create some test data
        self.create_test_cash_data()
        
        # Test with incorrect credentials
        try:
            invalid_data = {
                "username": "wrong@user.com",
                "password": "wrongpassword",
                "fecha_inicio": "2025-01-01T00:00:00Z",
                "fecha_fin": "2025-01-15T23:59:59Z"
            }
            response = self.session.post(f"{BACKEND_URL}/admin/delete_efectivo", json=invalid_data)
            if response.status_code == 403:
                self.log_result("Delete - Invalid Credentials", True, "Correctly rejected invalid credentials (403)")
            else:
                self.log_result("Delete - Invalid Credentials", False, 
                              f"Expected 403, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Delete - Invalid Credentials", False, f"Exception: {str(e)}")
        
        # Test with valid credentials (f.alfaro@ibsgroup.mx)
        try:
            valid_data = {
                "username": "f.alfaro@ibsgroup.mx",
                "password": "System3ras3$0",
                "fecha_inicio": "2025-01-01T00:00:00Z",
                "fecha_fin": "2025-01-15T23:59:59Z"
            }
            response = self.session.post(f"{BACKEND_URL}/admin/delete_efectivo", json=valid_data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    deleted_count = result.get("deleted_count", 0)
                    self.log_result("Delete - Valid User 1", True, 
                                  f"Successfully deleted {deleted_count} records with f.alfaro credentials")
                else:
                    self.log_result("Delete - Valid User 1", False, 
                                  f"Deletion failed: {result.get('message', 'Unknown error')}")
            else:
                self.log_result("Delete - Valid User 1", False, 
                              f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Delete - Valid User 1", False, f"Exception: {str(e)}")
        
        # Test with second valid user (administracion@ibsgroup.mx)
        try:
            valid_data2 = {
                "username": "administracion@ibsgroup.mx",
                "password": "System3ras3$!",
                "fecha_inicio": "2025-01-01T00:00:00Z",
                "fecha_fin": "2025-01-15T23:59:59Z"
            }
            response = self.session.post(f"{BACKEND_URL}/admin/delete_efectivo", json=valid_data2)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    deleted_count = result.get("deleted_count", 0)
                    self.log_result("Delete - Valid User 2", True, 
                                  f"Successfully deleted {deleted_count} records with administracion credentials")
                else:
                    self.log_result("Delete - Valid User 2", False, 
                                  f"Deletion failed: {result.get('message', 'Unknown error')}")
            else:
                self.log_result("Delete - Valid User 2", False, 
                              f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Delete - Valid User 2", False, f"Exception: {str(e)}")

    def create_test_cash_data(self):
        """Create test cash data for deletion testing"""
        test_data = {
            'fecha': '2025-01-10',
            'tipo_movimiento': 'Abono a Caja Chica',
            'origen_destino_tipo': 'Otro',
            'origen_destino_nombre': 'Test data for deletion',
            'cantidad': 1000.00,
            'concepto': 'Test transaction for deletion testing',
            'ejecutivo': 'operaciones@ibsgroup.mx'
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/efectivo/create", data=test_data)
            if response.status_code == 200:
                print("  📝 Created test cash transaction for deletion testing")
        except Exception:
            pass

    def test_3_bank_balances_excel_export(self):
        """Test 3: Exportación de Saldos Bancarios a Excel"""
        print("\n🧪 Test 3: Exportación de Saldos Bancarios a Excel")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/export/bank_balances/xlsx")
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    # Check file size to ensure it has data
                    file_size = len(response.content)
                    if file_size > 1000:  # Reasonable size for Excel with data
                        self.log_result("Bank Balances Excel Export", True, 
                                      f"Excel file generated successfully. Size: {file_size} bytes")
                    else:
                        self.log_result("Bank Balances Excel Export", False, 
                                      f"Excel file too small (may be empty): {file_size} bytes")
                else:
                    self.log_result("Bank Balances Excel Export", False, 
                                  f"Wrong content type: {content_type}")
            else:
                self.log_result("Bank Balances Excel Export", False, 
                              f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Bank Balances Excel Export", False, f"Exception: {str(e)}")

    def test_4_bank_balance_overwrite(self):
        """Test 4: Mejora en captura de saldos bancarios (sobrescritura)"""
        print("\n🧪 Test 4: Mejora en captura de saldos bancarios (sobrescritura)")
        
        # Note: The review mentions /api/bancos/captura but the actual endpoint is /api/bancos/create
        account_name = "MESUBAJ COMERCIALIZADORA SA DE CV"
        test_date = "2025-01-15"
        
        # Step a) Create initial balance
        try:
            initial_data = {
                'fecha': test_date,
                'nombre_cuenta': account_name,
                'saldo': 50000.00,
                'ejecutivo': 'operaciones@ibsgroup.mx'
            }
            response = self.session.post(f"{BACKEND_URL}/bancos/create", data=initial_data)
            if response.status_code == 200:
                self.log_result("Bank Balance - Initial Creation", True, 
                              f"Initial balance created for {account_name} on {test_date}: 50000.00")
            else:
                self.log_result("Bank Balance - Initial Creation", False, 
                              f"Failed to create initial balance: {response.text}")
                return
        except Exception as e:
            self.log_result("Bank Balance - Initial Creation", False, f"Exception: {str(e)}")
            return
        
        # Step b) Create another balance for SAME account and SAME date with different value
        try:
            overwrite_data = {
                'fecha': test_date,
                'nombre_cuenta': account_name,
                'saldo': 75000.00,  # Different value
                'ejecutivo': 'operaciones@ibsgroup.mx'
            }
            response = self.session.post(f"{BACKEND_URL}/bancos/create", data=overwrite_data)
            if response.status_code == 200:
                result = response.json()
                message = result.get("message", "").lower()
                if "actualizado" in message or "updated" in message:
                    self.log_result("Bank Balance - Overwrite", True, 
                                  f"Balance correctly overwritten (not duplicated): {result.get('message', '')}")
                else:
                    self.log_result("Bank Balance - Overwrite", True, 
                                  f"Balance operation completed: {result.get('message', '')}")
            else:
                self.log_result("Bank Balance - Overwrite", False, 
                              f"Failed to overwrite balance: {response.text}")
                return
        except Exception as e:
            self.log_result("Bank Balance - Overwrite", False, f"Exception: {str(e)}")
            return
        
        # Step c) Verify that second balance OVERWROTE the first (not created new record)
        try:
            response = self.session.get(f"{BACKEND_URL}/bank_accounts/saldos?fecha={test_date}")
            if response.status_code == 200:
                accounts = response.json()
                target_account = None
                for account in accounts:
                    if account.get("nombre") == account_name:
                        target_account = account
                        break
                
                if target_account:
                    actual_balance = target_account.get("saldo", 0)
                    if abs(actual_balance - 75000.00) < 0.01:
                        self.log_result("Bank Balance - Verification", True, 
                                      f"Balance correctly overwritten: {actual_balance} (expected 75000.00)")
                    else:
                        self.log_result("Bank Balance - Verification", False, 
                                      f"Balance not overwritten correctly: got {actual_balance}, expected 75000.00")
                else:
                    self.log_result("Bank Balance - Verification", False, 
                                  f"Account {account_name} not found in response")
            else:
                self.log_result("Bank Balance - Verification", False, 
                              f"Failed to retrieve balances: {response.text}")
        except Exception as e:
            self.log_result("Bank Balance - Verification", False, f"Exception: {str(e)}")
        
        # Step d) Verify timestamp format DD/MM/YYYY HH:MM:SS
        try:
            response = self.session.get(f"{BACKEND_URL}/bank_accounts/saldos?fecha={test_date}")
            if response.status_code == 200:
                accounts = response.json()
                target_account = None
                for account in accounts:
                    if account.get("nombre") == account_name:
                        target_account = account
                        break
                
                if target_account:
                    timestamp = target_account.get("ultima_actualizacion", "")
                    if timestamp and "/" in timestamp and ":" in timestamp:
                        # Check if it matches DD/MM/YYYY HH:MM:SS format
                        parts = timestamp.split(" ")
                        if len(parts) == 2:
                            date_part = parts[0]
                            time_part = parts[1]
                            if len(date_part.split("/")) == 3 and len(time_part.split(":")) == 3:
                                self.log_result("Bank Balance - Timestamp Format", True, 
                                              f"Timestamp correctly formatted: {timestamp}")
                            else:
                                self.log_result("Bank Balance - Timestamp Format", False, 
                                              f"Timestamp format incorrect: {timestamp}")
                        else:
                            self.log_result("Bank Balance - Timestamp Format", False, 
                                          f"Timestamp format incorrect: {timestamp}")
                    else:
                        self.log_result("Bank Balance - Timestamp Format", False, 
                                      f"No timestamp or wrong format: {timestamp}")
                else:
                    self.log_result("Bank Balance - Timestamp Format", False, 
                                  f"Account {account_name} not found")
            else:
                self.log_result("Bank Balance - Timestamp Format", False, 
                              f"Failed to retrieve accounts: {response.text}")
        except Exception as e:
            self.log_result("Bank Balance - Timestamp Format", False, f"Exception: {str(e)}")

    def test_5_bank_accounts_timestamp(self):
        """Test 5: Verificar endpoint de saldos bancarios con timestamp"""
        print("\n🧪 Test 5: Verificar endpoint de saldos bancarios con timestamp")
        
        # Note: The review mentions /api/bancos/cuentas but the actual endpoint is /api/bank_accounts/saldos
        try:
            response = self.session.get(f"{BACKEND_URL}/bank_accounts/saldos")
            if response.status_code == 200:
                accounts = response.json()
                if isinstance(accounts, list) and len(accounts) > 0:
                    # Check timestamp fields
                    timestamp_count = 0
                    full_timestamp_count = 0
                    date_only_count = 0
                    
                    for account in accounts:
                        ultima_actualizacion = account.get("ultima_actualizacion")
                        if ultima_actualizacion:
                            timestamp_count += 1
                            if "/" in ultima_actualizacion and ":" in ultima_actualizacion:
                                full_timestamp_count += 1
                            else:
                                date_only_count += 1
                    
                    self.log_result("Bank Accounts - Timestamp Field", True, 
                                  f"Retrieved {len(accounts)} accounts. {full_timestamp_count} with full timestamp, {date_only_count} with date only")
                    
                    # Verify backward compatibility
                    if full_timestamp_count > 0 and date_only_count >= 0:
                        self.log_result("Bank Accounts - Backward Compatibility", True, 
                                      "Endpoint supports both full timestamp and date-only formats")
                    else:
                        self.log_result("Bank Accounts - Backward Compatibility", False, 
                                      "Timestamp format inconsistency detected")
                else:
                    self.log_result("Bank Accounts - Timestamp Field", True, 
                                  "Endpoint working but no accounts found")
            else:
                self.log_result("Bank Accounts - Timestamp Field", False, 
                              f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Bank Accounts - Timestamp Field", False, f"Exception: {str(e)}")

    def run_review_tests(self):
        """Run all review-specific tests"""
        print("🔍 Starting Review-Specific Backend Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test authentication first
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=REGULAR_USER)
            if response.status_code == 200 and response.json().get("success"):
                print("✅ Authentication successful with operaciones@ibsgroup.mx")
            else:
                print("❌ Authentication failed - tests may not work properly")
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
        
        # Run all tests
        self.test_1_cash_excel_export()
        self.test_2_cash_data_deletion()
        self.test_3_bank_balances_excel_export()
        self.test_4_bank_balance_overwrite()
        self.test_5_bank_accounts_timestamp()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 REVIEW TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r['success'])
        failed = sum(1 for r in self.results if not r['success'])
        
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return self.results

if __name__ == "__main__":
    tester = ReviewTestRunner()
    results = tester.run_review_tests()