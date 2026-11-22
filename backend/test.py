from embeddings import create_embedding

text = "Hello world"

embedding = create_embedding(text)

print("Length:", len(embedding))
print(embedding[:10])