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
POST_CONVERSATION_URL = "http://127.0.0.1:8000/conversation";
GET_CONVERSATION_URL = "http://127.0.0.1:8000/conversation";




const create_conversation_button = (title, id) => {
    const newButton = document.createElement("button");
    newButton.classList.add("conversation");
    newButton.innerText = title;
    newButton.dataset.id = id;
    newButton.addEventListener("click", async (e) => {
        const token = document.cookie.split("; ").find(row => row.startsWith("access_token="))
        ?.split("=")[1];
        const clickedId = e.target.dataset.id;
        currentConversation_Id = clickedId;
        get_chat_url = `http://127.0.0.1:8000/chat/${currentConversation_Id}`;
        const response = await fetch(get_chat_url, {
            method: "GET",
            headers: {
                "AUTHORIZATION" : `Bearer ${token}`
            }
        });
        messages = await response.json()
        messages.forEach(msg => {
            if(msg.role === "user"){
                user_msg.innerText = msg.content;
            }
            else if(msg.role === "assistant"){
                ai_msg.innerText = msg.content;
            }
        })
        console.log(messages)
        console.log(`Switched to conversations: ${currentConversation_Id}`);
    });
    conversations_container.appendChild(newButton);
}

const load_saved_conversation = async ()  => {
    const token = document.cookie.split("; ").find(row => row.startsWith("access_token="))
    ?.split("=")[1];
    const response = await fetch(GET_CONVERSATION_URL, {
        method: "GET",
        headers: {
            "Authorization" : `Bearer ${token}`
        }
    });
    let conversations = await response.json();
    conversations.forEach(chat => {
        create_conversation_button(chat.title, chat.id);
    });
}

load_saved_conversation();

new_chat_btn.addEventListener("click", async() => {
    const token = document.
    cookie.split("; ").find(row => row.startsWith("access_token="))?.split("=")[1];
    const response = await fetch(POST_CONVERSATION_URL, {
        method: "POST",
        headers: {
            "content-Type" : "application/json",
            "Authorization" : `Bearer ${token}`
        },
        body: JSON.stringify({title: "New Chat"})
    });
    const newConversation = await response.json();
    currentConversation_Id = newConversation.id;
    create_conversation_button(newConversation.title, currentConversation_Id);
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
