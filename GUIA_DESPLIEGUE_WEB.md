# 🌐 Guía de Despliegue Web - Sistema de Registro de Operaciones

## ✅ Estado Actual de la Aplicación

Su aplicación **YA ESTÁ DESPLEGADA Y FUNCIONANDO** en la web en:
**URL:** https://cash-flow-mgr-1.preview.emergentagent.com

### Elementos ya Configurados:

1. **Backend (FastAPI):**
   - ✅ API REST funcionando en puerto 8001
   - ✅ Endpoints con prefijo `/api`
   - ✅ CORS configurado para permitir acceso desde el frontend
   - ✅ Conexión a MongoDB configurada

2. **Frontend (React):**
   - ✅ Aplicación React compilada y servida
   - ✅ Variable de entorno `REACT_APP_BACKEND_URL` configurada
   - ✅ Diseño responsive funcionando

3. **Base de Datos:**
   - ✅ MongoDB funcionando
   - ✅ Colecciones: users, clients, transactions, treasury_balances

---

## 📋 Para Despliegue en Producción (Servidor Propio)

### Opción 1: Despliegue Tradicional (VPS/Servidor Dedicado)

#### Requisitos del Servidor:
- **Sistema Operativo:** Ubuntu 20.04+ o similar
- **RAM:** Mínimo 2GB (Recomendado 4GB)
- **CPU:** 2 cores
- **Almacenamiento:** 20GB
- **Software necesario:**
  - Python 3.11+
  - Node.js 16+
  - MongoDB 5.0+
  - Nginx

#### Pasos de Instalación:

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias
sudo apt install -y python3.11 python3-pip nodejs npm mongodb nginx

# 3. Clonar o copiar los archivos del proyecto
# (copiar carpetas backend/ y frontend/)

# 4. Configurar Backend
cd /ruta/al/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configurar Frontend
cd /ruta/al/frontend
npm install
npm run build

# 6. Configurar Nginx
sudo nano /etc/nginx/sites-available/ibsgroup-operations
```

#### Configuración de Nginx:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Frontend
    location / {
        root /ruta/al/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activar configuración
sudo ln -s /etc/nginx/sites-available/ibsgroup-operations /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Configurar SSL (HTTPS) con Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

#### Crear Servicios Systemd:

**Backend Service** (`/etc/systemd/system/ibsgroup-backend.service`):
```ini
[Unit]
Description=IBS Group Operations Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/ruta/al/backend
Environment="PATH=/ruta/al/backend/venv/bin"
ExecStart=/ruta/al/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ibsgroup-backend
sudo systemctl start ibsgroup-backend
```

---

### Opción 2: Despliegue en la Nube (Más Fácil)

#### A. Vercel (Frontend) + Railway/Render (Backend)

**Frontend en Vercel:**
1. Crear cuenta en https://vercel.com
2. Conectar repositorio de GitHub con el código
3. Configurar variables de entorno:
   - `REACT_APP_BACKEND_URL=https://tu-api.railway.app`
4. Desplegar automáticamente

**Backend en Railway:**
1. Crear cuenta en https://railway.app
2. Crear nuevo proyecto
3. Conectar repositorio
4. Configurar variables de entorno:
   - `MONGO_URL=tu-conexión-mongodb`
5. Railway detectará automáticamente Python y desplegará

#### B. DigitalOcean App Platform

1. Crear cuenta en DigitalOcean
2. Crear "App" desde el panel
3. Conectar repositorio
4. DigitalOcean detectará automáticamente React + FastAPI
5. Configurar variables de entorno
6. Desplegar

#### C. AWS Elastic Beanstalk

1. Instalar AWS CLI y EB CLI
2. Configurar credenciales AWS
3. Inicializar proyecto:
```bash
eb init
eb create production
```

---

### Opción 3: Docker (Recomendado para Portabilidad)

#### Dockerfile Backend:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Dockerfile Frontend:
```dockerfile
FROM node:16 as build

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install

COPY . .
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

#### docker-compose.yml:
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secretpassword

  backend:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://admin:secretpassword@mongodb:27017
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

```bash
docker-compose up -d
```

---

## 🔐 Variables de Entorno Necesarias

### Backend (.env):
```env
MONGO_URL=mongodb://localhost:27017/treasury_db
# o para MongoDB Atlas:
# MONGO_URL=mongodb+srv://usuario:password@cluster.mongodb.net/treasury_db
```

### Frontend (.env):
```env
REACT_APP_BACKEND_URL=https://tu-dominio.com
# o si está en el mismo dominio:
# REACT_APP_BACKEND_URL=
```

---

## 📊 Base de Datos - Opciones

### Opción 1: MongoDB Local
```bash
sudo apt install mongodb
sudo systemctl start mongodb
```

### Opción 2: MongoDB Atlas (Cloud - Gratis)
1. Crear cuenta en https://www.mongodb.com/cloud/atlas
2. Crear cluster gratuito
3. Obtener connection string
4. Configurar IP whitelist (0.0.0.0/0 para acceso público)

---

## 🔒 Seguridad en Producción

1. **Cambiar contraseñas de usuarios:**
   - Los usuarios actuales tienen contraseñas simples (Sistema1-Sistema17)
   - Implementar hash de contraseñas (bcrypt)

2. **Configurar firewall:**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

3. **Configurar rate limiting en Nginx:**
```nginx
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

location /api/auth/login {
    limit_req zone=login burst=3;
    proxy_pass http://localhost:8001;
}
```

4. **Variables de entorno seguras:**
   - Nunca subir archivos .env a Git
   - Usar secrets managers en producción

---

## 📈 Monitoreo y Logs

### Ver logs del backend:
```bash
sudo journalctl -u ibsgroup-backend -f
```

### Ver logs de Nginx:
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔄 Actualización del Sistema

```bash
# 1. Actualizar código
git pull origin main

# 2. Actualizar backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ibsgroup-backend

# 3. Actualizar frontend
cd frontend
npm install
npm run build
sudo systemctl reload nginx
```

---

## ✅ Checklist de Producción

- [ ] SSL/HTTPS configurado
- [ ] Contraseñas de usuarios actualizadas
- [ ] MongoDB con autenticación habilitada
- [ ] Backups automáticos configurados
- [ ] Firewall configurado
- [ ] Rate limiting habilitado
- [ ] Variables de entorno seguras
- [ ] Logs configurados
- [ ] Dominio configurado
- [ ] DNS apuntando al servidor

---

## 🆘 Soporte

Para más información sobre despliegue en Emergent (plataforma actual):
- La aplicación ya está funcionando en: https://cash-flow-mgr-1.preview.emergentagent.com
- Esta es una URL de preview que funciona perfectamente para acceso web

Para un dominio personalizado (ej: operaciones.ibsgroup.mx), necesitarás:
1. Registrar el dominio
2. Configurar DNS para apuntar a tu servidor
3. Configurar SSL/HTTPS
4. Actualizar REACT_APP_BACKEND_URL en el frontend
