import { useState } from "react";
import { FiUploadCloud } from "react-icons/fi";

function UploadButton() {
    const [isDragging, setIsDragging] = useState(false);
    const [progress, setProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);

    const handleDrop = (event) => {
        event.preventDefault();
        setIsDragging(false);
        setIsUploading(true);

        const file = event.dataTransfer.files?.[0];
        if (!file) {
            setIsUploading(false);
            return;
        }

        let completed = 0;
        const timer = setInterval(() => {
            completed += 10;
            setProgress((prev) => (prev >= 100 ? 100 : Math.max(prev, completed)));
            if (completed >= 100) {
                clearInterval(timer);
                setTimeout(() => {
                    setIsUploading(false);
                    setProgress(0);
                }, 500);
            }
        }, 120);
    };

    return (
        <div className="w-full max-w-xl rounded-[28px] border border-white/10 bg-slate-950/70 p-4 shadow-2xl shadow-cyan-500/10 backdrop-blur-xl">
            <div
                onDragOver={(event) => {
                    event.preventDefault();
                    setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`rounded-[24px] border-2 border-dashed p-8 text-center transition ${isDragging
                        ? "border-cyan-400 bg-cyan-500/10"
                        : "border-white/10 bg-white/5"
                    }`}
            >
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500/20 via-violet-500/20 to-fuchsia-500/20 text-sky-200">
                    <FiUploadCloud className="h-6 w-6" />
                </div>

                <h3 className="mt-4 text-lg font-semibold text-white">Drop files to upload</h3>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                    Support for documents, PDFs, and knowledge files in one smooth flow.
                </p>

                {isUploading && (
                    <div className="mt-5">
                        <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                            <div
                                className="h-full rounded-full bg-gradient-to-r from-sky-500 via-violet-500 to-fuchsia-500 transition-all duration-200"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                        <p className="mt-2 text-sm text-slate-300">Uploading… {progress}%</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default UploadButton;
