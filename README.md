# Task Management System API

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.0%2B-green)
![PostgreSQL](https://img.shields.io/badge/postgresql-13%2B-blue)
![Redis](https://img.shields.io/badge/redis-6%2B-red)
![Docker](https://img.shields.io/badge/docker-20.10%2B-blue)

A production-ready task management system with role-based access control and automated processing.

## Features

- **Secure Authentication**: JWT with refresh tokens
- **Role-Based Access Control**: Admin, Manager, User roles
- **Task Operations**: Full CRUD with soft deletion
- **Daily Processing**: Automated task logging via Celery
- **Performance**: Redis caching for frequent requests
- **Audit Logs**: Track all system changes


## API Endpoints

Base URL: `http://localhost:5000/api`

### Authentication
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/login` | POST | User login | No |

### Task Operations
| Endpoint | Method | Description | Auth Required | Roles |
|----------|--------|-------------|---------------|-------|
| `/upload-csv` | POST | Bulk upload tasks from CSV | Yes | Admin |
| `/tasks` | GET | List all tasks (paginated) | Yes | Any |
| `/task/<id>` | GET | Get task details | Yes | Any |
| `/task` | POST | Create new task | Yes | Any |
| `/task/<id>` | PUT | Update task | Yes | Owner/Admin |
| `/task/<id>` | DELETE | Soft delete task | Yes | Admin |

## Request Examples

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"username": "admin", "role": "admin"}'
```
## Configuration

Create a `.env` file with these variables:

```ini
# Database Configuration (Neon PostgreSQL)
DEV_DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Security Configuration
JWT_SECRET_KEY=your_secure_random_jwt_secret
SECRET_KEY=your_secure_random_flask_secret
```
## 🚀 Development Setup

### Prerequisites
- Python 3.9+
- Docker 20.10+
- Neon PostgreSQL account

### Local Setup
```bash
# 1. Clone repository
git clone https://github.com/itzharshit99/mediaamp-flask-backend
cd mediaamp-flask-backend

# 2. Configure environment
cp .env.example .env
nano .env  # Add your Neon credentials

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run command
python run.py
```

## 🐳 Docker Commands

### Basic Operations
```bash
# First-time build
docker-compose build

# Start all services (detached mode)
docker-compose up -d

# Stop all services
docker-compose down

# View running containers
docker ps
```

## API Testing Results:
## User Login
![Screenshot 2025-04-06 162931](https://github.com/user-attachments/assets/a940984d-30ba-4258-a4a4-bdd8b6174bb7)

## Upload CSV
![Screenshot 2025-04-06 163355](https://github.com/user-attachments/assets/c68ee6c5-4243-4d59-a1a0-90b9fe9edd3c)
![Screenshot 2025-04-06 163445](https://github.com/user-attachments/assets/9d65afa8-02e8-47e1-b627-2a00bd1940f9)

## All Tasks Fetched from database
![Screenshot 2025-04-06 163539](https://github.com/user-attachments/assets/20f04d67-5c5f-4b11-9a10-d91c0e9a01d6)

## Tasks getting Fetched on the basis of their id from database
![Screenshot 2025-04-06 163637](https://github.com/user-attachments/assets/45052088-3ba8-4778-8ca8-ea2f7b709c9e)

## Adding task staticly
![Screenshot 2025-04-06 163916](https://github.com/user-attachments/assets/5fbc0aed-9ac6-44c0-a0ed-d80162a35162)

## Updating the task
![Screenshot 2025-04-06 164011](https://github.com/user-attachments/assets/d9446ae7-9631-4f59-9c98-034c09c43036)

## Soft deletion of task
![Screenshot 2025-04-06 164102](https://github.com/user-attachments/assets/88d39843-3e51-4773-9955-f8ca96f45b16)

## User table
![Screenshot 2025-04-06 164406](https://github.com/user-attachments/assets/d450559a-5d22-4d26-97db-4df4ddb6a4c6)


## 🤝 Contributing  
1. Fork the repo  
2. Create a branch (`git checkout -b feature/awesome-feature`)  
3. Commit changes (`git commit -m 'Add feature'`)  
4. Push (`git push origin feature/awesome-feature`)  
5. Open a PR!  

## 📜 License  
MIT © Harshit Jain
