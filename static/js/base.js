document.addEventListener("DOMContentLoaded", function () {
    const navCollapse = document.getElementById("mainNav");
    if (navCollapse && window.bootstrap) {
        navCollapse.addEventListener("click", function (event) {
            const target = event.target.closest("a.nav-link, a.btn");
            if (!target) {
                return;
            }
            const collapse = window.bootstrap.Collapse.getInstance(navCollapse);
            if (collapse && navCollapse.classList.contains("show")) {
                collapse.hide();
            }
        });
    }

    document.querySelectorAll("[data-auto-submit]").forEach(function (select) {
        select.addEventListener("change", function () {
            if (select.form && typeof select.form.requestSubmit === "function") {
                select.form.requestSubmit();
            }
        });
    });
});

(function () {
    function setupAgentChat() {
        const app = document.getElementById("agentChatApp");
        if (!app) {
            return;
        }

        const messagesEl = document.getElementById("chatMessages");
        const form = document.getElementById("chatForm");
        const input = document.getElementById("chatInput");
        const sendBtn = document.getElementById("chatSendBtn");
        const errorEl = document.getElementById("chatError");

        if (!messagesEl || !form || !input || !sendBtn || !errorEl) {
            return;
        }

        const chatUrl = app.dataset.chatUrl;
        const csrfToken = app.dataset.csrfToken || "";

        function clearError() {
            errorEl.textContent = "";
        }

        function setError(message) {
            errorEl.textContent = message;
        }

        function getResponseError(response, data) {
            if (data && data.error) {
                return data.error;
            }
            if (response.status === 403) {
                return "页面凭证已过期，请刷新页面后再试。";
            }
            if (response.status >= 500) {
                return "服务器暂时异常，请稍后再试。";
            }
            return "请求失败（" + response.status + "），请稍后再试。";
        }

        function createRow(role, text, isTyping) {
            const row = document.createElement("div");
            row.className = "chat-row " + role;

            const avatar = document.createElement("span");
            avatar.className = "chat-avatar";
            avatar.textContent = role === "user" ? "我" : "AI";

            const bubble = document.createElement("div");
            bubble.className = "chat-bubble" + (isTyping ? " chat-typing" : "");
            bubble.textContent = text;

            row.appendChild(avatar);
            row.appendChild(bubble);
            messagesEl.appendChild(row);
            messagesEl.scrollTop = messagesEl.scrollHeight;
            return bubble;
        }

        function setLoading(loading) {
            sendBtn.disabled = loading;
            sendBtn.textContent = loading ? "AI 正在思考…" : "发送";
            if (loading) {
                input.setAttribute("aria-busy", "true");
            } else {
                input.removeAttribute("aria-busy");
            }
        }

        async function sendMessage(userText) {
            clearError();
            createRow("user", userText);
            input.value = "";
            setLoading(true);

            const typingBubble = createRow("assistant", "AI 正在思考…", true);

            try {
                const response = await fetch(chatUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify({ message: userText }),
                    credentials: "same-origin",
                });

                let data = null;
                try {
                    data = await response.json();
                } catch (_) {
                    data = null;
                }

                if (!response.ok || !data || !data.success) {
                    const errorMessage = getResponseError(response, data);
                    typingBubble.textContent = errorMessage;
                    typingBubble.classList.remove("chat-typing");
                    setError(errorMessage);
                    return;
                }

                typingBubble.textContent = data.reply || "未获取到回答，请稍后再试。";
                typingBubble.classList.remove("chat-typing");
            } catch (_) {
                const errorMessage = "请求没有发出去，请检查网络或刷新页面后再试。";
                typingBubble.textContent = errorMessage;
                typingBubble.classList.remove("chat-typing");
                setError(errorMessage);
            } finally {
                setLoading(false);
                input.focus();
            }
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();
            if (sendBtn.disabled) {
                return;
            }

            const userText = input.value.trim();
            if (!userText) {
                setError("请输入消息后再发送。");
                input.focus();
                return;
            }
            sendMessage(userText);
        });

        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                form.requestSubmit();
            }
        });

        input.addEventListener("input", function () {
            if (input.value.trim() && errorEl.textContent === "请输入消息后再发送。") {
                clearError();
            }
        });
    }

    document.addEventListener("DOMContentLoaded", setupAgentChat);
})();
