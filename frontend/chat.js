const new_chat_btn = document.querySelector(".new-chat");
const conversation_btn = document.querySelectorAll(".conversation");
const profile_btn = document.querySelector(".profile");
const add_btn = document.querySelector(".add-button");
const user_input = document.querySelector(".user-input");
const send_btn = document.querySelector(".send-button");
const user_msg = document.querySelector(".user-message");
const ai_msg = document.querySelector(".ai-reply");

send_btn.addEventListener("click", () => {
    user_msg.innerText = user_input.value;
});