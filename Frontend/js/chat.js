/* ============================================================================
   ArmWork Chat Script
   Կառավարում է Messages/iMessage ոճով chat պատուհանը և backend API կապը։
   ============================================================================ */

function getArmWorkChatApiBaseUrl() {
    const configuredUrl = window.ARMWORK_API_BASE_URL || window.ARMWORK_CONFIG?.API_BASE_URL;
    if (configuredUrl) return configuredUrl.replace(/\/$/, "");

    if (window.location.protocol === "file:") {
        return "http://127.0.0.1:5050/api";
    }

    return `${window.location.origin}/api`;
}

const CHAT_API_BASE_URL = getArmWorkChatApiBaseUrl();
const CHAT_CURRENT_USER_KEY = "armwork_current_user";

function getCurrentUser() {
    try {
        return JSON.parse(localStorage.getItem(CHAT_CURRENT_USER_KEY));
    } catch (error) {
        return null;
    }
}

function initialsFromName(name) {
    const words = String(name || "AW").trim().split(/\s+/).filter(Boolean);
    return words.slice(0, 2).map((word) => word[0]).join("").toUpperCase() || "AW";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatChatTime(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";

    const today = new Date();
    const isToday = date.toDateString() === today.toDateString();

    if (isToday) {
        return date.toLocaleTimeString("hy-AM", { hour: "2-digit", minute: "2-digit" });
    }

    return "Yesterday";
}

async function chatRequest(path, options) {
    const response = await fetch(`${CHAT_API_BASE_URL}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "Սերվերի հետ կապի խնդիր կա։");
    }

    return data;
}

document.addEventListener("DOMContentLoaded", function () {
    const currentUser = getCurrentUser();
    const chatBtn = document.querySelector(".chat-icon-btn");
    const chatOverlay = document.getElementById("chatOverlay");
    const chatModal = document.getElementById("chatModal");
    const closeChatBtn = document.getElementById("closeChatBtn");
    const messagesMenuBtn = document.getElementById("messagesMenuBtn");
    const messagesList = document.getElementById("messagesList");
    const messagesSearchResults = document.getElementById("messagesSearchResults");
    const usernameSearch = document.getElementById("chatUsernameSearch");
    const startChatBtn = document.getElementById("startChatBtn");
    const messagesListView = document.getElementById("messagesListView");
    const messageThreadView = document.getElementById("messageThreadView");
    const threadBackBtn = document.getElementById("threadBackBtn");
    const threadAvatar = document.getElementById("threadAvatar");
    const threadName = document.getElementById("threadName");
    const threadUsername = document.getElementById("threadUsername");
    const threadMessages = document.getElementById("threadMessages");
    const messageForm = document.getElementById("messageForm");
    const messageInput = document.getElementById("messageInput");

    if (!chatBtn || !chatOverlay || !chatModal || !messagesList) return;

    let activeChat = null;
    let searchTimer = null;

    // Dashboard-ի անունը ցույց ենք տալիս login/register-ից եկած user-ով։
    if (currentUser?.full_name) {
        document.querySelectorAll(".user-profile-badge").forEach((badge) => {
            badge.textContent = currentUser.full_name;
        });
    }

    function setModalOriginFromButton() {
        const buttonRect = chatBtn.getBoundingClientRect();
        const buttonCenterX = buttonRect.left + buttonRect.width / 2;
        const buttonCenterY = buttonRect.top + buttonRect.height / 2;

        // Քանի որ modal-ը կենտրոնում է, հաշվում ենք վերջնական դիրքը և origin-ը դնում ենք կոճակի կետին։
        const modalWidth = chatModal.offsetWidth;
        const modalHeight = chatModal.offsetHeight;
        const modalLeft = (window.innerWidth - modalWidth) / 2;
        const modalTop = (window.innerHeight - modalHeight) / 2;

        chatModal.style.setProperty("--chat-origin-x", `${buttonCenterX - modalLeft}px`);
        chatModal.style.setProperty("--chat-origin-y", `${buttonCenterY - modalTop}px`);
    }

    function openChat() {
        setModalOriginFromButton();
        chatOverlay.classList.add("active");
        chatOverlay.setAttribute("aria-hidden", "false");
        showListView();
        loadChats();
    }

    function closeChat() {
        chatOverlay.classList.remove("active");
        chatOverlay.setAttribute("aria-hidden", "true");
    }

    function showListView() {
        messagesListView.classList.remove("is-hidden");
        messageThreadView.classList.add("is-hidden");
        activeChat = null;
    }

    function showThreadView(chat) {
        activeChat = chat;
        messagesListView.classList.add("is-hidden");
        messageThreadView.classList.remove("is-hidden");
        threadAvatar.textContent = initialsFromName(chat.other_full_name || chat.other_username);
        threadName.textContent = chat.other_full_name || chat.other_username;
        threadUsername.textContent = `@${chat.other_username}`;
        loadMessages(chat.conversation_id);
    }

    function renderEmptyState(text) {
        messagesList.innerHTML = `
            <div class="messages-empty-state">
                <h3>Չաթեր դեռ չկան</h3>
                <p>${escapeHtml(text)}</p>
            </div>
        `;
    }

    function renderChats(chats) {
        if (!currentUser) {
            renderEmptyState("Մուտք գործիր կամ գրանցվիր, որպեսզի կարողանաս ուղարկել հաղորդագրություններ։");
            return;
        }

        if (!chats.length) {
            renderEmptyState("Սկսիր նոր չաթ՝ ներքևի որոնման դաշտում գրելով օգտատիրոջ username-ը։");
            return;
        }

        messagesList.innerHTML = chats.map((chat) => `
            <button type="button" class="messages-row" data-chat-id="${chat.conversation_id}">
                <div class="messages-avatar">${initialsFromName(chat.other_full_name || chat.other_username)}</div>
                <div class="messages-row-content">
                    <div class="messages-row-title">${escapeHtml(chat.other_full_name || chat.other_username)}</div>
                    <div class="messages-row-preview">${escapeHtml(chat.last_message || `@${chat.other_username}`)}</div>
                </div>
                <div class="messages-row-meta">${formatChatTime(chat.last_message_at)}</div>
            </button>
        `).join("");

        messagesList.querySelectorAll(".messages-row").forEach((row) => {
            row.addEventListener("click", function () {
                const chat = chats.find((item) => String(item.conversation_id) === row.dataset.chatId);
                if (chat) showThreadView(chat);
            });
        });
    }

    async function loadChats() {
        if (!currentUser?.user_id) {
            renderChats([]);
            return;
        }

        try {
            const data = await chatRequest(`/chats?user_id=${currentUser.user_id}`);
            renderChats(data.chats || []);
        } catch (error) {
            renderEmptyState(error.message);
        }
    }

    function renderSearchResults(users) {
        if (!users.length) {
            messagesSearchResults.innerHTML = `
                <div class="messages-result-empty">
                    <p>Այդ username-ով օգտատեր չգտնվեց։</p>
                </div>
            `;
            messagesSearchResults.classList.add("is-visible");
            return;
        }

        messagesSearchResults.innerHTML = users.map((user) => `
            <button type="button" class="messages-result-btn" data-user-id="${user.user_id}" data-username="${user.username}">
                <div class="messages-avatar">${initialsFromName(user.full_name || user.username)}</div>
                <div>
                    <div class="messages-result-name">${escapeHtml(user.full_name || user.username)}</div>
                    <div class="messages-result-username">@${escapeHtml(user.username)} · ${escapeHtml(user.role)}</div>
                </div>
            </button>
        `).join("");

        messagesSearchResults.classList.add("is-visible");

        messagesSearchResults.querySelectorAll(".messages-result-btn").forEach((button) => {
            button.addEventListener("click", function () {
                startChatWithUsername(button.dataset.username);
            });
        });
    }

    async function searchUsers() {
        const query = usernameSearch.value.trim();
        if (!query || query.length < 2 || !currentUser?.user_id) {
            messagesSearchResults.classList.remove("is-visible");
            messagesSearchResults.innerHTML = "";
            return;
        }

        try {
            const data = await chatRequest(`/users/search?username=${encodeURIComponent(query)}&current_user_id=${currentUser.user_id}`);
            renderSearchResults(data.users || []);
        } catch (error) {
            messagesSearchResults.classList.remove("is-visible");
        }
    }

    async function startChatWithUsername(username) {
        const cleanUsername = String(username || usernameSearch.value || "").trim();
        if (!cleanUsername || !currentUser?.user_id) return;

        try {
            const data = await chatRequest("/chats/start", {
                method: "POST",
                body: JSON.stringify({
                    current_user_id: currentUser.user_id,
                    username: cleanUsername,
                }),
            });

            usernameSearch.value = "";
            messagesSearchResults.classList.remove("is-visible");
            messagesSearchResults.innerHTML = "";
            showThreadView(data.chat);
        } catch (error) {
            renderSearchResults([]);
        }
    }

    async function loadMessages(conversationId) {
        threadMessages.innerHTML = `<div class="thread-empty">Բեռնում ենք հաղորդագրությունները...</div>`;

        try {
            const data = await chatRequest(`/chats/${conversationId}/messages?user_id=${currentUser.user_id}`);
            const messages = data.messages || [];

            if (!messages.length) {
                threadMessages.innerHTML = `<div class="thread-empty">Գրիր առաջին հաղորդագրությունը։</div>`;
                return;
            }

            threadMessages.innerHTML = `
                <div class="message-day-label">Այսօր</div>
                ${messages.map((message) => `
                    <div class="chat-bubble ${message.sender_id === currentUser.user_id ? "bubble-sent" : "bubble-received"}">
                        ${escapeHtml(message.body)}
                    </div>
                `).join("")}
            `;
            threadMessages.scrollTop = threadMessages.scrollHeight;
        } catch (error) {
            threadMessages.innerHTML = `<div class="thread-empty">${escapeHtml(error.message)}</div>`;
        }
    }

    async function sendMessage(event) {
        event.preventDefault();
        const body = messageInput.value.trim();

        if (!body || !activeChat || !currentUser?.user_id) return;

        messageInput.value = "";

        try {
            await chatRequest(`/chats/${activeChat.conversation_id}/messages`, {
                method: "POST",
                body: JSON.stringify({
                    sender_id: currentUser.user_id,
                    body,
                }),
            });
            loadMessages(activeChat.conversation_id);
        } catch (error) {
            threadMessages.insertAdjacentHTML("beforeend", `<div class="thread-empty">${escapeHtml(error.message)}</div>`);
        }
    }

    chatBtn.addEventListener("click", openChat);
    closeChatBtn.addEventListener("click", closeChat);
    messagesMenuBtn.addEventListener("click", closeChat);
    chatOverlay.addEventListener("click", function (event) {
        if (event.target === chatOverlay) closeChat();
    });

    threadBackBtn.addEventListener("click", function () {
        showListView();
        loadChats();
    });

    usernameSearch.addEventListener("input", function () {
        window.clearTimeout(searchTimer);
        searchTimer = window.setTimeout(searchUsers, 260);
    });

    usernameSearch.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            startChatWithUsername();
        }
    });

    startChatBtn.addEventListener("click", function () {
        if (usernameSearch.value.trim()) {
            startChatWithUsername();
            return;
        }
        usernameSearch.focus();
    });

    messageForm.addEventListener("submit", sendMessage);
});
