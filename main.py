from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from db import SessionLocal
from table import Task
from pydanticmodels import TaskCreate, TaskResponse
from messaging import publish_task_created

logger = logging.getLogger(__name__)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/tasks/", response_model=List[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@app.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    if db.query(Task).filter(Task.description == task.description).first():
        raise HTTPException(status_code=409, detail="Task already exists.")

    new_task = Task(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    try:
        publish_task_created(
            task_id=new_task.id,
            description=new_task.description,
            status=new_task.status,
        )
    except Exception as e:
        # Task is already persisted — log the failure but don't roll back or
        # return a 500. The caller gets the created task; the bus failure is
        # an ops concern surfaced via logs.
        logger.error("Failed to publish task_created event for id=%s: %s", new_task.id, e)

    return new_task


@app.put("/tasks/update/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task does not exist.")

    for field, value in task.dict().items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


@app.put("/tasks/change-status/{task_id}", response_model=TaskResponse)
def change_status(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task does not exist.")

    db_task.status = not db_task.status

    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task does not exist.")

    db.delete(db_task)
    db.commit()
    return {"message": "Task Deleted"}