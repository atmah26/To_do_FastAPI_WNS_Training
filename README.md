# ✅ To-Do REST API

A Task management REST API built with **FastAPI**, **SQLAlchemy**, and **Pydantic v2**, developed as part of WNS Training. New task creation events are published to an **Azure Service Bus Queue**.

---

## 📁 Project Structure

```
To_do_FastAPI_WNS_Training/
├── main.py              # FastAPI app — routes and endpoint logic
├── pydanticmodels.py    # Pydantic schemas with field validators
├── messaging.py         # Azure Service Bus publisher
├── table.py             # SQLAlchemy ORM model (Task table)
├── db.py                # Database engine and session setup
├── .env.example         # Required environment variables (copy to .env)
├── .gitignore
└── README.md
```

---

## ⚙️ Tech Stack

| Layer         | Library           |
|---------------|-------------------|
| Web Framework | FastAPI           |
| ORM           | SQLAlchemy        |
| Validation    | Pydantic v2       |
| Database      | SQLite            |
| Messaging     | Azure Service Bus |
| Server        | Uvicorn           |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/atmah26/To_do_FastAPI_WNS_Training.git
cd To_do_FastAPI_WNS_Training
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi sqlalchemy pydantic uvicorn azure-servicebus python-dotenv
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your Azure Service Bus credentials:

```
AZURE_SERVICE_BUS_CONNECTION_STRING=Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=<policy>;SharedAccessKey=<key>
AZURE_SERVICE_BUS_QUEUE_NAME=<your-queue-name>
```

You can find the connection string in the Azure Portal under your Service Bus namespace → **Shared access policies**.

### 5. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive docs (Swagger UI) at `http://127.0.0.1:8000/docs`.

---

## 📌 API Endpoints

| Method   | Endpoint                          | Description                            |
|----------|-----------------------------------|----------------------------------------|
| `GET`    | `/tasks/`                         | Get all tasks                          |
| `GET`    | `/tasks/{task_id}`                | Get a task by ID                       |
| `POST`   | `/tasks/`                         | Create a new task *(publishes to bus)* |
| `PUT`    | `/tasks/update/{task_id}`         | Update a task                          |
| `PUT`    | `/tasks/change-status/{task_id}`  | Toggle a task's status                 |
| `DELETE` | `/tasks/{task_id}`                | Delete a task                          |

---

## 📨 Azure Service Bus Integration

When a task is successfully created via `POST /tasks/`, a JSON event is published to the configured Service Bus queue.

**Message payload:**
```json
{
  "event": "task_created",
  "timestamp": "2025-05-20T10:30:00+00:00",
  "data": {
    "id": 1,
    "description": "Buy groceries",
    "status": false
  }
}
```

**Message properties:**
- `content_type`: `application/json`
- `subject`: `task_created`

**Error handling:** if the Service Bus publish fails, the task is still saved to the database and a response is returned to the caller. The failure is logged as an error and will not interrupt the API.

---

## 📦 Request & Response Examples

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

---

### Delete a Task — `DELETE /tasks/1`

**Response `200`:**
```json
{
  "message": "Task Deleted"
}
```

---

## 🛡️ Validation Rules

Defined in `pydanticmodels.py` using `@field_validator`:

| Field         | Rules                                                                                              |
|---------------|----------------------------------------------------------------------------------------------------|
| `description` | Required · 3–100 characters · must contain at least one letter · whitespace stripped · auto sentence-cased |
| `status`      | Required · boolean (`true` / `false`)                                                              |

Invalid requests return `422 Unprocessable Entity` with a message identifying which field failed and why.

---

## 🗄️ Database

The app uses **SQLite**. The file `users.db` is created automatically on first run via:

```python
Base.metadata.create_all(engine)
```

To switch to PostgreSQL or MySQL, update the connection URL in `db.py`:

```python
# PostgreSQL example
engine = create_engine("postgresql://user:password@localhost/dbname")
```

---

## 📐 Data Model

**Task**

| Column        | Type        | Constraints                 |
|---------------|-------------|-----------------------------|
| `id`          | Integer     | Primary key, auto-increment |
| `description` | String(100) | Not null                    |
| `status`      | Boolean     | Not null                    |
