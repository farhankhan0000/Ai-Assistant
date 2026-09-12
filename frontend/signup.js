const email = document.querySelector(".email-input");
const name = document.querySelector(".name-input");
const password = document.querySelector(".password-input")
const signup_button = document.querySelector(".signup-btn")
const SIGN_UP_URL = "http://localhost:8000/auth/register";


signup_button.addEventListener("click", async () => {

    const request_body = {
        email: email.value,
        name: name.value,
        password: password.value
    }

    try {
        const response = await fetch(SIGN_UP_URL, {
        method: "POST",
        headers: {
            "Content-Type" : "application/json"
        },
        credentials: "include",

        body: JSON.stringify(request_body)
        });

        if(response.ok){
            localStorage.setItem("username", request_body.name)
            window.location.href = "login.html";
        }else{
            const errorData = await response.json();
            alert(errorData.detail || "Signup Failed");
        }

    } catch (error){
        console.error("Error during Signup:", error)
    }


});