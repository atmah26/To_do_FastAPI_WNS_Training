# ✅ To-Do REST API

---

## 📁 Project Structure

```
To_do_FastAPI_WNS_Training/
├── main.py              # FastAPI app — routes and endpoint logic
├── pydanticmodels.py    # Pydantic schemas with field validators
├── table.py             # SQLAlchemy ORM model (Task table)
├── db.py                # Database engine and session setup
├── .gitignore
└── README.md
```

---

## Tech Stack

| Layer         | Library    |
|---------------|------------|
| Web Framework | FastAPI    |
| ORM           | SQLAlchemy |
| Validation    | Pydantic v2|
| Database      | SQLite     |
| Server        | Uvicorn    |

---
##  API Endpoints

| Method   | Endpoint                          | Description             |
|----------|-----------------------------------|-------------------------|
| `GET`    | `/tasks/`                         | Get all tasks           |
| `GET`    | `/tasks/{task_id}`                | Get a task by ID        |
| `POST`   | `/tasks/`                         | Create a new task       |
| `PUT`    | `/tasks/update/{task_id}`         | Update a task           |
| `PUT`    | `/tasks/change-status/{task_id}`  | Toggle a task's status  |
| `DELETE` | `/tasks/{task_id}`                | Delete a task           |

---

##  Request & Response Examples

### Create a Task — `POST /tasks/`

**Request body:**
```json
{
  "description": "buy groceries",
  "status": false
}
```

**Response `200`:**
```json
{
  "id": 1,
  "description": "Buy groceries",
  "status": false
}
```

> Descriptions are automatically sentence-cased by the validator (e.g. `"buy groceries"` → `"Buy groceries"`).

---

### Update a Task — `PUT /tasks/update/1`

Replaces both fields. Both `description` and `status` are required.

```json
{
  "description": "Buy groceries and cook dinner",
  "status": false
}
```

---

### Toggle Status — `PUT /tasks/change-status/1`

No request body needed. Flips `status` between `true` and `false`.

**Response `200`:**
```json
{
  "id": 1,
  "description": "Buy groceries and cook dinner",
  "status": true
}
```

---

### Delete a Task — `DELETE /tasks/1`

**Response `200`:**
```json
{
  "message": "Task Deleted"
}
```

---

## Validation Rules

Defined in `pydanticmodels.py` using `@field_validator`:

| Field         | Rules                                                                  |
|---------------|------------------------------------------------------------------------|
| `description` | Required · 3–100 characters · must contain at least one letter · leading/trailing whitespace stripped · auto sentence-cased |
| `status`      | Required · boolean (`true` / `false`)                                  |

Invalid requests return `422 Unprocessable Entity` with a message identifying which field failed and why.

---

##  Database

The app uses **SQLite**. The database file `users.db` is created automatically on first run via:

```python
Base.metadata.create_all(engine)
```

To switch to PostgreSQL or MySQL, update the connection URL in `db.py`:

```python
# PostgreSQL example
engine = create_engine("postgresql://user:password@localhost/dbname")
```

---

##  Data Model

**Task**

| Column        | Type       | Constraints              |
|---------------|------------|--------------------------|
| `id`          | Integer    | Primary key, auto-increment |
| `description` | String(100)| Not null                 |
| `status`      | Boolean    | Not null                 |

---
