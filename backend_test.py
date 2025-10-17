#!/usr/bin/env python3
"""
Treasury Management System Backend Testing
Tests all backend API endpoints with comprehensive scenarios
"""

import requests
import json
import os
from pathlib import Path
import time

# Configuration
BACKEND_URL = "https://cash-flow-mgr-1.preview.emergentagent.com/api"
TEST_FILE_PATH = "/app/test_layout.xlsm"

# Test credentials - Updated to use new email-based system
VALID_CREDENTIALS = [
    {"username": "operaciones@ibsgroup.mx", "password": "Sistema2"},
    {"username": "administracion@ibsgroup.mx", "password": "Sistema4"}
]

INVALID_CREDENTIALS = [
    {"username": "InvalidUser", "password": "InvalidPass"},
    {"username": "Ejecutivo1", "password": "WrongPassword"},
    {"username": "", "password": ""},
]

# Classification types to test
CLASSIFICATION_TYPES = [
    "Abono a Tesorería",
    "Cargo/Retiro de Tesorería", 
    "Transacción Fondeada Directamente",
    "Transacción de Servicio/Facturación"
]

# Expected values from test_layout.xlsm - Note: client name has trailing space in database
EXPECTED_VALUES = {
    "cliente": "COMERCIALIZADORA ASAP DE CHIHUAHUA ",  # Note trailing space
    "rfc": "CAC231019F51",
    "subtotal": 41508.62,
    "iva": 6641.38,
    "total_factura": 48150.0
}

class TreasuryTestRunner:
    def __init__(self):
        self.results = {
            "auth_tests": [],
            "upload_tests": [],
            "treasury_tests": [],
            "cash_tests": [],
            "dashboard_tests": [],
            "errors": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_result(self, test_name, success, details, category="general"):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if category in self.results:
            self.results[category].append(result)
        
        self.results["summary"]["total"] += 1
        if success:
            self.results["summary"]["passed"] += 1
            print(f"✅ {test_name}: {details}")
        else:
            self.results["summary"]["failed"] += 1
            print(f"❌ {test_name}: {details}")
            
    def test_health_check(self):
        """Test health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", True, f"API is healthy: {data.get('message', '')}")
                return True
            else:
                self.log_result("Health Check", False, f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Health check error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test valid credentials
        for creds in VALID_CREDENTIALS:
            try:
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=creds)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("username") == creds["username"]:
                        self.log_result(
                            f"Valid Login - {creds['username']}", 
                            True, 
                            f"Login successful for {creds['username']}", 
                            "auth_tests"
                        )
                    else:
                        self.log_result(
                            f"Valid Login - {creds['username']}", 
                            False, 
                            f"Login response invalid: {data}", 
                            "auth_tests"
                        )
                else:
                    self.log_result(
                        f"Valid Login - {creds['username']}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}", 
                        "auth_tests"
                    )
            except Exception as e:
                self.log_result(
                    f"Valid Login - {creds['username']}", 
                    False, 
                    f"Exception: {str(e)}", 
                    "auth_tests"
                )
        
        # Test invalid credentials
        for creds in INVALID_CREDENTIALS:
            try:
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=creds)
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("success"):
                        self.log_result(
                            f"Invalid Login - {creds['username']}", 
                            True, 
                            "Correctly rejected invalid credentials", 
                            "auth_tests"
                        )
                    else:
                        self.log_result(
                            f"Invalid Login - {creds['username']}", 
                            False, 
                            f"Should have rejected invalid credentials: {data}", 
                            "auth_tests"
                        )
                else:
                    self.log_result(
                        f"Invalid Login - {creds['username']}", 
                        False, 
                        f"Unexpected HTTP {response.status_code}: {response.text}", 
                        "auth_tests"
                    )
            except Exception as e:
                self.log_result(
                    f"Invalid Login - {creds['username']}", 
                    False, 
                    f"Exception: {str(e)}", 
                    "auth_tests"
                )

    def test_file_upload(self):
        """Test Excel file upload and processing"""
        print("\n📁 Testing File Upload and Processing...")
        
        if not os.path.exists(TEST_FILE_PATH):
            self.log_result("File Upload", False, f"Test file not found: {TEST_FILE_PATH}", "upload_tests")
            return
        
        # Test with default commission rates
        self.upload_test_scenario(
            "Default Commission Rates",
            comision=5.0,
            comision_estructura=2.5,
            clasificacion="Abono a Tesorería",
            ejecutivo="operaciones@ibsgroup.mx"
        )
        
        # Test with custom commission rates
        self.upload_test_scenario(
            "Custom Commission Rates",
            comision=7.5,
            comision_estructura=3.0,
            clasificacion="Transacción Fondeada Directamente",
            ejecutivo="administracion@ibsgroup.mx"
        )
        
        # Test all classification types
        for i, clasificacion in enumerate(CLASSIFICATION_TYPES):
            self.upload_test_scenario(
                f"Classification - {clasificacion}",
                comision=5.0,
                comision_estructura=2.5,
                clasificacion=clasificacion,
                ejecutivo=f"Ejecutivo{(i % 2) + 1}"
            )
    
    def upload_test_scenario(self, test_name, comision, comision_estructura, clasificacion, ejecutivo):
        """Test a specific upload scenario"""
        try:
            with open(TEST_FILE_PATH, 'rb') as file:
                files = {'file': ('test_layout.xlsm', file, 'application/vnd.ms-excel.sheet.macroEnabled.12')}
                data = {
                    'comision': comision,
                    'comision_estructura': comision_estructura,
                    'clasificacion': clasificacion,
                    'ejecutivo': ejecutivo
                }
                
                response = self.session.post(f"{BACKEND_URL}/upload", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        # Verify extracted data
                        client_data = result.get("data", {}).get("client", {})
                        transaction_data = result.get("data", {}).get("transaction", {})
                        
                        validation_results = []
                        
                        # Check expected client values
                        if client_data.get("cliente") == EXPECTED_VALUES["cliente"]:
                            validation_results.append("✓ Cliente name correct")
                        else:
                            validation_results.append(f"✗ Cliente mismatch: got '{client_data.get('cliente')}', expected '{EXPECTED_VALUES['cliente']}'")
                        
                        if client_data.get("rfc") == EXPECTED_VALUES["rfc"]:
                            validation_results.append("✓ RFC correct")
                        else:
                            validation_results.append(f"✗ RFC mismatch: got '{client_data.get('rfc')}', expected '{EXPECTED_VALUES['rfc']}'")
                        
                        # Check financial values
                        if abs(transaction_data.get("subtotal", 0) - EXPECTED_VALUES["subtotal"]) < 0.01:
                            validation_results.append("✓ Subtotal correct")
                        else:
                            validation_results.append(f"✗ Subtotal mismatch: got {transaction_data.get('subtotal')}, expected {EXPECTED_VALUES['subtotal']}")
                        
                        if abs(transaction_data.get("iva", 0) - EXPECTED_VALUES["iva"]) < 0.01:
                            validation_results.append("✓ IVA correct")
                        else:
                            validation_results.append(f"✗ IVA mismatch: got {transaction_data.get('iva')}, expected {EXPECTED_VALUES['iva']}")
                        
                        if abs(transaction_data.get("total_factura", 0) - EXPECTED_VALUES["total_factura"]) < 0.01:
                            validation_results.append("✓ Total Factura correct")
                        else:
                            validation_results.append(f"✗ Total Factura mismatch: got {transaction_data.get('total_factura')}, expected {EXPECTED_VALUES['total_factura']}")
                        
                        # Check commission calculations
                        expected_comision_1 = EXPECTED_VALUES["subtotal"] * (comision / 100)
                        if abs(transaction_data.get("comision_1", 0) - expected_comision_1) < 0.01:
                            validation_results.append("✓ Comision 1 calculation correct")
                        else:
                            validation_results.append(f"✗ Comision 1 mismatch: got {transaction_data.get('comision_1')}, expected {expected_comision_1}")
                        
                        # Check classification
                        if transaction_data.get("clasificacion") == clasificacion:
                            validation_results.append("✓ Classification correct")
                        else:
                            validation_results.append(f"✗ Classification mismatch: got '{transaction_data.get('clasificacion')}', expected '{clasificacion}'")
                        
                        # Determine if test passed
                        failed_validations = [v for v in validation_results if v.startswith("✗")]
                        if not failed_validations:
                            self.log_result(test_name, True, f"Upload successful. {'; '.join(validation_results)}", "upload_tests")
                        else:
                            self.log_result(test_name, False, f"Validation failed. {'; '.join(validation_results)}", "upload_tests")
                    else:
                        self.log_result(test_name, False, f"Upload failed: {result.get('message', 'Unknown error')}", "upload_tests")
                else:
                    self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}", "upload_tests")
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}", "upload_tests")

    def test_treasury_balance(self):
        """Test treasury balance management"""
        print("\n💰 Testing Treasury Balance Management...")
        
        # First, upload an "Abono" transaction
        try:
            with open(TEST_FILE_PATH, 'rb') as file:
                files = {'file': ('test_layout.xlsm', file, 'application/vnd.ms-excel.sheet.macroEnabled.12')}
                data = {
                    'comision': 5.0,
                    'comision_estructura': 2.5,
                    'clasificacion': 'Abono a Tesorería',
                    'ejecutivo': 'operaciones@ibsgroup.mx'
                }
                
                response = self.session.post(f"{BACKEND_URL}/upload", files=files, data=data)
                if response.status_code == 200:
                    self.log_result("Treasury Abono Upload", True, "Abono transaction uploaded successfully", "treasury_tests")
                else:
                    self.log_result("Treasury Abono Upload", False, f"Failed to upload Abono: {response.text}", "treasury_tests")
                    
        except Exception as e:
            self.log_result("Treasury Abono Upload", False, f"Exception uploading Abono: {str(e)}", "treasury_tests")
        
        # Then upload a "Cargo/Retiro" transaction
        try:
            with open(TEST_FILE_PATH, 'rb') as file:
                files = {'file': ('test_layout.xlsm', file, 'application/vnd.ms-excel.sheet.macroEnabled.12')}
                data = {
                    'comision': 5.0,
                    'comision_estructura': 2.5,
                    'clasificacion': 'Cargo/Retiro de Tesorería',
                    'ejecutivo': 'Ejecutivo2'
                }
                
                response = self.session.post(f"{BACKEND_URL}/upload", files=files, data=data)
                if response.status_code == 200:
                    self.log_result("Treasury Cargo Upload", True, "Cargo transaction uploaded successfully", "treasury_tests")
                else:
                    self.log_result("Treasury Cargo Upload", False, f"Failed to upload Cargo: {response.text}", "treasury_tests")
                    
        except Exception as e:
            self.log_result("Treasury Cargo Upload", False, f"Exception uploading Cargo: {str(e)}", "treasury_tests")

    def test_cash_treasury_impact(self):
        """Test Afectación a Tesorería functionality in Caja Chica"""
        print("\n💸 Testing Cash Treasury Impact (Afectación a Tesorería)...")
        
        # First, ensure we have bank accounts and treasury data
        self.setup_test_data()
        
        # Test Scenario 1: Abono en caja chica + Abono a cuenta bancaria
        self.test_cash_to_bank_impact()
        
        # Test Scenario 2: Abono en caja chica + Abono a tesorería
        self.test_cash_to_treasury_impact()
    
    def setup_test_data(self):
        """Setup initial test data for cash treasury impact tests"""
        try:
            # Create bank accounts if they don't exist
            response = self.session.post(f"{BACKEND_URL}/bank_accounts/bulk_insert")
            if response.status_code == 200:
                self.log_result("Setup Bank Accounts", True, "Bank accounts initialized", "cash_tests")
            else:
                self.log_result("Setup Bank Accounts", False, f"Failed to setup bank accounts: {response.text}", "cash_tests")
        except Exception as e:
            self.log_result("Setup Bank Accounts", False, f"Exception setting up bank accounts: {str(e)}", "cash_tests")
    
    def get_bank_balance(self, account_name, fecha=None):
        """Get current balance for a specific bank account"""
        try:
            url = f"{BACKEND_URL}/bank_accounts/saldos"
            if fecha:
                url += f"?fecha={fecha}"
            response = self.session.get(url)
            if response.status_code == 200:
                accounts = response.json()
                for account in accounts:
                    if account.get("nombre") == account_name:
                        return account.get("saldo", 0.0)
                return 0.0
            else:
                return None
        except Exception as e:
            return None
    
    def get_treasury_balance(self, client_name):
        """Get current treasury balance for a specific client"""
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard/treasury")
            if response.status_code == 200:
                treasuries = response.json()
                for treasury in treasuries:
                    if treasury.get("client_name") == client_name:
                        return treasury.get("balance", 0.0)
                return 0.0
            else:
                return None
        except Exception as e:
            return None
    
    def test_cash_to_bank_impact(self):
        """Test Abono en caja chica + Abono a cuenta bancaria"""
        print("\n  🏦 Testing Cash to Bank Account Impact...")
        
        # Use a known bank account from the bulk insert
        account_name = "MESUBAJ COMERCIALIZADORA SA DE CV"
        test_amount = 5000.00
        
        # Get initial bank balance
        initial_balance = self.get_bank_balance(account_name)
        if initial_balance is None:
            self.log_result("Cash to Bank - Get Initial Balance", False, "Could not retrieve initial bank balance", "cash_tests")
            return
        
        # Create initial balance record if account has no balance
        if initial_balance == 0.0:
            try:
                data = {
                    'fecha': '2025-01-15',
                    'nombre_cuenta': account_name,
                    'saldo': 10000.00,  # Initial balance
                    'ejecutivo': 'Ejecutivo1'
                }
                response = self.session.post(f"{BACKEND_URL}/bancos/create", data=data)
                if response.status_code == 200:
                    initial_balance = 10000.00
                    self.log_result("Cash to Bank - Setup Initial Balance", True, f"Set initial balance to {initial_balance}", "cash_tests")
                else:
                    self.log_result("Cash to Bank - Setup Initial Balance", False, f"Failed to set initial balance: {response.text}", "cash_tests")
                    return
            except Exception as e:
                self.log_result("Cash to Bank - Setup Initial Balance", False, f"Exception setting initial balance: {str(e)}", "cash_tests")
                return
        
        # Create cash transaction with bank account impact
        try:
            data = {
                'fecha': '2025-01-15',
                'tipo_movimiento': 'Abono a Caja Chica',
                'origen_destino_tipo': 'Cuenta Bancaria',
                'origen_destino_nombre': f"{account_name} - BBVA (0121565796)",
                'afectacion_origen_destino': 'Abono',  # Should increase bank balance
                'cantidad': test_amount,
                'concepto': 'Test abono caja chica con afectación a cuenta bancaria',
                'ejecutivo': 'Ejecutivo1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/efectivo/create", data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Cash to Bank - Transaction Created", True, "Cash transaction created successfully", "cash_tests")
                    
                    # Verify bank balance increased
                    time.sleep(1)  # Small delay to ensure database update
                    new_balance = self.get_bank_balance(account_name)
                    
                    if new_balance is not None:
                        expected_balance = initial_balance + test_amount
                        if abs(new_balance - expected_balance) < 0.01:
                            self.log_result("Cash to Bank - Balance Verification", True, 
                                          f"Bank balance correctly increased from {initial_balance} to {new_balance} (expected {expected_balance})", "cash_tests")
                        else:
                            self.log_result("Cash to Bank - Balance Verification", False, 
                                          f"Bank balance incorrect: got {new_balance}, expected {expected_balance} (initial: {initial_balance})", "cash_tests")
                    else:
                        self.log_result("Cash to Bank - Balance Verification", False, "Could not retrieve updated bank balance", "cash_tests")
                else:
                    self.log_result("Cash to Bank - Transaction Created", False, f"Transaction failed: {result.get('message', 'Unknown error')}", "cash_tests")
            else:
                self.log_result("Cash to Bank - Transaction Created", False, f"HTTP {response.status_code}: {response.text}", "cash_tests")
                
        except Exception as e:
            self.log_result("Cash to Bank - Transaction Created", False, f"Exception: {str(e)}", "cash_tests")
    
    def test_cash_to_treasury_impact(self):
        """Test Abono en caja chica + Abono a tesorería"""
        print("\n  🏛️ Testing Cash to Treasury Impact...")
        
        client_name = "COMERCIALIZADORA ASAP DE CHIHUAHUA "  # Note trailing space
        test_amount = 5000.00
        
        # Get initial treasury balance
        initial_balance = self.get_treasury_balance(client_name)
        if initial_balance is None:
            self.log_result("Cash to Treasury - Get Initial Balance", False, "Could not retrieve initial treasury balance", "cash_tests")
            return
        
        # Create cash transaction with treasury impact
        try:
            data = {
                'fecha': '2025-01-15',
                'tipo_movimiento': 'Abono a Caja Chica',
                'origen_destino_tipo': 'Tesorería Cliente',
                'origen_destino_nombre': client_name,
                'afectacion_origen_destino': 'Abono',  # Should increase treasury balance
                'cantidad': test_amount,
                'concepto': 'Test abono caja chica con afectación a tesorería cliente',
                'ejecutivo': 'Ejecutivo1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/efectivo/create", data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Cash to Treasury - Transaction Created", True, "Cash transaction created successfully", "cash_tests")
                    
                    # Verify treasury balance increased
                    time.sleep(1)  # Small delay to ensure database update
                    new_balance = self.get_treasury_balance(client_name)
                    
                    if new_balance is not None:
                        expected_balance = initial_balance + test_amount
                        if abs(new_balance - expected_balance) < 0.01:
                            self.log_result("Cash to Treasury - Balance Verification", True, 
                                          f"Treasury balance correctly increased from {initial_balance} to {new_balance} (expected {expected_balance})", "cash_tests")
                        else:
                            self.log_result("Cash to Treasury - Balance Verification", False, 
                                          f"Treasury balance incorrect: got {new_balance}, expected {expected_balance} (initial: {initial_balance})", "cash_tests")
                    else:
                        self.log_result("Cash to Treasury - Balance Verification", False, "Could not retrieve updated treasury balance", "cash_tests")
                else:
                    self.log_result("Cash to Treasury - Transaction Created", False, f"Transaction failed: {result.get('message', 'Unknown error')}", "cash_tests")
            else:
                self.log_result("Cash to Treasury - Transaction Created", False, f"HTTP {response.status_code}: {response.text}", "cash_tests")
                
        except Exception as e:
            self.log_result("Cash to Treasury - Transaction Created", False, f"Exception: {str(e)}", "cash_tests")

    def test_dashboard_endpoints(self):
        """Test dashboard API endpoints"""
        print("\n📊 Testing Dashboard Endpoints...")
        
        # Test treasury balances endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard/treasury")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Treasury Dashboard", True, f"Retrieved {len(data)} treasury balance records", "dashboard_tests")
                else:
                    self.log_result("Treasury Dashboard", False, f"Expected list, got: {type(data)}", "dashboard_tests")
            else:
                self.log_result("Treasury Dashboard", False, f"HTTP {response.status_code}: {response.text}", "dashboard_tests")
        except Exception as e:
            self.log_result("Treasury Dashboard", False, f"Exception: {str(e)}", "dashboard_tests")
        
        # Test treasury balances with client filter
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard/treasury?client_name=COMERCIALIZADORA")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Treasury Dashboard with Filter", True, f"Filtered treasury data retrieved: {len(data)} records", "dashboard_tests")
            else:
                self.log_result("Treasury Dashboard with Filter", False, f"HTTP {response.status_code}: {response.text}", "dashboard_tests")
        except Exception as e:
            self.log_result("Treasury Dashboard with Filter", False, f"Exception: {str(e)}", "dashboard_tests")
        
        # Test transactions endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard/transactions")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Transactions Dashboard", True, f"Retrieved {len(data)} transaction records", "dashboard_tests")
                else:
                    self.log_result("Transactions Dashboard", False, f"Expected list, got: {type(data)}", "dashboard_tests")
            else:
                self.log_result("Transactions Dashboard", False, f"HTTP {response.status_code}: {response.text}", "dashboard_tests")
        except Exception as e:
            self.log_result("Transactions Dashboard", False, f"Exception: {str(e)}", "dashboard_tests")
        
        # Test transactions with client filter
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard/transactions?client_name=COMERCIALIZADORA")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Transactions Dashboard with Filter", True, f"Filtered transactions retrieved: {len(data)} records", "dashboard_tests")
            else:
                self.log_result("Transactions Dashboard with Filter", False, f"HTTP {response.status_code}: {response.text}", "dashboard_tests")
        except Exception as e:
            self.log_result("Transactions Dashboard with Filter", False, f"Exception: {str(e)}", "dashboard_tests")
        
        # Test clients endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/clients")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Clients Endpoint", True, f"Retrieved {len(data)} client records", "dashboard_tests")
                else:
                    self.log_result("Clients Endpoint", False, f"Expected list, got: {type(data)}", "dashboard_tests")
            else:
                self.log_result("Clients Endpoint", False, f"HTTP {response.status_code}: {response.text}", "dashboard_tests")
        except Exception as e:
            self.log_result("Clients Endpoint", False, f"Exception: {str(e)}", "dashboard_tests")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Treasury Management System Backend Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test file: {TEST_FILE_PATH}")
        print("=" * 60)
        
        # Run tests in order
        if self.test_health_check():
            self.test_authentication()
            self.test_file_upload()
            self.test_treasury_balance()
            self.test_cash_treasury_impact()  # New test for Afectación a Tesorería
            self.test_dashboard_endpoints()
        else:
            print("❌ Health check failed - skipping other tests")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        
        if self.results['summary']['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            for category in ['auth_tests', 'upload_tests', 'treasury_tests', 'cash_tests', 'dashboard_tests']:
                failed_tests = [t for t in self.results[category] if not t['success']]
                if failed_tests:
                    print(f"\n{category.upper()}:")
                    for test in failed_tests:
                        print(f"  - {test['test']}: {test['details']}")
        
        return self.results

if __name__ == "__main__":
    tester = TreasuryTestRunner()
    results = tester.run_all_tests()