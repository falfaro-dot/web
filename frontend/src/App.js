import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState('');
  const [activeView, setActiveView] = useState('dashboard');
  
  // Login state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  
  // Upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [comision, setComision] = useState(5.0);
  const [comisionEstructura, setComisionEstructura] = useState(2.5);
  const [clasificacion, setClasificacion] = useState('Abono a Tesorería');
  const [uploadMessage, setUploadMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Dashboard state
  const [treasuryBalances, setTreasuryBalances] = useState([]);
  const [operationsSummary, setOperationsSummary] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [dashboardTransactions, setDashboardTransactions] = useState([]);
  const [searchRFC, setSearchRFC] = useState('');
  const [searchDateStart, setSearchDateStart] = useState('');
  const [searchDateEnd, setSearchDateEnd] = useState('');
  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [cancelMotivo, setCancelMotivo] = useState('Solicitud del cliente');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteUsername, setDeleteUsername] = useState('');
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteDateStart, setDeleteDateStart] = useState('');
  const [deleteDateEnd, setDeleteDateEnd] = useState('');
  const [deleteCajaModalOpen, setDeleteCajaModalOpen] = useState(false);
  const [deleteCajaUsername, setDeleteCajaUsername] = useState('');
  const [deleteCajaPassword, setDeleteCajaPassword] = useState('');
  const [deleteCajaDateStart, setDeleteCajaDateStart] = useState('');
  const [deleteCajaDateEnd, setDeleteCajaDateEnd] = useState('');
  const [deleteConfirmModalOpen, setDeleteConfirmModalOpen] = useState(false);
  const [deleteCajaConfirmModalOpen, setDeleteCajaConfirmModalOpen] = useState(false);
  
  // Caja Chica state
  const [cajaFecha, setCajaFecha] = useState('');
  const [cajaTipoMovimiento, setCajaTipoMovimiento] = useState('Abono a Caja Chica');
  const [cajaOrigenDestinoTipo, setCajaOrigenDestinoTipo] = useState('Tesorería Cliente');
  const [cajaOrigenDestinoNombre, setCajaOrigenDestinoNombre] = useState('');
  const [cajaAfectacionOrigenDestino, setCajaAfectacionOrigenDestino] = useState('Cargo');
  const [cajaCantidad, setCajaCantidad] = useState('');
  const [cajaFolioCheque, setCajaFolioCheque] = useState('');
  const [cajaConcepto, setCajaConcepto] = useState('');
  const [cajaMessage, setCajaMessage] = useState('');
  const [cajaTransactions, setCajaTransactions] = useState([]);
  const [cajaSaldo, setCajaSaldo] = useState(0);
  const [treasuryClients, setTreasuryClients] = useState([]);
  
  // Bancos state
  const [bancoFecha, setBancoFecha] = useState('');
  const [bancoCuenta, setBancoCuenta] = useState('');
  const [bancoSaldo, setBancoSaldo] = useState('');
  const [bancoMessage, setBancoMessage] = useState('');
  const [bancoSaldoTotal, setBancoSaldoTotal] = useState(0);
  
  // Bank Accounts state
  const [cuentaEstructura, setCuentaEstructura] = useState('');
  const [cuentaNivel, setCuentaNivel] = useState('Primer Nivel');
  const [cuentaTipoMovimiento, setCuentaTipoMovimiento] = useState('TRASPASO SIMPLE');
  const [cuentaNombre, setCuentaNombre] = useState('');
  const [cuentaBanco, setCuentaBanco] = useState('');
  const [cuentaNumero, setCuentaNumero] = useState('');
  const [cuentaClabe, setCuentaClabe] = useState('');
  const [cuentaMessage, setCuentaMessage] = useState('');
  const [bankAccounts, setBankAccounts] = useState([]);
  const [bankAccountsWithBalances, setBankAccountsWithBalances] = useState([]);
  
  // Check login status
  useEffect(() => {
    const user = localStorage.getItem('username');
    if (user) {
      setIsLoggedIn(true);
      setCurrentUser(user);
    }
  }, []);
  
  // Login handler
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIsLoggedIn(true);
        setCurrentUser(username);
        localStorage.setItem('username', username);
      } else {
        setLoginError(data.message);
      }
    } catch (error) {
      setLoginError('Error de conexión. Intente nuevamente.');
    }
  };
  
  // Logout handler
  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser('');
    localStorage.removeItem('username');
    setUsername('');
    setPassword('');
  };
  
  // File upload handler
  const handleFileUpload = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setUploadMessage('Por favor seleccione un archivo');
      return;
    }
    
    setIsProcessing(true);
    setUploadMessage('');
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('comision', comision);
      formData.append('comision_estructura', comisionEstructura);
      formData.append('clasificacion', clasificacion);
      formData.append('ejecutivo', currentUser);
      
      const response = await fetch(`${BACKEND_URL}/api/upload`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (data.success) {
        setUploadMessage('✓ Archivo procesado exitosamente');
        setSelectedFile(null);
        document.getElementById('fileInput').value = '';
      } else {
        setUploadMessage('✗ Error: ' + data.message);
      }
    } catch (error) {
      setUploadMessage('✗ Error de conexión: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Load treasury balances
  const loadTreasuryBalances = async () => {
    try {
      const url = searchRFC 
        ? `${BACKEND_URL}/api/dashboard/treasury?rfc=${encodeURIComponent(searchRFC)}`
        : `${BACKEND_URL}/api/dashboard/treasury`;
      
      const response = await fetch(url);
      const data = await response.json();
      setTreasuryBalances(data);
    } catch (error) {
      console.error('Error loading treasury balances:', error);
    }
  };
  
  // Load operations summary
  const loadOperationsSummary = async () => {
    try {
      let url = `${BACKEND_URL}/api/dashboard/operations_summary?`;
      if (searchDateStart) url += `fecha_inicio=${searchDateStart}T00:00:00Z&`;
      if (searchDateEnd) url += `fecha_fin=${searchDateEnd}T23:59:59Z&`;
      
      const response = await fetch(url);
      const data = await response.json();
      setOperationsSummary(data);
    } catch (error) {
      console.error('Error loading operations summary:', error);
    }
  };
  
  // Load transactions
  const loadTransactions = async () => {
    try {
      let url = `${BACKEND_URL}/api/dashboard/transactions?`;
      if (searchRFC) url += `client_name=${encodeURIComponent(searchRFC)}&`;
      if (searchDateStart) url += `fecha_inicio=${searchDateStart}T00:00:00Z&`;
      if (searchDateEnd) url += `fecha_fin=${searchDateEnd}T23:59:59Z&`;
      
      const response = await fetch(url);
      const data = await response.json();
      setTransactions(data);
    } catch (error) {
      console.error('Error loading transactions:', error);
    }
  };
  
  // Load dashboard transactions for calculations
  const loadDashboardTransactions = async () => {
    try {
      let url = `${BACKEND_URL}/api/dashboard/transactions?`;
      if (searchDateStart) url += `fecha_inicio=${searchDateStart}T00:00:00Z&`;
      if (searchDateEnd) url += `fecha_fin=${searchDateEnd}T23:59:59Z&`;
      
      const response = await fetch(url);
      const data = await response.json();
      setDashboardTransactions(data);
    } catch (error) {
      console.error('Error loading dashboard transactions:', error);
    }
  };
  
  // Handle Caja Chica submission
  const handleCajaChicaSubmit = async (e) => {
    e.preventDefault();
    setCajaMessage('');
    
    try {
      const formData = new FormData();
      formData.append('fecha', cajaFecha);
      formData.append('tipo_movimiento', cajaTipoMovimiento);
      formData.append('origen_destino_tipo', cajaOrigenDestinoTipo);
      formData.append('origen_destino_nombre', cajaOrigenDestinoNombre);
      formData.append('afectacion_origen_destino', cajaAfectacionOrigenDestino);
      formData.append('cantidad', cajaCantidad);
      formData.append('folio_cheque', cajaFolioCheque);
      formData.append('concepto', cajaConcepto);
      formData.append('ejecutivo', currentUser);
      
      const response = await fetch(`${BACKEND_URL}/api/efectivo/create`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      if (data.success) {
        setCajaMessage('✓ Transacción de Caja Chica registrada exitosamente');
        setCajaFecha('');
        setCajaOrigenDestinoNombre('');
        setCajaCantidad('');
        setCajaFolioCheque('');
        setCajaConcepto('');
        loadCajaChicaTransactions();
      }
    } catch (error) {
      setCajaMessage('✗ Error: ' + error.message);
    }
  };
  
  // Handle banco submission
  const handleBancoSubmit = async (e) => {
    e.preventDefault();
    setBancoMessage('');
    
    try {
      const formData = new FormData();
      formData.append('fecha', bancoFecha);
      formData.append('nombre_cuenta', bancoCuenta);
      formData.append('saldo', bancoSaldo);
      formData.append('ejecutivo', currentUser);
      
      const response = await fetch(`${BACKEND_URL}/api/bancos/create`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      if (data.success) {
        setBancoMessage('✓ Saldo bancario registrado exitosamente');
        setBancoFecha('');
        setBancoCuenta('');
        setBancoSaldo('');
      }
    } catch (error) {
      setBancoMessage('✗ Error: ' + error.message);
    }
  };
  
  // Load Caja Chica transactions
  const loadCajaChicaTransactions = async () => {
    try {
      let url = `${BACKEND_URL}/api/efectivo/transactions?`;
      if (searchDateStart) url += `fecha_inicio=${searchDateStart}&`;
      if (searchDateEnd) url += `fecha_fin=${searchDateEnd}&`;
      
      const response = await fetch(url);
      const data = await response.json();
      setCajaTransactions(data);
    } catch (error) {
      console.error('Error loading Caja Chica:', error);
    }
  };
  
  // Load treasury clients
  const loadTreasuryClients = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/treasury/clients`);
      const data = await response.json();
      setTreasuryClients(data);
    } catch (error) {
      console.error('Error loading treasury clients:', error);
    }
  };
  
  // Load saldos for dashboard
  const loadSaldos = async () => {
    try {
      const fecha = searchDateEnd || searchDateStart || new Date().toISOString().split('T')[0];
      
      // Caja Chica (was Efectivo)
      const cajaResp = await fetch(`${BACKEND_URL}/api/efectivo/saldo?fecha=${fecha}`);
      const cajaData = await cajaResp.json();
      setCajaSaldo(cajaData.saldo);
      
      // Bancos
      const bancosResp = await fetch(`${BACKEND_URL}/api/bancos/saldo_total?fecha=${fecha}`);
      const bancosData = await bancosResp.json();
      setBancoSaldoTotal(bancosData.saldo_total);
    } catch (error) {
      console.error('Error loading saldos:', error);
    }
  };
  
  // Handle bank account creation
  const handleCuentaSubmit = async (e) => {
    e.preventDefault();
    setCuentaMessage('');
    
    try {
      const formData = new FormData();
      formData.append('estructura', cuentaEstructura);
      formData.append('nivel', cuentaNivel);
      formData.append('tipo_movimiento', cuentaTipoMovimiento);
      formData.append('nombre', cuentaNombre);
      formData.append('banco', cuentaBanco);
      formData.append('cuenta', cuentaNumero);
      formData.append('clabe', cuentaClabe);
      
      const response = await fetch(`${BACKEND_URL}/api/bank_accounts/create`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      if (data.success) {
        setCuentaMessage('✓ Cuenta bancaria registrada exitosamente');
        setCuentaEstructura('');
        setCuentaNombre('');
        setCuentaBanco('');
        setCuentaNumero('');
        setCuentaClabe('');
        loadBankAccounts();
      }
    } catch (error) {
      setCuentaMessage('✗ Error: ' + error.message);
    }
  };
  
  // Load bank accounts
  const loadBankAccounts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/bank_accounts`);
      const data = await response.json();
      setBankAccounts(data);
    } catch (error) {
      console.error('Error loading bank accounts:', error);
    }
  };
  
  // Load bank accounts with balances
  const loadBankAccountsWithBalances = async () => {
    try {
      const fecha = searchDateEnd || searchDateStart || new Date().toISOString().split('T')[0];
      const response = await fetch(`${BACKEND_URL}/api/bank_accounts/saldos?fecha=${fecha}`);
      const data = await response.json();
      setBankAccountsWithBalances(data);
    } catch (error) {
      console.error('Error loading bank accounts with balances:', error);
    }
  };
  
  // Initialize bank accounts data
  const initializeBankAccounts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/bank_accounts/bulk_insert`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        alert(data.message);
        loadBankAccounts();
      }
    } catch (error) {
      alert('Error inicializando cuentas: ' + error.message);
    }
  };
  
  // Load dashboard data when view changes
  useEffect(() => {
    if (activeView === 'dashboard') {
      loadTreasuryBalances();
      loadOperationsSummary();
      loadDashboardTransactions();
      loadSaldos();
    } else if (activeView === 'transactions') {
      loadTransactions();
    } else if (activeView === 'efectivo') {
      loadCajaChicaTransactions();
      loadTreasuryClients();
    } else if (activeView === 'cuentas') {
      loadBankAccounts();
      loadBankAccountsWithBalances();
    }
  }, [activeView]);
  
  // Delete data by date range
  const handleDeleteData = async () => {
    console.log('handleDeleteData called');
    console.log('deleteDateStart:', deleteDateStart);
    console.log('deleteDateEnd:', deleteDateEnd);
    console.log('deleteUsername:', deleteUsername);
    console.log('deletePassword:', deletePassword ? '***' : 'empty');
    
    if (!deleteDateStart || !deleteDateEnd) {
      alert('Por favor seleccione ambas fechas');
      return;
    }
    
    if (!deleteUsername || !deletePassword) {
      alert('Por favor ingrese usuario y contraseña');
      return;
    }
    
    // Open confirmation modal instead of using window.confirm
    setDeleteConfirmModalOpen(true);
  };
  
  // Execute delete after confirmation
  const executeDeleteData = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/delete_data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: deleteUsername,
          password: deletePassword,
          fecha_inicio: deleteDateStart + 'T00:00:00Z',
          fecha_fin: deleteDateEnd + 'T23:59:59Z'
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        alert(`✓ ${data.deleted_count} transacciones eliminadas exitosamente`);
        setDeleteConfirmModalOpen(false);
        setDeleteModalOpen(false);
        setDeleteUsername('');
        setDeletePassword('');
        setDeleteDateStart('');
        setDeleteDateEnd('');
        loadTransactions();
      } else {
        alert('✗ ' + (data.detail || 'Error eliminando datos'));
        setDeleteConfirmModalOpen(false);
      }
    } catch (error) {
      alert('✗ Error de conexión: ' + error.message);
      setDeleteConfirmModalOpen(false);
    }
  };

  // Delete Caja Chica data by date range
  const handleDeleteCajaData = async () => {
    console.log('handleDeleteCajaData called');
    console.log('deleteCajaDateStart:', deleteCajaDateStart);
    console.log('deleteCajaDateEnd:', deleteCajaDateEnd);
    console.log('deleteCajaUsername:', deleteCajaUsername);
    console.log('deleteCajaPassword:', deleteCajaPassword ? '***' : 'empty');
    
    if (!deleteCajaDateStart || !deleteCajaDateEnd) {
      alert('Por favor seleccione ambas fechas');
      return;
    }
    
    if (!deleteCajaUsername || !deleteCajaPassword) {
      alert('Por favor ingrese usuario y contraseña');
      return;
    }
    
    // Open confirmation modal instead of using window.confirm
    setDeleteCajaConfirmModalOpen(true);
  };
  
  // Execute delete Caja Chica after confirmation
  const executeDeleteCajaData = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/delete_efectivo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: deleteCajaUsername,
          password: deleteCajaPassword,
          fecha_inicio: deleteCajaDateStart + 'T00:00:00Z',
          fecha_fin: deleteCajaDateEnd + 'T23:59:59Z'
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        alert(`✓ ${data.deleted_count} movimientos de Caja Chica eliminados exitosamente`);
        setDeleteCajaConfirmModalOpen(false);
        setDeleteCajaModalOpen(false);
        setDeleteCajaUsername('');
        setDeleteCajaPassword('');
        setDeleteCajaDateStart('');
        setDeleteCajaDateEnd('');
        loadCajaChicaTransactions();
      } else {
        alert('✗ ' + (data.detail || 'Error eliminando datos'));
        setDeleteCajaConfirmModalOpen(false);
      }
    } catch (error) {
      alert('✗ Error de conexión: ' + error.message);
      setDeleteCajaConfirmModalOpen(false);
    }
  };

  
  // Cancel transaction
  const handleCancelTransaction = async () => {
    if (!selectedTransaction) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/transactions/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_id: selectedTransaction.id,
          motivo: cancelMotivo,
          ejecutivo: currentUser
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert('Transacción cancelada exitosamente');
        loadTransactions();
        setCancelModalOpen(false);
        setSelectedTransaction(null);
      } else {
        alert('Error cancelando transacción');
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    }
  };
  
  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(amount);
  };
  
  // Format date
  const formatDate = (isoDate) => {
    return new Date(isoDate).toLocaleString('es-MX', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  // Login Screen
  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-box">
          <div className="logo-container">
            <img src="https://customer-assets.emergentagent.com/job_finance-parser-4/artifacts/zggp8w9v_logo2.jpg" alt="IBS Group" className="logo" />
          </div>
          <h1>Sistema de Registro de Operaciones</h1>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Usuario</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="usuario@ibsgroup.mx"
                required
              />
            </div>
            <div className="form-group">
              <label>Contraseña</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            {loginError && <div className="error-message">{loginError}</div>}
            <button type="submit" className="btn-primary">Iniciar Sesión</button>
          </form>
        </div>
      </div>
    );
  }
  
  // Main Application
  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <img src="https://customer-assets.emergentagent.com/job_finance-parser-4/artifacts/ums9p6bn_IBS%20GROUP-LOGO_SYMBOL-2.png" alt="IBS" className="header-logo" />
            <h1>Sistema de Registro de Operaciones</h1>
          </div>
          <div className="header-right">
            <span className="user-info">👤 {currentUser}</span>
            <button onClick={handleLogout} className="btn-logout">Cerrar Sesión</button>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="app-nav">
        <button
          className={activeView === 'dashboard' ? 'nav-btn active' : 'nav-btn'}
          onClick={() => setActiveView('dashboard')}
        >
          📊 Dashboard
        </button>
        <button
          className={activeView === 'transactions' ? 'nav-btn active' : 'nav-btn'}
          onClick={() => setActiveView('transactions')}
        >
          📋 Transacciones
        </button>
        <button
          className={activeView === 'upload' ? 'nav-btn active' : 'nav-btn'}
          onClick={() => setActiveView('upload')}
        >
          📤 Cargar información
        </button>
        <button
          className={activeView === 'efectivo' ? 'nav-btn active' : 'nav-btn'}
          onClick={() => setActiveView('efectivo')}
        >
          💵 Caja Chica
        </button>
        <button
          className={activeView === 'cuentas' ? 'nav-btn active' : 'nav-btn'}
          onClick={() => setActiveView('cuentas')}
        >
          🏦 Cuentas Bancarias
        </button>
      </nav>
      
      {/* Main Content */}
      <main className="app-main">
        {activeView === 'upload' && (
          <div className="upload-section">
            {/* Excel Upload */}
            <div className="section-card">
              <h2>📁 Cargar Archivo Excel</h2>
              <form onSubmit={handleFileUpload}>
                <div className="form-group">
                  <label>Archivo Layout (.xlsm)</label>
                  <input
                    id="fileInput"
                    type="file"
                    accept=".xlsm,.xlsx"
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                    required
                  />
                  {selectedFile && <span className="file-name">✓ {selectedFile.name}</span>}
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Comisión 1 (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={comision}
                      onChange={(e) => setComision(parseFloat(e.target.value))}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Comisión Estructura (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={comisionEstructura}
                      onChange={(e) => setComisionEstructura(parseFloat(e.target.value))}
                      required
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Clasificación de Transacción</label>
                  <select
                    value={clasificacion}
                    onChange={(e) => setClasificacion(e.target.value)}
                    required
                  >
                    <option value="Abono a Tesorería">Abono a Tesorería</option>
                    <option value="Cargo/Retiro de Tesorería">Cargo/Retiro de Tesorería</option>
                    <option value="Transacción Fondeada Directamente">Transacción Fondeada Directamente</option>
                    <option value="Transacción de Efectivo">Transacción de Efectivo</option>
                  </select>
                </div>
                
                {uploadMessage && (
                  <div className={uploadMessage.includes('✓') ? 'success-message' : 'error-message'}>
                    {uploadMessage}
                  </div>
                )}
                
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isProcessing}
                >
                  {isProcessing ? '⏳ Procesando...' : '🚀 Procesar Archivo'}
                </button>
              </form>
            </div>
            
            {/* Captura de Caja Chica */}
            <div className="section-card">
              <h2>💵 Captura de Movimientos - Caja Chica</h2>
              <form onSubmit={handleCajaChicaSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Fecha</label>
                    <input
                      type="date"
                      value={cajaFecha}
                      onChange={(e) => setCajaFecha(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Tipo de Movimiento</label>
                    <select
                      value={cajaTipoMovimiento}
                      onChange={(e) => setCajaTipoMovimiento(e.target.value)}
                      required
                    >
                      <option value="Abono a Caja Chica">Abono a Caja Chica</option>
                      <option value="Cargo a Caja Chica">Cargo a Caja Chica</option>
                    </select>
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Origen/Destino</label>
                    <select
                      value={cajaOrigenDestinoTipo}
                      onChange={(e) => {
                        setCajaOrigenDestinoTipo(e.target.value);
                        setCajaOrigenDestinoNombre('');
                        // Set default afectacion based on tipo_movimiento
                        if (cajaTipoMovimiento === 'Abono a Caja Chica') {
                          setCajaAfectacionOrigenDestino('Cargo');
                        } else {
                          setCajaAfectacionOrigenDestino('Abono');
                        }
                      }}
                      required
                    >
                      <option value="Tesorería Cliente">Tesorería Cliente</option>
                      <option value="Cuenta Bancaria">Cuenta Bancaria</option>
                      <option value="Otro">Otro</option>
                    </select>
                  </div>
                  
                  {(cajaOrigenDestinoTipo === 'Tesorería Cliente' || cajaOrigenDestinoTipo === 'Cuenta Bancaria') && (
                    <div className="form-group">
                      <label>Afectación a {cajaOrigenDestinoTipo === 'Tesorería Cliente' ? 'Tesorería' : 'Cuenta'}</label>
                      <select
                        value={cajaAfectacionOrigenDestino}
                        onChange={(e) => setCajaAfectacionOrigenDestino(e.target.value)}
                        required
                        className="afectacion-select"
                      >
                        <option value="Cargo">Cargo (Disminuye Saldo)</option>
                        <option value="Abono">Abono (Aumenta Saldo)</option>
                      </select>
                      <small style={{display: 'block', marginTop: '5px', color: '#666'}}>
                        {cajaAfectacionOrigenDestino === 'Cargo' ? 
                          '⚠️ Restará del saldo actual' : 
                          '✓ Sumará al saldo actual'}
                      </small>
                    </div>
                  )}
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>
                      {cajaOrigenDestinoTipo === 'Tesorería Cliente' ? 'Cliente' :
                       cajaOrigenDestinoTipo === 'Cuenta Bancaria' ? 'Cuenta' : 'Descripción'}
                    </label>
                    {cajaOrigenDestinoTipo === 'Tesorería Cliente' ? (
                      <select
                        value={cajaOrigenDestinoNombre}
                        onChange={(e) => setCajaOrigenDestinoNombre(e.target.value)}
                        required
                        onFocus={() => {
                          if (treasuryClients.length === 0) loadTreasuryClients();
                        }}
                      >
                        <option value="">Seleccione un cliente</option>
                        {treasuryClients.map((client, idx) => (
                          <option key={idx} value={client.client_name}>
                            {client.client_name} (Saldo: {formatCurrency(client.balance)})
                          </option>
                        ))}
                      </select>
                    ) : cajaOrigenDestinoTipo === 'Cuenta Bancaria' ? (
                      <select
                        value={cajaOrigenDestinoNombre}
                        onChange={(e) => setCajaOrigenDestinoNombre(e.target.value)}
                        required
                        onFocus={() => {
                          if (bankAccounts.length === 0) loadBankAccounts();
                        }}
                      >
                        <option value="">Seleccione una cuenta</option>
                        {bankAccounts.map((acc, idx) => (
                          <option key={idx} value={`${acc.nombre} - ${acc.banco} (${acc.cuenta})`}>
                            {acc.nombre} - {acc.banco} ({acc.cuenta})
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={cajaOrigenDestinoNombre}
                        onChange={(e) => setCajaOrigenDestinoNombre(e.target.value)}
                        placeholder="Descripción del origen/destino"
                        required
                      />
                    )}
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Cantidad</label>
                    <input
                      type="number"
                      step="0.01"
                      value={cajaCantidad}
                      onChange={(e) => setCajaCantidad(e.target.value)}
                      placeholder="0.00"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Folio de Cheque (Opcional)</label>
                    <input
                      type="text"
                      value={cajaFolioCheque}
                      onChange={(e) => setCajaFolioCheque(e.target.value)}
                      placeholder="Ej: 356"
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Concepto</label>
                  <textarea
                    value={cajaConcepto}
                    onChange={(e) => setCajaConcepto(e.target.value)}
                    placeholder="Describa el concepto del movimiento"
                    rows="2"
                    required
                    style={{width: '100%', padding: '12px', borderRadius: '6px', border: '2px solid #e0e0e0'}}
                  />
                </div>
                
                {cajaMessage && (
                  <div className={cajaMessage.includes('✓') ? 'success-message' : 'error-message'}>
                    {cajaMessage}
                  </div>
                )}
                
                <button type="submit" className="btn-primary">
                  💾 Registrar Movimiento
                </button>
              </form>
            </div>
            
            {/* Captura de Saldos Bancos */}
            <div className="section-card">
              <h2>🏦 Captura de Saldos Bancos</h2>
              <form onSubmit={handleBancoSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Fecha</label>
                    <input
                      type="date"
                      value={bancoFecha}
                      onChange={(e) => setBancoFecha(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Cuenta Bancaria</label>
                    <select
                      value={bancoCuenta}
                      onChange={(e) => setBancoCuenta(e.target.value)}
                      required
                      onFocus={() => {
                        if (bankAccounts.length === 0) loadBankAccounts();
                      }}
                    >
                      <option value="">Seleccione una cuenta</option>
                      {bankAccounts.map((acc, idx) => (
                        <option key={idx} value={acc.nombre}>
                          {acc.nombre} - {acc.banco} ({acc.cuenta})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Saldo de la Cuenta</label>
                  <input
                    type="number"
                    step="0.01"
                    value={bancoSaldo}
                    onChange={(e) => setBancoSaldo(e.target.value)}
                    placeholder="0.00"
                    required
                  />
                </div>
                
                {bancoMessage && (
                  <div className={bancoMessage.includes('✓') ? 'success-message' : 'error-message'}>
                    {bancoMessage}
                  </div>
                )}
                
                <button type="submit" className="btn-primary">
                  💾 Registrar Saldo Bancario
                </button>
              </form>
            </div>
          </div>
        )}
        
        {activeView === 'dashboard' && (
          <div className="dashboard-section">
            {/* Search Filters */}
            <div className="section-card">
              <h2>🔍 Filtros de Búsqueda</h2>
              <div className="filter-row">
                <div className="form-group">
                  <label>RFC Cliente</label>
                  <input
                    type="text"
                    placeholder="Buscar por RFC"
                    value={searchRFC}
                    onChange={(e) => setSearchRFC(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Fecha Inicio</label>
                  <input
                    type="date"
                    value={searchDateStart}
                    onChange={(e) => setSearchDateStart(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Fecha Fin</label>
                  <input
                    type="date"
                    value={searchDateEnd}
                    onChange={(e) => setSearchDateEnd(e.target.value)}
                  />
                </div>
                <button
                  className="btn-search"
                  onClick={() => {
                    loadTreasuryBalances();
                    loadOperationsSummary();
                    loadDashboardTransactions();
                    loadSaldos();
                  }}
                >
                  🔍 Buscar
                </button>
              </div>
            </div>
            
            {/* First Row - Balance Tesorería y Total Facturado */}
            <div className="totals-grid-2x2">
              <div className="total-card total-card-grid">
                <div className="total-content">
                  <div className="total-label">
                    <span className="total-icon">💎</span>
                    <span>Balance Total de Tesorería</span>
                  </div>
                  <div className="total-amount">
                    {formatCurrency(
                      treasuryBalances.reduce((sum, balance) => sum + balance.balance, 0)
                    )}
                  </div>
                </div>
              </div>
              
              <div className="total-card total-card-grid">
                <div className="total-content">
                  <div className="total-label">
                    <span className="total-icon">📊</span>
                    <span>Total Facturado</span>
                  </div>
                  <div className="total-amount">
                    {formatCurrency(
                      operationsSummary.reduce((sum, op) => sum + (op.total_facturado || 0), 0)
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Second Row - Comisiones IBSG y Financiados */}
            <div className="totals-grid-2x2">
              <div className="total-card total-card-grid">
                <div className="total-content">
                  <div className="total-label">
                    <span className="total-icon">💰</span>
                    <span>Total Comisiones IBSG</span>
                  </div>
                  <div className="total-amount">
                    {formatCurrency(
                      operationsSummary.reduce((sum, op) => sum + (op.total_comision_ibsg || 0), 0)
                    )}
                  </div>
                </div>
              </div>
              
              <div className="total-card total-card-grid">
                <div className="total-content">
                  <div className="total-label">
                    <span className="total-icon">💵</span>
                    <span>Total de Financiados</span>
                  </div>
                  <div className="total-amount">
                    {formatCurrency(
                      dashboardTransactions
                        .filter(tx => tx.estado === 'Pagado' && (tx.fondeado || 'Pendiente') === 'Pendiente')
                        .reduce((sum, tx) => sum + tx.retorno_1, 0)
                    )}
                  </div>
                </div>
              </div>
              
            </div>
            
            {/* Third Row - Retornos Enviados y Pagados */}
            <div className="totals-grid-2x2">
              <div className="total-card total-card-grid">
                <div className="total-content">
                  <div className="total-label">
                    <span className="total-icon">📤</span>
                    <span>Retornos Enviados</span>
                  </div>
                  <div className="total-amount">
                    {formatCurrency(
                      dashboardTransactions
                        .filter(tx => (tx.estado || 'Enviado') === 'Enviado')
                        .reduce((sum, tx) => sum + tx.retorno_1, 0)
                    )}
                  </div>
                </div>
              </div>
              
              <div className="total-card total-card-grid">
                <div className="total-content">
                  <div className="total-label">
                    <span className="total-icon">✅</span>
                    <span>Retornos Pagados</span>
                  </div>
                  <div className="total-amount">
                    {formatCurrency(
                      dashboardTransactions
                        .filter(tx => tx.estado === 'Pagado')
                        .reduce((sum, tx) => sum + tx.retorno_1, 0)
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Fourth Row - Saldos en Bancos y Efectivo */}
            <div className="totals-grid-2x2">
              <div className="total-card total-card-grid">
                <div className="total-content">
                  <div className="total-label">
                    <span className="total-icon">🏦</span>
                    <span>Saldos en Bancos</span>
                  </div>
                  <div className="total-amount">
                    {formatCurrency(bancoSaldoTotal)}
                  </div>
                </div>
              </div>
              
              <div className="total-card total-card-grid">
                <div className="total-content">
                  <div className="total-label">
                    <span className="total-icon">💵</span>
                    <span>Saldo Caja Chica</span>
                  </div>
                  <div className="total-amount">
                    {formatCurrency(cajaSaldo)}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Treasury Balances */}
            <div className="section-card">
              <div className="transactions-header">
                <h2>💰 Balance de Tesorería por Cliente</h2>
                <div className="export-buttons">
                  <button
                    className="btn-export"
                    onClick={() => {
                      let url = `${BACKEND_URL}/api/export/treasury/xlsx?`;
                      if (searchRFC) url += `rfc=${encodeURIComponent(searchRFC)}&`;
                      window.open(url, '_blank');
                    }}
                  >
                    📥 Descargar Excel
                  </button>
                </div>
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>RFC</th>
                      <th>Cliente</th>
                      <th>Balance Actual</th>
                      <th>Última Actualización</th>
                    </tr>
                  </thead>
                  <tbody>
                    {treasuryBalances.length === 0 ? (
                      <tr>
                        <td colSpan="4" className="no-data">No hay datos de tesorería</td>
                      </tr>
                    ) : (
                      treasuryBalances.map((balance) => (
                        <tr key={balance.client_id}>
                          <td className="rfc-cell">{balance.client_rfc || 'N/A'}</td>
                          <td>{balance.client_name}</td>
                          <td className={balance.balance >= 0 ? 'positive' : 'negative'}>
                            {formatCurrency(balance.balance)}
                          </td>
                          <td>{formatDate(balance.last_updated)}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
            
            {/* Operations Summary */}
            <div className="section-card">
              <div className="transactions-header">
                <h2>📊 Resumen de Operaciones por Cliente</h2>
                <div className="export-buttons">
                  <button
                    className="btn-export"
                    onClick={() => {
                      let url = `${BACKEND_URL}/api/export/operations_summary/xlsx?`;
                      if (searchDateStart) url += `fecha_inicio=${searchDateStart}T00:00:00Z&`;
                      if (searchDateEnd) url += `fecha_fin=${searchDateEnd}T23:59:59Z&`;
                      window.open(url, '_blank');
                    }}
                  >
                    📥 Descargar Excel
                  </button>
                </div>
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>RFC</th>
                      <th>Cliente</th>
                      <th>Transacciones</th>
                      <th>Total Facturado</th>
                      <th>Comisiones</th>
                      <th>Comisión Estructura</th>
                      <th>Comisión IBSG</th>
                      <th>Retornos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {operationsSummary.length === 0 ? (
                      <tr>
                        <td colSpan="8" className="no-data">No hay datos de operaciones</td>
                      </tr>
                    ) : (
                      operationsSummary.map((op, idx) => (
                        <tr key={idx}>
                          <td className="rfc-cell">{op.rfc}</td>
                          <td>{op.client_name}</td>
                          <td className="centered">{op.transaction_count}</td>
                          <td>{formatCurrency(op.total_facturado)}</td>
                          <td>{formatCurrency(op.total_comisiones)}</td>
                          <td>{formatCurrency(op.total_comision_estructura || 0)}</td>
                          <td>{formatCurrency(op.total_comision_ibsg || 0)}</td>
                          <td>{formatCurrency(op.total_retornos)}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
        
        {activeView === 'efectivo' && (
          <div className="efectivo-section">
            {/* Search Filters */}
            <div className="section-card">
              <h2>🔍 Filtros de Búsqueda</h2>
              <div className="filter-row">
                <div className="form-group">
                  <label>Fecha Inicio</label>
                  <input
                    type="date"
                    value={searchDateStart}
                    onChange={(e) => setSearchDateStart(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Fecha Fin</label>
                  <input
                    type="date"
                    value={searchDateEnd}
                    onChange={(e) => setSearchDateEnd(e.target.value)}
                  />
                </div>
                <button
                  className="btn-search"
                  onClick={loadCajaChicaTransactions}
                >
                  🔍 Buscar
                </button>
              </div>
            </div>
            
            {/* Caja Chica Transactions Table */}
            <div className="section-card">
              <div className="transactions-header">
                <h2>💵 Historial de Movimientos - Caja Chica</h2>
                <div className="export-buttons">
                  <button
                    className="btn-export"
                    onClick={() => {
                      let url = `${BACKEND_URL}/api/export/efectivo/xlsx?`;
                      if (searchDateStart) url += `fecha_inicio=${searchDateStart}T00:00:00Z&`;
                      if (searchDateEnd) url += `fecha_fin=${searchDateEnd}T23:59:59Z&`;
                      window.open(url, '_blank');
                    }}
                  >
                    📥 Descargar Excel
                  </button>
                  <button
                    className="btn-delete"
                    onClick={() => setDeleteCajaModalOpen(true)}
                  >
                    🗑️ Borrar Datos
                  </button>
                </div>
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Tipo Movimiento</th>
                      <th>Origen/Destino</th>
                      <th>Afectación</th>
                      <th>Concepto</th>
                      <th>Folio Cheque</th>
                      <th>Cargo Caja</th>
                      <th>Abono Caja</th>
                      <th>Saldo Caja Chica</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cajaTransactions.length === 0 ? (
                      <tr>
                        <td colSpan="9" className="no-data">No hay movimientos de Caja Chica</td>
                      </tr>
                    ) : (
                      cajaTransactions.map((tx, idx) => (
                        <tr key={idx}>
                          <td>{tx.fecha}</td>
                          <td>
                            <span className={tx.tipo_movimiento === 'Abono a Caja Chica' ? 'badge-green' : 'badge-red'}>
                              {tx.tipo_movimiento}
                            </span>
                          </td>
                          <td>
                            <strong>{tx.origen_destino_tipo}</strong>
                            <br />
                            <small>{tx.origen_destino_nombre}</small>
                          </td>
                          <td>
                            {tx.afectacion_origen_destino ? (
                              <span className={tx.afectacion_origen_destino === 'Cargo' ? 'badge-red' : 'badge-green'}>
                                {tx.afectacion_origen_destino}
                              </span>
                            ) : '-'}
                          </td>
                          <td className="description-cell">{tx.concepto}</td>
                          <td>{tx.folio_cheque || '-'}</td>
                          <td className={tx.tipo_movimiento === 'Cargo a Caja Chica' ? 'negative' : ''}>
                            {tx.tipo_movimiento === 'Cargo a Caja Chica' ? formatCurrency(tx.cantidad) : '-'}
                          </td>
                          <td className={tx.tipo_movimiento === 'Abono a Caja Chica' ? 'positive' : ''}>
                            {tx.tipo_movimiento === 'Abono a Caja Chica' ? formatCurrency(tx.cantidad) : '-'}
                          </td>
                          <td className={tx.saldo_caja_chica >= 0 ? 'positive' : 'negative'}>
                            <strong>{formatCurrency(tx.saldo_caja_chica)}</strong>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
        
        {activeView === 'transactions' && (
          <div className="transactions-section">
            {/* Search Filters */}
            <div className="section-card">
              <h2>🔍 Filtros de Búsqueda</h2>
              <div className="filter-row">
                <div className="form-group">
                  <label>RFC/Cliente</label>
                  <input
                    type="text"
                    placeholder="Buscar por RFC o nombre"
                    value={searchRFC}
                    onChange={(e) => setSearchRFC(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Fecha Inicio</label>
                  <input
                    type="date"
                    value={searchDateStart}
                    onChange={(e) => setSearchDateStart(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Fecha Fin</label>
                  <input
                    type="date"
                    value={searchDateEnd}
                    onChange={(e) => setSearchDateEnd(e.target.value)}
                  />
                </div>
                <button
                  className="btn-search"
                  onClick={loadTransactions}
                >
                  🔍 Buscar
                </button>
              </div>
            </div>
            
            {/* Transactions Table */}
            <div className="section-card">
              <div className="transactions-header">
                <h2>📋 Historial de Transacciones</h2>
                <div className="export-buttons">
                  <button
                    className="btn-export"
                    onClick={() => {
                      let url = `${BACKEND_URL}/api/export/transactions/xlsx?`;
                      if (searchRFC) url += `client_name=${encodeURIComponent(searchRFC)}&`;
                      if (searchDateStart) url += `fecha_inicio=${searchDateStart}T00:00:00Z&`;
                      if (searchDateEnd) url += `fecha_fin=${searchDateEnd}T23:59:59Z&`;
                      window.open(url, '_blank');
                    }}
                  >
                    📥 Descargar Excel
                  </button>
                  <button
                    className="btn-export"
                    onClick={() => {
                      let url = `${BACKEND_URL}/api/export/transactions/csv?`;
                      if (searchRFC) url += `client_name=${encodeURIComponent(searchRFC)}&`;
                      if (searchDateStart) url += `fecha_inicio=${searchDateStart}T00:00:00Z&`;
                      if (searchDateEnd) url += `fecha_fin=${searchDateEnd}T23:59:59Z&`;
                      window.open(url, '_blank');
                    }}
                  >
                    📥 Descargar CSV
                  </button>
                  <button
                    className="btn-delete"
                    onClick={() => setDeleteModalOpen(true)}
                  >
                    🗑️ Borrar Datos
                  </button>
                </div>
              </div>
              <div className="table-container">
                <table className="data-table transactions-table">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>RFC</th>
                      <th>Cliente</th>
                      <th>Descripción</th>
                      <th>Subtotal</th>
                      <th>IVA</th>
                      <th>Total Factura</th>
                      <th>Comisión 1</th>
                      <th>Retorno 1</th>
                      <th>Comisión Estructura</th>
                      <th>Comisión IBSG</th>
                      <th>Clasificación</th>
                      <th>Estado</th>
                      <th>Fondeado</th>
                      <th>Usuario</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.length === 0 ? (
                      <tr>
                        <td colSpan="16" className="no-data">No hay transacciones</td>
                      </tr>
                    ) : (
                      transactions.map((tx) => (
                        <tr key={tx.id} className={tx.total_factura < 0 ? 'cancelled-row' : ''}>
                          <td>{formatDate(tx.fecha)}</td>
                          <td className="rfc-cell">{tx.client_rfc || 'N/A'}</td>
                          <td>{tx.client_name}</td>
                          <td className="description-cell">{tx.descripcion}</td>
                          <td className={tx.subtotal < 0 ? 'negative' : ''}>{formatCurrency(tx.subtotal)}</td>
                          <td className={tx.iva < 0 ? 'negative' : ''}>{formatCurrency(tx.iva)}</td>
                          <td className={tx.total_factura < 0 ? 'negative' : ''}>{formatCurrency(tx.total_factura)}</td>
                          <td className={tx.comision_1 < 0 ? 'negative' : ''}>{formatCurrency(tx.comision_1)}</td>
                          <td className={tx.retorno_1 < 0 ? 'negative' : ''}>{formatCurrency(tx.retorno_1)}</td>
                          <td className={tx.comision_estructura < 0 ? 'negative' : ''}>{formatCurrency(tx.comision_estructura)}</td>
                          <td>{formatCurrency(Math.abs(tx.comision_ibsg))}</td>
                          <td><span className="badge">{tx.clasificacion}</span></td>
                          <td>
                            <select
                              className="status-select"
                              value={tx.estado || 'Enviado'}
                              onChange={async (e) => {
                                try {
                                  const response = await fetch(`${BACKEND_URL}/api/transactions/update_state`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                      transaction_id: tx.id,
                                      estado: e.target.value
                                    })
                                  });
                                  if (response.ok) {
                                    loadTransactions();
                                  }
                                } catch (error) {
                                  console.error('Error updating state:', error);
                                }
                              }}
                            >
                              <option value="Enviado">Enviado</option>
                              <option value="Pagado">Pagado</option>
                            </select>
                          </td>
                          <td>
                            <select
                              className={`status-select ${(tx.fondeado || 'Pendiente') === 'Pendiente' ? 'status-pendiente' : ''}`}
                              value={tx.fondeado || 'Pendiente'}
                              onChange={async (e) => {
                                try {
                                  const response = await fetch(`${BACKEND_URL}/api/transactions/update_fondeado`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                      transaction_id: tx.id,
                                      fondeado: e.target.value
                                    })
                                  });
                                  if (response.ok) {
                                    loadTransactions();
                                  }
                                } catch (error) {
                                  console.error('Error updating fondeado:', error);
                                }
                              }}
                            >
                              <option value="Pendiente">Pendiente</option>
                              <option value="Pagado">Pagado</option>
                            </select>
                          </td>
                          <td className="user-cell">{tx.ejecutivo}</td>
                          <td>
                            {!tx.clasificacion.includes('CANCELADA') && tx.total_factura > 0 && (
                              <button
                                className="btn-cancel"
                                onClick={() => {
                                  setSelectedTransaction(tx);
                                  setCancelModalOpen(true);
                                }}
                              >
                                ❌
                              </button>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
      
      {/* Cancel Modal */}
      {cancelModalOpen && (
        <div className="modal-overlay" onClick={() => setCancelModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>⚠️ Cancelar Transacción</h2>
            <p>¿Está seguro de que desea cancelar esta transacción?</p>
            <p className="modal-info"><strong>Cliente:</strong> {selectedTransaction?.client_name}</p>
            <p className="modal-info"><strong>Total:</strong> {formatCurrency(selectedTransaction?.total_factura || 0)}</p>
            
            <div className="form-group">
              <label>Motivo de Cancelación</label>
              <select
                value={cancelMotivo}
                onChange={(e) => setCancelMotivo(e.target.value)}
                className="modal-select"
              >
                <option value="Solicitud del cliente">Solicitud del cliente</option>
                <option value="Solicitud de Dirección">Solicitud de Dirección</option>
                <option value="Falta de fondeo">Falta de fondeo</option>
              </select>
            </div>
            
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setCancelModalOpen(false)}>
                Cerrar
              </button>
              <button className="btn-danger" onClick={handleCancelTransaction}>
                Confirmar Cancelación
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Delete Data Modal */}
      {deleteModalOpen && (
        <div className="modal-overlay" onClick={() => setDeleteModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>🗑️ Borrar Datos por Rango de Fechas</h2>
            <p className="warning-text">⚠️ ADVERTENCIA: Esta acción es permanente y no se puede deshacer.</p>
            <p className="modal-info">Solo usuarios autorizados pueden realizar esta acción.</p>
            
            <div className="form-group">
              <label>Usuario Autorizado</label>
              <input
                type="text"
                value={deleteUsername}
                onChange={(e) => setDeleteUsername(e.target.value)}
                placeholder="usuario@ibsgroup.mx"
                className="modal-input"
              />
            </div>
            
            <div className="form-group">
              <label>Contraseña</label>
              <input
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="••••••••"
                className="modal-input"
              />
            </div>
            
            <div className="form-group">
              <label>Fecha Inicio</label>
              <input
                type="date"
                value={deleteDateStart}
                onChange={(e) => setDeleteDateStart(e.target.value)}
                className="modal-input"
              />
            </div>
            
            <div className="form-group">
              <label>Fecha Fin</label>
              <input
                type="date"
                value={deleteDateEnd}
                onChange={(e) => setDeleteDateEnd(e.target.value)}
                className="modal-input"
              />
            </div>
            
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setDeleteModalOpen(false)}>
                Cancelar
              </button>
              <button className="btn-danger" onClick={handleDeleteData}>
                Borrar Datos
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Caja Chica Data Modal */}
      {deleteCajaModalOpen && (
        <div className="modal-overlay" onClick={() => setDeleteCajaModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>🗑️ Borrar Datos de Caja Chica por Rango de Fechas</h2>
            <p className="warning-text">⚠️ ADVERTENCIA: Esta acción es permanente y no se puede deshacer.</p>
            <p className="modal-info">Solo usuarios autorizados pueden realizar esta acción.</p>
            
            <div className="form-group">
              <label>Usuario Autorizado</label>
              <input
                type="text"
                value={deleteCajaUsername}
                onChange={(e) => setDeleteCajaUsername(e.target.value)}
                placeholder="usuario@ibsgroup.mx"
                className="modal-input"
              />
            </div>
            
            <div className="form-group">
              <label>Contraseña</label>
              <input
                type="password"
                value={deleteCajaPassword}
                onChange={(e) => setDeleteCajaPassword(e.target.value)}
                placeholder="••••••••"
                className="modal-input"
              />
            </div>
            
            <div className="form-group">
              <label>Fecha Inicio</label>
              <input
                type="date"
                value={deleteCajaDateStart}
                onChange={(e) => setDeleteCajaDateStart(e.target.value)}
                className="modal-input"
              />
            </div>
            
            <div className="form-group">
              <label>Fecha Fin</label>
              <input
                type="date"
                value={deleteCajaDateEnd}
                onChange={(e) => setDeleteCajaDateEnd(e.target.value)}
                className="modal-input"
              />
            </div>
            
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setDeleteCajaModalOpen(false)}>
                Cancelar
              </button>
              <button className="btn-danger" onClick={handleDeleteCajaData}>
                Borrar Datos
              </button>
            </div>
          </div>
        </div>
      )}

      
        {activeView === 'cuentas' && (
          <div className="cuentas-section">
            {/* Alta de Cuentas */}
            <div className="section-card">
              <h2>🏦 Alta de Cuenta Bancaria</h2>
              <form onSubmit={handleCuentaSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Nombre de Estructura</label>
                    <input
                      type="text"
                      value={cuentaEstructura}
                      onChange={(e) => setCuentaEstructura(e.target.value)}
                      placeholder="Ej: Guadalajara Mario F"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Nivel</label>
                    <select
                      value={cuentaNivel}
                      onChange={(e) => setCuentaNivel(e.target.value)}
                      required
                    >
                      <option value="Primer Nivel">Primer Nivel</option>
                      <option value="Segundo Nivel">Segundo Nivel</option>
                    </select>
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Tipo de Movimiento</label>
                    <select
                      value={cuentaTipoMovimiento}
                      onChange={(e) => setCuentaTipoMovimiento(e.target.value)}
                      required
                    >
                      <option value="TRASPASO SIMPLE">TRASPASO SIMPLE</option>
                      <option value="DE MONEY GIVER">DE MONEY GIVER</option>
                      <option value="CUENTAS DIVIDENDO">CUENTAS DIVIDENDO</option>
                      <option value="CUENTAS CUCA">CUENTAS CUCA</option>
                      <option value="ANTICIPO REMANENTE">ANTICIPO REMANENTE</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label>Nombre</label>
                    <input
                      type="text"
                      value={cuentaNombre}
                      onChange={(e) => setCuentaNombre(e.target.value)}
                      placeholder="Nombre de la empresa"
                      required
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Banco</label>
                    <input
                      type="text"
                      value={cuentaBanco}
                      onChange={(e) => setCuentaBanco(e.target.value)}
                      placeholder="Ej: BBVA, Bankaool, etc."
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Número de Cuenta</label>
                    <input
                      type="text"
                      value={cuentaNumero}
                      onChange={(e) => setCuentaNumero(e.target.value)}
                      placeholder="Número de cuenta"
                      required
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label>CLABE</label>
                  <input
                    type="text"
                    value={cuentaClabe}
                    onChange={(e) => setCuentaClabe(e.target.value)}
                    placeholder="CLABE interbancaria"
                    required
                  />
                </div>
                
                {cuentaMessage && (
                  <div className={cuentaMessage.includes('✓') ? 'success-message' : 'error-message'}>
                    {cuentaMessage}
                  </div>
                )}
                
                <button type="submit" className="btn-primary">
                  💾 Registrar Cuenta
                </button>
              </form>
            </div>
            
            {/* Tabla de Saldos de Cuentas Bancarias */}
            <div className="section-card">
              <div className="transactions-header">
                <h2>💰 Saldos de Cuentas Bancarias</h2>
                <div className="export-buttons">
                  <button
                    className="btn-export"
                    onClick={() => {
                      const url = `${BACKEND_URL}/api/export/bank_balances/xlsx`;
                      window.open(url, '_blank');
                    }}
                  >
                    📥 Descargar Excel
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={initializeBankAccounts}
                    style={{padding: '10px 20px'}}
                  >
                    🔄 Inicializar Cuentas Base
                  </button>
                </div>
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Estructura</th>
                      <th>Nivel</th>
                      <th>Tipo</th>
                      <th>Nombre</th>
                      <th>Banco</th>
                      <th>Cuenta</th>
                      <th>Saldo</th>
                      <th>Última Actualización</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bankAccountsWithBalances.length === 0 ? (
                      <tr>
                        <td colSpan="8" className="no-data">
                          No hay cuentas bancarias registradas.
                          <br />
                          <button
                            onClick={initializeBankAccounts}
                            className="btn-primary"
                            style={{marginTop: '10px'}}
                          >
                            Cargar Cuentas Iniciales
                          </button>
                        </td>
                      </tr>
                    ) : (
                      bankAccountsWithBalances.map((account, idx) => (
                        <tr key={idx}>
                          <td>{account.estructura}</td>
                          <td><span className="badge-small">{account.nivel}</span></td>
                          <td><span className="badge-small">{account.tipo_movimiento}</span></td>
                          <td>{account.nombre}</td>
                          <td><strong>{account.banco}</strong></td>
                          <td className="cuenta-cell">{account.cuenta}</td>
                          <td className={account.saldo >= 0 ? 'positive' : 'negative'}>
                            {formatCurrency(account.saldo)}
                          </td>
                          <td>{account.ultima_actualizacion || 'Sin movimientos'}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
            
            {/* Listado de Todas las Cuentas */}
            <div className="section-card">
              <div className="transactions-header">
                <h2>📋 Catálogo de Cuentas Bancarias</h2>
                <button
                  className="btn-export"
                  onClick={() => {
                    const url = `${BACKEND_URL}/api/export/bank_accounts_catalog/xlsx`;
                    window.open(url, '_blank');
                  }}
                >
                  📥 Descargar Excel
                </button>
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Estructura</th>
                      <th>Nivel</th>
                      <th>Tipo de Movimiento</th>
                      <th>Nombre</th>
                      <th>Banco</th>
                      <th>Cuenta</th>
                      <th>CLABE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bankAccounts.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="no-data">No hay cuentas registradas</td>
                      </tr>
                    ) : (
                      bankAccounts.map((account, idx) => (
                        <tr key={idx}>
                          <td>{account.estructura}</td>
                          <td><span className="badge-small">{account.nivel}</span></td>
                          <td><span className="badge-small">{account.tipo_movimiento}</span></td>
                          <td>{account.nombre}</td>
                          <td><strong>{account.banco}</strong></td>
                          <td className="cuenta-cell">{account.cuenta}</td>
                          <td className="clabe-cell">{account.clabe}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      
      {/* Footer */}
      <footer className="app-footer">
        <p>© 2025 IBS Group - Integra Business Solutions</p>
      </footer>
    </div>
  );
}

export default App;
