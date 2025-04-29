"""
Script to invoke the retrieval graph for answering questions.
"""
import asyncio
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from dataclasses import asdict
from retrieval_graph.configuration import AgentConfiguration
from retrieval_graph.graph import graph
# import os
# from dotenv import load_dotenv, find_dotenv

# load_dotenv(find_dotenv())
# OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]

async def main(question: str) -> None:
    # Create a configuration with your preferred models
    config = AgentConfiguration(
        query_model="azure-openai/gpt-4o-mini",  
        response_model="azure-openai/gpt-4o-mini", 
        thread_id=1,
    )
    
    # Prepare input for the graph 
    input_data = {
        "messages": [HumanMessage(content=question)]
    }
    
    # Invoke the graph
    # Convert the configuration to a dictionary
    # langgraph library expects the config parameter to be a dictionary-like object, not an instance of a custom class like AgentConfiguration

    config_dict = asdict(config)
    result = await graph.ainvoke(input_data, {"configurable": config_dict }, 
                                #  debug = True,
                                 )

    # Print the result
    print("\nQuestion:", question)
    print("\nResponse:", result["messages"][-1].content)


async def run_interactive_session():
    """Run an interactive session that properly handles the event loop."""
    while True:
        question = input("Enter your question (or 'exit' to quit): ")
        if question.lower() in ['exit', 'bye']:
            print("Exiting...")
            break

        # Call the main function with the user input
        await main(question)

if __name__ == "__main__":
    # Use a single event loop for the entire session
    asyncio.run(run_interactive_session())