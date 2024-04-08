from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeLangChain
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

loader = TextLoader('macbooks.txt', encoding = 'UTF-8')
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=4)
docs = text_splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings()

# index уже должен быть создан, так как Serverless в trial версии отсутствует
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = "langchain-mac"
docsearch = PineconeLangChain.from_documents(docs, embeddings, index_name=index_name)