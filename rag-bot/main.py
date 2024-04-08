from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeLangChain
from pinecone import Pinecone

from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough

from dotenv import load_dotenv
import os
import aiohttp
import json
import requests
import ollama

def generate(input):
    """
        send request to ollama api to get answer
    """
    ollama_base_url = os.getenv("OLLAMA_BASE_URL")
    ollama_port = os.getenv("OLLAMA_PORT")
    ollama_model = os.getenv("MODEL")    
    
    response = ollama.chat(model=ollama_model, messages=[
    {
        'role': 'user',
        'content': str(input),
    },
    ])
    return response['message']['content']


class ChatBot():
    load_dotenv()

    index_name = "langchain-mac"
    embeddings = HuggingFaceEmbeddings()
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    docsearch = PineconeLangChain.from_existing_index(index_name, embeddings)  

    template = """{question}. Context: {context}"""
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    rag_chain = (
      {"context": docsearch.as_retriever(),  "question": RunnablePassthrough()} 
      | prompt
      | generate
    )

    