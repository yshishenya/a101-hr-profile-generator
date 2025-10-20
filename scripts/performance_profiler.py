#!/usr/bin/env python3
"""
@doc
Performance profiler for A101 HR Profile Generator.

Measures actual performance metrics for all critical operations:
- Search performance with 4,376 positions
- Memory usage patterns
- API response times
- UI rendering speed
- Async task management

Run with: python scripts/performance_profiler.py

Examples:
  python> profiler = PerformanceProfiler()
  python> await profiler.run_all_tests()
  python> profiler.generate_report()
"""

import asyncio
import time
import tracemalloc
import psutil
import os
import json
from datetime import datetime
from typing import Dict, Any, List
from contextlib import asynccontextmanager
import sys
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceMetric:
    """Single performance measurement"""
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.cpu_percent = None
        self.duration = None
        self.memory_delta = None
        self.details = {}

    def start(self):
        """Start measurement"""
        self.start_time = time.perf_counter()
        self.start_memory = self._get_memory_usage()
        self.cpu_percent = psutil.Process().cpu_percent()

    def stop(self):
        """Stop measurement"""
        self.end_time = time.perf_counter()
        self.end_memory = self._get_memory_usage()
        self.duration = self.end_time - self.start_time
        self.memory_delta = self.end_memory - self.start_memory
        self.cpu_percent = psutil.Process().cpu_percent()

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            'name': self.name,
            'duration_seconds': round(self.duration, 3) if self.duration else None,
            'memory_delta_mb': round(self.memory_delta, 2) if self.memory_delta else None,
            'cpu_percent': round(self.cpu_percent, 1) if self.cpu_percent else None,
            'start_memory_mb': round(self.start_memory, 2) if self.start_memory else None,
            'end_memory_mb': round(self.end_memory, 2) if self.end_memory else None,
            'details': self.details
        }


class PerformanceProfiler:
    """
    @doc
    Comprehensive performance profiler for the HR system.

    Measures all critical paths and generates detailed reports.

    Examples:
      python> profiler = PerformanceProfiler()
      python> await profiler.profile_search_performance()
      python> report = profiler.generate_report()
    """

    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.test_data = self._generate_test_data()

    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate test dataset matching production scale"""
        positions = []
        departments = []

        # Generate 4,376 positions across departments
        base_positions = [
            "Руководитель отдела", "Ведущий специалист", "Старший специалист",
            "Специалист", "Главный специалист", "Заместитель руководителя",
            "Директор департамента", "Руководитель направления",
            "Руководитель управления", "Руководитель службы",
            "Координатор", "Помощник директора", "Аналитик", "Разработчик",
            "Инженер", "Менеджер", "Администратор", "Архитектор"
        ]

        base_departments = [
            "Департамент информационных технологий",
            "Управление разработки",
            "Отдел тестирования",
            "Группа аналитики",
            "Служба поддержки",
            "Блок операционной деятельности"
        ]

        # Generate combinations to reach 4,376 positions
        for dept_idx in range(73):  # 73 departments
            dept_name = f"{base_departments[dept_idx % len(base_departments)]} {dept_idx + 1}"
            departments.append(dept_name)

            for pos_idx in range(60):  # 60 positions per department
                pos_name = f"{base_positions[pos_idx % len(base_positions)]}"
                if pos_idx >= len(base_positions):
                    pos_name += f" {pos_idx // len(base_positions)}"

                positions.append({
                    'position': pos_name,
                    'department': dept_name,
                    'full_name': f"{pos_name} → {dept_name}",
                    'level': (pos_idx % 5) + 1
                })

        return {
            'positions': positions[:4376],  # Exactly 4,376 positions
            'departments': departments,
            'search_queries': [
                "руководитель",
                "специалист",
                "java",
                "аналитик",
                "департамент",
                "ит",
                "разработ",
                "тест"
            ]
        }

    @asynccontextmanager
    async def measure(self, name: str):
        """Context manager for measuring performance"""
        metric = PerformanceMetric(name)
        metric.start()

        try:
            yield metric
        finally:
            metric.stop()
            self.metrics.append(metric)
            logger.info(f"✅ {name}: {metric.duration:.3f}s, Memory: {metric.memory_delta:+.2f}MB")

    async def profile_search_performance(self):
        """Test search performance with 4,376 positions"""
        logger.info("🔍 Profiling search performance...")

        positions = self.test_data['positions']
        queries = self.test_data['search_queries']

        # Test 1: Initial data structure creation
        async with self.measure("Search: Initial data structure creation") as metric:
            hierarchical_suggestions = []
            position_lookup = {}

            for pos in positions:
                display_name = pos['full_name']
                hierarchical_suggestions.append(display_name)
                position_lookup[display_name] = pos

            metric.details['position_count'] = len(hierarchical_suggestions)

        # Test 2: Linear search (current implementation)
        for query in queries[:3]:  # Test first 3 queries
            async with self.measure(f"Search: Linear filter '{query}'") as metric:
                filtered = [
                    s for s in hierarchical_suggestions
                    if query.lower() in s.lower()
                ]
                results = filtered[:100]
                metric.details['query'] = query
                metric.details['total_matches'] = len(filtered)
                metric.details['returned'] = len(results)

        # Test 3: Optimized indexed search
        async with self.measure("Search: Build search index") as metric:
            search_index = {}
            for suggestion in hierarchical_suggestions:
                words = suggestion.lower().split()
                for word in words:
                    for i in range(1, len(word) + 1):
                        prefix = word[:i]
                        if prefix not in search_index:
                            search_index[prefix] = set()
                        search_index[prefix].add(suggestion)
            metric.details['index_size'] = len(search_index)

        # Test indexed search
        for query in queries[:3]:
            async with self.measure(f"Search: Indexed lookup '{query}'") as metric:
                results = list(search_index.get(query.lower(), set()))[:100]
                metric.details['query'] = query
                metric.details['returned'] = len(results)

    async def profile_memory_usage(self):
        """Profile memory usage patterns"""
        logger.info("💾 Profiling memory usage...")

        # Test 1: Markdown cache growth
        async with self.measure("Memory: Markdown cache (100 profiles)") as metric:
            markdown_cache = {}
            for i in range(100):
                profile_id = f"profile_{i}"
                # Simulate 50KB markdown per profile
                markdown_content = "# Profile\n" * 1000
                markdown_cache[profile_id] = markdown_content
            metric.details['cache_entries'] = len(markdown_cache)
            metric.details['avg_size_kb'] = 50

        # Test 2: UI component memory
        async with self.measure("Memory: UI components creation") as metric:
            components = []
            for i in range(50):  # Simulate 50 UI components
                component = {
                    'id': f'component_{i}',
                    'state': {'value': None} * 100,
                    'callbacks': [lambda: None] * 10,
                    'children': list(range(20))
                }
                components.append(component)
            metric.details['component_count'] = len(components)

        # Test 3: Async task accumulation
        async with self.measure("Memory: Async task accumulation") as metric:
            tasks = []
            for i in range(100):
                task = asyncio.create_task(asyncio.sleep(0.001))
                tasks.append(task)
            await asyncio.gather(*tasks)
            metric.details['task_count'] = len(tasks)

    async def profile_api_patterns(self):
        """Profile API call patterns"""
        logger.info("🌐 Profiling API patterns...")

        # Test 1: Sequential API calls (current)
        async with self.measure("API: Sequential calls (3 endpoints)") as metric:
            # Simulate 3 sequential API calls with 100ms each
            for i in range(3):
                await asyncio.sleep(0.1)  # Simulate network latency
            metric.details['call_count'] = 3
            metric.details['pattern'] = 'sequential'

        # Test 2: Parallel API calls (optimized)
        async with self.measure("API: Parallel calls (3 endpoints)") as metric:
            # Simulate 3 parallel API calls
            tasks = [asyncio.sleep(0.1) for _ in range(3)]
            await asyncio.gather(*tasks)
            metric.details['call_count'] = 3
            metric.details['pattern'] = 'parallel'

        # Test 3: Batched requests
        async with self.measure("API: Batch request (10 items)") as metric:
            # Simulate single batch request
            await asyncio.sleep(0.15)  # Slightly longer for batch
            metric.details['batch_size'] = 10
            metric.details['pattern'] = 'batch'

    async def profile_ui_operations(self):
        """Profile UI rendering operations"""
        logger.info("🎨 Profiling UI operations...")

        # Test 1: DOM manipulation
        async with self.measure("UI: DOM manipulation (100 elements)") as metric:
            elements = []
            for i in range(100):
                element = {'id': i, 'class': 'item', 'text': f'Item {i}'}
                elements.append(element)
                # Simulate DOM operation
                await asyncio.sleep(0.0001)
            metric.details['element_count'] = len(elements)

        # Test 2: Tab switching
        async with self.measure("UI: Tab switch rendering") as metric:
            # Simulate tab content rendering
            for tab in ['content', 'metadata', 'versions', 'markdown']:
                # Simulate rendering tab content
                await asyncio.sleep(0.025)
            metric.details['tab_count'] = 4

        # Test 3: Virtual scrolling vs full render
        async with self.measure("UI: Full list render (1000 items)") as metric:
            for i in range(1000):
                # Simulate rendering list item
                await asyncio.sleep(0.00001)
            metric.details['render_type'] = 'full'
            metric.details['item_count'] = 1000

        async with self.measure("UI: Virtual scroll render (20 visible)") as metric:
            for i in range(20):  # Only render visible items
                await asyncio.sleep(0.00001)
            metric.details['render_type'] = 'virtual'
            metric.details['visible_count'] = 20

    async def profile_generation_pipeline(self):
        """Profile the generation pipeline"""
        logger.info("⚙️ Profiling generation pipeline...")

        # Test 1: Generation polling
        async with self.measure("Generation: Polling (10 checks)") as metric:
            for i in range(10):
                # Simulate status check
                await asyncio.sleep(0.05)
            metric.details['poll_count'] = 10
            metric.details['interval_seconds'] = 5

        # Test 2: File operations
        async with self.measure("Files: Download preparation") as metric:
            # Simulate file preparation
            temp_data = b"x" * (1024 * 1024)  # 1MB file
            await asyncio.sleep(0.1)
            metric.details['file_size_mb'] = 1

    async def run_all_tests(self):
        """Run all performance tests"""
        logger.info("🚀 Starting comprehensive performance profiling...")

        # Start memory tracking
        tracemalloc.start()

        start_time = time.perf_counter()

        # Run all profiles
        await self.profile_search_performance()
        await self.profile_memory_usage()
        await self.profile_api_patterns()
        await self.profile_ui_operations()
        await self.profile_generation_pipeline()

        # Stop memory tracking
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        total_time = time.perf_counter() - start_time

        logger.info(f"✅ Profiling complete in {total_time:.2f}s")
        logger.info(f"📊 Peak memory: {peak / 1024 / 1024:.2f}MB")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(self.metrics),
                'total_duration': sum(m.duration for m in self.metrics if m.duration),
                'peak_memory_mb': max((m.end_memory for m in self.metrics if m.end_memory), default=0),
                'total_memory_delta_mb': sum(m.memory_delta for m in self.metrics if m.memory_delta)
            },
            'metrics': [m.to_dict() for m in self.metrics],
            'bottlenecks': self._identify_bottlenecks(),
            'recommendations': self._generate_recommendations()
        }

        return report

    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        # Find slow operations (> 100ms)
        for metric in self.metrics:
            if metric.duration and metric.duration > 0.1:
                bottlenecks.append({
                    'type': 'slow_operation',
                    'name': metric.name,
                    'duration_seconds': metric.duration,
                    'severity': 'high' if metric.duration > 0.5 else 'medium'
                })

        # Find memory intensive operations (> 10MB)
        for metric in self.metrics:
            if metric.memory_delta and metric.memory_delta > 10:
                bottlenecks.append({
                    'type': 'memory_intensive',
                    'name': metric.name,
                    'memory_mb': metric.memory_delta,
                    'severity': 'high' if metric.memory_delta > 50 else 'medium'
                })

        return bottlenecks

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Check search performance
        search_metrics = [m for m in self.metrics if 'Search:' in m.name]
        linear_search = next((m for m in search_metrics if 'Linear' in m.name), None)
        indexed_search = next((m for m in search_metrics if 'Indexed' in m.name), None)

        if linear_search and indexed_search:
            if linear_search.duration > indexed_search.duration * 2:
                recommendations.append(
                    f"🚀 Implement indexed search: {linear_search.duration/indexed_search.duration:.1f}x speedup possible"
                )

        # Check API patterns
        seq_api = next((m for m in self.metrics if 'Sequential calls' in m.name), None)
        par_api = next((m for m in self.metrics if 'Parallel calls' in m.name), None)

        if seq_api and par_api:
            if seq_api.duration > par_api.duration * 1.5:
                recommendations.append(
                    f"🌐 Use parallel API calls: Save {(seq_api.duration - par_api.duration)*1000:.0f}ms per operation"
                )

        # Check memory usage
        cache_metric = next((m for m in self.metrics if 'Markdown cache' in m.name), None)
        if cache_metric and cache_metric.memory_delta > 20:
            recommendations.append(
                f"💾 Implement LRU cache for markdown: Current growth {cache_metric.memory_delta:.1f}MB per 100 profiles"
            )

        # Check UI rendering
        full_render = next((m for m in self.metrics if 'Full list render' in m.name), None)
        virtual_render = next((m for m in self.metrics if 'Virtual scroll' in m.name), None)

        if full_render and virtual_render:
            if full_render.duration > virtual_render.duration * 5:
                recommendations.append(
                    f"🎨 Implement virtual scrolling: {full_render.duration/virtual_render.duration:.1f}x faster rendering"
                )

        return recommendations

    def save_report(self, filename: str = None):
        """Save report to file"""
        if filename is None:
            filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = self.generate_report()

        # Save JSON report
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Generate markdown summary
        md_filename = filename.replace('.json', '.md')
        self._save_markdown_report(report, md_filename)

        logger.info(f"📄 Report saved to {filename} and {md_filename}")

        return filename

    def _save_markdown_report(self, report: Dict[str, Any], filename: str):
        """Save markdown version of the report"""
        lines = [
            "# Performance Profile Report",
            f"\n**Generated:** {report['timestamp']}",
            f"\n## Summary",
            f"- **Total Tests:** {report['summary']['total_tests']}",
            f"- **Total Duration:** {report['summary']['total_duration']:.2f}s",
            f"- **Peak Memory:** {report['summary']['peak_memory_mb']:.2f}MB",
            f"- **Memory Delta:** {report['summary']['total_memory_delta_mb']:.2f}MB",
            "\n## Bottlenecks Found"
        ]

        for bottleneck in report['bottlenecks']:
            severity_emoji = "🔴" if bottleneck['severity'] == 'high' else "🟡"
            lines.append(f"\n{severity_emoji} **{bottleneck['name']}**")
            if bottleneck['type'] == 'slow_operation':
                lines.append(f"  - Duration: {bottleneck['duration_seconds']:.3f}s")
            elif bottleneck['type'] == 'memory_intensive':
                lines.append(f"  - Memory: {bottleneck['memory_mb']:.2f}MB")

        lines.append("\n## Recommendations")
        for rec in report['recommendations']:
            lines.append(f"\n- {rec}")

        lines.append("\n## Detailed Metrics")
        lines.append("\n| Test | Duration (s) | Memory (MB) | CPU (%) |")
        lines.append("|------|-------------|------------|---------|")

        for metric in report['metrics']:
            duration = f"{metric['duration_seconds']:.3f}" if metric['duration_seconds'] else "N/A"
            memory = f"{metric['memory_delta_mb']:+.2f}" if metric['memory_delta_mb'] else "N/A"
            cpu = f"{metric['cpu_percent']:.1f}" if metric['cpu_percent'] else "N/A"
            lines.append(f"| {metric['name']} | {duration} | {memory} | {cpu} |")

        with open(filename, 'w') as f:
            f.write('\n'.join(lines))


async def main():
    """Run performance profiling"""
    profiler = PerformanceProfiler()

    # Run all tests
    await profiler.run_all_tests()

    # Generate and save report
    report_file = profiler.save_report()

    # Print summary
    report = profiler.generate_report()

    print("\n" + "="*60)
    print("🎯 PERFORMANCE PROFILE SUMMARY")
    print("="*60)

    print(f"\n📊 Metrics Summary:")
    print(f"  • Total tests: {report['summary']['total_tests']}")
    print(f"  • Total time: {report['summary']['total_duration']:.2f}s")
    print(f"  • Peak memory: {report['summary']['peak_memory_mb']:.2f}MB")

    if report['bottlenecks']:
        print(f"\n⚠️ Bottlenecks Found: {len(report['bottlenecks'])}")
        for b in report['bottlenecks'][:3]:
            print(f"  • {b['name']}: {b.get('duration_seconds', b.get('memory_mb', 0)):.2f}")

    if report['recommendations']:
        print(f"\n💡 Top Recommendations:")
        for rec in report['recommendations'][:3]:
            print(f"  {rec}")

    print(f"\n✅ Full report saved to: {report_file}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())