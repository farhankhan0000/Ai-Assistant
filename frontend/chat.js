const new_chat_btn = document.querySelector(".new-chat");
const conversation_btn = document.querySelectorAll(".conversation");
const profile_btn = document.querySelector(".profile");
const add_btn = document.querySelector(".add-button");
const user_input = document.querySelector(".user-input");
const send_btn = document.querySelector(".send-button");
const user_msg = document.querySelector(".user-message");
const ai_msg = document.querySelector(".ai-reply");
const currentConversation_Id = null;
CHAT_URL = "http://127.0.0.1:8000/chat";
CONVERSATION_URL = "http://127.0.0.1:8000/conversation";



send_btn.addEventListener("click", async () => {
    const chat_request = {
        content: user_input.value,
        conversation_id: 1
    };
    user_msg.innerText = user_input.value;
    const token = document.cookie.split("; ")
        .find(row => row.startsWith("access_token="))?.split("=")[1];
    const response = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : `Bearer ${token}`
        },
        body: JSON.stringify(chat_request)
    });
    const ai_reply = await response.json();
    ai_msg.innerText = ai_reply.ai_reply;
    console.log(ai_reply);
});

new_chat_btn.addEventListener("click", async() => {
    const token = document.
    cookie.split("; ").find(row => row.startsWith("access_token="))?.split("=")[1];
})