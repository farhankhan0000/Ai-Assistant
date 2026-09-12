const new_chat_btn = document.querySelector(".new-chat");
const user_input = document.querySelector(".user-input");
const send_btn = document.querySelector(".send-button");
const msg_container = document.querySelector(".message-container");
const conversations_container = document.querySelector(".conversations");
let currentConversation_Id = null;
const API_BASE_URL = "http://127.0.0.1:8000";


const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return {};
    }
    return {
        "Content-Type" : "application/json",
        "Authorization" : `Bearer ${token}`
    };
};



const create_message_bubble = (role, text) => {
    const newDiv = document.createElement("div");
    if(role === "user"){
        newDiv.classList.add("user-message");

    }
    else if(role === "assistant"){
        newDiv.classList.add("ai-reply");
    }
    newDiv.innerHTML = marked.parse(text);
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


    const deleteButton = document.createElement("button");
    deleteButton.classList.add("delete-button");
    deleteButton.innerText = "Delete";

    const dropDownContainer = document.createElement("div");
    dropDownContainer.classList.add("drop-down");
    dropDownContainer.appendChild(deleteButton);



    const newDiv = document.createElement("div");
    newDiv.classList.add("conversation-wrapper");
    newDiv.appendChild(newButton);
    newDiv.appendChild(optionsButton);

    document.body.appendChild(dropDownContainer);


    newButton.addEventListener("click", async (e) => {
        const clickedId = e.target.dataset.id;
        currentConversation_Id = clickedId;
        const response = await fetch(`${API_BASE_URL}/chat/${currentConversation_Id}`, {
            method: "GET",
            headers: getAuthHeaders()
        });
        if(response.ok){
            const messages = await response.json();
            msg_container.innerHTML = "";
            messages.forEach(msg => {
                create_message_bubble(msg.role, msg.content);
            })
        }
    });

    optionsButton.addEventListener("click", (e) => {
        e.stopPropagation();

        const rect = optionsButton.getBoundingClientRect();

        dropDownContainer.style.position = "fixed";
        dropDownContainer.style.top = `${rect.top}px`;
        dropDownContainer.style.left = `${rect.right + 15}px`;

        const allOpenMenus = document.querySelectorAll(".drop-down.show");

        allOpenMenus.forEach(menu => {
            if(menu !== dropDownContainer){
                menu.classList.remove("show");
            }
        });

        dropDownContainer.classList.toggle("show");

    });

    deleteButton.addEventListener("click", async  (e) => {
        e.stopPropagation();
        const delete_url = `${API_BASE_URL}/conversation/${id}`;
        const response = await fetch(delete_url, {
            method: "DELETE",
            headers : getAuthHeaders()
        });
        if(response.ok){
            newDiv.remove()
            dropDownContainer.remove()

            if(currentConversation_Id == id){
                msg_container.innerHTML = "";
                currentConversation_Id = null;
        }
        }
        else{
            console.log("Failed to delete the conversation on backend");
        }
    });
    conversations_container.appendChild(newDiv);
}

const load_saved_conversation = async ()  => {
    const response = await fetch(`${API_BASE_URL}/conversation`, {
        method: "GET",
        headers: getAuthHeaders()
    });
    if(response.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "login.html";
        return;
    }
    if(response.ok){
        const conversations = await response.json();
        conversations.forEach(chat => {
        create_conversation_button(chat.title, chat.id);
        });

    }
}


new_chat_btn.addEventListener("click", async() => {
    const response = await fetch(`${API_BASE_URL}/conversation`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({title: "New Chat"})
    });
    if(response.ok){
        const newConversation = await response.json();
        currentConversation_Id = newConversation.id;
        create_conversation_button(newConversation.title, currentConversation_Id);
        msg_container.innerHTML = "";
    }
});



send_btn.addEventListener("click", async () => {
    const userText = user_input.value.trim();
    if(!userText){
        return;
    }
    create_message_bubble("user", userText);
    user_input.value = "";

    if(!currentConversation_Id){
        const convResponse = await fetch(`${API_BASE_URL}/conversation`, {
            method: "POST",
            headers:getAuthHeaders(),
            body: JSON.stringify({title: "New Chat"})
        });
        if(!convResponse.ok) return;
        const newConvo = await convResponse.json();
        currentConversation_Id = newConvo.id;
        create_conversation_button("New Chat", currentConversation_Id);
    }
    const chat_request = {
        content: userText,
        conversation_id: currentConversation_Id
    };
    send_btn.disabled = true;
    send_btn.innerText = "Wait.."
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(chat_request)
    });
    send_btn.disabled = false;
    send_btn.innerText = "↑";
    if(response.ok){
        const ai_reply = await response.json();
        create_message_bubble("assistant", ai_reply.ai_reply);
        const active_button = document.querySelector(`.conversation[data-id="${currentConversation_Id}"]`);
    if (active_button && active_button.innerText === "New Chat"){
        const title_change_request = {
        content: userText,
        conversation_id: currentConversation_Id
    }
    const title_change_response = await fetch(`${API_BASE_URL}/conversation`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(title_change_request)
    });
    if(title_change_response.ok){
        const title_data = await title_change_response.json()
        active_button.innerText = title_data.new_title;
    }
    }
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


document.addEventListener("click", () => {
    document.querySelectorAll(".drop-down.show").forEach(menu => {
        menu.classList.remove("show");
    });
});

load_saved_conversation();