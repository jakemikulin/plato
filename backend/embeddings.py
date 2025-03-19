from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

# Load efficient embedding model
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

def load_and_chunk_documents():
    """Loads PDFs and text files, splits them into smaller chunks."""
    doc_path = "sums/"
    loaders = [
        DirectoryLoader(doc_path, glob="*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(doc_path, glob="*.txt", loader_cls=TextLoader)
    ]

    documents = []
    for loader in loaders:
        documents.extend(loader.load())

    # Split long documents into smaller chunks (~512 tokens each)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    chunked_docs = text_splitter.split_documents(documents)

    return chunked_docs

def store_embeddings():
    """Convert documents into vector embeddings and store them in ChromaDB."""
    if not os.path.exists("vectorstore/"):
        os.makedirs("vectorstore/")

    docs = load_and_chunk_documents()
    db = Chroma.from_documents(docs, embedding_model, persist_directory="vectorstore/")
    print("✅ Document embeddings stored in ChromaDB.")

if __name__ == "__main__":
    store_embeddings()
