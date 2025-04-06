from celery import shared_task
from datetime import datetime, timedelta
from app import db
from app.models import TaskManager, TaskLogger

@shared_task(bind=True)
def transfer_active_tasks(self):
    """Celery task to transfer active tasks daily"""
    try:
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        
        # Get existing logs for today (optimized query)
        existing_logs = db.session.query(TaskLogger.task_id).filter(
            TaskLogger.created_at >= start_of_day
        ).all()
        logged_task_ids = {task_id for (task_id,) in existing_logs}
        
        # Process in batches for memory efficiency
        batch_size = 1000
        query = TaskManager.query.filter(
            TaskManager.status == True,
            ~TaskManager.id.in_(logged_task_ids)
        )
        
        total_processed = 0
        while True:
            tasks = query.limit(batch_size).all()
            if not tasks:
                break
                
            new_logs = [
                TaskLogger(
                    task_id=task.id,
                    status=task.status,
                    priority=task.priority,
                    changed_by=1  # System user
                ) for task in tasks
            ]
            
            db.session.bulk_save_objects(new_logs)
            db.session.commit()
            total_processed += len(tasks)
            
            # Update query to get next batch
            if len(tasks) < batch_size:
                break
            last_id = tasks[-1].id
            query = query.filter(TaskManager.id > last_id)
        
        return f"Processed {total_processed} tasks"
    except Exception as e:
        db.session.rollback()
        raise self.retry(exc=e, countdown=60)