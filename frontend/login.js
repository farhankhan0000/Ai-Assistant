const email_input = document.querySelector(".email-input");
const password_input = document.querySelector(".password-input");
const login_btn = document.querySelector(".login-button");
const LOGIN_URL = "http://127.0.0.1:8000/auth/login";






login_btn.addEventListener("click", async() => {
    const form_data = new URLSearchParams();
    form_data.append("username", email_input.value);
    form_data.append("password", password_input.value);
    const response =  await fetch(LOGIN_URL, {
    method: "post",
    body: form_data
});
    if(response.ok){
        window.location.href="chat.html";
    }
    const data = await response.json();
    console.log(data);
});


