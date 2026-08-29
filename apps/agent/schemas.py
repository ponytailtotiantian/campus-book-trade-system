"""Small validation and result helpers for the read-only Agent tools."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

LISTING_TYPES = {"SALE", "DONATION"}
ORDER_STATUSES = {"PENDING", "LOCKED", "PICKUP_PENDING", "COMPLETED", "CANCELLED"}
ROLES = {"buyer", "seller", "all"}


class ToolValidationError(ValueError):
    """Raised when an Agent tool receives unusable parameters."""


def clean_text(value: Any, field_name: str = "value", max_length: int = 100) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > max_length:
        raise ToolValidationError(f"{field_name} 过长，最大允许 {max_length} 个字符。")
    return text


def parse_non_negative_decimal(value: Any, field_name: str) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ToolValidationError(f"{field_name} 必须是有效数字。") from None
    if not number.is_finite() or number < 0:
        raise ToolValidationError(f"{field_name} 必须是非负有限数字。")
    return number


def normalize_limit(value: Any, default: int, maximum: int) -> int:
    if value is None:
        return default
    try:
        limit = int(value)
    except (TypeError, ValueError):
        raise ToolValidationError("limit 必须是整数。") from None
    if limit < 1:
        raise ToolValidationError("limit 必须大于 0。")
    return min(limit, maximum)


def validate_listing_type(value: Any) -> str | None:
    if value is None or value == "":
        return None
    listing_type = str(value).strip().upper()
    if listing_type not in LISTING_TYPES:
        raise ToolValidationError("listing_type 只能是 SALE 或 DONATION。")
    return listing_type


def validate_role(value: Any) -> str:
    role = clean_text(value, "role", 10) or "buyer"
    role = role.lower()
    if role not in ROLES:
        raise ToolValidationError("role 只能是 buyer、seller 或 all。")
    return role


def validate_order_status(value: Any) -> str | None:
    if value is None or value == "":
        return None
    status = str(value).strip().upper()
    if status not in ORDER_STATUSES:
        raise ToolValidationError("status 必须是数据库已有的订单状态。")
    return status


def parse_positive_id(value: Any) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise ToolValidationError("ID 必须是整数。") from None
    if result < 1:
        raise ToolValidationError("ID 必须大于 0。")
    return result


def validation_error(message: str) -> dict[str, Any]:
    return {"error": message}


def not_found_result(listing_id: Any) -> dict[str, Any]:
    return {
        "not_found": True,
        "message": f"未找到在售商品，listing_id={listing_id}。",
        "listing_id": listing_id,
    }


def authentication_required_result() -> dict[str, Any]:
    return {
        "authentication_required": True,
        "message": "请先登录后再查询我的订单。",
    }


def iso_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat()
