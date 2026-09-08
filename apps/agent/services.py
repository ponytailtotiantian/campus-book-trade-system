"""Agent service that connects DeepSeek to the four read-only tools."""
from __future__ import annotations

import json
import logging
from typing import Any

from apps.agent.llm_client import DeepSeekAPIError, DeepSeekClient, DeepSeekConfigurationError
from apps.agent.schemas import ToolValidationError, validation_error
from apps.agent.tools import get_book_detail, get_my_orders, recommend_books, search_books


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
你是校园二手书交易系统的智能助手。
你只能通过提供的四个工具查询系统数据：
- search_books
- get_book_detail
- recommend_books
- get_my_orders

禁止虚构数据库中不存在的商品、订单或用户信息。
如果用户询问数据库中的实时信息，应调用工具。
如果没有查询到数据，应明确告诉用户没有找到。
不要声称执行了没有执行的操作。

当前 Agent 是只读助手，不能：
- 下单
- 支付
- 发布商品
- 修改订单
- 修改库存
- 删除数据

如果用户要求执行这些操作，应明确说明当前 Agent 不支持。
""".strip()


AGENT_TOOL_FUNCTIONS = {
    "search_books": search_books,
    "get_book_detail": get_book_detail,
    "recommend_books": recommend_books,
    "get_my_orders": get_my_orders,
}


AGENT_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": "搜索当前校园二手书系统中在售的二手书。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "书名、作者、ISBN 或课程名称关键词。",
                    },
                    "category": {
                        "type": "string",
                        "description": "图书分类名称，例如计算机、教材。",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "价格上限。",
                    },
                    "listing_type": {
                        "type": "string",
                        "enum": ["SALE", "DONATION"],
                        "description": "SALE 表示出售，DONATION 表示赠送。",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回数量上限，默认 10，最大 20。",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_book_detail",
            "description": "查询指定在售二手书商品的详细信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "listing_id": {
                        "type": "integer",
                        "description": "二手书商品 listing 的 ID。",
                    }
                },
                "required": ["listing_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_books",
            "description": "根据关键词、分类和价格偏好推荐在售二手书。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "书名、作者、分类或课程名称关键词。",
                    },
                    "category": {
                        "type": "string",
                        "description": "图书分类名称。",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "价格上限。",
                    },
                    "listing_type": {
                        "type": "string",
                        "enum": ["SALE", "DONATION"],
                    },
                    "prefer_low_price": {
                        "type": "boolean",
                        "description": "是否优先返回低价商品，默认 true。",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回数量上限，默认 5，最大 10。",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_orders",
            "description": "查询当前登录用户自己的订单。用户身份由系统注入，LLM 不需要也不能提供用户 ID。",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "可选，指定订单 ID。",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["PENDING", "LOCKED", "PICKUP_PENDING", "COMPLETED", "CANCELLED"],
                        "description": "订单状态。",
                    },
                    "order_type": {
                        "type": "string",
                        "enum": ["SALE", "DONATION"],
                        "description": "订单类型。",
                    },
                    "role": {
                        "type": "string",
                        "enum": ["buyer", "seller", "all"],
                        "description": "查询角度，默认 buyer。",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回数量上限，默认 20，最大 50。",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]


def _parse_tool_arguments(arguments: Any) -> dict[str, Any]:
    if isinstance(arguments, dict):
        return arguments
    if not isinstance(arguments, str):
        raise ValueError("arguments must be a JSON string or dict")
    parsed = json.loads(arguments)
    if not isinstance(parsed, dict):
        raise ValueError("arguments must be a JSON object")
    return parsed


def _execute_tool(name: str, arguments: Any, request: Any) -> dict[str, Any]:
    if name not in AGENT_TOOL_FUNCTIONS:
        return validation_error(f"Tool '{name}' 不存在，拒绝执行。")

    try:
        args = _parse_tool_arguments(arguments)
    except (json.JSONDecodeError, TypeError, ValueError):
        return validation_error("Tool 参数不是合法 JSON。")

    if name == "get_my_orders":
        if "user_id" in args:
            return validation_error("不允许通过 LLM 参数指定用户身份。")
        if "request" in args:
            return validation_error("request 参数不允许由 LLM 提供。")
        args["request"] = request

    try:
        return AGENT_TOOL_FUNCTIONS[name](**args)
    except ToolValidationError as exc:
        return validation_error(str(exc))
    except TypeError as exc:
        logger.warning("Agent tool %s received invalid parameters: %s", name, exc)
        return validation_error("Tool 参数不正确。")
    except Exception:
        logger.exception("Agent tool %s failed", name)
        return validation_error("查询失败，请稍后再试。")


class AgentService:
    """Runs the smallest possible DeepSeek Function Calling loop."""

    def __init__(self, client: DeepSeekClient | None = None, max_tool_rounds: int = 3) -> None:
        self.client = client or DeepSeekClient()
        self.max_tool_rounds = max_tool_rounds

    def chat(self, request: Any, user_message: str) -> dict[str, Any]:
        message_text = str(user_message or "").strip()
        if not message_text:
            return {"error": "用户消息不能为空。"}

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message_text},
        ]

        try:
            return self._run(messages, request)
        except DeepSeekConfigurationError:
            logger.warning("DeepSeek configuration is missing.")
            return {"error": "DeepSeek API Key 未配置。"}
        except DeepSeekAPIError:
            logger.warning("DeepSeek API call failed.")
            return {"error": "智能助手暂时无法连接，请稍后再试。"}
        except Exception:
            logger.exception("AgentService.chat failed")
            return {"error": "智能助手暂时无法连接，请稍后再试。"}

    def _run(self, messages: list[dict[str, Any]], request: Any) -> dict[str, Any]:
        for _ in range(self.max_tool_rounds + 1):
            response = self.client.chat(messages, tools=AGENT_TOOL_SCHEMAS)
            try:
                message = response.choices[0].message
            except (AttributeError, IndexError) as exc:
                raise DeepSeekAPIError("invalid response") from exc

            tool_calls = getattr(message, "tool_calls", None) or []
            if not tool_calls:
                content = getattr(message, "content", None) or "未获取到回答。"
                return {"reply": content}

            messages.append(
                {
                    "role": "assistant",
                    "content": getattr(message, "content", None),
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in tool_calls
                    ],
                }
            )
            reasoning_content = getattr(message, "reasoning_content", None)
            if reasoning_content:
                messages[-1]["reasoning_content"] = reasoning_content

            for tool_call in tool_calls:
                result = _execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                    request,
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

            final_messages = messages + [
                {
                    "role": "user",
                    "content": (
                        "请根据上面的工具查询结果直接回答用户，"
                        "不要继续调用工具。回答要简洁，列出商品编号、书名、价格、库存和类型。"
                    ),
                }
            ]
            final_response = self.client.chat(final_messages)
            try:
                final_message = final_response.choices[0].message
            except (AttributeError, IndexError) as exc:
                raise DeepSeekAPIError("invalid final response") from exc
            content = getattr(final_message, "content", None) or "未获取到回答。"
            return {"reply": content}

        return {"error": "智能助手 Tool 调用次数过多，请简化问题后重试。"}
