const email_input = document.querySelector(".email-input");
const password_input = document.querySelector(".password-input");
const login_btn = document.querySelector(".login-button");
const API_BASE_URL = "http://127.0.0.1:8000";







login_btn.addEventListener("click", async() => {
    const form_data = new URLSearchParams();
    form_data.append("username", email_input.value);
    form_data.append("password", password_input.value);
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "post",
            body: form_data
        });
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("token", data.access_token);
            window.location.href = "chat.html";
        } else {
            const data = await response.json();
            alert(data.detail || "Login Failed")
        }
    } catch (error) {
        console.error("Login request Failed:", error)
    }
    });


