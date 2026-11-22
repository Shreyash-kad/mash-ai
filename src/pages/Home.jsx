import { useEffect, useRef, useState } from "react";

import Sidebar from "../components/Sidebar/Sidebar";
import ChatBox from "../components/Chat/ChatBox";
import Header from "../components/Header/Header";

import {
    createChat,
    getChats,
} from "../services/api";


function Home() {

    const [chats, setChats] = useState([]);
    const [activeChatId, setActiveChatId] = useState(null);

    const [loading, setLoading] = useState(true);
    const [documentRefreshVersion, setDocumentRefreshVersion] = useState(0);

    const chatActionRef = useRef(0);
    const creatingChatRef = useRef(false);


    // ==================================================
    // LOAD CHATS
    // ==================================================

    useEffect(() => {

        loadChats();

    }, []);


    const loadChats = async () => {

        try {

            const response = await getChats();

            setChats(response.chats || []);

        } catch (error) {

            console.error(
                "Failed to load chats:",
                error
            );

        } finally {

            setLoading(false);

        }

    };


    // ==================================================
    // NEW CHAT
    // ==================================================

    const handleNewChat = async () => {
        if (creatingChatRef.current) return;

        creatingChatRef.current = true;
        const actionId = ++chatActionRef.current;

        try {
            const response = await createChat();
            const newChatId = response.chat?.id;

            if (!newChatId) {
                throw new Error("The server did not return a chat ID.");
            }

            if (chatActionRef.current === actionId) {
                setActiveChatId(newChatId);
            }

            await loadChats();
        } catch (error) {
            console.error("Failed to create chat:", error);

            if (chatActionRef.current === actionId) {
                alert("Failed to create a new chat. Please try again.");
            }
        } finally {
            creatingChatRef.current = false;
        }

    };


    // ==================================================
    // SELECT OLD CHAT
    // ==================================================

    const handleSelectChat = (chatId) => {
        chatActionRef.current += 1;
        setActiveChatId(chatId);

    };


    // ==================================================
    // CHAT UPDATED
    // ==================================================

    const handleChatUpdated = async () => {

        await loadChats();

    };

    const handleDocumentUploaded = () => {
        setDocumentRefreshVersion((version) => version + 1);
    };


    // ==================================================
    // UI
    // ==================================================

    return (

        <div className="app-layout flex h-screen flex-col">

            <Header />

            <div className="app-body flex min-h-0 flex-1">

                <Sidebar
                    chats={chats}
                    activeChatId={activeChatId}
                    onNewChat={handleNewChat}
                    onSelectChat={handleSelectChat}
                    onChatUpdated={handleChatUpdated}
                    onDocumentUploaded={handleDocumentUploaded}
                    loading={loading}
                />


                <main className="chat-shell flex min-w-0 flex-1">

                    <ChatBox
                        chatId={activeChatId}
                        onChatUpdated={handleChatUpdated}
                        onDocumentUploaded={handleDocumentUploaded}
                        documentRefreshVersion={documentRefreshVersion}
                    />

                </main>

            </div>
        </div>

    );

}


export default Home;