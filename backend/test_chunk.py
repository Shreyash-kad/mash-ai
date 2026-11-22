from chunker import split_text
text = """
Python is a programming language.

It is used in AI.

It is also used in Web Development.

Machine Learning is built using Python.

Data Science uses Python.

FastAPI is a Python framework.

This is a long paragraph used only for testing.
""" * 20

chunks = split_text(text)

print("Total Chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print("=" * 40)
    print("Chunk", i + 1)
    print(chunk[:200])