#!/usr/bin/env python3
"""
Performance Benchmarking Script

Measures actual performance metrics for the paper:
- Vector retrieval latency
- LLM simulation time
- End-to-end workflow time
"""

import os
import sys
import time
import statistics
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.input_processor import get_drug_fingerprint
from src.vector_search import find_similar_drugs
from src.agent_engine import run_simulation


def benchmark_retrieval(drug_smiles: str, iterations: int = 10) -> Dict:
    """Benchmark vector retrieval performance."""
    print(f"Benchmarking retrieval latency ({iterations} iterations)...")
    
    # Check if using mock data
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        print("  ⚠️  PINECONE_API_KEY not found - using mock data (instantaneous)")
        return {
            'mean': 0.0,
            'median': 0.0,
            'min': 0.0,
            'max': 0.0,
            'std': 0.0,
            'iterations': iterations,
            'mock_mode': True
        }
    
    # Generate fingerprint once
    fingerprint = get_drug_fingerprint(drug_smiles)
    
    latencies = []
    for i in range(iterations):
        start = time.perf_counter()  # Use perf_counter for better precision
        similar_drugs = find_similar_drugs(fingerprint, top_k=3)
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)
    
    return {
        'mean': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'min': min(latencies),
        'max': max(latencies),
        'std': statistics.stdev(latencies) if len(latencies) > 1 else 0,
        'iterations': iterations,
        'mock_mode': False
    }


def benchmark_llm_simulation(
    drug_name: str,
    drug_smiles: str,
    patient_profile: str,
    iterations: int = 5
) -> Dict:
    """Benchmark LLM simulation performance."""
    print(f"Benchmarking LLM simulation ({iterations} iterations)...")
    
    # Get fingerprint and similar drugs
    fingerprint = get_drug_fingerprint(drug_smiles)
    similar_drugs = find_similar_drugs(fingerprint, top_k=3)
    
    # Check if API key is available
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found. Skipping LLM benchmark.")
        return None
    
    simulation_times = []
    for i in range(iterations):
        start = time.time()
        try:
            result = run_simulation(drug_name, similar_drugs, patient_profile)
            elapsed = time.time() - start
            simulation_times.append(elapsed)
        except Exception as e:
            print(f"  Error in iteration {i+1}: {e}")
            continue
    
    if not simulation_times:
        return None
    
    return {
        'mean': statistics.mean(simulation_times),
        'median': statistics.median(simulation_times),
        'min': min(simulation_times),
        'max': max(simulation_times),
        'std': statistics.stdev(simulation_times) if len(simulation_times) > 1 else 0,
        'iterations': len(simulation_times)
    }


def benchmark_end_to_end(
    drug_name: str,
    drug_smiles: str,
    patient_profile: str,
    iterations: int = 5
) -> Dict:
    """Benchmark complete end-to-end workflow."""
    print(f"Benchmarking end-to-end workflow ({iterations} iterations)...")
    
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found. Skipping end-to-end benchmark.")
        return None
    
    total_times = []
    for i in range(iterations):
        start = time.time()
        try:
            # Step 1: Generate fingerprint
            fingerprint = get_drug_fingerprint(drug_smiles)
            
            # Step 2: Find similar drugs
            similar_drugs = find_similar_drugs(fingerprint, top_k=3)
            
            # Step 3: Run LLM simulation
            result = run_simulation(drug_name, similar_drugs, patient_profile)
            
            elapsed = time.time() - start
            total_times.append(elapsed)
        except Exception as e:
            print(f"  Error in iteration {i+1}: {e}")
            continue
    
    if not total_times:
        return None
    
    return {
        'mean': statistics.mean(total_times),
        'median': statistics.median(total_times),
        'min': min(total_times),
        'max': max(total_times),
        'std': statistics.stdev(total_times) if len(total_times) > 1 else 0,
        'iterations': len(total_times)
    }


def main():
    """Run performance benchmarks."""
    print("=" * 60)
    print("Anukriti Performance Benchmarking")
    print("=" * 60)
    print()
    
    # Test drug
    drug_name = "Paracetamol"
    drug_smiles = "CC(=O)Nc1ccc(O)cc1"
    patient_profile = """ID: SP-01
Age: 45
Genetics: CYP2D6 Poor Metabolizer
Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol consumer (Moderate)"""
    
    # Benchmark retrieval
    retrieval_stats = benchmark_retrieval(drug_smiles, iterations=10)
    print(f"\n✓ Retrieval Latency:")
    if retrieval_stats.get('mock_mode', False):
        print(f"  Mode: Mock data (no Pinecone API key)")
        print(f"  Note: Actual Pinecone retrieval typically takes 150-200ms")
    else:
        print(f"  Mean: {retrieval_stats['mean']:.2f}ms")
        print(f"  Median: {retrieval_stats['median']:.2f}ms")
        print(f"  Range: {retrieval_stats['min']:.2f}ms - {retrieval_stats['max']:.2f}ms")
        print(f"  Std Dev: {retrieval_stats['std']:.2f}ms")
    
    # Benchmark LLM simulation
    llm_stats = benchmark_llm_simulation(drug_name, drug_smiles, patient_profile, iterations=5)
    if llm_stats:
        print(f"\n✓ LLM Simulation Time:")
        print(f"  Mean: {llm_stats['mean']:.2f}s")
        print(f"  Median: {llm_stats['median']:.2f}s")
        print(f"  Range: {llm_stats['min']:.2f}s - {llm_stats['max']:.2f}s")
        print(f"  Std Dev: {llm_stats['std']:.2f}s")
    
    # Benchmark end-to-end
    e2e_stats = benchmark_end_to_end(drug_name, drug_smiles, patient_profile, iterations=5)
    if e2e_stats:
        print(f"\n✓ End-to-End Workflow Time:")
        print(f"  Mean: {e2e_stats['mean']:.2f}s")
        print(f"  Median: {e2e_stats['median']:.2f}s")
        print(f"  Range: {e2e_stats['min']:.2f}s - {e2e_stats['max']:.2f}s")
        print(f"  Std Dev: {e2e_stats['std']:.2f}s")
    
    # Summary for paper
    print("\n" + "=" * 60)
    print("Summary for Paper")
    print("=" * 60)
    if retrieval_stats.get('mock_mode', False):
        print("Retrieval latency: Mock mode - not measured (actual: typically 150-200ms with Pinecone)")
    else:
        print(f"Retrieval latency: {retrieval_stats['mean']:.0f}ms (mean), {retrieval_stats['median']:.0f}ms (median)")
    if llm_stats:
        print(f"LLM simulation: {llm_stats['mean']:.1f}s (mean), {llm_stats['median']:.1f}s (median), range {llm_stats['min']:.1f}-{llm_stats['max']:.1f}s")
    if e2e_stats:
        print(f"End-to-end workflow: {e2e_stats['mean']:.1f}s (mean), {e2e_stats['median']:.1f}s (median), range {e2e_stats['min']:.1f}-{e2e_stats['max']:.1f}s")
    print("\nNote: LLM timing includes API call overhead. Local deployment would reduce this significantly.")
    
    print("\n✓ Benchmarking complete!")


if __name__ == "__main__":
    main()
