
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user queries with diagrams and visuals when applicable."),
        ("user", "Question:{question}")
    ]
)

# Streamlit Framework
st.title('T.O.N.Y (Text-Oriented Neural Yield) - Visual AI Assistant')
input_text = st.text_input("Ask anything or explore a topic")

# Ollama LLAMA2 LLM
llm = Ollama(model="llama2")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

if input_text:
    st.write(chain.invoke({"question": input_text}))
