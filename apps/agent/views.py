import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from apps.agent.services import AgentService


logger = logging.getLogger(__name__)


@require_GET
@ensure_csrf_cookie
def agent_chat_page(request):
    return render(request, "agent/chat.html", {"page_title": "校园二手书 AI 助手"})


@require_POST
def agent_chat_api(request):
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "请求格式不正确，请稍后再试。"},
            status=400,
        )

    message = str(payload.get("message") or "").strip()
    if not message:
        return JsonResponse(
            {"success": False, "error": "请输入消息后再发送。"},
            status=400,
        )
    if len(message) > 1000:
        return JsonResponse(
            {"success": False, "error": "消息过长，请控制在 1000 字以内。"},
            status=400,
        )

    try:
        result = AgentService().chat(request, message)
    except Exception:
        logger.exception("agent chat api failed")
        return JsonResponse(
            {"success": False, "error": "智能助手暂时无法连接，请稍后再试。"},
            status=500,
        )

    if result.get("error"):
        return JsonResponse(
            {"success": False, "error": result["error"]},
            status=502,
        )

    return JsonResponse(
        {"success": True, "reply": result.get("reply", "未获取到回答，请稍后再试。")}
    )
