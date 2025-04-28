"""
Script to invoke the retrieval graph for answering questions.
"""
import asyncio
from typing import Dict, Any
from langchain_core.messages import HumanMessage

from retrieval_graph.configuration import AgentConfiguration
from retrieval_graph.graph import graph
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]

print("OPENAI_API_VERSION::", OPENAI_API_VERSION)

async def main():
    # Create a configuration with your preferred models
    config = AgentConfiguration(
        query_model="azure-openai/gpt-4o-mini",  
        response_model="azure-openai/gpt-4o-mini", 
    )
    
    # Question
    question = "what are top langchain's functionalities?"
    
    # Prepare input for the graph 
    input_data = {
        "messages": [HumanMessage(content=question)]
    }
    
    # Invoke the graph
    result = await graph.ainvoke(input_data, {"configurable": {"config": config}})
    
    # Print the result
    print("\nQuestion:", question)
    print("\nResponse:", result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())