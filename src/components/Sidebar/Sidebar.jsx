import {
    FiPlus,
    FiClock,
    FiTrash2,
    FiBookmark,
} from "react-icons/fi";

import FileUpload from "./FileUpload";

import {
    deleteChat,
    togglePinChat,
} from "../../services/api";


function Sidebar({
    chats,
    activeChatId,
    onNewChat,
    onSelectChat,
    onChatUpdated,
    onDocumentUploaded,
    loading,
}) {


    // ================================================
    // DELETE CHAT
    // ================================================

    const handleDelete = async (event, chatId) => {

        event.stopPropagation();

        try {

            await deleteChat(chatId);

            await onChatUpdated();

        } catch (error) {

            console.error(
                "Failed to delete chat:",
                error
            );

        }
    };


    // ================================================
    // PIN / UNPIN CHAT
    // ================================================

    const handlePin = async (event, chatId) => {

        event.stopPropagation();

        try {

            await togglePinChat(chatId);

            await onChatUpdated();

        } catch (error) {

            console.error(
                "Failed to pin chat:",
                error
            );

        }
    };


    return (

        <aside className="sidebar-shell w-80 border-r">

            <div className="flex h-full flex-col p-4">


                {/* ======================================
                    NEW CHAT
                ====================================== */}

                <button
                    onClick={onNewChat}
                    className="new-chat-button mb-4 flex w-full items-center justify-center gap-2 rounded-2xl py-3 font-semibold transition"
                >

                    <FiPlus size={20} />

                    New Chat

                </button>


                {/* ======================================
                    UPLOAD DOCUMENT
                ====================================== */}

                <div className="mb-6">

                    <FileUpload
                        chatId={activeChatId}
                        onUploadSuccess={onDocumentUploaded}
                    />

                </div>


                {/* ======================================
                    RECENT CHATS
                ====================================== */}

                <h3 className="sidebar-heading mb-4 flex items-center gap-2">

                    <FiClock />

                    Recent Chats

                </h3>


                {/* ======================================
                    CHAT LIST
                ====================================== */}

                <div className="flex-1 space-y-2 overflow-y-auto">


                    {loading && (

                        <p className="sidebar-empty-state px-2 text-sm">

                            Loading chats...

                        </p>

                    )}


                    {!loading && chats.length === 0 && (

                        <p className="sidebar-empty-state px-2 text-sm">

                            No previous chats yet.

                        </p>

                    )}


                    {!loading && chats.map((chat) => (

                        <div
                            key={chat.id}
                            onClick={() =>
                                onSelectChat(chat.id)
                            }
                            className={`conversation-row group flex cursor-pointer items-center justify-between rounded-xl p-3 transition ${
                                activeChatId === chat.id
                                    ? "is-active"
                                    : ""
                            }`}
                        >


                            {/* CHAT TITLE */}

                            <div className="min-w-0 flex-1">

                                <p className="conversation-title truncate text-sm">

                                    {chat.title}

                                </p>

                            </div>


                            {/* ACTION BUTTONS */}

                            <div className="ml-2 flex items-center gap-1 opacity-0 transition group-hover:opacity-100">


                                {/* PIN */}

                                <button
                                    onClick={(event) =>
                                        handlePin(
                                            event,
                                            chat.id
                                        )
                                    }
                                    title={
                                        chat.pinned
                                            ? "Unpin chat"
                                            : "Pin chat"
                                    }
                                    className="rounded-lg p-2 transition hover:bg-slate-600"
                                >

                                    <FiBookmark
                                        size={16}
                                        className={
                                            chat.pinned
                                                ? "text-cyan-400"
                                                : "text-slate-400"
                                        }
                                    />

                                </button>


                                {/* DELETE */}

                                <button
                                    onClick={(event) =>
                                        handleDelete(
                                            event,
                                            chat.id
                                        )
                                    }
                                    title="Delete chat"
                                    className="rounded-lg p-2 transition hover:bg-red-900/40"
                                >

                                    <FiTrash2
                                        size={16}
                                        className="text-slate-400 hover:text-red-400"
                                    />

                                </button>


                            </div>

                        </div>

                    ))}


                </div>

            </div>

        </aside>

    );
}


export default Sidebar;