"""GET /items and GET /items/{id} — list every item, or read one."""

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

LIST_ROUTE = "GET /items"
GET_ROUTE = "GET /items/{id}"


def respond(status_code: int, body: Any) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
    }


def list_items() -> dict[str, Any]:
    """Return every item, following pagination.

    A scan reads the whole table, which is fine at lab size. Without the
    LastEvaluatedKey loop it would also silently stop at 1MB of results.
    """
    items: list[dict[str, Any]] = []
    kwargs: dict[str, Any] = {}

    while True:
        response = table.scan(**kwargs)
        items.extend(response.get("Items", []))

        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            return respond(200, items)
        kwargs["ExclusiveStartKey"] = last_key


def get_item(item_id: str) -> dict[str, Any]:
    response = table.get_item(Key={"id": item_id})

    # get_item omits Item entirely when nothing matches, rather than erroring.
    item = response.get("Item")
    if item is None:
        return respond(404, f"No item with id {item_id}")
    return respond(200, item)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    route_key = event.get("routeKey")

    try:
        if route_key == LIST_ROUTE:
            return list_items()

        if route_key == GET_ROUTE:
            item_id = (event.get("pathParameters") or {}).get("id")
            if not item_id:
                return respond(400, "Missing path parameter: id")
            return get_item(item_id)
    except Exception:
        logger.exception("read failed for route=%s", route_key)
        return respond(500, "Could not read items")

    return respond(404, f"Unsupported route: {route_key!r}")
