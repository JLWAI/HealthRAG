"""
Performance Utilities for HealthRAG

Provides timing decorators, logging, and caching utilities to measure
and optimize application performance.

Author: Claude (Anthropic)
Date: November 2025
"""

import time
import functools
import logging
from typing import Callable, Any
from datetime import datetime

# Configure performance logger
perf_logger = logging.getLogger('healthrag.performance')
perf_logger.setLevel(logging.INFO)

# Create file handler if not exists
if not perf_logger.handlers:
    handler = logging.FileHandler('data/performance.log')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    perf_logger.addHandler(handler)


def timing_decorator(threshold_ms: float = 1000):
    """
    Decorator to measure function execution time and log slow operations.

    Args:
        threshold_ms: Log warning if execution exceeds this (default 1000ms)

    Usage:
        @timing_decorator(threshold_ms=500)
        def slow_function():
            time.sleep(1)
            return "done"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000

            func_name = f"{func.__module__}.{func.__name__}"

            if elapsed_ms > threshold_ms:
                perf_logger.warning(
                    f"SLOW: {func_name} took {elapsed_ms:.1f}ms (threshold: {threshold_ms}ms)"
                )
            else:
                perf_logger.info(
                    f"{func_name} took {elapsed_ms:.1f}ms"
                )

            return result
        return wrapper
    return decorator


class PerformanceTimer:
    """
    Context manager for timing code blocks.

    Usage:
        with PerformanceTimer("database_query") as timer:
            results = db.query()
        print(f"Query took {timer.elapsed_ms}ms")
    """

    def __init__(self, operation_name: str, threshold_ms: float = 1000):
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time = None
        self.elapsed_ms = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = (time.time() - self.start_time) * 1000

        if self.elapsed_ms > self.threshold_ms:
            perf_logger.warning(
                f"SLOW: {self.operation_name} took {self.elapsed_ms:.1f}ms "
                f"(threshold: {self.threshold_ms}ms)"
            )
        else:
            perf_logger.info(
                f"{self.operation_name} took {self.elapsed_ms:.1f}ms"
            )


def log_query_performance(query_name: str, row_count: int, elapsed_ms: float):
    """
    Log database query performance.

    Args:
        query_name: Descriptive query name
        row_count: Number of rows returned
        elapsed_ms: Execution time in milliseconds
    """
    perf_logger.info(
        f"QUERY: {query_name} returned {row_count} rows in {elapsed_ms:.1f}ms"
    )

    if elapsed_ms > 1000:
        perf_logger.warning(
            f"SLOW QUERY: {query_name} took {elapsed_ms:.1f}ms - consider optimization"
        )


def get_performance_summary(log_file: str = 'data/performance.log',
                           last_n_lines: int = 100) -> dict:
    """
    Get summary of recent performance metrics.

    Args:
        log_file: Path to performance log file
        last_n_lines: Number of recent log lines to analyze

    Returns:
        Dictionary with performance statistics
    """
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()[-last_n_lines:]

        slow_operations = []
        total_operations = 0

        for line in lines:
            if 'SLOW:' in line:
                slow_operations.append(line.strip())
            total_operations += 1

        return {
            'total_operations': total_operations,
            'slow_operations_count': len(slow_operations),
            'slow_operations': slow_operations,
            'slow_percentage': (len(slow_operations) / total_operations * 100)
                              if total_operations > 0 else 0
        }

    except FileNotFoundError:
        return {
            'total_operations': 0,
            'slow_operations_count': 0,
            'slow_operations': [],
            'slow_percentage': 0
        }
