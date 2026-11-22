import { useEffect, useRef, useState } from "react";

import {
    FiCopy,
    FiCheck,
    FiPaperclip,
    FiFileText,
} from "react-icons/fi";

import ReactMarkdown from "react-markdown";

import {
    sendMessage,
    getChatMessages,
    getChatDocuments,
    uploadFile,
} from "../../services/api";

import MessageInput from "./MessageInput";


// ==================================================
// CODE BLOCK
// ==================================================

function CodeBlock({ children }) {

    const [copied, setCopied] = useState(false);

    const code = String(children).replace(/\n$/, "");


    const copyCode = async () => {

        try {

            await navigator.clipboard.writeText(code);

            setCopied(true);

            setTimeout(() => {
                setCopied(false);
            }, 2000);

        } catch (error) {

            console.error(
                "Copy failed:",
                error
            );

        }

    };


    return (

        <div className="code-block my-3 overflow-hidden rounded-xl">

            <div className="code-block-header flex items-center justify-between px-4 py-2">

                <span className="code-block-label">
                    Code
                </span>

                <button
                    onClick={copyCode}
                    className="code-copy-button flex items-center gap-2 transition"
                    aria-label={copied ? "Code copied" : "Copy code"}
                >

                    {copied ? (
                        <>
                            <FiCheck />
                            Copied
                        </>
                    ) : (
                        <>
                            <FiCopy />
                            Copy
                        </>
                    )}

                </button>

            </div>

            <pre className="code-block-content overflow-x-auto p-4">

                <code>
                    {code}
                </code>

            </pre>

        </div>

    );

}


// ==================================================
// CHAT BOX
// ==================================================

function ChatBox({
    chatId,
    onChatUpdated,
    onDocumentUploaded,
    documentRefreshVersion,
}) {

    const [messages, setMessages] = useState([]);
    const [documents, setDocuments] = useState([]);

    const [loading, setLoading] = useState(false);

    const [uploading, setUploading] = useState(false);

    const [dragging, setDragging] = useState(false);


    const fileInputRef = useRef(null);

    const messagesEndRef = useRef(null);
    const activeChatIdRef = useRef(chatId);
    activeChatIdRef.current = chatId;


    // ==================================================
    // AUTO SCROLL
    // ==================================================

    useEffect(() => {

        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });

    }, [messages, loading]);


    // ==================================================
    // LOAD OLD CHAT
    // ==================================================

    useEffect(() => {
        let isCurrent = true;

        setMessages([]);
        setLoading(false);
        setUploading(false);

        if (chatId) {
            getChatMessages(chatId)
                .then((response) => {
                    if (isCurrent && activeChatIdRef.current === chatId) {
                        setMessages(
                            response.messages.map((message) => ({
                                role: message.role,
                                content: message.message,
                            }))
                        );
                    }
                })
                .catch((error) => {
                    if (isCurrent) {
                        console.error("Failed to load chat:", error);
                    }
                });
        }

        return () => {
            isCurrent = false;
        };
    }, [chatId]);

    useEffect(() => {
        let isCurrent = true;

        setDocuments([]);

        if (!chatId) {
            return () => {
                isCurrent = false;
            };
        }

        getChatDocuments(chatId)
            .then((response) => {
                if (isCurrent && activeChatIdRef.current === chatId) {
                    setDocuments(response.documents || []);
                }
            })
            .catch((error) => {
                if (isCurrent) {
                    console.error("Failed to load chat documents:", error);
                }
            });

        return () => {
            isCurrent = false;
        };
    }, [chatId, documentRefreshVersion]);


    // ==================================================
    // UPLOAD DOCUMENT
    // ==================================================

    const handleFileUpload = async (file) => {

        if (!file) return;


        // ----------------------------------------------
        // CHAT CHECK
        // ----------------------------------------------

        const uploadChatId = chatId;

        if (!uploadChatId) {

            alert(
                "Please create or select a chat before uploading a document."
            );

            return;

        }


        const allowedTypes = [
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ];


        const allowedExtensions = [
            ".pdf",
            ".txt",
            ".docx",
        ];


        const extension =
            "." + file.name.split(".").pop().toLowerCase();


        if (
            !allowedTypes.includes(file.type) &&
            !allowedExtensions.includes(extension)
        ) {

            alert(
                "Please upload a PDF, DOCX, or TXT file."
            );

            return;

        }


        try {

            setUploading(true);


            // ------------------------------------------
            // IMPORTANT:
            // SEND FILE + CHAT ID
            // ------------------------------------------

            const response =
                await uploadFile(file, uploadChatId);

            onDocumentUploaded();

            if (activeChatIdRef.current === uploadChatId) {
                setMessages((prev) => [
                    ...prev,
                    {
                        role: "system",
                        content:
                            `📄 ${response.filename} uploaded successfully.\n\n✓ ${response.chunks_added} chunks indexed\n✓ Ready for questions`,
                    },
                ]);
            }

        } catch (error) {

            console.error(
                "Upload failed:",
                error
            );


            if (activeChatIdRef.current === uploadChatId) {
                setMessages((prev) => [
                    ...prev,
                    {
                        role: "system",
                        content: "❌ Document upload failed. Please try again.",
                    },
                ]);
            }

        } finally {

            if (activeChatIdRef.current === uploadChatId) {
                setUploading(false);
            }

        }

    };


    // ==================================================
    // FILE SELECT
    // ==================================================

    const handleFileChange = (event) => {

        const file =
            event.target.files?.[0];


        if (file) {

            handleFileUpload(file);

        }


        event.target.value = "";

    };


    // ==================================================
    // DRAG & DROP
    // ==================================================

    const handleDragOver = (event) => {

        event.preventDefault();

        setDragging(true);

    };


    const handleDragLeave = (event) => {

        event.preventDefault();

        setDragging(false);

    };


    const handleDrop = (event) => {

        event.preventDefault();

        setDragging(false);


        const file =
            event.dataTransfer.files?.[0];


        if (file) {

            handleFileUpload(file);

        }

    };


    // ==================================================
    // SEND MESSAGE
    // ==================================================

    const handleSend = async (text) => {

        if (!text.trim() || loading) {

            return;

        }

        const requestChatId = chatId;

        if (!requestChatId) return;

        setMessages((prev) => [

            ...prev,

            {
                role: "user",
                content: text,
            },

        ]);


        setLoading(true);


        try {

            const response =
                await sendMessage(
                    text,
                    requestChatId
                );

            if (activeChatIdRef.current === requestChatId) {
                setMessages((prev) => [
                    ...prev,
                    {
                        role: "assistant",
                        content: response.answer,
                    },
                ]);
            }

            await onChatUpdated();

        } catch (error) {

            console.error(
                "Failed to send message:",
                error
            );


            if (activeChatIdRef.current === requestChatId) {
                setMessages((prev) => [
                    ...prev,
                    {
                        role: "assistant",
                        content: "❌ Failed to connect to backend.",
                    },
                ]);
            }

        } finally {

            if (activeChatIdRef.current === requestChatId) {
                setLoading(false);
            }

        }

    };


    // ==================================================
    // EMPTY STATE
    // ==================================================

    if (!chatId) {

        return (

            <div className="welcome-state flex flex-1 items-center justify-center">

                <div className="text-center">

                    <h1 className="mb-2 text-3xl font-bold">
                        Welcome to Mash AI
                    </h1>

                    <p className="text-slate-400">
                        Create a new chat to get started.
                    </p>

                </div>

            </div>

        );

    }


    // ==================================================
    // CHAT UI
    // ==================================================

    return (

        <div
            className="relative flex h-full flex-1 flex-col"
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >


            {/* =========================================
                DRAG OVERLAY
            ========================================= */}

            {dragging && (

                <div className="drag-overlay absolute inset-0 z-50 flex items-center justify-center backdrop-blur-sm">

                    <div className="drag-card rounded-3xl border-2 border-dashed px-12 py-10 text-center">

                        <FiFileText
                            size={45}
                            className="mx-auto mb-4"
                        />

                        <h2 className="text-xl font-bold text-white">
                            Drop your document here
                        </h2>

                        <p className="mt-2 text-sm text-slate-400">
                            PDF, DOCX or TXT
                        </p>

                    </div>

                </div>

            )}


            {/* =========================================
                MESSAGES
            ========================================= */}

            <div className="chat-messages flex-1 space-y-5 overflow-y-auto p-6">

                {documents.length > 0 && (
                    <div className="document-preview rounded-xl border p-4">
                        <p className="document-preview-heading mb-3">
                            Documents in this chat
                        </p>
                        <div className="space-y-2.5">
                            {documents.map((document) => (
                                <div
                                    key={document.id}
                                    className="document-row flex items-center gap-2 text-sm"
                                >
                                    <FiFileText className="document-icon shrink-0" />
                                    <span className="document-name truncate">{document.filename}</span>
                                    <span className="document-meta shrink-0">
                                        {document.file_type} · {document.chunk_count} chunks
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map(
                    (msg, index) => (

                        <div
                            key={index}
                            className={`chat-message max-w-[80%] rounded-2xl px-5 py-3 ${
                                msg.role === "user"
                                        ? "user-message ml-auto text-white"
                                    : msg.role === "system"
                                        ? "system-message"
                                        : "assistant-message"
                            }`}
                        >

                            {msg.role === "assistant" ? (

                                <div className="assistant-markdown">
                                    <ReactMarkdown
                                        components={{

                                        code({
                                            inline,
                                            children,
                                        }) {

                                            if (inline) {

                                                return (
                                                    <code className="inline-code">
                                                        {children}
                                                    </code>
                                                );

                                            }


                                            return (
                                                <CodeBlock>
                                                    {children}
                                                </CodeBlock>
                                            );

                                        },


                                        p({ children }) {

                                            return (
                                                <p className="mb-3 last:mb-0">
                                                    {children}
                                                </p>
                                            );

                                        },


                                        ul({ children }) {

                                            return (
                                                <ul className="mb-3 list-disc space-y-1 pl-5">
                                                    {children}
                                                </ul>
                                            );

                                        },


                                        ol({ children }) {

                                            return (
                                                <ol className="mb-3 list-decimal space-y-1 pl-5">
                                                    {children}
                                                </ol>
                                            );

                                        },


                                        h1({ children }) {

                                            return (
                                                <h1 className="mb-3 text-2xl font-bold">
                                                    {children}
                                                </h1>
                                            );

                                        },


                                        h2({ children }) {

                                            return (
                                                <h2 className="mb-3 text-xl font-bold">
                                                    {children}
                                                </h2>
                                            );

                                        },


                                        h3({ children }) {

                                            return (
                                                <h3 className="mb-2 text-lg font-bold">
                                                    {children}
                                                </h3>
                                            );

                                        },


                                        strong({ children }) {

                                            return (
                                                <strong className="font-bold">
                                                    {children}
                                                </strong>
                                            );

                                        },

                                        }}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>

                            ) : (

                                <div className="whitespace-pre-line">
                                    {msg.content}
                                </div>

                            )}

                        </div>

                    )
                )}


                {/* LOADING */}

                {loading && (

                    <div className="thinking-indicator flex w-fit items-center gap-3 rounded-2xl px-5 py-3">

                        <span className="thinking-dot" aria-hidden="true" />
                        <span>
                            Mash AI is thinking
                        </span>

                        <span className="thinking-ellipsis" aria-hidden="true">
                            ...
                        </span>

                    </div>

                )}


                <div ref={messagesEndRef} />

            </div>


            {/* =========================================
                UPLOADING INDICATOR
            ========================================= */}

            {uploading && (

                <div className="px-4 pb-2">

                    <div className="upload-status flex items-center gap-3 rounded-xl border px-4 py-3 text-sm">

                        <FiFileText className="upload-status-icon" />

                        <span>
                            Uploading and indexing document...
                        </span>

                        <span className="upload-status-dots" aria-hidden="true">
                            ...
                        </span>

                    </div>

                </div>

            )}


            {/* =========================================
                INPUT AREA
            ========================================= */}

            <div className="chat-composer border-t p-4">

                <input
                    ref={fileInputRef}
                    type="file"
                    hidden
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileChange}
                />


                <div className="composer-toolbar mb-3 flex items-center">

                    <button
                        type="button"
                        onClick={() =>
                            fileInputRef.current?.click()
                        }
                        disabled={uploading}
                        title="Attach document"
                        className="attach-button flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition disabled:opacity-40"
                    >

                        <FiPaperclip />

                        Attach Document

                    </button>

                </div>


                <MessageInput
                    onSend={handleSend}
                />

            </div>

        </div>

    );

}


export default ChatBox;