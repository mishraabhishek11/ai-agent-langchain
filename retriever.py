from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS


loader = TextLoader(
    "notes.txt",
    encoding="utf-8"
)

documents = loader.load()


splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)


embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


vector_store = FAISS.from_documents(
    chunks,
    embeddings
)


retriever = vector_store.as_retriever()
