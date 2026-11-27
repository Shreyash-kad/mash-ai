
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import uuid

from backend.file_loader import read_file
from backend.rag import index_document, search_documents

from backend.db import (
    create_database,
    create_chat,
    get_chats,
    get_chat,
    update_chat_title,
    toggle_pin,
    delete_chat,
    save_message,
    get_messages,
    get_memories,
    save_document,
    get_documents,
    get_document,
    delete_document,
)

from backend.chatbot import ask_gemini


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Mash AI API",
    description="Personal AI chatbot with RAG, memory and document processing",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://mash-ai-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE AND DOCUMENT STORAGE
# ============================================================

create_database()

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DOCUMENT_FOLDER = os.path.join(BASE_DIR, "documents")
os.makedirs(DOCUMENT_FOLDER, exist_ok=True)


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):
    message: str
    chat_id: int | None = None


class CreateChatRequest(BaseModel):
    title: str = "New Chat"


# ============================================================
# ROOT AND HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "success": True,
        "message": "Mash AI backend is running.",
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "backend": "online",
    }


# ============================================================
# CHATS
# ============================================================

@app.get("/chats")
def get_all_chats():
    try:
        return {
            "success": True,
            "chats": get_chats(),
        }
    except Exception as error:
        print("Get chats error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to load chats.",
        )


@app.post("/chats")
def create_new_chat(request: CreateChatRequest):
    try:
        chat_id = create_chat(request.title)
        return {
            "success": True,
            "chat": get_chat(chat_id),
        }
    except Exception as error:
        print("Create chat error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to create chat.",
        )


@app.get("/chats/{chat_id}/messages")
def get_chat_messages(chat_id: int):
    try:
        chat = get_chat(chat_id)

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found.",
            )

        return {
            "success": True,
            "chat": chat,
            "messages": get_messages(chat_id),
        }
    except HTTPException:
        raise
    except Exception as error:
        print("Get messages error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to load messages.",
        )


@app.patch("/chats/{chat_id}/pin")
def pin_chat(chat_id: int):
    try:
        if not get_chat(chat_id):
            raise HTTPException(
                status_code=404,
                detail="Chat not found.",
            )

        toggle_pin(chat_id)

        return {
            "success": True,
            "chat": get_chat(chat_id),
        }
    except HTTPException:
        raise
    except Exception as error:
        print("Pin chat error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to update chat.",
        )


@app.delete("/chats/{chat_id}")
def remove_chat(chat_id: int):
    try:
        if not get_chat(chat_id):
            raise HTTPException(
                status_code=404,
                detail="Chat not found.",
            )

        delete_chat(chat_id)

        return {
            "success": True,
            "message": "Chat deleted successfully.",
        }
    except HTTPException:
        raise
    except Exception as error:
        print("Delete chat error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete chat.",
        )


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chat_id: int | None = None,
):
    if chat_id is None:
        raise HTTPException(
            status_code=400,
            detail="chat_id is required when uploading a document.",
        )

    if not get_chat(chat_id):
        raise HTTPException(
            status_code=404,
            detail="Chat not found.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    original_filename = os.path.basename(file.filename)
    extension = os.path.splitext(original_filename)[1].lower()

    if extension not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF, DOCX and TXT files are supported.",
        )

    safe_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = os.path.join(DOCUMENT_FOLDER, safe_filename)

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        with open(file_path, "wb") as output:
            output.write(contents)

        text = read_file(file_path)

        if not text or len(text.strip()) < 20:
            raise HTTPException(
                status_code=422,
                detail="No readable text was found inside this document.",
            )

        chunks = index_document(
            text=text,
            filename=original_filename,
            chat_id=chat_id,
        )

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="The document was read but no chunks were indexed.",
            )

        # Save document metadata to SQLite.
       document_id = save_document(
    chat_id=chat_id,
    filename=original_filename,
    file_path=file_path,
)

        return {
            "success": True,
            "document_id": document_id,
            "chat_id": chat_id,
            "filename": original_filename,
            "file_type": extension,
            "chunks": chunks,
            "chunks_added": chunks,
            "message": f"{original_filename} uploaded successfully.",
        }

    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

    except Exception as error:
        print("Upload error:", error)

        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail="Failed to upload and index the document. Check the backend terminal for details.",
        )

    finally:
        await file.close()


# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================

@app.get("/documents")
def get_all_documents(chat_id: int | None = None):
    try:
        if chat_id is not None and not get_chat(chat_id):
            raise HTTPException(
                status_code=404,
                detail="Chat not found.",
            )

        return {
            "success": True,
            "chat_id": chat_id,
            "documents": get_documents(chat_id),
        }
    except HTTPException:
        raise
    except Exception as error:
        print("Get documents error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to load documents.",
        )


@app.get("/documents/{document_id}")
def get_one_document(document_id: int):
    try:
        document = get_document(document_id)

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        return {
            "success": True,
            "document": document,
        }
    except HTTPException:
        raise
    except Exception as error:
        print("Get document error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to load document.",
        )


@app.delete("/documents/{document_id}")
def remove_document(document_id: int):
    try:
        document = get_document(document_id)

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        file_path = document.get("file_path")

        # Delete the database record first, then the stored file.
        delete_document(document_id)

        if file_path and os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError as error:
                print("Could not remove physical document:", error)

        return {
            "success": True,
            "message": "Document deleted successfully.",
        }
    except HTTPException:
        raise
    except Exception as error:
        print("Delete document error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document.",
        )


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    chat_id = request.chat_id

    try:
        # Create a chat automatically if no chat ID was provided.
        if chat_id is None:
            title = request.message.strip()

            if len(title) > 40:
                title = title[:40] + "..."

            chat_id = create_chat(title)

        chat_record = get_chat(chat_id)

        if not chat_record:
            raise HTTPException(
                status_code=404,
                detail="Chat not found.",
            )

        if chat_record["title"] == "New Chat" and not get_messages(chat_id):
            title = request.message.strip()

            if len(title) > 40:
                title = title[:40] + "..."

            update_chat_title(chat_id, title)

        # Save the user's message.
        save_message(chat_id, "user", request.message)

        # Load conversation history, excluding the latest user message
        # because the current question is passed separately to Gemini.
        messages = get_messages(chat_id)
        history = messages[:-1][-20:]

        # Load saved long-term memory.
        memory = get_memories()

        # Retrieve relevant document context for this chat.
        context = ""
        score = 0
        source = "Unknown"

        try:
            result = search_documents(
                request.message,
                chat_id=chat_id,
            )

            if isinstance(result, tuple):
                if len(result) >= 3:
                    context, score, source = result[:3]
                elif len(result) == 2:
                    context, score = result
                elif len(result) == 1:
                    context = result[0]
            elif isinstance(result, str):
                context = result

        except Exception as rag_error:
            print("RAG search error:", rag_error)

        # Generate the answer.
        answer = ask_gemini(
            question=request.message,
            context=context,
            history=history,
            memory=memory,
        )

        # Save the assistant's response.
        save_message(chat_id, "assistant", answer)

        return {
            "success": True,
            "chat_id": chat_id,
            "question": request.message,
            "answer": answer,
            "context": context,
            "source": source,
            "similarity_score": score,
        }

    except HTTPException:
        raise
    except Exception as error:
        print("CHAT ERROR:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat message.",
        )
