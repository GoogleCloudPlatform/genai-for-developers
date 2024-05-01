import click
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import ChatVertexAI
import os

# TODO: Remove API KEY

# Load environment variables for Gemini Pro
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# # AIzaSyDRkzVLmGe-ze3wNX0mcv7dBPF4tpXESmw


@click.command()
@click.option('-q', '--qry', required=False, type=str, default="")
def query(qry):

    # Load the ChromaDB
    persist_directory = "./chroma_db_store"
    embedding_function = VertexAIEmbeddings(
        requests_per_minute=100,  # Adjust rate limiting as needed
        num_instances_per_batch=5,
        model_name="textembedding-gecko@latest"
    )
    db = Chroma(persist_directory=persist_directory,
                embedding_function=embedding_function)

    # Create a retriever from ChromaDB (adjust parameters as needed)
    # Get top 3 most similar documents
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Load the Gemini Pro model

    llm = ChatVertexAI(
        # model_name="projects/your-project-id/locations/global/models/gemini-1.5-pro-latest",
        # model_name="gemini-1.5-pro-latest",
        model_name="gemini-pro",
        safety_settings={},
        temperature=.2,
        # max_output_tokens=256,
        # top_p=0.9,
        # presence_penalty=0.1,
        convert_system_message_to_human=True
    )

    # Create a RetrievalQA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

    query = qry
    result = qa.invoke({"query": query})
    answer = result['result']
    source_documents = result['source_documents']
    print(f"Answer: {answer}")
    print("\nRelevant Source Code:")
    for doc in source_documents:
        print(doc.page_content)
    print("\n")


   

