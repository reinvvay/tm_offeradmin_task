# 🚀 How to Run the Project

This project includes two main parts:

- **Litestar service** — async API backend  
- **Django admin panel** — admin interface  
- **Nginx** — reverse proxy connecting both services

---

## 🧩 Step-by-step launch guide

### 1. Go to the Litestar service folder
```bash
cd litestar_service
docker compose up --build -d
```

### 2. Go back to the project root
```bash
cd ..
docker compose up --build -d
```

### 3. Available endpoints
```bash
- API docs (Swagger): `http://localhost/api/schema` 
- Admin login: `http://localhost/offers/admin/`  
```