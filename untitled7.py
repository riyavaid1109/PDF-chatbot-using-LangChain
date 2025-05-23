# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JUYvZGgNnPpN56iGe9-S2NidA55_J8Py
"""

!pip install -q langchain openai faiss-cpu PyPDF2

from google.colab import files

uploaded = files.upload()  # Select a PDF file from your local machine
pdf_file_path = next(iter(uploaded))  # Get the file name

from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

document_text = extract_text_from_pdf(pdf_file_path)
print(document_text[:1000])  # print preview of first 1000 characters

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_text(document_text)
print(f"Number of chunks: {len(chunks)}")
print(chunks[0])  # see first chunk

!pip install -U langchain-community

!pip install tiktoken

import time
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 🔑 Replace 'your-api-key-here' with your actual OpenAI API key
OPENAI_API_KEY = "secet key"  # Replace with your key

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Introduce a delay between embedding calls to avoid rate limiting
vectordb = FAISS.from_texts(chunks, embeddings, request_timeout=60)  # Added request_timeout for longer timeouts

# Add a delay after creating the vector database to avoid hitting rate limits
time.sleep(5)

print("Embeddings created and stored.")

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm,
    retriever=vectordb.as_retriever()
)

chat_history = []

while True:
    query = input("Ask something about the PDF (type 'exit' to quit): ")
    if query.lower() == "exit":
        break
    result = qa_chain.run({"question": query, "chat_history": chat_history})
    print("🤖:", result)
    chat_history.append((query, result))