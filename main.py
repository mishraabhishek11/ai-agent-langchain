import asyncio

from langchain.agents import create_agent
from langchain_core.tools import tool

from model import model
from mcp_tools import client
from retriever import retriever


@tool
def search_knowledge(question: str) -> str:
    """Search the local knowledge base and return relevant information."""

    documents = retriever.invoke(question)

    return "\n\n".join(
        document.page_content
        for document in documents
    )


async def main():
    mcp_tools = await client.get_tools()

    tools = mcp_tools + [
        search_knowledge
    ]

    agent = create_agent(
        model=model,
        tools=tools
    )

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "According to my notes, what is MCP?"
                }
            ]
        }
    )

    print("\nFINAL ANSWER")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())

