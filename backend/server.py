from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import uuid
from openpyxl import load_workbook
import shutil
from pathlib import Path
from bson import ObjectId

load_dotenv()

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.treasury_db

# Create upload directory
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    """Convert MongoDB document ObjectId to string for JSON serialization"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == "_id" and isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    return doc

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    username: Optional[str] = None

class ClientData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    emisor: str
    cliente: str
    rfc: str
    calle: str
    colonia: str
    estado: str

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    client_name: str
    descripcion: str
    subtotal: float
    iva: float
    total_factura: float
    comision_porcentaje: float
    comision_1: float
    retorno_1: float
    comision_estructura_porcentaje: float
    comision_estructura: float
    comision_ibsg: float
    retorno_2: float
    clasificacion: str
    fecha: str
    ejecutivo: str

class TreasuryBalance(BaseModel):
    client_id: str
    client_name: str
    balance: float
    last_updated: str

class CancelTransactionRequest(BaseModel):
    transaction_id: str
    motivo: str
    ejecutivo: str

# Initialize default users
@app.on_event("startup")
async def startup_event():
    # Create default users if not exist
    users_collection = db.users
    
    # Remove old users
    await users_collection.delete_many({"username": {"$in": ["Ejecutivo1", "Ejecutivo2"]}})
    
    # New users list
    new_users = [
        {"username": "direccion@ibsgroup.mx", "password": "Sistema1"},
        {"username": "operaciones@ibsgroup.mx", "password": "Sistema2"},
        {"username": "f.alfaro@ibsgroup.mx", "password": "Sistema3"},
        {"username": "administracion@ibsgroup.mx", "password": "Sistema4"},
        {"username": "b.martinez@ibsgroup.mx", "password": "Sistema5"},
        {"username": "auditoria@ibsgroup.mx", "password": "Sistema6"},
        {"username": "irma.rh@ibsgroup.mx", "password": "Sistema7"},
        {"username": "alicia.auditoria@ibsgroup.mx", "password": "Sistema8"},
        {"username": "fernanda.auditoria@ibsgroup.mx", "password": "Sistema9"},
        {"username": "cesar.enlace@ibsgroup.mx", "password": "Sistema10"},
        {"username": "daniel.enlace@ibsgroup.mx", "password": "Sistema11"},
        {"username": "cinthya.operaciones@ibsgroup.mx", "password": "Sistema12"},
        {"username": "fabiola.operaciones@ibsgroup.mx", "password": "Sistema13"},
        {"username": "jazmin.operaciones@ibsgroup.mx", "password": "Sistema14"},
        {"username": "jorge.operaciones@ibsgroup.mx", "password": "Sistema15"},
        {"username": "arturo.operaciones@ibsgroup.mx", "password": "Sistema16"},
        {"username": "bry.operaciones@ibsgroup.mx", "password": "Sistema17"},
    ]
    
    for user_data in new_users:
        existing_user = await users_collection.find_one({"username": user_data["username"]})
        if not existing_user:
            user = User(username=user_data["username"], password=user_data["password"])
            await users_collection.insert_one(user.dict())
            print(f"Created user: {user_data['username']}")

# Authentication
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    user = await db.users.find_one({
        "username": credentials.username,
        "password": credentials.password
    })
    
    if user:
        return LoginResponse(success=True, message="Login exitoso", username=credentials.username)
    else:
        return LoginResponse(success=False, message="Credenciales inválidas")

# Excel Processing Function
def process_excel_file(file_path: str, comision_pct: float, comision_estructura_pct: float):
    """Process the Excel file and extract all required data"""
    wb = load_workbook(file_path, data_only=True)
    ws = wb.active
    
    # Extract client data from fixed cells
    client_data = {
        "emisor": ws['D2'].value or "",
        "cliente": ws['D6'].value or "",
        "rfc": ws['D7'].value or "",
        "calle": ws['D8'].value or "",
        "colonia": ws['D9'].value or "",
        "estado": ws['D10'].value or ""
    }
    
    # Extract description
    descripcion = ws['E13'].value or ""
    
    # Search for financial values in column K
    subtotal = 0.0
    iva = 0.0
    total_factura = 0.0
    
    for row in range(12, 100):  # Search up to row 100
        cell_k = ws[f'K{row}'].value
        cell_l = ws[f'L{row}'].value
        
        if cell_k and isinstance(cell_k, str):
            cell_k_lower = cell_k.lower().strip()
            
            if 'subtotal' in cell_k_lower and 'iva' not in cell_k_lower:
                subtotal = float(cell_l) if cell_l else 0.0
            elif 'iva' in cell_k_lower:
                iva = float(cell_l) if cell_l else 0.0
            elif 'total' in cell_k_lower and 'factura' in cell_k_lower:
                total_factura = float(cell_l) if cell_l else 0.0
    
    wb.close()
    
    # Calculate commissions
    comision_1 = subtotal * (comision_pct / 100)
    retorno_1 = total_factura - comision_1
    comision_estructura = subtotal * (comision_estructura_pct / 100)
    comision_ibsg = comision_estructura - comision_1
    retorno_2 = total_factura - comision_1 - comision_ibsg
    
    return {
        "client_data": client_data,
        "descripcion": descripcion,
        "financial_data": {
            "subtotal": round(subtotal, 2),
            "iva": round(iva, 2),
            "total_factura": round(total_factura, 2),
            "comision_1": round(comision_1, 2),
            "retorno_1": round(retorno_1, 2),
            "comision_estructura": round(comision_estructura, 2),
            "comision_ibsg": round(comision_ibsg, 2),
            "retorno_2": round(retorno_2, 2)
        }
    }

# Upload and Process File
@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    comision: float = Form(5.0),
    comision_estructura: float = Form(2.5),
    clasificacion: str = Form(...),
    ejecutivo: str = Form(...)
):
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the Excel file
        result = process_excel_file(str(file_path), comision, comision_estructura)
        
        # Save or update client
        client_data = result["client_data"]
        existing_client = await db.clients.find_one({"rfc": client_data["rfc"]})
        
        if existing_client:
            client_id = existing_client["id"]
        else:
            client = ClientData(**client_data)
            await db.clients.insert_one(client.dict())
            client_id = client.id
        
        # Create transaction record
        transaction = Transaction(
            client_id=client_id,
            client_name=client_data["cliente"],
            descripcion=result["descripcion"],
            subtotal=result["financial_data"]["subtotal"],
            iva=result["financial_data"]["iva"],
            total_factura=result["financial_data"]["total_factura"],
            comision_porcentaje=comision,
            comision_1=result["financial_data"]["comision_1"],
            retorno_1=result["financial_data"]["retorno_1"],
            comision_estructura_porcentaje=comision_estructura,
            comision_estructura=result["financial_data"]["comision_estructura"],
            comision_ibsg=result["financial_data"]["comision_ibsg"],
            retorno_2=result["financial_data"]["retorno_2"],
            clasificacion=clasificacion,
            fecha=datetime.now(timezone.utc).isoformat(),
            ejecutivo=ejecutivo
        )
        await db.transactions.insert_one(transaction.dict())
        
        # Update treasury balance based on classification
        if clasificacion in ["Abono a Tesorería", "Cargo/Retiro de Tesorería"]:
            treasury = await db.treasury_balances.find_one({"client_id": client_id})
            
            if treasury:
                current_balance = treasury["balance"]
            else:
                current_balance = 0.0
            
            # Update balance
            if clasificacion == "Abono a Tesorería":
                new_balance = current_balance + result["financial_data"]["total_factura"]
            else:  # Cargo/Retiro
                new_balance = current_balance - result["financial_data"]["total_factura"]
            
            treasury_record = TreasuryBalance(
                client_id=client_id,
                client_name=client_data["cliente"],
                balance=round(new_balance, 2),
                last_updated=datetime.now(timezone.utc).isoformat()
            )
            
            await db.treasury_balances.update_one(
                {"client_id": client_id},
                {"$set": treasury_record.dict()},
                upsert=True
            )
        
        # Clean up uploaded file
        file_path.unlink()
        
        return {
            "success": True,
            "message": "Archivo procesado exitosamente",
            "data": {
                "client": client_data,
                "transaction": transaction.dict()
            }
        }
        
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

# Dashboard Endpoints
@app.get("/api/dashboard/treasury")
async def get_treasury_balances(client_name: Optional[str] = None):
    """Get treasury balances for all clients or filtered by client name"""
    query = {}
    if client_name:
        query["client_name"] = {"$regex": client_name, "$options": "i"}
    
    balances = await db.treasury_balances.find(query).to_list(length=None)
    return serialize_doc(balances)

@app.get("/api/dashboard/transactions")
async def get_transactions(
    client_name: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    """Get transactions with optional filters"""
    query = {}
    
    if client_name:
        query["client_name"] = {"$regex": client_name, "$options": "i"}
    
    if fecha_inicio and fecha_fin:
        query["fecha"] = {
            "$gte": fecha_inicio,
            "$lte": fecha_fin
        }
    
    transactions = await db.transactions.find(query).sort("fecha", -1).to_list(length=None)
    return serialize_doc(transactions)

@app.get("/api/clients")
async def get_clients():
    """Get all clients"""
    clients = await db.clients.find().to_list(length=None)
    return serialize_doc(clients)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Treasury Management System API"}
