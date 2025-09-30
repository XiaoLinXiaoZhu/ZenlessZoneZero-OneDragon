"""
Python 3.13.7 自动升级脚本
自动完成Python版本升级和测试
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

class PythonUpgrader:
    def __init__(self, project_root=".."):
        self.project_root = Path(project_root).resolve()
        self.test_dir = Path(".").resolve()
        self.backup_dir = self.test_dir / "backups"
        self.results_dir = self.test_dir / "results"
        
        # 创建必要的目录
        self.backup_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
    def log(self, message):
        """记录日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_command(self, command, cwd=None):
        """运行命令"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd or self.project_root
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def backup_files(self):
        """备份重要文件"""
        self.log("备份重要文件...")
        
        files_to_backup = [
            "pyproject.toml",
            "uv.lock"
        ]
        
        for file in files_to_backup:
            src = self.project_root / file
            if src.exists():
                dst = self.backup_dir / f"{file}.backup"
                shutil.copy2(src, dst)
                self.log(f"已备份: {file}")
            else:
                self.log(f"警告: 文件不存在 {file}")
    
    def install_python_versions(self):
        """安装Python版本"""
        self.log("安装Python 3.13.7...")
        
        # 安装普通版本
        success, stdout, stderr = self.run_command("uv python install 3.13.7")
        if success:
            self.log("✅ Python 3.13.7 安装成功")
        else:
            self.log(f"❌ Python 3.13.7 安装失败: {stderr}")
            return False
        
        # 安装freethreaded版本
        self.log("安装Python 3.13.7+freethreaded...")
        success, stdout, stderr = self.run_command("uv python install 3.13.7+freethreaded")
        if success:
            self.log("✅ Python 3.13.7+freethreaded 安装成功")
        else:
            self.log(f"⚠️ Python 3.13.7+freethreaded 安装失败: {stderr}")
        
        return True
    
    def test_python_version(self, version):
        """测试特定Python版本"""
        self.log(f"测试Python版本: {version}")
        
        # 设置Python版本
        success, stdout, stderr = self.run_command(f"uv python pin {version}")
        if not success:
            self.log(f"❌ 设置Python版本失败: {stderr}")
            return False
        
        # 同步依赖
        self.log("同步依赖...")
        success, stdout, stderr = self.run_command("uv sync")
        if not success:
            self.log(f"❌ 依赖同步失败: {stderr}")
            return False
        
        # 运行兼容性测试
        self.log("运行兼容性测试...")
        success, stdout, stderr = self.run_command("python compatibility_test.py", cwd=self.test_dir)
        
        # 保存测试结果
        result_file = self.results_dir / f"compatibility_{version.replace('+', '_')}.txt"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"Python版本: {version}\n")
            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            f.write("STDOUT:\n")
            f.write(stdout)
            f.write("\nSTDERR:\n")
            f.write(stderr)
        
        if success:
            self.log(f"✅ 兼容性测试通过: {version}")
        else:
            self.log(f"❌ 兼容性测试失败: {version}")
        
        return success
    
    def test_performance(self, version):
        """测试性能"""
        self.log(f"测试性能: {version}")
        
        # 设置Python版本
        success, stdout, stderr = self.run_command(f"uv python pin {version}")
        if not success:
            return False
        
        # 运行性能测试
        success, stdout, stderr = self.run_command("python performance_comparison.py", cwd=self.test_dir)
        
        # 保存性能结果
        result_file = self.results_dir / f"performance_{version.replace('+', '_')}.txt"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"Python版本: {version}\n")
            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            f.write("STDOUT:\n")
            f.write(stdout)
            f.write("\nSTDERR:\n")
            f.write(stderr)
        
        if success:
            self.log(f"✅ 性能测试完成: {version}")
        else:
            self.log(f"❌ 性能测试失败: {version}")
        
        return success
    
    def update_pyproject(self, python_version):
        """更新pyproject.toml"""
        self.log(f"更新pyproject.toml为Python {python_version}")
        
        pyproject_file = self.project_root / "pyproject.toml"
        if not pyproject_file.exists():
            self.log("❌ pyproject.toml不存在")
            return False
        
        # 读取文件
        with open(pyproject_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新Python版本要求
        if python_version.startswith("3.13"):
            new_requires = 'requires-python = ">=3.13.7,<3.14"'
            new_target = 'target-version = "py313"'
        else:
            new_requires = 'requires-python = ">=3.11.9,<3.12"'
            new_target = 'target-version = "py311"'
        
        # 替换内容
        content = content.replace('requires-python = ">=3.11.9,<3.12"', new_requires)
        content = content.replace('requires-python = ">=3.13.7,<3.14"', new_requires)
        content = content.replace('target-version = "py311"', new_target)
        content = content.replace('target-version = "py313"', new_target)
        
        # 写回文件
        with open(pyproject_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.log(f"✅ pyproject.toml已更新")
        return True
    
    def generate_report(self):
        """生成测试报告"""
        self.log("生成测试报告...")
        
        report_file = self.results_dir / "upgrade_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Python 3.13.7 升级测试报告\n\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 测试概述\n\n")
            f.write("本报告包含Python 3.13.7升级的兼容性和性能测试结果。\n\n")
            
            f.write("## 测试结果文件\n\n")
            for file in self.results_dir.glob("*.txt"):
                f.write(f"- {file.name}\n")
            
            f.write("\n## 建议\n\n")
            f.write("1. 查看各个测试结果文件了解详细信息\n")
            f.write("2. 根据兼容性测试结果决定是否升级\n")
            f.write("3. 根据性能测试结果选择最适合的Python版本\n")
        
        self.log(f"✅ 测试报告已生成: {report_file}")
    
    def run_full_test(self):
        """运行完整测试"""
        self.log("开始Python 3.13.7升级测试")
        
        # 1. 备份文件
        self.backup_files()
        
        # 2. 安装Python版本
        if not self.install_python_versions():
            self.log("❌ Python版本安装失败，测试终止")
            return False
        
        # 3. 测试普通版本
        self.log("=" * 60)
        self.log("测试Python 3.13.7 (普通版本)")
        self.log("=" * 60)
        
        self.update_pyproject("3.13.7")
        compat_normal = self.test_python_version("3.13.7")
        perf_normal = self.test_performance("3.13.7")
        
        # 4. 测试freethreaded版本
        self.log("=" * 60)
        self.log("测试Python 3.13.7+freethreaded")
        self.log("=" * 60)
        
        compat_freethreaded = self.test_python_version("3.13.7+freethreaded")
        perf_freethreaded = self.test_performance("3.13.7+freethreaded")
        
        # 5. 生成报告
        self.generate_report()
        
        # 6. 总结
        self.log("=" * 60)
        self.log("测试总结")
        self.log("=" * 60)
        
        self.log(f"Python 3.13.7 兼容性: {'✅ 通过' if compat_normal else '❌ 失败'}")
        self.log(f"Python 3.13.7 性能测试: {'✅ 完成' if perf_normal else '❌ 失败'}")
        self.log(f"Python 3.13.7+freethreaded 兼容性: {'✅ 通过' if compat_freethreaded else '❌ 失败'}")
        self.log(f"Python 3.13.7+freethreaded 性能测试: {'✅ 完成' if perf_freethreaded else '❌ 失败'}")
        
        if compat_normal and compat_freethreaded:
            self.log("🎉 两个版本都兼容，可以根据性能测试结果选择")
        elif compat_normal:
            self.log("✅ 建议使用Python 3.13.7普通版本")
        else:
            self.log("❌ 建议暂时不升级，等待依赖兼容性改善")
        
        return True

def main():
    """主函数"""
    upgrader = PythonUpgrader()
    upgrader.run_full_test()

if __name__ == "__main__":
    main()
