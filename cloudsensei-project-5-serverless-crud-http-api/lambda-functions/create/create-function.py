"""POST /items — write one item to the table."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Resolved once at cold start. The table name comes from the environment because
# the function has no business discovering it at runtime.
TABLE_NAME = os.environ["TABLE_NAME"]
table = boto3.resource("dynamodb").Table(TABLE_NAME)

ROUTE = "POST /items"
REQUIRED_FIELDS = ("id", "name", "price")


def respond(status_code: int, body: Any) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
    }


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    route_key = event.get("routeKey")
    if route_key != ROUTE:
        return respond(404, f"Unsupported route: {route_key!r}")

    try:
        item = json.loads(event["body"])
    except (KeyError, TypeError, ValueError):
        return respond(400, "Request body is not valid JSON")

    missing = [field for field in REQUIRED_FIELDS if field not in item]
    if missing:
        return respond(400, f"Missing required field(s): {', '.join(missing)}")

    try:
        table.put_item(
            Item={
                "id": str(item["id"]),
                "name": str(item["name"]),
                "price": str(item["price"]),
            }
        )
    except Exception:
        # Logged with the traceback so CloudWatch has something to work with,
        # but not returned — the caller doesn't need our internals.
        logger.exception("put_item failed for id=%s", item.get("id"))
        return respond(500, "Could not store item")

    return respond(201, f"Created item {item['id']}")
