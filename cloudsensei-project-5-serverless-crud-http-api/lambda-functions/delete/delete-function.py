"""DELETE /items/{id} — remove one item."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ["TABLE_NAME"]
table = boto3.resource("dynamodb").Table(TABLE_NAME)

ROUTE = "DELETE /items/{id}"


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

    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        return respond(400, "Missing path parameter: id")

    try:
        # ReturnValues lets us tell "deleted something" from "there was nothing
        # there", which DynamoDB otherwise treats identically.
        response = table.delete_item(Key={"id": item_id}, ReturnValues="ALL_OLD")
    except Exception:
        logger.exception("delete_item failed for id=%s", item_id)
        return respond(500, "Could not delete item")

    if "Attributes" not in response:
        return respond(404, f"No item with id {item_id}")

    return respond(200, f"Deleted item {item_id}")
