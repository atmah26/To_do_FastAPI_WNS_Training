import azure.functions as func
import os
import logging
import json
from datetime import datetime, timezone

app = func.FunctionApp()


@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name=os.environ["AZURE_SERVICE_BUS_QUEUE_NAME"],
    connection="AZURE_SERVICE_BUS_CONNECTION_STRING",
)
def todo_created_handler(msg: func.ServiceBusMessage) -> None:
    """
    Triggers whenever a message lands on the Service Bus queue.
    Logs the event and can be extended to notify, persist, or forward.
    """
    received_at = datetime.now(timezone.utc).isoformat()

    try:
        raw = msg.get_body().decode("utf-8")
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        logging.error("Failed to deserialise message body: %s", e)
        # Raising here sends the message to the dead-letter queue after
        # max delivery attempts, rather than silently dropping it.
        raise

    event = payload.get("event")
    data  = payload.get("data", {})

    if event != "task_created":
        logging.warning("Unexpected event type '%s' — skipping.", event)
        return

    task_id     = data.get("id")
    description = data.get("description")
    status      = data.get("status")

    if task_id is None or description is None or status is None:
        logging.error("Malformed task_created payload — missing fields: %s", payload)
        raise ValueError("Malformed payload")

    logging.info(
        "task_created event received | id=%s | description='%s' | status=%s | received_at=%s",
        task_id,
        description,
        status,
        received_at,
    )