from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain_chroma import Chroma  # ✅ FIXED IMPORT
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
import time
import requests

# 🔹 Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

# 🔹 Load ChromaDB retriever
def get_retriever():
    db = Chroma(persist_directory="vectorstore/", embedding_function=embedding_model)
    return db.as_retriever()

# 🔹 Chat memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 🔹 Define custom prompt template
prompt_template = """

Previous conversation history:
{chat_history}

Retrieved documents:
{context}

User question: {question}

If the documents do not answer the question, provide the best possible answer using the user question and system prompt ignoring the retrieved documents.
Keep responses factual and concise.

"""

prompt = PromptTemplate(
    template=prompt_template, 
    input_variables=["chat_history", "context", "question"]
)

# 🔹 Ensure Ollama is running before making requests
def is_ollama_running():
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False

# 🔹 Function to handle questions
def ask_question(query):
    if not is_ollama_running():
        yield "Error: Ollama is not running. Please start Ollama and try again."
        return

    llm = OllamaLLM(
        model="phi4-mini",
        system_prompt=(
            "You are an empathetic AI assistant specialising in mental health resources for students at The University of Edinburgh. "
            "Keep your responses concise (maximum 500 characters). "
            "Do not reference the documents"
            "Talk about the documents as if you know their content as fact"

            "Crisis & Support Contacts: "
            "- For emergencies (including suicidal thoughts or self-harm), advise calling 999. "
            "- For urgent but non-emergency medical support, direct users to NHS 111. "
            "- For mental health support, recommend Samaritans, Mind, or SHOUT. "

            "Guidance on Using the Sorted (FeelingGood) App: "
            "- Tracks 1, 2, and 3 are great for getting started. "
            "- For depression, recommend tracks 5, 6, 9, and 10. "
            "- For anxiety, suggest tracks 4, 5, 7, and 8. "
            "- For stress, advise tracks 5, 8, 10, and 12. "
            "- For interpersonal issues, suggest tracks 8, 9, 10, and 12. "
            "- For sleep difficulties, recommend trying the Sleep Better module. "

            "Always prioritise the user's well-being, providing empathetic and resourceful responses."
            "Always provide specifics tools and options from the retrieved documents such as named resources or strategies."
    )
    )
    
    retriever = get_retriever()

    # ✅ Load chat history
    chat_history = memory.load_memory_variables({}).get("chat_history", [])

    # ✅ Start retrieval
    start_retrieval = time.time()
    docs = retriever.invoke(query)[:3]  # Fetch top 3 relevant documents
    retrieval_time = time.time() - start_retrieval
    print(f"\n⏳ Retrieval Time: {retrieval_time:.2f} seconds")

    if docs:
        context = "\n\n".join([f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(docs)])
        print("\n🔍 Retrieved Context for LLM:\n")
        print(context[:500])  # Print first 500 characters for debugging
    else:
        print("❌ No relevant documents found. Using general model response.")
        context = "No relevant documents found."

    formatted_chat_history = "\n".join([msg.content for msg in chat_history])

    # ✅ Construct final prompt including chat history
    final_prompt = prompt.format(
        chat_history=formatted_chat_history,
        context=context,
        question=query
    )

    print("\n🔹 FINAL PROMPT SENT TO LLM:\n")
    print(final_prompt[:500])  # Print first 500 characters for debugging

    # ✅ Stream the response
    full_response = ""  # Store full response for memory saving
    for chunk in llm.stream(final_prompt):
        full_response += chunk + " "  # Append to final response
        yield chunk + " "  # Yield each chunk as it comes

    # ✅ Update chat memory after the response is completed
    memory.save_context({"input": query}, {"output": full_response})