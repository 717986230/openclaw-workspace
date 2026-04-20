"""
Example: Vector Database Comparison

Compare different vector databases for RAG workloads.
"""

import asyncio
import time
from typing import List
import numpy as np


async def benchmark_vector_db(db_type: str, config: dict, num_vectors: int = 10000):
    """
    Benchmark a vector database.
    
    Args:
        db_type: Database type (milvus, chromadb, etc.)
        config: Database configuration
        num_vectors: Number of vectors to test
    """
    from integrations.rag.vector_db import get_vector_db
    
    print(f"\n{'='*60}")
    print(f"Benchmarking: {db_type.upper()}")
    print(f"{'='*60}")
    
    # Initialize
    db = get_vector_db(db_type, **config)
    
    # Connect
    start = time.time()
    await db.connect()
    connect_time = time.time() - start
    print(f"✓ Connected in {connect_time:.3f}s")
    
    # Create collection
    collection_name = f"benchmark_{db_type}"
    dimension = 1536
    
    if await db.collection_exists(collection_name):
        await db.drop_collection(collection_name)
    
    start = time.time()
    await db.create_collection(
        name=collection_name,
        dimension=dimension,
        metric="cosine"
    )
    create_time = time.time() - start
    print(f"✓ Collection created in {create_time:.3f}s")
    
    # Generate test vectors
    print(f"\nGenerating {num_vectors} test vectors...")
    vectors = [np.random.rand(dimension).astype(np.float32) for _ in range(num_vectors)]
    metadatas = [{"id": i, "batch": i // 1000} for i in range(num_vectors)]
    
    # Insert benchmark
    print(f"\nInserting {num_vectors} vectors...")
    start = time.time()
    ids = await db.insert(
        collection=collection_name,
        vectors=vectors,
        metadatas=metadatas,
        batch_size=500
    )
    insert_time = time.time() - start
    insert_rate = num_vectors / insert_time
    print(f"✓ Inserted in {insert_time:.3f}s ({insert_rate:.0f} vectors/sec)")
    
    # Search benchmark
    print(f"\nRunning search queries...")
    num_queries = 100
    query_vectors = [np.random.rand(dimension).astype(np.float32) for _ in range(num_queries)]
    
    latencies = []
    for i, query in enumerate(query_vectors):
        start = time.time()
        results = await db.search(
            collection=collection_name,
            query_vector=query,
            top_k=10
        )
        latency = time.time() - start
        latencies.append(latency)
        
        if i == 0:
            print(f"  Sample result count: {len(results)}")
    
    avg_latency = np.mean(latencies) * 1000
    p50_latency = np.percentile(latencies, 50) * 1000
    p95_latency = np.percentile(latencies, 95) * 1000
    p99_latency = np.percentile(latencies, 99) * 1000
    
    print(f"\nSearch Latency ({num_queries} queries):")
    print(f"  Average: {avg_latency:.2f}ms")
    print(f"  P50: {p50_latency:.2f}ms")
    print(f"  P95: {p95_latency:.2f}ms")
    print(f"  P99: {p99_latency:.2f}ms")
    
    # Get count
    count = await db.count(collection_name)
    print(f"\nTotal vectors: {count}")
    
    # Cleanup
    await db.drop_collection(collection_name)
    await db.disconnect()
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  Insert: {insert_rate:.0f} vectors/sec")
    print(f"  Search: {avg_latency:.2f}ms avg")
    print(f"{'='*60}")
    
    return {
        "db_type": db_type,
        "insert_rate": insert_rate,
        "avg_latency_ms": avg_latency,
        "p50_latency_ms": p50_latency,
        "p95_latency_ms": p95_latency,
        "p99_latency_ms": p99_latency
    }


async def compare_databases():
    """Compare multiple vector databases."""
    
    configs = {
        "chromadb": {
            "persist_directory": "./benchmark_chromadb"
        },
        # Add other databases when available:
        # "milvus": {"host": "localhost", "port": 19530},
        # "pinecone": {"api_key": "...", "environment": "..."},
    }
    
    results = []
    
    for db_type, config in configs.items():
        try:
            result = await benchmark_vector_db(db_type, config, num_vectors=5000)
            results.append(result)
        except Exception as e:
            print(f"✗ Failed to benchmark {db_type}: {e}")
    
    # Print comparison
    if len(results) > 1:
        print("\n" + "=" * 60)
        print("COMPARISON")
        print("=" * 60)
        print(f"{'Database':<15} {'Insert (v/s)':<15} {'Search (ms)':<15}")
        print("-" * 45)
        for r in results:
            print(f"{r['db_type']:<15} {r['insert_rate']:<15.0f} {r['avg_latency_ms']:<15.2f}")


if __name__ == "__main__":
    asyncio.run(compare_databases())
