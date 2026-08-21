const new_chat_btn = document.querySelector(".new-chat");
const conversation_btn = document.querySelectorAll(".conversation");
const profile_btn = document.querySelector(".profile");
const add_btn = document.querySelector(".add-button");
const user_input = document.querySelector(".user-input");
const send_btn = document.querySelector(".send-button");
const user_msg = document.querySelector(".user-message");
const ai_msg = document.querySelector(".ai-reply");
const conversations_container = document.querySelector(".conversations");
let currentConversation_Id = null;
CHAT_URL = "http://127.0.0.1:8000/chat";
CONVERSATION_URL = "http://127.0.0.1:8000/conversation";


const create_conversation_button = (title, id) => {
    const newButton = document.createElement("button");
    newButton.classList.add("conversation");
    newButton.innerText = title;
    newButton.dataset.id = id;
    conversations_container.appendChild(newButton);
}

new_chat_btn.addEventListener("click", async() => {
    const token = document.
    cookie.split("; ").find(row => row.startsWith("access_token="))?.split("=")[1];
    const response = await fetch(CONVERSATION_URL, {
        method: "POST",
        headers: {
            "content-Type" : "application/json",
            "Authorization" : `Bearer ${token}`
        },
        body: JSON.stringify({title: "New Chat"})
    });
    const newConversation = await response.json();
    currentConversation_Id = newConversation.conversation_id;
    create_conversation_button(newConversation.conversation_title, currentConversation_Id);
    console.log(newConversation);
});



send_btn.addEventListener("click", async () => {
    const chat_request = {
        content: user_input.value,
        conversation_id: currentConversation_Id
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
