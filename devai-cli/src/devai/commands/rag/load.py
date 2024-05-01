import click
from google.cloud import aiplatform
import os
import shutil
from pathlib import Path
from git import Repo

from langchain_community.document_loaders import GitLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import Chroma


def load_docs(repo_path, branch, local_dir, allowed_extensions):
    if Path(local_dir).exists():
        try:
            repo = Repo(local_dir)
            repo.remotes.origin.pull()
        except Exception as e:
            print(f"Error pulling updates: {e}")
            shutil.rmtree(local_dir)
            Repo.clone_from(repo_path, local_dir)
    else:
        Repo.clone_from(repo_path, local_dir)

    def file_filter(file_path: str) -> bool:
        return any(file_path.endswith(ext) for ext in allowed_extensions)

    loader = GitLoader(local_dir, branch=branch, file_filter=file_filter)
    return loader.load()


@click.command()
def load():
    repo_path = "https://github.com/GoogleCloudPlatform/generative-ai"
    branch = "main"
    local_dir = "./generative-ai"

    # Common source code file extensions and markdown
    allowed_extensions = [
        ".py", ".java", ".cpp", ".c", ".cs", ".js", ".ts",
        ".php", ".rb", ".go", ".swift", ".rs", ".md"
    ]

    # 1. Load filtered documents
    documents = load_docs(repo_path, branch, local_dir, allowed_extensions)

    # 2. Split into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # 3. Generate Embeddings (Replace with your preferred embedding model if not using Vertex AI)
    EMBEDDING_QPM = 100
    EMBEDDING_NUM_BATCH = 5
    embeddings = VertexAIEmbeddings(
        requests_per_minute=EMBEDDING_QPM,
        num_instances_per_batch=EMBEDDING_NUM_BATCH,
        model_name="textembedding-gecko@latest",
    )

    # 4. Store in ChromaDB
    db = Chroma.from_documents(
        texts, embeddings,
        persist_directory="./chroma_db_store",
        collection_name="source_code_embeddings"
    )
    db.persist()

    print("Done with load")


@click.command()
def testdb():
    # 1. Load existing ChromaDB if it exists
    db = None
    persist_directory = "./chroma_db_store"
    if Path(persist_directory).exists():
        # Assuming same embeddings were used to create the DB
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

    # 2. Simple test if DB loaded
    if db:
        # Sample query
        sample_query = "what is Cymbal starlight"
        docs = db.similarity_search(sample_query)

        if docs:
            print("Database loaded successfully. Sample query results:")
            for doc in docs:
                # Print a snippet of each relevant document
                print(doc.page_content[:100])
        else:
            print("Database loaded, but no results for sample query.")
    else:
        print("Database could not be loaded.")
