const new_chat_btn = document.querySelector(".new-chat");
const conversation_btn = document.querySelectorAll(".conversation");
const profile_btn = document.querySelector(".profile");
const add_btn = document.querySelector(".add-button");
const user_input = document.querySelector(".user-input");
const send_btn = document.querySelector(".send-button");
const user_msg = document.querySelector(".user-message");
const ai_msg = document.querySelector(".ai-reply");
const msg_container = document.querySelector(".message-container");
const conversations_container = document.querySelector(".conversations");
let currentConversation_Id = null;
CHAT_URL = "http://127.0.0.1:8000/chat";
POST_CONVERSATION_URL = "http://127.0.0.1:8000/conversation";
GET_CONVERSATION_URL = "http://127.0.0.1:8000/conversation";
CHANGE_TITLE_URL = "http://127.0.0.1:8000/conversation";
CONVERSATION_DELETE_URL = "http://127.0.0.1:8000/conversation";



const create_message_bubble = (role, text) => {
    const newDiv = document.createElement("div");
    if(role === "user"){
        newDiv.classList.add("user-message");

    }
    else if(role === "assistant"){
        newDiv.classList.add("ai-reply");
    }
    newDiv.innerText = text;
    msg_container.appendChild(newDiv);
    setTimeout(() => {
        msg_container.scrollTo({
            top: msg_container.scrollHeight,
            behavior: "smooth"
    });
    }, 10);
}

const create_conversation_button = (title, id) => {

    const newButton = document.createElement("button");
    newButton.classList.add("conversation");
    newButton.innerText = title;
    newButton.dataset.id = id;

    const optionsButton = document.createElement("button");
    optionsButton.classList.add("options-button");
    optionsButton.innerText = "⋮";


    const newDiv = document.createElement("div");
    newDiv.classList.add("conversation_wrapper");
    newDiv.appendChild(newButton);
    newDiv.appendChild(newDeleteButton);


    newButton.addEventListener("click", async (e) => {
        const token = document.cookie.split("; ").find(row => row.startsWith("access_token="))
        ?.split("=")[1];
        const clickedId = e.target.dataset.id;
        currentConversation_Id = clickedId;
        const get_chat_url = `http://127.0.0.1:8000/chat/${currentConversation_Id}`;
        const response = await fetch(get_chat_url, {
            method: "GET",
            headers: {
                "Authorization" : `Bearer ${token}`
            }
        });
        let messages = await response.json();
        msg_container.innerHTML = "";
        messages.forEach(msg => {
            create_message_bubble(msg.role, msg.content);
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
    msg_container.innerHTML = "";
    console.log(newConversation);
});



send_btn.addEventListener("click", async () => {
    const userText = user_input.value;
    create_message_bubble("user", userText);
    user_input.value = "";
    const token = document.cookie.split("; ")
        .find(row => row.startsWith("access_token="))?.split("=")[1];

    if(!currentConversation_Id){
        const convResponse = await fetch(POST_CONVERSATION_URL, {
            method: "POST",
            headers:{
                "Content-Type" : "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({title: "New Chat"})
        });
        const newConvo = await convResponse.json();

        currentConversation_Id = newConvo.id;

        create_conversation_button("New Chat", currentConversation_Id);
    }
    const chat_request = {
        content: userText,
        conversation_id: currentConversation_Id
    };
    const response = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : `Bearer ${token}`
        },
        body: JSON.stringify(chat_request)
    });
    const ai_reply = await response.json();
    create_message_bubble("assistant", ai_reply.ai_reply);

    const active_button = document.querySelector(`.conversation[data-id="${currentConversation_Id}"]`);
    if (active_button.innerText === "New Chat"){
        const title_change_request = {
        content: userText,
        conversation_id: currentConversation_Id
    }
    const title_change_response = await fetch(CHANGE_TITLE_URL, {
        method: "PUT",
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : `Bearer ${token}`
        },
        body: JSON.stringify(title_change_request)
    });

        const title_data = await title_change_response.json()
        active_button.innerText = title_data.new_title;
    console.log(ai_reply);
    }

});

user_input.addEventListener("keydown",  (e) => {
    if(e.key === "Enter"){
        e.preventDefault();

        if(user_input.value.trim() !== ""){
            send_btn.click();
        }
    }
});


load_saved_conversation();