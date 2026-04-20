"""
Example: Basic RAG Pipeline

Demonstrates how to use the RAG framework for a simple
retrieval-augmented generation pipeline.
"""

import asyncio
from integrations.rag import (
    KnowledgeBase,
    RetrievalConfig
)


async def basic_rag_example():
    """Basic RAG pipeline example."""
    
    # Initialize knowledge base
    kb = KnowledgeBase(
        name="demo_knowledge",
        vector_db="chromadb",  # Local-first for demo
        vector_db_config={
            "persist_directory": "./demo_chromadb"
        }
    )
    
    await kb.initialize()
    print("✓ Knowledge base initialized")
    
    # Add sample documents
    documents = [
        {
            "content": "RAG (Retrieval-Augmented Generation) combines retrieval systems with LLMs to provide more accurate and contextual responses.",
            "metadata": {"topic": "rag", "source": "guide"}
        },
        {
            "content": "Vector databases store embeddings and enable fast similarity search. Examples include Milvus, Pinecone, and ChromaDB.",
            "metadata": {"topic": "vector_db", "source": "guide"}
        },
        {
            "content": "Embedding models convert text into dense vectors. Popular models include OpenAI's text-embedding-ada-002 and open-source alternatives like sentence-transformers.",
            "metadata": {"topic": "embeddings", "source": "guide"}
        }
    ]
    
    for doc in documents:
        doc_id = await kb.add_text(doc["content"], doc["metadata"])
        print(f"✓ Added document: {doc_id}")
    
    # Search the knowledge base
    query = "What is RAG?"
    results = await kb.search(query, top_k=3)
    
    print(f"\nQuery: {query}")
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result.score:.4f}")
        print(f"   Content: {result.content[:100]}...")
        print(f"   Source: {result.metadata.get('source', 'unknown')}")
        print()
    
    # Cleanup
    await kb.close()
    print("✓ Knowledge base closed")


async def rag_with_filtering():
    """RAG with metadata filtering."""
    
    kb = KnowledgeBase(
        name="filtered_demo",
        vector_db="chromadb"
    )
    
    await kb.initialize()
    
    # Add categorized documents
    categories = {
        "tech": [
            "Python is a versatile programming language for AI.",
            "JavaScript is widely used for web development.",
        ],
        "science": [
            "Photosynthesis converts sunlight to energy.",
            "Newton's laws describe motion and forces.",
        ],
        "history": [
            "The Renaissance began in Italy.",
            "The Industrial Revolution changed manufacturing.",
        ]
    }
    
    for category, texts in categories.items():
        for text in texts:
            await kb.add_text(text, {"category": category})
    
    # Search within category
    query = "What programming language for AI?"
    results = await kb.search(
        query,
        top_k=5,
        filter={"category": "tech"}
    )
    
    print(f"Query: {query}")
    print(f"Filtered to 'tech' category:")
    for result in results:
        print(f"  - {result.content}")
    
    await kb.close()


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Basic RAG Example")
    print("=" * 60)
    await basic_rag_example()
    
    print("\n" + "=" * 60)
    print("RAG with Filtering Example")
    print("=" * 60)
    await rag_with_filtering()


if __name__ == "__main__":
    asyncio.run(main())
