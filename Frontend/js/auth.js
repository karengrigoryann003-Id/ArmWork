/* ============================================================================
   ArmWork Auth Script
   Կապում է գրանցման և մուտքի form-երը Python backend API-ների հետ։
   ============================================================================ */

function getArmWorkApiBaseUrl() {
    const configuredUrl = window.ARMWORK_API_BASE_URL || window.ARMWORK_CONFIG?.API_BASE_URL;
    if (configuredUrl) return configuredUrl.replace(/\/$/, "");

    if (window.location.protocol === "file:") {
        return "http://127.0.0.1:5050/api";
    }

    return `${window.location.origin}/api`;
}

const API_BASE_URL = getArmWorkApiBaseUrl();
const CURRENT_USER_KEY = "armwork_current_user";

function getValue(id) {
    const element = document.getElementById(id);
    return element ? element.value.trim() : "";
}

function showFormMessage(elementId, text, type) {
    const messageElement = document.getElementById(elementId);
    if (!messageElement) return;

    messageElement.textContent = text;
    messageElement.classList.remove("is-error", "is-success");

    if (type) {
        messageElement.classList.add(`is-${type}`);
    }
}

async function requestApi(path, options) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "Սերվերի հետ կապի խնդիր կա։");
    }

    return data;
}

function saveUserAndRedirect(user) {
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));

    if (user.role === "client") {
        window.location.href = "dashboard-client.html";
        return;
    }

    window.location.href = "dashboard-freelancer.html";
}

function connectLoginForm(formId, messageId, role) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        showFormMessage(messageId, "Մուտք ենք գործում...", "success");

        try {
            const data = await requestApi("/auth/login", {
                method: "POST",
                body: JSON.stringify({
                    role,
                    email: getValue(role === "client" ? "client-email" : "email"),
                    password: getValue(role === "client" ? "client-password" : "password"),
                }),
            });

            saveUserAndRedirect(data.user);
        } catch (error) {
            showFormMessage(messageId, error.message, "error");
        }
    });
}

function connectFreelancerRegisterForm() {
    const form = document.getElementById("registerFreelancerForm");
    if (!form) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        showFormMessage("registerFreelancerMessage", "Ստեղծում ենք հաշիվը...", "success");

        try {
            const data = await requestApi("/auth/register", {
                method: "POST",
                body: JSON.stringify({
                    role: "freelancer",
                    full_name: getValue("fullname"),
                    email: getValue("email"),
                    username: getValue("username"),
                    specialty: getValue("specialty"),
                    password: getValue("password"),
                }),
            });

            saveUserAndRedirect(data.user);
        } catch (error) {
            showFormMessage("registerFreelancerMessage", error.message, "error");
        }
    });
}

function connectClientRegisterForm() {
    const form = document.getElementById("registerClientForm");
    if (!form) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        showFormMessage("registerClientMessage", "Ստեղծում ենք հաշիվը...", "success");

        try {
            const companyName = getValue("company-name");

            const data = await requestApi("/auth/register", {
                method: "POST",
                body: JSON.stringify({
                    role: "client",
                    full_name: companyName,
                    company_name: companyName,
                    email: getValue("company-email"),
                    username: getValue("client-username"),
                    password: getValue("company-password"),
                }),
            });

            saveUserAndRedirect(data.user);
        } catch (error) {
            showFormMessage("registerClientMessage", error.message, "error");
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    connectLoginForm("loginFreelancerForm", "loginFreelancerMessage", "freelancer");
    connectLoginForm("loginClientForm", "loginClientMessage", "client");
    connectFreelancerRegisterForm();
    connectClientRegisterForm();
});
