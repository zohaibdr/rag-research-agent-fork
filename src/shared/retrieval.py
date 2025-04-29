"""Manage the configuration of various retrievers.

This module provides functionality to create and manage retrievers for different
vector store backends, specifically Elasticsearch, Pinecone, and MongoDB.
"""

import os
from contextlib import contextmanager
from typing import Generator

from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableConfig
from langchain_core.vectorstores import VectorStoreRetriever

from shared.configuration import BaseConfiguration
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


## Encoder constructors
def make_text_encoder() -> Embeddings:
    """Connect to the configured text encoder."""

    from langchain_openai import AzureOpenAIEmbeddings
    model = "text-embedding-ada-002" 
    
    embedding_function = AzureOpenAIEmbeddings(
        openai_api_key = os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint = os.environ["AZURE_EMBEDDINGS_ENDPOINT"],
        model = model,
        chunk_size = 16,
        max_retries = 3,
        # show_progress_bar = True,
    )
    return embedding_function


## Retriever constructors

@contextmanager
def make_mongodb_retriever(
    configuration: BaseConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific MongoDB Atlas index & namespaces."""
    from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

    vstore = MongoDBAtlasVectorSearch.from_connection_string(
        os.environ["MONGODB_URI"],
        namespace="langgraph_retrieval_agent.default",
        embedding=embedding_model,
    )
    yield vstore.as_retriever(search_kwargs=configuration.search_kwargs)

@contextmanager
def make_faiss_retriever(
    configuration: BaseConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to load local faiss store."""

    from langchain_community.vectorstores import FAISS

    # load an already created in memory faiss index
    # print("cwd:::", os.getcwd() )

    vstore = FAISS.load_local(
        folder_path="./notebooks/faiss_index",
        index_name= "index", 
        embeddings = embedding_model,
        allow_dangerous_deserialization=True,
    )

    faiss_kwargs = configuration.search_kwargs  #get default from config or define your own dict

    yield vstore.as_retriever(
        search_type  = "similarity",
        search_kwargs = faiss_kwargs
        )

@contextmanager
def make_retriever(
    config: RunnableConfig,
) -> Generator[VectorStoreRetriever, None, None]:
    """Create a retriever for the agent, based on the current configuration."""
    configuration = BaseConfiguration.from_runnable_config(config)
    embedding_model = make_text_encoder()

    match configuration.retriever_provider:
        
        case "faiss":
            with make_faiss_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case _:
            raise ValueError(
                "Unrecognized retriever_provider in configuration. "
                f"Expected one of: {', '.join(BaseConfiguration.__annotations__['retriever_provider'].__args__)}\n"
                f"Got: {configuration.retriever_provider}"
            )