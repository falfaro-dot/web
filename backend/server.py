from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import uuid
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, PatternFill
import shutil
from pathlib import Path
from bson import ObjectId
import io
import csv

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
    client_rfc: str
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
            client_rfc=client_data["rfc"],
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
async def get_treasury_balances(rfc: Optional[str] = None):
    """Get treasury balances for all clients or filtered by RFC"""
    query = {}
    
    if rfc:
        # Find client by RFC
        client = await db.clients.find_one({"rfc": {"$regex": rfc, "$options": "i"}})
        if client:
            query["client_id"] = client["id"]
    
    balances = await db.treasury_balances.find(query).to_list(length=None)
    
    # Enrich with RFC data
    enriched_balances = []
    for balance in balances:
        client = await db.clients.find_one({"id": balance["client_id"]})
        if client:
            balance["client_rfc"] = client["rfc"]
        enriched_balances.append(balance)
    
    return serialize_doc(enriched_balances)

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

@app.post("/api/transactions/cancel")
async def cancel_transaction(request: CancelTransactionRequest):
    """Cancel a transaction by creating a negative entry"""
    try:
        # Get original transaction
        original_tx = await db.transactions.find_one({"id": request.transaction_id})
        if not original_tx:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        
        # Create cancellation transaction (negative values)
        cancel_tx = Transaction(
            client_id=original_tx["client_id"],
            client_name=original_tx["client_name"],
            client_rfc=original_tx.get("client_rfc", "N/A"),
            descripcion=f"CANCELACIÓN - {original_tx['descripcion']} - Motivo: {request.motivo}",
            subtotal=-original_tx["subtotal"],
            iva=-original_tx["iva"],
            total_factura=-original_tx["total_factura"],
            comision_porcentaje=original_tx["comision_porcentaje"],
            comision_1=-original_tx["comision_1"],
            retorno_1=-original_tx["retorno_1"],
            comision_estructura_porcentaje=original_tx["comision_estructura_porcentaje"],
            comision_estructura=-original_tx["comision_estructura"],
            comision_ibsg=-original_tx["comision_ibsg"],
            retorno_2=-original_tx["retorno_2"],
            clasificacion=f"CANCELADA - {original_tx['clasificacion']}",
            fecha=datetime.now(timezone.utc).isoformat(),
            ejecutivo=request.ejecutivo
        )
        await db.transactions.insert_one(cancel_tx.dict())
        
        # Update treasury balance if original was Abono or Cargo
        if original_tx["clasificacion"] in ["Abono a Tesorería", "Cargo/Retiro de Tesorería"]:
            treasury = await db.treasury_balances.find_one({"client_id": original_tx["client_id"]})
            if treasury:
                # Reverse the original operation
                if "Abono" in original_tx["clasificacion"]:
                    new_balance = treasury["balance"] - original_tx["total_factura"]
                else:
                    new_balance = treasury["balance"] + original_tx["total_factura"]
                
                await db.treasury_balances.update_one(
                    {"client_id": original_tx["client_id"]},
                    {"$set": {
                        "balance": round(new_balance, 2),
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }}
                )
        
        return {
            "success": True,
            "message": "Transacción cancelada exitosamente",
            "cancel_transaction": cancel_tx.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelando transacción: {str(e)}")

@app.get("/api/dashboard/operations_summary")
async def get_operations_summary(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    """Get operations summary by client with transaction count, total billed, commissions, and returns"""
    try:
        # Build query for date filter
        query = {}
        if fecha_inicio and fecha_fin:
            query["fecha"] = {
                "$gte": fecha_inicio,
                "$lte": fecha_fin
            }
        
        # Get all transactions
        transactions = await db.transactions.find(query).to_list(length=None)
        
        # Group by client and calculate summaries
        summary_dict = {}
        for tx in transactions:
            client_id = tx["client_id"]
            if client_id not in summary_dict:
                # Get client RFC
                client = await db.clients.find_one({"id": client_id})
                summary_dict[client_id] = {
                    "rfc": client["rfc"] if client else tx.get("client_rfc", "N/A"),
                    "client_name": tx["client_name"],
                    "transaction_count": 0,
                    "total_facturado": 0.0,
                    "total_comisiones": 0.0,
                    "total_retornos": 0.0
                }
            
            # Accumulate values
            summary_dict[client_id]["transaction_count"] += 1
            summary_dict[client_id]["total_facturado"] += tx["total_factura"]
            summary_dict[client_id]["total_comisiones"] += tx["comision_1"]
            summary_dict[client_id]["total_retornos"] += tx["retorno_1"]
        
        # Convert to list and round values
        summary_list = []
        for client_id, data in summary_dict.items():
            summary_list.append({
                "rfc": data["rfc"],
                "client_name": data["client_name"],
                "transaction_count": data["transaction_count"],
                "total_facturado": round(data["total_facturado"], 2),
                "total_comisiones": round(data["total_comisiones"], 2),
                "total_retornos": round(data["total_retornos"], 2)
            })
        
        return serialize_doc(summary_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando resumen: {str(e)}")

@app.get("/api/export/transactions/xlsx")
async def export_transactions_xlsx(
    client_name: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    """Export transactions to Excel file"""
    try:
        # Build query
        query = {}
        if client_name:
            query["client_name"] = {"$regex": client_name, "$options": "i"}
        if fecha_inicio and fecha_fin:
            query["fecha"] = {"$gte": fecha_inicio, "$lte": fecha_fin}
        
        # Get transactions
        transactions = await db.transactions.find(query).sort("fecha", -1).to_list(length=None)
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Transacciones"
        
        # Define headers
        headers = [
            "Fecha", "RFC", "Cliente", "Descripción", "Subtotal", "IVA", 
            "Total Factura", "Comisión 1", "Retorno 1", "Comisión Estructura", 
            "Comisión IBSG", "Clasificación", "Usuario"
        ]
        
        # Style for headers
        header_fill = PatternFill(start_color="C5B77D", end_color="C5B77D", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        # Write headers
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        
        # Write data
        for row_num, tx in enumerate(transactions, 2):
            # Get client RFC
            client = await db.clients.find_one({"id": tx["client_id"]})
            client_rfc = client["rfc"] if client else "N/A"
            
            ws.cell(row=row_num, column=1, value=tx["fecha"])
            ws.cell(row=row_num, column=2, value=tx["client_name"])
            ws.cell(row=row_num, column=3, value=client_rfc)
            ws.cell(row=row_num, column=4, value=tx["descripcion"])
            ws.cell(row=row_num, column=5, value=tx["subtotal"])
            ws.cell(row=row_num, column=6, value=tx["iva"])
            ws.cell(row=row_num, column=7, value=tx["total_factura"])
            ws.cell(row=row_num, column=8, value=tx["comision_1"])
            ws.cell(row=row_num, column=9, value=tx["retorno_1"])
            ws.cell(row=row_num, column=10, value=tx["comision_estructura"])
            ws.cell(row=row_num, column=11, value=abs(tx["comision_ibsg"]))  # Absolute value
            ws.cell(row=row_num, column=12, value=tx["clasificacion"])
            ws.cell(row=row_num, column=13, value=tx["ejecutivo"])
            
            # Apply red color for cancelled transactions
            if tx["total_factura"] < 0:
                for col in range(1, 14):
                    ws.cell(row=row_num, column=col).font = Font(color="FF0000")
        
        # Adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width
        
        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Return as streaming response
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=transacciones.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando: {str(e)}")

@app.get("/api/export/transactions/csv")
async def export_transactions_csv(
    client_name: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    """Export transactions to CSV file"""
    try:
        # Build query
        query = {}
        if client_name:
            query["client_name"] = {"$regex": client_name, "$options": "i"}
        if fecha_inicio and fecha_fin:
            query["fecha"] = {"$gte": fecha_inicio, "$lte": fecha_fin}
        
        # Get transactions
        transactions = await db.transactions.find(query).sort("fecha", -1).to_list(length=None)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            "Fecha", "Cliente", "RFC", "Descripción", "Subtotal", "IVA",
            "Total Factura", "Comisión 1", "Retorno 1", "Comisión Estructura",
            "Comisión IBSG", "Clasificación", "Usuario"
        ])
        
        # Write data
        for tx in transactions:
            # Get client RFC
            client = await db.clients.find_one({"id": tx["client_id"]})
            client_rfc = client["rfc"] if client else "N/A"
            
            writer.writerow([
                tx["fecha"],
                tx["client_name"],
                client_rfc,
                tx["descripcion"],
                tx["subtotal"],
                tx["iva"],
                tx["total_factura"],
                tx["comision_1"],
                tx["retorno_1"],
                tx["comision_estructura"],
                abs(tx["comision_ibsg"]),  # Absolute value
                tx["clasificacion"],
                tx["ejecutivo"]
            ])
        
        # Convert to bytes
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=transacciones.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Treasury Management System API"}
