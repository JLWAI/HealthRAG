"""
Model Comparison Test Suite for HealthRAG

Tests different local LLM models on health/fitness consulting tasks:
- Qwen2.5-Coder:14B
- Llama 3.1:8B
- MLX Llama 3.1:70B (4-bit quantized)

Evaluates:
1. Response quality for fitness questions
2. Accuracy with RAG-retrieved information
3. Response time
4. Reasoning capabilities
5. Instruction following
"""

import time
import json
from typing import Dict, List, Tuple
import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag_system import HealthRAG


# Test queries representing typical user interactions
TEST_QUERIES = [
    {
        "category": "nutrition_calculation",
        "query": "I'm a 35-year-old male, 6 feet tall, 185 lbs, moderately active. Calculate my TDEE and recommend macros for a cut.",
        "evaluation_keywords": ["TDEE", "calories", "protein", "carbs", "fats", "deficit", "cut"],
        "requires_reasoning": True
    },
    {
        "category": "program_design",
        "query": "Design a 4-day upper/lower split for intermediate lifter focused on hypertrophy. I have access to a full gym.",
        "evaluation_keywords": ["upper", "lower", "4-day", "hypertrophy", "sets", "reps", "exercises"],
        "requires_reasoning": True
    },
    {
        "category": "exercise_selection",
        "query": "What are the best exercises for building chest mass? Rank them by effectiveness.",
        "evaluation_keywords": ["bench press", "dumbbell", "chest", "hypertrophy", "effective"],
        "requires_reasoning": False
    },
    {
        "category": "nutrition_science",
        "query": "Explain the role of protein synthesis in muscle growth and how meal timing affects it.",
        "evaluation_keywords": ["protein synthesis", "muscle", "amino acids", "mTOR", "timing"],
        "requires_reasoning": False
    },
    {
        "category": "progressive_overload",
        "query": "I've been benching 225 for 8 reps for 3 weeks. How should I progress to avoid plateau?",
        "evaluation_keywords": ["progressive overload", "increase", "weight", "reps", "volume", "intensity"],
        "requires_reasoning": True
    }
]


def evaluate_response(response: str, keywords: List[str]) -> float:
    """
    Score response based on keyword presence and quality.
    Returns score 0-1.
    """
    if not response or len(response) < 50:
        return 0.0

    # Keyword coverage (0-0.5)
    keyword_score = sum(1 for kw in keywords if kw.lower() in response.lower()) / len(keywords) * 0.5

    # Length appropriateness (0-0.25)
    length_score = 0.25
    if len(response) < 100:
        length_score *= 0.5
    elif len(response) > 2000:
        length_score *= 0.7

    # Structure score (0-0.25)
    structure_score = 0.25
    if response.count('\n') < 2:  # Poor formatting
        structure_score *= 0.5
    if any(indicator in response for indicator in ['**', '###', '1.', '2.', '-']):  # Good formatting
        structure_score = 0.25

    return keyword_score + length_score + structure_score


def evaluate_model(model_name: str, backend: str, test_queries: List[Dict]) -> Dict:
    """
    Test a specific model configuration.

    Args:
        model_name: Name of the model to test
        backend: 'ollama' or 'mlx'
        test_queries: List of test queries

    Returns:
        Results dictionary with scores and timing
    """
    print(f"\n{'='*60}")
    print(f"Testing: {model_name} ({backend})")
    print(f"{'='*60}\n")

    try:
        # Initialize RAG system
        print(f"Initializing {backend} backend with {model_name}...")
        rag = HealthRAG(backend=backend)

        if backend == "ollama":
            rag.llm.switch_model(model_name)
        elif backend == "mlx":
            rag.llm.switch_model(model_name)

        print(f"✅ Model loaded successfully\n")

        results = {
            "model": model_name,
            "backend": backend,
            "queries": [],
            "total_time": 0,
            "avg_score": 0,
            "avg_response_time": 0
        }

        total_score = 0

        for i, test in enumerate(test_queries, 1):
            print(f"\n[Query {i}/{len(test_queries)}] Category: {test['category']}")
            print(f"Q: {test['query'][:80]}...")

            # Query the model
            start_time = time.time()
            response, response_time = rag.query(test['query'])
            elapsed = time.time() - start_time

            # Evaluate response
            score = evaluate_response(response, test['evaluation_keywords'])
            total_score += score

            print(f"⏱️  Response time: {response_time:.1f}s")
            print(f"📊 Score: {score:.2f}/1.00")
            print(f"📝 Response length: {len(response)} chars")

            results['queries'].append({
                "query": test['query'],
                "category": test['category'],
                "response_time": response_time,
                "score": score,
                "response_length": len(response),
                "keywords_found": sum(1 for kw in test['evaluation_keywords']
                                     if kw.lower() in response.lower())
            })

            results['total_time'] += response_time

        results['avg_score'] = total_score / len(test_queries)
        results['avg_response_time'] = results['total_time'] / len(test_queries)

        print(f"\n{'='*60}")
        print(f"📊 RESULTS FOR {model_name}")
        print(f"{'='*60}")
        print(f"Average Score: {results['avg_score']:.2f}/1.00")
        print(f"Average Response Time: {results['avg_response_time']:.1f}s")
        print(f"Total Time: {results['total_time']:.1f}s")
        print(f"{'='*60}\n")

        return results

    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        return {
            "model": model_name,
            "backend": backend,
            "error": str(e)
        }


def main():
    """Run comprehensive model comparison."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         HealthRAG Model Comparison Test Suite               ║
    ║                                                              ║
    ║  Testing local models for health/fitness consulting          ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Models to test
    models_to_test = [
        {"name": "llama3.1:8b", "backend": "ollama"},
        {"name": "qwen2.5-coder:14b", "backend": "ollama"},
        {"name": "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit", "backend": "mlx"},
    ]

    all_results = []

    for model_config in models_to_test:
        result = evaluate_model(
            model_config["name"],
            model_config["backend"],
            TEST_QUERIES
        )
        all_results.append(result)

        # Short pause between model tests
        time.sleep(2)

    # Generate comparison report
    print("\n\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                   COMPARISON SUMMARY                         ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # Sort by average score
    valid_results = [r for r in all_results if 'error' not in r]
    valid_results.sort(key=lambda x: x['avg_score'], reverse=True)

    print(f"{'Rank':<6} {'Model':<45} {'Avg Score':<12} {'Avg Time':<12}")
    print("-" * 75)

    for i, result in enumerate(valid_results, 1):
        model_display = f"{result['model']} ({result['backend']})"
        print(f"{i:<6} {model_display:<45} {result['avg_score']:.2f}/1.00   {result['avg_response_time']:.1f}s")

    # Recommendation
    if valid_results:
        best = valid_results[0]
        print(f"\n🏆 RECOMMENDED MODEL: {best['model']} ({best['backend']})")
        print(f"   - Best average score: {best['avg_score']:.2f}/1.00")
        print(f"   - Average response time: {best['avg_response_time']:.1f}s")

        # Find fastest model
        fastest = min(valid_results, key=lambda x: x['avg_response_time'])
        if fastest['model'] != best['model']:
            print(f"\n⚡ FASTEST MODEL: {fastest['model']} ({fastest['backend']})")
            print(f"   - Average response time: {fastest['avg_response_time']:.1f}s")
            print(f"   - Average score: {fastest['avg_score']:.2f}/1.00")

    # Save results to file
    output_file = "model_comparison_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n💾 Full results saved to: {output_file}")

    return all_results


if __name__ == "__main__":
    main()


@pytest.mark.skipif(
    os.getenv("ENABLE_MODEL_COMPARISON") != "1",
    reason="Requires local LLM backends (Ollama/MLX); disabled by default."
)
def test_model_comparison_suite():
    """Optional end-to-end model comparison, gated behind an environment flag."""
    main()
