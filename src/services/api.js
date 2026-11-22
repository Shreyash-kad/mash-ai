import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000",
});


// Create new chat
export const createChat = async (title = "New Chat") => {
    const response = await API.post("/chats", {
        title,
    });

    return response.data;
};


// Get all chats
export const getChats = async () => {
    const response = await API.get("/chats");

    return response.data;
};


// Get messages of a chat
export const getChatMessages = async (chatId) => {
    const response = await API.get(
        `/chats/${chatId}/messages`
    );

    return response.data;
};

// Get documents of a chat
export const getChatDocuments = async (chatId) => {
    const response = await API.get(
        `/documents?chat_id=${chatId}`
    );

    return response.data;
};


// Send message
export const sendMessage = async (message, chatId = null) => {
    const response = await API.post("/chat", {
        message,
        chat_id: chatId,
    });

    return response.data;
};


// Pin / unpin chat
export const togglePinChat = async (chatId) => {
    const response = await API.patch(
        `/chats/${chatId}/pin`
    );

    return response.data;
};


// Delete chat
export const deleteChat = async (chatId) => {
    const response = await API.delete(
        `/chats/${chatId}`
    );

    return response.data;
};


export const uploadFile = async (file, chatId) => {
    const formData = new FormData();

    formData.append("file", file);

    const response = await API.post(
        `/upload?chat_id=${chatId}`,
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};