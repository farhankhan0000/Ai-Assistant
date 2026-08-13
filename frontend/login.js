const email_input = document.querySelector(".email-input");
const password_input = document.querySelector(".password-input");
const login_btn = document.querySelector(".login-button");
const form_data = new FormData();
const LOGIN_URL = "http://127.0.0.1:8000/auth/login";


form_data.append("username", email_input.value);
form_data.append("password", email_input.value);

fetch(LOGIN_URL, {
    method: "post",
    body: form_data
});
