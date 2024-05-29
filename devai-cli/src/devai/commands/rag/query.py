import click
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI


@click.command()
@click.option('-q', '--qry', required=False, type=str, default="")
@click.option('-d', '--db_path', required=False, type=str, default="./chroma_db_store", help="Provide the path to persist the DB")
def query(qry, db_path):

    # Load the ChromaDB
    persist_directory = db_path
    EMBEDDING_QPM = 100
    EMBEDDING_NUM_BATCH = 5
    embeddings = VertexAIEmbeddings(
        requests_per_minute=EMBEDDING_QPM,
        num_instances_per_batch=EMBEDDING_NUM_BATCH,
        model_name="textembedding-gecko@latest",
    )
    db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="source_code_embeddings"
    )

    # Create a retriever from ChromaDB (adjust parameters as needed)
    # Get top 3 most similar documents
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, 
                       "mmr_repetition_penalty": 1.2,
                       })

    # Load the Gemini Pro model

    llm = ChatVertexAI(
        model_name="gemini-1.5-pro",
        safety_settings={},
        temperature=.1,
        # max_output_tokens=256,
        # top_p=0.9,
        # presence_penalty=0.1,
        convert_system_message_to_human=True
    )

    question = qry


    result_direct_retreival = retriever.get_relevant_documents(question)
    
    # Create a RetrievalQA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", 
        retriever=retriever, 
        return_source_documents=True)

    template="Respond to the following query as best you can using the context provided. Keep your answers short and concise. If you don't know say you don't know. {qry}"
    query = template.format(qry=qry)
    result = qa.invoke({"query": query})
    answer = result['result']
    source_documents = result['source_documents']
    print(f"Answer: {answer}")
    print("\nRelevant Source Code:")
    for doc in source_documents:
        print(doc.page_content)
    print("\n")


   

