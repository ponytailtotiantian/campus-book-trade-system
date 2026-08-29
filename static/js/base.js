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
                    typingBubble.textContent = "未获取到回答，请稍后再试。";
                    setError(data && data.error ? data.error : "网络请求失败，请稍后再试。");
                    return;
                }

                typingBubble.textContent = data.reply || "未获取到回答，请稍后再试。";
                typingBubble.classList.remove("chat-typing");
            } catch (_) {
                typingBubble.textContent = "未获取到回答，请稍后再试。";
                setError("网络请求失败，请稍后再试。");
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
