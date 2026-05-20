# ✅ To-Do REST API + Azure Function Consumer

A Task management REST API built with **FastAPI**, **SQLAlchemy**, and **Pydantic v2**. New task creation events are published to an **Azure Service Bus Queue** and consumed by a **Python v2 Azure Function**.

---

## 📁 Project Structure

```
To_do_FastAPI_WNS_Training/
│
├── api/                          # FastAPI application
│   ├── main.py                   # Routes and endpoint logic
│   ├── pydanticmodels.py         # Pydantic schemas with field validators
│   ├── messaging.py              # Azure Service Bus publisher
│   ├── table.py                  # SQLAlchemy ORM model (Task table)
│   ├── db.py                     # Database engine and session setup
│   └── .env.example              # API environment variables template
│
├── functions/                    # Azure Function App
│   ├── function_app.py           # Service Bus trigger + handler logic
│   ├── host.json                 # Azure Functions host configuration
│   ├── requirements.txt          # Function dependencies
│   └── local.settings.json.example  # Function environment variables template
│
├── .gitignore
└── README.md
```

---

## 🏗️ Architecture

```
┌─────────────────┐     POST /tasks/     ┌─────────────────┐
│                 │ ──────────────────── │                 │
│   HTTP Client   │                      │   FastAPI API   │
│  (Swagger/curl) │ ◄─────────────────── │   (main.py)     │
│                 │    201 + task JSON   │                 │
└─────────────────┘                      └────────┬────────┘
                                                  │
                                                  │ publish task_created event
                                                  ▼
                                         ┌─────────────────┐
                                         │  Azure Service  │
                                         │   Bus Queue     │
                                         └────────┬────────┘
                                                  │
                                                  │ trigger on new message
                                                  ▼
                                         ┌─────────────────┐
                                         │ Azure Function  │
                                         │ (function_app)  │
                                         └─────────────────┘
```

---

## ⚙️ Tech Stack

| Layer              | Library / Service         |
|--------------------|---------------------------|
| Web Framework      | FastAPI                   |
| ORM                | SQLAlchemy                |
| Validation         | Pydantic v2               |
| Database           | SQLite                    |
| Messaging          | Azure Service Bus         |
| Event Consumer     | Azure Functions (Python v2)|
| API Server         | Uvicorn                   |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- An Azure account with a Service Bus namespace and queue
- [Azure Functions Core Tools v4](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) (for running the function locally)

---

### Part 1 — FastAPI App

#### 1. Clone the repository

```bash
git clone https://github.com/atmah26/To_do_FastAPI_WNS_Training.git
cd To_do_FastAPI_WNS_Training/api
```

#### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install fastapi sqlalchemy pydantic uvicorn azure-servicebus python-dotenv
```

#### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
AZURE_SERVICE_BUS_CONNECTION_STRING=Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=<policy>;SharedAccessKey=<key>
AZURE_SERVICE_BUS_QUEUE_NAME=<your-queue-name>
```

#### 5. Run the API

```bash
uvicorn main:app --reload
```

API available at `http://127.0.0.1:8000`.  
Swagger UI at `http://127.0.0.1:8000/docs`.

---

### Part 2 — Azure Function

#### 1. Navigate to the functions folder

```bash
cd ../functions
```

#### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure local settings

```bash
cp local.settings.json.example local.settings.json
```

Edit `local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_SERVICE_BUS_CONNECTION_STRING": "Endpoint=sb://...",
    "AZURE_SERVICE_BUS_QUEUE_NAME": "task-created"
  }
}
```

#### 5. Start the function

```bash
func start
```

You will see:
```
Functions:
    todo_created_handler: serviceBusTrigger
```

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

### Publisher (API → Queue)

When a task is successfully created via `POST /tasks/`, `messaging.py` publishes a JSON event to the queue.

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

If the publish fails, the task is still saved and the API still responds. The failure is logged as an error and does not affect the caller.

---

### Consumer (Queue → Azure Function)

`function_app.py` triggers automatically when a message lands on the queue.

**What it does:**
- Decodes and deserialises the message body
- Validates the event type and required fields
- Logs the event details
- Raises on malformed messages, sending them to the **dead-letter queue** for inspection after max retries

**Delivery behaviour (configured in `host.json`):**

| Setting                  | Value  | Effect                                              |
|--------------------------|--------|-----------------------------------------------------|
| `autoCompleteMessages`   | `true` | Message removed from queue on successful return     |
| `maxConcurrentCalls`     | `1`    | Processes one message at a time                     |
| `maxAutoLockRenewalDuration` | `5 min` | Keeps the message locked during slow processing |

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

> Descriptions are automatically sentence-cased (`"buy groceries"` → `"Buy groceries"`).

---

### Update a Task — `PUT /tasks/update/1`

```json
{
  "description": "Buy groceries and cook dinner",
  "status": false
}
```

---

### Toggle Status — `PUT /tasks/change-status/1`

No request body. Flips `status` between `true` and `false`.

---

### Delete a Task — `DELETE /tasks/1`

```json
{ "message": "Task Deleted" }
```

---

## 🛡️ Validation Rules

Defined in `pydanticmodels.py` using `@field_validator`:

| Field         | Rules                                                                                              |
|---------------|----------------------------------------------------------------------------------------------------|
| `description` | Required · 3–100 characters · must contain at least one letter · whitespace stripped · auto sentence-cased |
| `status`      | Required · boolean (`true` / `false`)                                                              |

Invalid requests return `422 Unprocessable Entity`.

---

## 🗄️ Database

SQLite — `users.db` is created automatically on first run. To switch databases, update the connection URL in `db.py`:

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
