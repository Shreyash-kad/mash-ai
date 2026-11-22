import { useRef, useState } from "react";
import {
    FiMic,
    FiMicOff,
    FiSend,
} from "react-icons/fi";


function MessageInput({ onSend }) {

    const [text, setText] = useState("");
    const [listening, setListening] = useState(false);

    const recognitionRef = useRef(null);


    // ==================================================
    // VOICE INPUT
    // ==================================================

    const startVoiceInput = () => {

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;


        if (!SpeechRecognition) {

            alert(
                "Voice input is not supported in this browser. Please use Google Chrome."
            );

            return;

        }


        const recognition = new SpeechRecognition();

        recognition.lang = "en-IN";

        recognition.continuous = false;

        recognition.interimResults = false;


        recognition.onstart = () => {

            setListening(true);

        };


        recognition.onresult = (event) => {

            const spokenText =
                event.results[0][0].transcript;

            setText((prev) => {

                if (prev.trim()) {

                    return prev + " " + spokenText;

                }

                return spokenText;

            });

        };


        recognition.onerror = (event) => {

            console.error(
                "Voice recognition error:",
                event.error
            );

            setListening(false);

        };


        recognition.onend = () => {

            setListening(false);

        };


        recognitionRef.current = recognition;

        recognition.start();

    };


    // ==================================================
    // STOP VOICE
    // ==================================================

    const stopVoiceInput = () => {

        if (recognitionRef.current) {

            recognitionRef.current.stop();

        }

        setListening(false);

    };


    // ==================================================
    // SEND MESSAGE
    // ==================================================

    const handleSend = () => {

        if (!text.trim()) return;

        onSend(text.trim());

        setText("");

    };


    // ==================================================
    // ENTER KEY
    // ==================================================

    const handleKeyDown = (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            handleSend();

        }

    };


    return (

        <div className="flex items-end gap-3">


            {/* =========================================
                TEXT INPUT
            ========================================= */}

            <textarea
                value={text}
                onChange={(event) =>
                    setText(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder={
                    listening
                        ? "Listening..."
                        : "Message Mash AI..."
                }
                rows={1}
                className="message-textarea min-h-[52px] flex-1 resize-none rounded-2xl border px-5 py-4 outline-none transition"
            />


            {/* =========================================
                VOICE BUTTON
            ========================================= */}

            <button
                type="button"
                onClick={
                    listening
                        ? stopVoiceInput
                        : startVoiceInput
                }
                title={
                    listening
                        ? "Stop recording"
                        : "Voice input"
                }
                className={`voice-button flex h-[52px] w-[52px] items-center justify-center rounded-2xl border transition ${
                    listening
                        ? "is-listening"
                        : ""
                }`}
            >

                {listening ? (
                    <FiMicOff size={20} />
                ) : (
                    <FiMic size={20} />
                )}

            </button>


            {/* =========================================
                SEND BUTTON
            ========================================= */}

            <button
                type="button"
                onClick={handleSend}
                disabled={!text.trim()}
                className="send-button flex h-[52px] w-[52px] items-center justify-center rounded-2xl text-white transition disabled:cursor-not-allowed disabled:opacity-40"
            >

                <FiSend size={20} />

            </button>

        </div>

    );

}


export default MessageInput;