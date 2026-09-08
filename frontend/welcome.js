const signupButton = document.querySelector(".signup-btn");
const loginButton = document.querySelector(".login-btn");

if(locationStorage.getItem("token")){
    window.location.href="chat.html";
}

signupButton.addEventListener("click", () => {
    window.location.href = "signup.html";
});

loginButton.addEventListener("click", () => {
    window.location.href = "login.html";
});

