import os

from dotenv import load_dotenv
import google.generativeai as genai


# ==================================================
# GEMINI SETUP
# ==================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from the .env file."
    )

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ==================================================
# ASK GEMINI
# ==================================================

def ask_gemini(
    question,
    context=None,
    history=None,
    memory=None
):

    prompt = ""


    # ------------------------------------------------
    # LONG-TERM MEMORY
    # ------------------------------------------------

    if memory:

        prompt += """
Long-Term User Memory:

The following information is known about the user.
Use it when it is relevant to the current question.

"""

        for item in memory:

            prompt += (
                f"{item['key']}: "
                f"{item['value']}\n"
            )

        prompt += "\n"


    # ------------------------------------------------
    # CONVERSATION HISTORY
    # ------------------------------------------------

    if history:

        prompt += """
Conversation History:

Use the previous conversation when it is relevant.
Do not assume information that is not present.

"""

        for chat in history:

            role = chat.get("role", "user")
            content = chat.get(
                "content",
                chat.get("message", "")
            )

            prompt += (
                f"{role.capitalize()}: "
                f"{content}\n"
            )

        prompt += "\n"


    # ------------------------------------------------
    # RAG DOCUMENT CONTEXT
    # ------------------------------------------------

    if context:

        prompt += """
Document Context:

The following information was retrieved
from the user's uploaded documents.

Use this information when answering
questions about those documents.

"""

        prompt += context

        prompt += "\n\n"


    # ------------------------------------------------
    # CURRENT QUESTION
    # ------------------------------------------------

    prompt += f"""
Current Question:

{question}

"""


    # ------------------------------------------------
    # SYSTEM INSTRUCTIONS
    # ------------------------------------------------

    prompt += """
Instructions:

1. Answer naturally and clearly.

2. If the user's long-term memory contains
   relevant information, use it.

3. If the conversation history contains
   relevant information, use it.

4. If document context is provided and the
   question is about the document, prioritize
   the retrieved document information.

5. Do not claim that you cannot access a
   document when relevant document context
   has been provided.

6. Do not invent information that is not
   present in the memory, conversation,
   document context, or your general knowledge.

7. Keep the answer relevant to the question.
"""


    # ------------------------------------------------
    # GENERATE RESPONSE
    # ------------------------------------------------

    response = model.generate_content(prompt)

    return response.text