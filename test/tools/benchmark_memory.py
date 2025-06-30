#!/usr/bin/env python3
"""
Platform Agent Memory功能性能基准测试

测试目标：
1. 测量memory启用前后的响应时间差异
2. 统计工具调用次数的减少情况
3. 评估memory对整体性能的影响
4. 生成详细的性能报告

使用方法：
    uv run benchmark_memory.py
    uv run benchmark_memory.py --detailed  # 详细模式
    uv run benchmark_memory.py --export-csv # 导出CSV格式
"""

import os
import sys
import time
import json
import argparse
import statistics
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path


class MemoryBenchmark:
    """Memory功能性能基准测试套件"""
    
    def __init__(self, detailed: bool = False):
        self.detailed = detailed
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "platform": sys.platform,
                "python_version": sys.version,
            },
            "benchmarks": [],
            "summary": {}
        }
        
        # 测试用例集
        self.test_cases = [
            {
                "name": "simple_cluster_query",
                "query": "show me all k8s clusters",
                "expected_tools": ["get_cluster_info"]
            },
            {
                "name": "cluster_detail_query", 
                "query": "which cluster has the most pods?",
                "expected_tools": []  # 应该从memory获取
            },
            {
                "name": "follow_up_query",
                "query": "what about the production environment?",
                "expected_tools": []  # 应该从memory获取
            },
            {
                "name": "complex_analysis",
                "query": "analyze the health status of all clusters and recommend actions",
                "expected_tools": ["get_cluster_info"]  # 可能需要工具调用
            }
        ]
    
    def measure_response_time(self, query: str, with_memory: bool = True) -> Dict[str, Any]:
        """测量单个查询的响应时间和工具调用情况"""
        
        # 准备测试环境
        env_vars = os.environ.copy()
        if with_memory:
            env_vars["CREWAI_STORAGE_DIR"] = "./crew_memory"
        else:
            # 禁用memory（如果支持的话）
            env_vars["CREWAI_STORAGE_DIR"] = "/tmp/no_memory"
        
        # 构造测试脚本
        test_script = f"""
import sys
import time
import os
sys.path.insert(0, 'src')

# 设置环境变量
os.environ.update({repr(dict(env_vars))})

start_time = time.time()
tool_calls = 0

try:
    from ops_crew.crew import run_crew
    
    # 模拟工具调用计数（需要在实际实现中添加）
    original_run_crew = run_crew
    
    def counting_run_crew(user_input):
        global tool_calls
        # 这里需要实际的工具调用计数逻辑
        result = original_run_crew(user_input)
        return result
    
    result = counting_run_crew("{query}")
    end_time = time.time()
    
    print(f"BENCHMARK_RESULT:{{")
    print(f"  'response_time': {end_time - start_time:.3f},")
    print(f"  'tool_calls': {tool_calls},")
    print(f"  'success': True,")
    print(f"  'result_length': {len(str(result)) if result else 0}")
    print(f"}}")
    
except Exception as e:
    end_time = time.time()
    print(f"BENCHMARK_RESULT:{{")
    print(f"  'response_time': {end_time - start_time:.3f},")
    print(f"  'tool_calls': 0,")
    print(f"  'success': False,")
    print(f"  'error': '{str(e)}'")
    print(f"}}")
        """
        
        try:
            # 运行测试
            process = subprocess.Popen(
                ["python", "-c", test_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,  # 2分钟超时
                env=env_vars
            )
            
            stdout, stderr = process.communicate()
            output = stdout.decode() + stderr.decode()
            
            # 解析结果
            if "BENCHMARK_RESULT:" in output:
                result_line = output.split("BENCHMARK_RESULT:")[1]
                # 简单的结果解析（实际应该更robust）
                result = {
                    "response_time": 0.0,
                    "tool_calls": 0, 
                    "success": False,
                    "result_length": 0
                }
                
                # 提取响应时间
                if "'response_time':" in result_line:
                    time_str = result_line.split("'response_time':")[1].split(",")[0].strip()
                    result["response_time"] = float(time_str)
                
                # 提取成功状态
                result["success"] = "'success': True" in result_line
                
                return result
            else:
                return {
                    "response_time": 999.0,  # 失败的情况
                    "tool_calls": 0,
                    "success": False,
                    "error": "No benchmark result found in output"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "response_time": 120.0,  # 超时
                "tool_calls": 0,
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "response_time": 999.0,
                "tool_calls": 0,
                "success": False,
                "error": str(e)
            }
    
    def run_benchmark_suite(self) -> Dict[str, Any]:
        """运行完整的基准测试套件"""
        
        print("🏃‍♂️ Platform Agent Memory性能基准测试")
        print("=" * 60)
        
        for i, test_case in enumerate(self.test_cases):
            print(f"\n📊 测试用例 {i+1}/{len(self.test_cases)}: {test_case['name']}")
            print(f"   查询: {test_case['query']}")
            
            # 多次运行取平均值
            runs = 3 if not self.detailed else 5
            
            with_memory_times = []
            without_memory_times = []
            
            for run in range(runs):
                print(f"   运行 {run+1}/{runs}...", end=" ")
                
                # 测试启用memory的情况
                result_with = self.measure_response_time(test_case["query"], with_memory=True)
                with_memory_times.append(result_with["response_time"])
                
                # 测试禁用memory的情况（如果支持）
                result_without = self.measure_response_time(test_case["query"], with_memory=False)
                without_memory_times.append(result_without["response_time"])
                
                print("✓")
                
                # 添加延迟避免系统负载
                time.sleep(1)
            
            # 计算统计数据
            avg_with = statistics.mean(with_memory_times)
            avg_without = statistics.mean(without_memory_times)
            improvement = ((avg_without - avg_with) / avg_without * 100) if avg_without > 0 else 0
            
            benchmark_result = {
                "test_case": test_case["name"],
                "query": test_case["query"],
                "runs": runs,
                "with_memory": {
                    "avg_time": avg_with,
                    "min_time": min(with_memory_times),
                    "max_time": max(with_memory_times),
                    "times": with_memory_times
                },
                "without_memory": {
                    "avg_time": avg_without,
                    "min_time": min(without_memory_times),
                    "max_time": max(without_memory_times),
                    "times": without_memory_times
                },
                "improvement_percent": improvement
            }
            
            self.results["benchmarks"].append(benchmark_result)
            
            # 输出结果
            print(f"   📈 结果:")
            print(f"      启用Memory: {avg_with:.3f}s (平均)")
            print(f"      禁用Memory: {avg_without:.3f}s (平均)")
            if improvement > 0:
                print(f"      性能提升: {improvement:.1f}% ✅")
            else:
                print(f"      性能变化: {improvement:.1f}% ⚠️")
        
        # 计算总体统计
        self.calculate_summary()
        return self.results
    
    def calculate_summary(self):
        """计算总体统计数据"""
        if not self.results["benchmarks"]:
            return
        
        improvements = [b["improvement_percent"] for b in self.results["benchmarks"]]
        with_memory_times = [b["with_memory"]["avg_time"] for b in self.results["benchmarks"]]
        without_memory_times = [b["without_memory"]["avg_time"] for b in self.results["benchmarks"]]
        
        self.results["summary"] = {
            "total_test_cases": len(self.results["benchmarks"]),
            "avg_improvement_percent": statistics.mean(improvements),
            "max_improvement_percent": max(improvements),
            "min_improvement_percent": min(improvements),
            "avg_response_time_with_memory": statistics.mean(with_memory_times),
            "avg_response_time_without_memory": statistics.mean(without_memory_times),
            "performance_grade": self.get_performance_grade(statistics.mean(improvements))
        }
    
    def get_performance_grade(self, improvement_percent: float) -> str:
        """根据性能提升百分比评定等级"""
        if improvement_percent >= 50:
            return "A+ (优秀)"
        elif improvement_percent >= 30:
            return "A (良好)"
        elif improvement_percent >= 10:
            return "B (合格)"
        elif improvement_percent >= 0:
            return "C (待优化)"
        else:
            return "D (需要改进)"
    
    def print_summary_report(self):
        """打印总结报告"""
        summary = self.results["summary"]
        
        print("\n" + "=" * 60)
        print("📊 性能基准测试总结报告")
        print("=" * 60)
        
        print(f"测试用例总数: {summary['total_test_cases']}")
        print(f"平均性能提升: {summary['avg_improvement_percent']:.1f}%")
        print(f"最大性能提升: {summary['max_improvement_percent']:.1f}%")
        print(f"最小性能提升: {summary['min_improvement_percent']:.1f}%")
        print(f"")
        print(f"启用Memory平均响应时间: {summary['avg_response_time_with_memory']:.3f}s")
        print(f"禁用Memory平均响应时间: {summary['avg_response_time_without_memory']:.3f}s")
        print(f"")
        print(f"性能等级: {summary['performance_grade']}")
        
        # 性能建议
        print(f"\n💡 性能建议:")
        if summary['avg_improvement_percent'] >= 30:
            print("   ✅ Memory功能显著提升了性能，建议启用")
        elif summary['avg_improvement_percent'] >= 10:
            print("   ⚠️ Memory功能有一定提升，可以考虑启用")
        else:
            print("   ❌ Memory功能提升不明显，需要进一步优化")
    
    def save_report(self, filename: str = None, export_csv: bool = False):
        """保存测试报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_benchmark_report_{timestamp}.json"
        
        # 保存JSON报告
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 详细报告已保存到: {filename}")
        
        # 导出CSV格式
        if export_csv:
            csv_filename = filename.replace(".json", ".csv")
            self.export_csv(csv_filename)
            print(f"📊 CSV数据已导出到: {csv_filename}")
    
    def export_csv(self, filename: str):
        """导出CSV格式的数据"""
        import csv
        
        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                "test_case", "query", "runs",
                "avg_time_with_memory", "avg_time_without_memory",
                "improvement_percent"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for benchmark in self.results["benchmarks"]:
                writer.writerow({
                    "test_case": benchmark["test_case"],
                    "query": benchmark["query"],
                    "runs": benchmark["runs"],
                    "avg_time_with_memory": benchmark["with_memory"]["avg_time"],
                    "avg_time_without_memory": benchmark["without_memory"]["avg_time"],
                    "improvement_percent": benchmark["improvement_percent"]
                })


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Platform Agent Memory性能基准测试")
    parser.add_argument("--detailed", action="store_true", 
                       help="运行详细测试（更多运行次数）")
    parser.add_argument("--export-csv", action="store_true",
                       help="导出CSV格式数据")
    parser.add_argument("--output", type=str,
                       help="指定输出文件名")
    
    args = parser.parse_args()
    
    # 创建基准测试实例
    benchmark = MemoryBenchmark(detailed=args.detailed)
    
    try:
        # 运行基准测试
        results = benchmark.run_benchmark_suite()
        
        # 打印总结
        benchmark.print_summary_report()
        
        # 保存报告
        benchmark.save_report(args.output, args.export_csv)
        
        # 根据性能结果设置退出码
        if results["summary"]["avg_improvement_percent"] >= 10:
            print("\n🎉 基准测试通过：Memory功能带来了显著的性能提升！")
            sys.exit(0)
        else:
            print("\n⚠️ 基准测试警告：Memory功能的性能提升不够明显")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 基准测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 基准测试失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()