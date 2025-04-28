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


# def make_text_encoder(model: str) -> Embeddings:
#     """Connect to the configured text encoder."""
#     provider, model = model.split("/", maxsplit=1)
#     match provider:
#         case "openai":
#             from langchain_openai import OpenAIEmbeddings

#             return OpenAIEmbeddings(model=model)
#         case "cohere":
#             from langchain_cohere import CohereEmbeddings

#             return CohereEmbeddings(model=model)  # type: ignore
#         case _:
#             raise ValueError(f"Unsupported embedding provider: {provider}")

def make_text_encoder() -> Embeddings:
    """Connect to the configured text encoder."""

    from langchain_openai import AzureOpenAIEmbeddings
    model = "text-embedding-ada-002" 
    openai_api_version = os.environ["OPENAI_API_VERSION"]
    
    embedding_function = AzureOpenAIEmbeddings(
        openai_api_key = os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint = os.environ["AZURE_EMBEDDINGS_ENDPOINT"],
        model = model,
        chunk_size = 16,
        max_retries = 3,
        retry_interval = 10,
        max_tokens = 8191,
        show_progress_bar = True,
    )
    return embedding_function



## Retriever constructors

@contextmanager
def make_elastic_retriever(
    configuration: BaseConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific elastic index."""
    from langchain_elasticsearch import ElasticsearchStore

    connection_options = {}
    if configuration.retriever_provider == "elastic-local":
        connection_options = {
            "es_user": os.environ["ELASTICSEARCH_USER"],
            "es_password": os.environ["ELASTICSEARCH_PASSWORD"],
        }

    else:
        connection_options = {"es_api_key": os.environ["ELASTICSEARCH_API_KEY"]}

    vstore = ElasticsearchStore(
        **connection_options,  # type: ignore
        es_url=os.environ["ELASTICSEARCH_URL"],
        index_name="langchain_index",
        embedding=embedding_model,
    )

    yield vstore.as_retriever(search_kwargs=configuration.search_kwargs)


@contextmanager
def make_pinecone_retriever(
    configuration: BaseConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific pinecone index."""
    from langchain_pinecone import PineconeVectorStore

    vstore = PineconeVectorStore.from_existing_index(
        os.environ["PINECONE_INDEX_NAME"], embedding=embedding_model
    )
    yield vstore.as_retriever(search_kwargs=configuration.search_kwargs)


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

    from langchain_community.vecctorstores import FAISS
    import faiss
    from langchain_community.docstore import InMemoryDocstore

    # index = faiss.IndexFlatIP(1536)
    # vstore = FAISS(
    #     index=index,
    #     embedding_function=embedding_model,
    #     index_path="../data/faiss_index",
    #     docstore = InMemoryDocstore(), 
    #     index_to_docstore_id = {}, 
    #     distance_strategy = "DistanceStrategy.MAX_INNER_PRODUCT", 
    # )

    # vstore.add_documents(data)
    # vstore.save_local("faiss_index")

    vstore = FAISS.load_local(
        os.path.join(os.path.dirname(__file__), "../data/faiss_index"),
        embedding_model,
        allow_dangerous_deserialization=True,
    )

    yield vstore.as_retriever(search_kwargs=configuration.search_kwargs)

@contextmanager
def make_retriever(
    config: RunnableConfig,
) -> Generator[VectorStoreRetriever, None, None]:
    """Create a retriever for the agent, based on the current configuration."""
    configuration = BaseConfiguration.from_runnable_config(config)
    embedding_model = make_text_encoder()

    match configuration.retriever_provider:
        # case "elastic" | "elastic-local":
        #     with make_elastic_retriever(configuration, embedding_model) as retriever:
        #         yield retriever

        # case "pinecone":
        #     with make_pinecone_retriever(configuration, embedding_model) as retriever:
        #         yield retriever

        # case "mongodb":
        #     with make_mongodb_retriever(configuration, embedding_model) as retriever:
        #         yield retriever
        
        case "faiss":
            with make_faiss_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case _:
            raise ValueError(
                "Unrecognized retriever_provider in configuration. "
                f"Expected one of: {', '.join(BaseConfiguration.__annotations__['retriever_provider'].__args__)}\n"
                f"Got: {configuration.retriever_provider}"
            )

# @contextmanager
# def make_retriever(
#     config: RunnableConfig,
# ) -> Generator[VectorStoreRetriever, None, None]:
#     """Create a retriever for the agent, based on the current configuration."""
#     configuration = BaseConfiguration.from_runnable_config(config)
#     embedding_model = make_text_encoder(configuration.embedding_model)

#     provider = configuration.retriever_provider

#     if provider in ("elastic", "elastic-local"):
#         with make_elastic_retriever(configuration, embedding_model) as retriever:
#             yield retriever
#     elif provider == "pinecone":
#         with make_pinecone_retriever(configuration, embedding_model) as retriever:
#             yield retriever
#     elif provider == "mongodb":
#         with make_mongodb_retriever(configuration, embedding_model) as retriever:
#             yield retriever
#     else:
#         expected = ', '.join(BaseConfiguration.__annotations__['retriever_provider'].__args__)
#         raise ValueError(
#             "Unrecognized retriever_provider in configuration. "
#             f"Expected one of: {expected}\n"
#             f"Got: {provider}"
#         ) 