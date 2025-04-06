from app import db  
from enum import Enum
from datetime import datetime

class Role(Enum):
    ADMIN = 'admin'
    USER = 'user'

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = 'critical'
    @classmethod
    def _missing_(cls, value):
        value = value.upper()
        for member in cls:
            if member.value == value:
                return member
        return None

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.Enum(Role), default=Role.USER, nullable=False)
    tasks = db.relationship('TaskManager', backref='user', lazy='dynamic')

class TaskManager(db.Model):
    __tablename__ = 'task_manager'
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Boolean, default=True, index=True)
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    logs = db.relationship('TaskLogger', backref='task', lazy='dynamic',
                         cascade='all, delete-orphan')
    __table_args__ = (db.Index('ix_task_status', 'status'),)

class TaskLogger(db.Model):
    __tablename__ = 'task_logger'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task_manager.id'), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    priority = db.Column(db.Enum(Priority), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))