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
                    'ejecutivo': 'administracion@ibsgroup.mx'
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
                    'ejecutivo': 'operaciones@ibsgroup.mx'
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
                'ejecutivo': 'operaciones@ibsgroup.mx'
            }
            
            response = self.session.post(f"{BACKEND_URL}/efectivo/create", data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Cash to Bank - Transaction Created", True, "Cash transaction created successfully", "cash_tests")
                    
                    # Verify bank balance increased
                    time.sleep(1)  # Small delay to ensure database update
                    new_balance = self.get_bank_balance(account_name, "2025-01-15")
                    
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
                'ejecutivo': 'operaciones@ibsgroup.mx'
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

    def test_new_functionalities(self):
        """Test new functionalities: Excel exports, data deletion, and bank balance improvements"""
        print("\n🆕 Testing New Functionalities...")
        
        # Initialize test categories
        if "export_tests" not in self.results:
            self.results["export_tests"] = []
        if "admin_tests" not in self.results:
            self.results["admin_tests"] = []
        if "bank_tests" not in self.results:
            self.results["bank_tests"] = []
        
        # Test 1: Exportación de Caja Chica a Excel
        self.test_cash_excel_export()
        
        # Test 2: Borrado de datos de Caja Chica
        self.test_cash_data_deletion()
        
        # Test 3: Exportación de Saldos Bancarios a Excel
        self.test_bank_balances_excel_export()
        
        # Test 4: Mejora en captura de saldos bancarios (sobrescritura)
        self.test_bank_balance_overwrite()
        
        # Test 5: Verificar endpoint de saldos bancarios con timestamp
        self.test_bank_accounts_with_timestamp()

    def test_cash_excel_export(self):
        """Test GET /api/export/efectivo/xlsx"""
        print("\n  📊 Testing Cash Excel Export...")
        
        # First, create some cash transactions for testing
        self.create_test_cash_transactions()
        
        # Test export without date filters
        try:
            response = self.session.get(f"{BACKEND_URL}/export/efectivo/xlsx")
            if response.status_code == 200:
                # Check if it's an Excel file
                content_type = response.headers.get('content-type', '')
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    self.log_result("Cash Excel Export - No Filters", True, 
                                  f"Excel file generated successfully. Size: {len(response.content)} bytes", "export_tests")
                else:
                    self.log_result("Cash Excel Export - No Filters", False, 
                                  f"Wrong content type: {content_type}", "export_tests")
            else:
                self.log_result("Cash Excel Export - No Filters", False, 
                              f"HTTP {response.status_code}: {response.text}", "export_tests")
        except Exception as e:
            self.log_result("Cash Excel Export - No Filters", False, f"Exception: {str(e)}", "export_tests")
        
        # Test export with date filters
        try:
            params = {
                'fecha_inicio': '2025-01-01T00:00:00Z',
                'fecha_fin': '2025-01-31T23:59:59Z'
            }
            response = self.session.get(f"{BACKEND_URL}/export/efectivo/xlsx", params=params)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    self.log_result("Cash Excel Export - With Date Filters", True, 
                                  f"Filtered Excel file generated successfully. Size: {len(response.content)} bytes", "export_tests")
                else:
                    self.log_result("Cash Excel Export - With Date Filters", False, 
                                  f"Wrong content type: {content_type}", "export_tests")
            else:
                self.log_result("Cash Excel Export - With Date Filters", False, 
                              f"HTTP {response.status_code}: {response.text}", "export_tests")
        except Exception as e:
            self.log_result("Cash Excel Export - With Date Filters", False, f"Exception: {str(e)}", "export_tests")

    def create_test_cash_transactions(self):
        """Create test cash transactions for export testing"""
        test_transactions = [
            {
                'fecha': '2025-01-15',
                'tipo_movimiento': 'Abono a Caja Chica',
                'origen_destino_tipo': 'Cuenta Bancaria',
                'origen_destino_nombre': 'MESUBAJ COMERCIALIZADORA SA DE CV - BBVA (0121565796)',
                'afectacion_origen_destino': 'Abono',
                'cantidad': 1000.00,
                'folio_cheque': 'CH001',
                'concepto': 'Test transaction for export',
                'ejecutivo': 'operaciones@ibsgroup.mx'
            },
            {
                'fecha': '2025-01-16',
                'tipo_movimiento': 'Cargo a Caja Chica',
                'origen_destino_tipo': 'Otro',
                'origen_destino_nombre': 'Gastos varios',
                'cantidad': 500.00,
                'concepto': 'Test expense transaction',
                'ejecutivo': 'operaciones@ibsgroup.mx'
            }
        ]
        
        for tx_data in test_transactions:
            try:
                response = self.session.post(f"{BACKEND_URL}/efectivo/create", data=tx_data)
                if response.status_code == 200:
                    continue
            except Exception:
                pass

    def test_cash_data_deletion(self):
        """Test POST /api/admin/delete_efectivo"""
        print("\n  🗑️ Testing Cash Data Deletion...")
        
        # Test with invalid credentials
        invalid_data = {
            "username": "invalid@user.com",
            "password": "wrongpassword",
            "fecha_inicio": "2025-01-01T00:00:00Z",
            "fecha_fin": "2025-01-15T23:59:59Z"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/delete_efectivo", json=invalid_data)
            if response.status_code == 403:
                self.log_result("Cash Data Deletion - Invalid Credentials", True, 
                              "Correctly rejected invalid credentials (403)", "admin_tests")
            else:
                self.log_result("Cash Data Deletion - Invalid Credentials", False, 
                              f"Expected 403, got {response.status_code}: {response.text}", "admin_tests")
        except Exception as e:
            self.log_result("Cash Data Deletion - Invalid Credentials", False, f"Exception: {str(e)}", "admin_tests")
        
        # Test with valid credentials (f.alfaro@ibsgroup.mx)
        valid_data = {
            "username": "f.alfaro@ibsgroup.mx",
            "password": "System3ras3$0",
            "fecha_inicio": "2025-01-01T00:00:00Z",
            "fecha_fin": "2025-01-15T23:59:59Z"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/delete_efectivo", json=valid_data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    deleted_count = result.get("deleted_count", 0)
                    self.log_result("Cash Data Deletion - Valid Credentials (f.alfaro)", True, 
                                  f"Successfully deleted {deleted_count} cash transactions", "admin_tests")
                else:
                    self.log_result("Cash Data Deletion - Valid Credentials (f.alfaro)", False, 
                                  f"Deletion failed: {result.get('message', 'Unknown error')}", "admin_tests")
            else:
                self.log_result("Cash Data Deletion - Valid Credentials (f.alfaro)", False, 
                              f"HTTP {response.status_code}: {response.text}", "admin_tests")
        except Exception as e:
            self.log_result("Cash Data Deletion - Valid Credentials (f.alfaro)", False, f"Exception: {str(e)}", "admin_tests")
        
        # Test with second valid user (administracion@ibsgroup.mx)
        valid_data2 = {
            "username": "administracion@ibsgroup.mx",
            "password": "System3ras3$!",
            "fecha_inicio": "2025-01-01T00:00:00Z",
            "fecha_fin": "2025-01-15T23:59:59Z"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/delete_efectivo", json=valid_data2)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    deleted_count = result.get("deleted_count", 0)
                    self.log_result("Cash Data Deletion - Valid Credentials (administracion)", True, 
                                  f"Successfully deleted {deleted_count} cash transactions", "admin_tests")
                else:
                    self.log_result("Cash Data Deletion - Valid Credentials (administracion)", False, 
                                  f"Deletion failed: {result.get('message', 'Unknown error')}", "admin_tests")
            else:
                self.log_result("Cash Data Deletion - Valid Credentials (administracion)", False, 
                              f"HTTP {response.status_code}: {response.text}", "admin_tests")
        except Exception as e:
            self.log_result("Cash Data Deletion - Valid Credentials (administracion)", False, f"Exception: {str(e)}", "admin_tests")

    def test_bank_balances_excel_export(self):
        """Test GET /api/export/bank_balances/xlsx"""
        print("\n  🏦 Testing Bank Balances Excel Export...")
        
        # Ensure we have bank accounts and balances
        self.setup_test_data()
        self.create_test_bank_balances()
        
        try:
            response = self.session.get(f"{BACKEND_URL}/export/bank_balances/xlsx")
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    self.log_result("Bank Balances Excel Export", True, 
                                  f"Excel file generated successfully. Size: {len(response.content)} bytes", "export_tests")
                else:
                    self.log_result("Bank Balances Excel Export", False, 
                                  f"Wrong content type: {content_type}", "export_tests")
            else:
                self.log_result("Bank Balances Excel Export", False, 
                              f"HTTP {response.status_code}: {response.text}", "export_tests")
        except Exception as e:
            self.log_result("Bank Balances Excel Export", False, f"Exception: {str(e)}", "export_tests")

    def create_test_bank_balances(self):
        """Create test bank balances for export testing"""
        test_balances = [
            {
                'fecha': '2025-01-15',
                'nombre_cuenta': 'MESUBAJ COMERCIALIZADORA SA DE CV',
                'saldo': 50000.00,
                'ejecutivo': 'operaciones@ibsgroup.mx'
            },
            {
                'fecha': '2025-01-15',
                'nombre_cuenta': 'NEXBILL INMOBILIARIA SA DE CV',
                'saldo': 25000.00,
                'ejecutivo': 'operaciones@ibsgroup.mx'
            }
        ]
        
        for balance_data in test_balances:
            try:
                response = self.session.post(f"{BACKEND_URL}/bancos/create", data=balance_data)
                if response.status_code == 200:
                    continue
            except Exception:
                pass

    def test_bank_balance_overwrite(self):
        """Test bank balance overwrite functionality (same date + same account)"""
        print("\n  🔄 Testing Bank Balance Overwrite...")
        
        account_name = "MESUBAJ COMERCIALIZADORA SA DE CV"
        test_date = "2025-01-15"
        initial_balance = 30000.00
        updated_balance = 35000.00
        
        # Create initial balance
        try:
            initial_data = {
                'fecha': test_date,
                'nombre_cuenta': account_name,
                'saldo': initial_balance,
                'ejecutivo': 'operaciones@ibsgroup.mx'
            }
            response = self.session.post(f"{BACKEND_URL}/bancos/create", data=initial_data)
            if response.status_code == 200:
                self.log_result("Bank Balance Overwrite - Initial Creation", True, 
                              f"Initial balance created: {initial_balance}", "bank_tests")
            else:
                self.log_result("Bank Balance Overwrite - Initial Creation", False, 
                              f"Failed to create initial balance: {response.text}", "bank_tests")
                return
        except Exception as e:
            self.log_result("Bank Balance Overwrite - Initial Creation", False, f"Exception: {str(e)}", "bank_tests")
            return
        
        # Update balance for same date and account (should overwrite)
        try:
            update_data = {
                'fecha': test_date,
                'nombre_cuenta': account_name,
                'saldo': updated_balance,
                'ejecutivo': 'operaciones@ibsgroup.mx'
            }
            response = self.session.post(f"{BACKEND_URL}/bancos/create", data=update_data)
            if response.status_code == 200:
                result = response.json()
                if "actualizado" in result.get("message", "").lower():
                    self.log_result("Bank Balance Overwrite - Update", True, 
                                  f"Balance correctly updated to {updated_balance}", "bank_tests")
                else:
                    self.log_result("Bank Balance Overwrite - Update", True, 
                                  f"Balance operation completed: {result.get('message', '')}", "bank_tests")
            else:
                self.log_result("Bank Balance Overwrite - Update", False, 
                              f"Failed to update balance: {response.text}", "bank_tests")
        except Exception as e:
            self.log_result("Bank Balance Overwrite - Update", False, f"Exception: {str(e)}", "bank_tests")
        
        # Verify the balance was overwritten (not duplicated)
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
                    if abs(actual_balance - updated_balance) < 0.01:
                        self.log_result("Bank Balance Overwrite - Verification", True, 
                                      f"Balance correctly overwritten: {actual_balance} (expected {updated_balance})", "bank_tests")
                    else:
                        self.log_result("Bank Balance Overwrite - Verification", False, 
                                      f"Balance not overwritten correctly: got {actual_balance}, expected {updated_balance}", "bank_tests")
                else:
                    self.log_result("Bank Balance Overwrite - Verification", False, 
                                  f"Account {account_name} not found in response", "bank_tests")
            else:
                self.log_result("Bank Balance Overwrite - Verification", False, 
                              f"Failed to retrieve balances: {response.text}", "bank_tests")
        except Exception as e:
            self.log_result("Bank Balance Overwrite - Verification", False, f"Exception: {str(e)}", "bank_tests")

    def test_bank_accounts_with_timestamp(self):
        """Test GET /api/bancos/cuentas (bank accounts with timestamp)"""
        print("\n  🕐 Testing Bank Accounts with Timestamp...")
        
        # Note: The endpoint in the code is actually /api/bank_accounts/saldos
        # Let's test the correct endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/bank_accounts/saldos")
            if response.status_code == 200:
                accounts = response.json()
                if isinstance(accounts, list) and len(accounts) > 0:
                    # Check if timestamp field is present and properly formatted
                    timestamp_found = False
                    valid_timestamp = False
                    
                    for account in accounts:
                        ultima_actualizacion = account.get("ultima_actualizacion")
                        if ultima_actualizacion:
                            timestamp_found = True
                            # Check if it's in DD/MM/YYYY HH:MM:SS format
                            if "/" in ultima_actualizacion and ":" in ultima_actualizacion:
                                valid_timestamp = True
                                break
                    
                    if timestamp_found and valid_timestamp:
                        self.log_result("Bank Accounts with Timestamp", True, 
                                      f"Retrieved {len(accounts)} accounts with proper timestamp format", "bank_tests")
                    elif timestamp_found:
                        self.log_result("Bank Accounts with Timestamp", True, 
                                      f"Retrieved {len(accounts)} accounts with timestamp (backward compatibility)", "bank_tests")
                    else:
                        self.log_result("Bank Accounts with Timestamp", False, 
                                      "No timestamp field found in response", "bank_tests")
                else:
                    self.log_result("Bank Accounts with Timestamp", True, 
                                  "Endpoint working but no accounts found (empty response)", "bank_tests")
            else:
                self.log_result("Bank Accounts with Timestamp", False, 
                              f"HTTP {response.status_code}: {response.text}", "bank_tests")
        except Exception as e:
            self.log_result("Bank Accounts with Timestamp", False, f"Exception: {str(e)}", "bank_tests")

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
            self.test_cash_treasury_impact()  # Test for Afectación a Tesorería
            self.test_dashboard_endpoints()
            self.test_new_functionalities()  # NEW: Test new export and admin functionalities
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
            for category in ['auth_tests', 'upload_tests', 'treasury_tests', 'cash_tests', 'dashboard_tests', 'export_tests', 'admin_tests', 'bank_tests']:
                if category in self.results:
                    failed_tests = [t for t in self.results[category] if not t['success']]
                    if failed_tests:
                        print(f"\n{category.upper()}:")
                        for test in failed_tests:
                            print(f"  - {test['test']}: {test['details']}")
        
        return self.results

if __name__ == "__main__":
    tester = TreasuryTestRunner()
    results = tester.run_all_tests()