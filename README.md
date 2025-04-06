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



