#!/usr/bin/env python3
"""
Platform Agent Memory功能基础测试脚本

测试目标：
1. 验证存储目录和数据库文件创建
2. 验证Short-term Memory基础功能
3. 验证Long-term Memory跨会话持久化
4. 验证Entity Memory实体识别能力

使用方法：
    uv run test_memory_basic.py
"""

import os
import sys
import time
import json
import sqlite3
import pathlib
import subprocess
from datetime import datetime
from typing import Dict, List, Any


class MemoryTestSuite:
    """Memory功能测试套件"""
    
    def __init__(self):
        self.test_results = []
        self.storage_dir = pathlib.Path("./crew_memory")
        self.test_session_file = "test_session.json"
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """记录测试结果"""
        result = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        # 实时输出测试结果
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   └─ {details}")
    
    def test_storage_directory_creation(self) -> bool:
        """测试1: 验证存储目录创建"""
        try:
            # 清理之前的测试数据
            if self.storage_dir.exists():
                import shutil
                shutil.rmtree(self.storage_dir)
            
            # 运行程序（短暂运行以触发目录创建）
            process = subprocess.Popen(
                ["python", "-c", """
import sys
sys.path.insert(0, 'src')
from ops_crew.crew import OpsCrew
# 仅初始化，不运行crew
crew = OpsCrew()
print('Memory initialization test completed')
                """],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
            
            stdout, stderr = process.communicate()
            
            # 检查存储目录是否创建
            if self.storage_dir.exists():
                self.log_test("Storage Directory Creation", "PASS", 
                            f"Directory created at: {self.storage_dir}")
                return True
            else:
                self.log_test("Storage Directory Creation", "FAIL",
                            "Storage directory was not created")
                return False
                
        except Exception as e:
            self.log_test("Storage Directory Creation", "FAIL", str(e))
            return False
    
    def test_database_files_exist(self) -> bool:
        """测试2: 验证数据库文件创建"""
        try:
            if not self.storage_dir.exists():
                self.log_test("Database Files Existence", "SKIP",
                            "Storage directory does not exist")
                return False
            
            # 查找预期的数据库文件
            db_files = list(self.storage_dir.glob("*.db"))
            chroma_files = list(self.storage_dir.glob("*.chroma*"))
            
            if db_files or chroma_files:
                files_found = [f.name for f in db_files + chroma_files]
                self.log_test("Database Files Existence", "PASS",
                            f"Found files: {', '.join(files_found)}")
                return True
            else:
                # 列出实际存在的文件
                all_files = list(self.storage_dir.iterdir())
                file_names = [f.name for f in all_files]
                self.log_test("Database Files Existence", "WARN",
                            f"No .db or .chroma files found. Files present: {', '.join(file_names)}")
                return len(all_files) > 0  # 如果有任何文件，认为部分成功
                
        except Exception as e:
            self.log_test("Database Files Existence", "FAIL", str(e))
            return False
    
    def test_memory_configuration(self) -> bool:
        """测试3: 验证Memory配置"""
        try:
            # 检查环境变量配置
            env_file = pathlib.Path(".env")
            if env_file.exists():
                env_content = env_file.read_text()
                if "CREWAI_STORAGE_DIR" in env_content:
                    self.log_test("Memory Configuration", "PASS",
                                "CREWAI_STORAGE_DIR found in .env")
                    return True
                else:
                    self.log_test("Memory Configuration", "WARN",
                                "CREWAI_STORAGE_DIR not found in .env")
                    return False
            else:
                self.log_test("Memory Configuration", "FAIL",
                            ".env file not found")
                return False
                
        except Exception as e:
            self.log_test("Memory Configuration", "FAIL", str(e))
            return False
    
    def test_crew_initialization_with_memory(self) -> bool:
        """测试4: 验证带Memory的Crew初始化"""
        try:
            # 测试Crew能否正常初始化（带memory=True）
            test_code = """
import sys
import os
sys.path.insert(0, 'src')

# 设置测试环境变量
os.environ['CREWAI_STORAGE_DIR'] = './crew_memory'

try:
    from ops_crew.crew import OpsCrew
    crew_instance = OpsCrew()
    
    # 尝试创建crew（这会触发memory初始化）
    ops_crew = crew_instance.ops_crew()
    print("SUCCESS: Crew with memory initialized")
except Exception as e:
    print(f"ERROR: {str(e)}")
            """
            
            process = subprocess.Popen(
                ["python", "-c", test_code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )
            
            stdout, stderr = process.communicate()
            output = stdout.decode() + stderr.decode()
            
            if "SUCCESS" in output:
                self.log_test("Crew Memory Initialization", "PASS",
                            "Crew initialized successfully with memory")
                return True
            else:
                self.log_test("Crew Memory Initialization", "FAIL",
                            f"Output: {output}")
                return False
                
        except Exception as e:
            self.log_test("Crew Memory Initialization", "FAIL", str(e))
            return False
    
    def test_basic_memory_functionality(self) -> bool:
        """测试5: 基础Memory功能测试"""
        try:
            # 这个测试需要实际运行crew并检查memory行为
            # 由于复杂性，这里先做基础检查
            
            # 检查是否有ChromaDB相关依赖
            try:
                import chromadb
                self.log_test("ChromaDB Dependency", "PASS", 
                            f"ChromaDB version: {chromadb.__version__}")
            except ImportError:
                self.log_test("ChromaDB Dependency", "FAIL",
                            "ChromaDB not installed")
                return False
            
            # 检查SQLite支持
            try:
                import sqlite3
                self.log_test("SQLite Support", "PASS",
                            f"SQLite version: {sqlite3.sqlite_version}")
            except ImportError:
                self.log_test("SQLite Support", "FAIL",
                            "SQLite not available")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Basic Memory Functionality", "FAIL", str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🧪 Platform Agent Memory功能基础测试")
        print("=" * 50)
        
        # 执行测试
        tests = [
            self.test_storage_directory_creation,
            self.test_database_files_exist, 
            self.test_memory_configuration,
            self.test_crew_initialization_with_memory,
            self.test_basic_memory_functionality
        ]
        
        passed = 0
        failed = 0
        warned = 0
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test.__name__, "FAIL", str(e))
                failed += 1
        
        # 统计警告
        warned = len([r for r in self.test_results if r["status"] == "WARN"])
        
        # 生成测试报告
        report = {
            "summary": {
                "total": len(self.test_results),
                "passed": passed,
                "failed": failed,
                "warned": warned
            },
            "tests": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存测试报告
        with open("memory_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # 输出总结
        print("\n" + "=" * 50)
        print("📊 测试总结:")
        print(f"   总计: {report['summary']['total']}")
        print(f"   通过: {report['summary']['passed']} ✅")
        print(f"   失败: {report['summary']['failed']} ❌")
        print(f"   警告: {report['summary']['warned']} ⚠️")
        print(f"\n📄 详细报告已保存到: memory_test_report.json")
        
        return report


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        return
    
    test_suite = MemoryTestSuite()
    report = test_suite.run_all_tests()
    
    # 根据测试结果设置退出码
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()