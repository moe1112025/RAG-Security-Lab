import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama

class RAGSystem:
    def __init__(self, db_dir="db"):
        self.db_dir = db_dir
        # Local Ollama Components
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = Ollama(model="llama3")
        self.vector_store = None
    def ingest_raw_text(self, text_content):
        """Stores raw text directly into the Vector Database"""
        documents = [Document(page_content=text_content)]
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
  
        self.vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=self.embeddings, 
            persist_directory=self.db_dir
        )
        print("[+] Data successfully stored in Vector Database.")

    def query(self, question):
        """Simplest way to query the database using raw semantic search context"""
        if not self.vector_store:
            self.vector_store = Chroma(persist_directory=self.db_dir, embedding=self.embeddings)
            
        # Get matching documents from DB
        docs = self.vector_store.similarity_search(question, k=1)
        context = docs[0].page_content if docs else "No context found."
        
        # Build manual safe prompt structure to avoid high-level chain errors
        prompt = (
            f"You are a helpful assistant. Use the following context to answer the question.\n"
            f"Context: {context}\n"
            f"Question: {question}\n"
            f"Answer:"
        )
        
        return self.llm.invoke(prompt)