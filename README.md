# 📚 Bookly - Backend FastAPI Book Services

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-brightgreen)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)
[![Celery](https://img.shields.io/badge/Celery-5.4-green)](https://docs.celeryq.dev/en/stable/)

Bookly is a backend service built using **FastAPI**, designed to manage books, users, and reviews efficiently. It provides robust API endpoints for managing book records, handling user authentication, sending emails, and more.

---

## 🚀 Features

- **User Authentication:** Secure login/signup using JWT authentication.
- **Book Management:** CRUD operations for books with user association.
- **Reviews:** Add and manage reviews for books.
- **Tagging System:** Assign and filter books using tags.
- **Email Notifications:** Asynchronous email sending via Celery and Redis.
- **Background Tasks:** Celery-based job processing for long-running tasks.
- **Error Handling:** Structured error responses with logging and monitoring.
- **Database Integration:** PostgreSQL with SQLAlchemy and SQLModel.

---

## 🛠️ Installation & Setup

### **1. Clone the Repository**
```bash
git clone https://github.com/janhvikaushal2403/Bookly---Backend-fastapi-services.git
cd Bookly---Backend-fastapi-services
```
### **2. Create a Virtual Environment**
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```
### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```
### **4. Set Up Environment Variables**
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bookly
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
REDIS_HOST=localhost
REDIS_PORT=6379
```
### **5. Run Database Migrations**
```bash
alembic upgrade head
```
### **6. Start the Application**
```bash
uvicorn src.main:app --reload
```

### **⚡ Running Celery Worker**
Ensure Redis is running, then start the Celery worker:
```bash
celery -A src.celery_tasks.c_app worker --loglevel=info
```

### **📧 Sending Emails via Celery
To start the Celery Flower dashboard:
```bash
celery -A src.celery_tasks.c_app flower

```
### **🧪 Running Tests**
```bash
pytest src/tests

```
📖 API Documentation
FastAPI provides built-in interactive documentation:

Swagger UI: http://127.0.0.1:8000/docs

Redoc UI: http://127.0.0.1:8000/redoc



