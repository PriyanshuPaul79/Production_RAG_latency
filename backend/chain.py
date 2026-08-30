# backend/chain.py
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Initialize Groq LLM
# Make sure you have set your GROQ_API_KEY in your environment variables
llm = ChatGroq(
    model="llama-3.1-8b-instant", 
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_answer(question: str, context_chunks: list):
    """
    Formats the context and question into a prompt, then asks the LLM for an answer.
    """
    print("--- CHAIN: Generating answer via Groq ---")
    
    if not context_chunks:
        return "I couldn't find any relevant information in this document."

    # Combine chunks into a single string
    context_text = "\n\n---\n\n".join(context_chunks)
    
    # Strict prompt to prevent hallucinations
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful AI assistant. Answer the user's question using ONLY the provided context. 
        If the answer is not in the context, say "I don't have enough information in this document to answer that."
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:"""
    )
    
    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": question})
    
    return response.content