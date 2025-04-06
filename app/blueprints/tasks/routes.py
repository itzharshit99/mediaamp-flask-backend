from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt
from app.models import TaskManager, TaskLogger, User, Priority, Role
from app import db  # Import db from app/__init__.py
from pydantic import BaseModel, ValidationError
from datetime import datetime
import csv
from io import StringIO
from typing import Optional
tasks_bp = Blueprint('tasks', __name__)

# Pydantic models
class TaskCreate(BaseModel):
    task_name: str
    description: Optional[str]
    status: bool
    priority: str

class TaskUpdate(BaseModel):
    task_name: Optional[str]
    description:Optional[str]
    status: Optional[bool]
    priority: Optional[str]

def role_required(role):
    def decorator(f):
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get_or_404(user_id)
            if user.role != role:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

@tasks_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    role = data.get('role', 'user')
    
    print(f"Received username: {username}, role: {role}")
    print(f"Available roles: {[r.name for r in Role]}")
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    try:
        role_key = role.upper()
        user_role = Role[role_key]
        print(f"Converted role: {user_role}")
    except KeyError:
        print(f"Error with role: {role}, valid options: {[r.name for r in Role]}")
        return jsonify({'error': 'Invalid role, use "admin" or "user"'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, role=user_role)
        db.session.add(user)
        db.session.commit()
    
    # Convert user.id to string
    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'User created/logged in',
        'user_id': user.id,
        'token': token
    }), 200

# Other endpoints remain the same...
@tasks_bp.route('/upload-csv', methods=['POST'])
@jwt_required()
def upload_csv():
    try:
        current_user_id = get_jwt_identity()
        print(f"Current User ID: {current_user_id}")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file format'}), 400
        
        stream = StringIO(file.stream.read().decode('utf-8'))
        csv_reader = csv.DictReader(stream)
        
        required_fields = {'task_name', 'description', 'status', 'priority', 'created_at', 'assigned_user'}
        if not all(field in csv_reader.fieldnames for field in required_fields):
            return jsonify({'error': 'Missing required CSV fields'}), 400
        
        print(f"Available Priorities: {[p.name for p in Priority]}")
        print(f"Priority Values: {[p.value for p in Priority]}")
        
        for row in csv_reader:
            print(f"Processing row: {row}")
            
            user = User.query.filter_by(username=row['assigned_user']).first()
            if not user:
                user = User(username=row['assigned_user'], role=Role.USER)
                db.session.add(user)
                db.session.flush()
            
            try:
                created_at = datetime.strptime(row['created_at'], '%m/%d/%Y')
                priority_value = row['priority'].lower()
                print(f"Priority from CSV: {priority_value}")
                
                # Validate priority
                valid_priorities = {p.value: p for p in Priority}  # Map of value to enum
                if priority_value not in valid_priorities:
                    raise ValueError(f"Invalid priority '{priority_value}'. Valid options: {list(valid_priorities.keys())}")
                
                # Use enum object directly
                task = TaskManager(
                    task_name=row['task_name'],
                    description=row['description'],
                    status=row['status'].upper() == 'TRUE',
                    priority=valid_priorities[priority_value],  # Yeh sahi enum object dega
                    created_at=created_at,
                    user_id=user.id
                )
                db.session.add(task)
                db.session.flush()
                
                log = TaskLogger(
                    task_id=task.id,
                    status=task.status,
                    priority=task.priority,
                    changed_by=current_user_id
                )
                db.session.add(log)
            except ValueError as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 400
        
        db.session.commit()
        return jsonify({'message': 'CSV uploaded successfully'}), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    date_filter = request.args.get('date')
    
    query = TaskLogger.query
    if date_filter:
        try:
            datetime.strptime(date_filter, '%Y-%m-%d')
            query = query.filter(db.func.date(TaskLogger.changed_at) == date_filter)
        except ValueError:
            return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400
    
    tasks = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'tasks': [{
            'id': t.id,
            'task_id': t.task_id,
            'status': t.status,
            'priority': t.priority.value,
            'changed_at': t.changed_at.isoformat()
        } for t in tasks.items],
        'total': tasks.total,
        'pages': tasks.pages
    })

@tasks_bp.route('/task/<int:task_logger_id>', methods=['GET'])
def get_task(task_logger_id):
    task = TaskLogger.query.get_or_404(task_logger_id)
    return jsonify({
        'id': task.id,
        'task_id': task.task_id,
        'status': task.status,
        'priority': task.priority.value,
        'changed_at': task.changed_at.isoformat()
    })

@tasks_bp.route('/task', methods=['POST'])
@jwt_required()
def create_task():
    try:
        data = TaskCreate(**request.json)
        user_id = get_jwt_identity()
        
        # Convert priority to uppercase once and reuse
        priority = Priority[data.priority.upper()]
        
        task = TaskManager(
            task_name=data.task_name,
            description=data.description,
            status=data.status,
            priority=priority,  # Using the already converted priority
            user_id=user_id
        )
        db.session.add(task)
        db.session.flush()
        
        log = TaskLogger(
            task_id=task.id,
            status=data.status,
            priority=priority,  # Using the same priority here
            changed_by=user_id
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'message': 'Task created', 'task_id': task.id}), 201
    except ValidationError as e:
        return jsonify(e.errors()), 400
    except (ValueError, KeyError):
        return jsonify({'error': 'Priority must be HIGH, MEDIUM or LOW'}), 400

@tasks_bp.route('/task/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        print(f"Current User ID from Token: {current_user_id} (Type: {type(current_user_id)})")
        print(f"Full JWT Payload: {get_jwt()}")  # This will now work with the import
        
        task = TaskManager.query.get_or_404(task_id)
        print(f"Task Owner ID: {task.user_id} (Type: {type(task.user_id)})")
        
        # Assuming task.user_id is an integer in the database
        if int(task.user_id) != int(current_user_id):
            return jsonify({
                'error': 'Unauthorized',
                'message': f'User {current_user_id} cannot update task owned by {task.user_id}'
            }), 403
        
        data = TaskUpdate(**request.json)
        updated = False
        
        fields_to_update = {
            'task_name': data.task_name,
            'description': data.description,
            'status': data.status,
            'priority': data.priority
        }
        
        for field, value in fields_to_update.items():
            if value is not None:
                if field == 'priority':
                    # Ensure consistent case handling with Priority enum
                    setattr(task, field, Priority[value.upper()])
                else:
                    setattr(task, field, value)
                updated = True
        
        if updated:
            log = TaskLogger(
                task_id=task_id,
                status=task.status,
                priority=task.priority,
                changed_by=current_user_id
            )
            db.session.add(log)
        db.session.commit()
        return jsonify({
            'message': 'Task updated successfully' if updated else 'No changes detected'
        }), 200
        
    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': 'Validation failed', 'details': e.errors()}), 400
    except KeyError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid priority value: {str(e)}'}), 400
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid user ID format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@tasks_bp.route('/task/<int:task_id>', methods=['DELETE'])
@jwt_required()
@role_required(Role.ADMIN)
def delete_task(task_id):
    task = TaskManager.query.get_or_404(task_id)
    task.status = False
    log = TaskLogger(
        task_id=task_id,
        status=False,
        priority=task.priority,
        changed_by=get_jwt_identity()
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Task soft deleted'})