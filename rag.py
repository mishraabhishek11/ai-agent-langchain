from model import model
from retriever import retriever

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


prompt = ChatPromptTemplate.from_template(
    """
Answer the question using only the provided context.

Context:
{context}

Question:
{question}
"""
)


def get_context(question):
    documents = retriever.invoke(question)

    return "\n\n".join(
        document.page_content
        for document in documents
    )


chain = (
    {
        "context": get_context,
        "question": lambda x: x
    }
    | prompt
    | model
    | StrOutputParser()
)


answer = chain.invoke(
    "What is MCP?"
)

print(answer)

