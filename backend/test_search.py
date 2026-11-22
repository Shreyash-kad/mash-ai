from rag import search_documents

question = "Who is King Kohli?"

answer = search_documents(question)

print(answer)