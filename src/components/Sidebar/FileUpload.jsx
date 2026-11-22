import { useRef, useState } from "react";
import { FiUpload, FiLoader } from "react-icons/fi";
import { uploadFile } from "../../services/api";

function FileUpload({ chatId, onUploadSuccess }) {
    const inputRef = useRef(null);
    const [uploading, setUploading] = useState(false);

    const handleUpload = async (event) => {
        const file = event.target.files?.[0];

        if (!file) return;

        if (!chatId) {
            alert("Please create or select a chat before uploading a document.");
            event.target.value = "";
            return;
        }

        try {
            setUploading(true);

            const response = await uploadFile(file, chatId);

            console.log("UPLOAD SUCCESS:", response);

            if (onUploadSuccess) {
                onUploadSuccess({
                    filename: response.filename,
                    chunks_added: response.chunks_added,
                });
            }

        } catch (error) {
            console.error("UPLOAD ERROR:", error);
            alert("Upload failed.");
        } finally {
            setUploading(false);

            // Allows selecting same file again
            event.target.value = "";
        }
    };

    return (
        <>
            <input
                ref={inputRef}
                type="file"
                hidden
                accept=".pdf,.docx,.txt"
                onChange={handleUpload}
            />

            <button
                onClick={() => inputRef.current?.click()}
                disabled={uploading || !chatId}
                title={!chatId ? "Create or select a chat before uploading" : "Upload document"}
                className="upload-button flex w-full items-center justify-center gap-3 rounded-2xl border py-4 text-lg transition-all disabled:opacity-50"
            >
                {uploading ? (
                    <>
                        <FiLoader className="animate-spin" />
                        Indexing...
                    </>
                ) : (
                    <>
                        <FiUpload />
                        Upload Document
                    </>
                )}
            </button>
        </>
    );
}

export default FileUpload;