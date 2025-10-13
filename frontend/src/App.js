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
  
  // Load dashboard data when view changes
  useEffect(() => {
    if (activeView === 'dashboard') {
      loadTreasuryBalances();
      loadOperationsSummary();
      loadDashboardTransactions();
    } else if (activeView === 'transactions') {
      loadTransactions();
    }
  }, [activeView]);
  
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
            <img src="https://customer-assets.emergentagent.com/job_finance-parser-4/artifacts/twvm8fyz_logo3.png" alt="IBS" className="header-logo" />
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
          📤 Cargar Archivo
        </button>
      </nav>
      
      {/* Main Content */}
      <main className="app-main">
        {activeView === 'upload' && (
          <div className="upload-section">
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
                    <option value="Transacción de Servicio/Facturación">Transacción de Servicio/Facturación</option>
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
                  }}
                >
                  🔍 Buscar
                </button>
              </div>
            </div>
            
            {/* Treasury Total */}
            <div className="total-card">
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
            
            {/* Grid 2x2 Totalizers */}
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
                              className="status-select"
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
      
      {/* Footer */}
      <footer className="app-footer">
        <p>© 2025 IBS Group - Integra Business Solutions</p>
      </footer>
    </div>
  );
}

export default App;
