"""PUT /items/{id} — replace one item."""

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

ROUTE = "PUT /items/{id}"
REQUIRED_FIELDS = ("name", "price")


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
        payload = json.loads(event["body"])
    except (KeyError, TypeError, ValueError):
        return respond(400, "Request body is not valid JSON")

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        return respond(400, f"Missing required field(s): {', '.join(missing)}")

    try:
        # PUT is a full replace, so put_item is the right call — the id comes
        # from the path and any id in the body is ignored.
        table.put_item(
            Item={
                "id": item_id,
                "name": str(payload["name"]),
                "price": str(payload["price"]),
            }
        )
    except Exception:
        logger.exception("put_item failed for id=%s", item_id)
        return respond(500, "Could not update item")

    return respond(200, f"Updated item {item_id}")
