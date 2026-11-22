import { FiCopy, FiCpu, FiUser } from "react-icons/fi";
import ReactMarkdown from "react-markdown";

function Message({ sender = "ai", text = "", source = "Workspace" }) {
    const isUser = sender === "user";

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(text);
        } catch (error) {
            console.error("Copy failed", error);
        }
    };

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`max-w-[90%] rounded-[24px] border px-4 py-3 shadow-sm sm:max-w-[80%] ${isUser
                        ? "border-cyan-400/20 bg-gradient-to-br from-cyan-500/20 to-violet-500/20 text-slate-50"
                        : "border-white/10 bg-slate-900/80 text-slate-100"
                    }`}
            >
                <div className="mb-2 flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-400">
                        {isUser ? <FiUser className="h-3.5 w-3.5" /> : <FiCpu className="h-3.5 w-3.5" />}
                        {isUser ? "You" : "Mash AI"}
                    </div>
                    <div className="flex items-center gap-2">
                        {!isUser && (
                            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-[10px] font-medium uppercase tracking-[0.2em] text-slate-400">
                                {source}
                            </span>
                        )}
                        <button
                            onClick={handleCopy}
                            className="rounded-full border border-white/10 bg-white/5 p-1.5 text-slate-300 transition hover:bg-white/10 hover:text-white"
                            aria-label="Copy message"
                        >
                            <FiCopy className="h-3.5 w-3.5" />
                        </button>
                    </div>
                </div>

                <div className="prose prose-invert max-w-none text-sm leading-7 text-slate-200 prose-pre:overflow-x-auto prose-pre:rounded-2xl prose-pre:border prose-pre:border-white/10 prose-pre:bg-slate-950/70 prose-pre:p-4 prose-code:rounded prose-code:bg-white/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:text-cyan-200">
                    <ReactMarkdown>{text}</ReactMarkdown>
                </div>
            </div>
        </div>
    );
}

export default Message;
