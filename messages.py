import json
import logging
import os
from datetime import datetime, timezone

from azure.servicebus import ServiceBusClient, ServiceBusMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CONNECTION_STRING = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
QUEUE_NAME = os.getenv("AZURE_SERVICE_BUS_QUEUE_NAME")


def publish_task_created(task_id: int, description: str, status: bool) -> None:
    if not CONNECTION_STRING or not QUEUE_NAME:
        raise RuntimeError(
            "Azure Service Bus is not configured. "
            "Set AZURE_SERVICE_BUS_CONNECTION_STRING and AZURE_SERVICE_BUS_QUEUE_NAME."
        )

    payload = {
        "event": "task_created",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "id": task_id,
            "description": description,
            "status": status,
        },
    }

    with ServiceBusClient.from_connection_string(CONNECTION_STRING) as client:
        with client.get_queue_sender(QUEUE_NAME) as sender:
            message = ServiceBusMessage(
                body=json.dumps(payload),
                content_type="application/json",
                subject="task_created",
            )
            sender.send_messages(message)
            logger.info("Published task_created event for task id=%s", task_id)