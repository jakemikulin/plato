from langchain.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

# Load embedding model (efficient & lightweight)
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

def load_documents():
    """Load PDFs and text documents from the docs/ folder."""
    doc_path = "docs/"
    loaders = [
        DirectoryLoader(doc_path, glob="*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(doc_path, glob="*.txt", loader_cls=TextLoader)
    ]
    
    documents = []
    for loader in loaders:
        documents.extend(loader.load())
    
    return documents

def store_embeddings():
    """Convert documents into vector embeddings and store them in ChromaDB."""
    if not os.path.exists("vectorstore/"):
        os.makedirs("vectorstore/")
    
    docs = load_documents()
    db = Chroma.from_documents(docs, embedding_model, persist_directory="vectorstore/")
    db.persist()
    print("✅ Document embeddings stored in ChromaDB.")

if __name__ == "__main__":
    store_embeddings()  # Run this once after scraping new university data
