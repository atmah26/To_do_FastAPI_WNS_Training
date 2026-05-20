from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import SessionLocal
from table import Task
from pydanticmodels import TaskCreate, TaskResponse

from typing import Optional, List


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

get_db()

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db:Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not Found")
    return task

@app.post("/tasks/" , response_model=TaskResponse)
def create_task(task : TaskCreate, db:Session = Depends(get_db)):
    if db.query(Task).filter(Task.description == task.description).first():
        raise HTTPException(status_code=404, detail="Task already exists")

    new_task = Task(**task.dict())
    db.add(new_task)
    db.commit()
    return new_task

@app.put("/tasks/update/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task : TaskCreate, db:Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task does not exist")

    for field, value in task.dict().items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task

@app.put("/tasks/change-status/{task_id}", response_model=TaskResponse)
def change_status(task_id: int, db:Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task does not exist")

    if db_task.status:
        db_task.status = False
    else:
        db_task.status = True

    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}")
def delete_user(task_id: int, db:Session = Depends(get_db)):
    to_delete = db.query(Task).filter(Task.id == task_id).first()
    if not to_delete:
        raise HTTPException(status_code=404, detail="Task does not exist")

    db.delete(to_delete)
    db.commit()
    return {"message" : "Task Deleted"}

@app.get("/tasks/", response_model=List[TaskResponse])
def get_all_tasks(db:Session = Depends(get_db)):
    return db.query(Task).all()


