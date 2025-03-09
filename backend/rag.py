from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

# Load ChromaDB retriever
def get_retriever():
    db = Chroma(persist_directory="vectorstore/", embedding_function=embedding_model)
    return db.as_retriever()

# Memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Always attempt retrieval first, fallback to LLM if no relevant docs
def ask_question(query):
    llm = OllamaLLM(model="llama3.2")
    retriever = get_retriever()
    
    # Setup Conversational RAG chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    
    # Get response
    response = qa_chain.invoke({"question": query})

    return response["answer"]
