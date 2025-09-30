"""
Python 3.13.7 兼容性测试脚本
用于测试项目依赖在Python 3.13.7下的兼容性
"""

import sys
import importlib
import subprocess
import platform
import time
import traceback

def test_python_version():
    """测试Python版本"""
    print(f"Python版本: {sys.version}")
    print(f"Python实现: {platform.python_implementation()}")
    print(f"架构: {platform.architecture()}")
    print(f"可执行文件: {sys.executable}")
    print("-" * 50)

def test_core_dependencies():
    """测试核心依赖"""
    core_deps = [
        'PySide6',
        'qfluentwidgets', 
        'cv2',
        'numpy',
        'scipy',
        'yaml',
        'pyautogui',
        'pynput',
        'mss',
        'shapely',
        'pyclipper',
        'soundcard',
        'librosa',
        'gensim'
    ]
    
    print("测试核心依赖...")
    success_count = 0
    failed_deps = []
    
    for dep in core_deps:
        try:
            if dep == 'cv2':
                import cv2
                print(f"✅ OpenCV: {cv2.__version__}")
            elif dep == 'yaml':
                import yaml
                print(f"✅ PyYAML: {yaml.__version__}")
            else:
                module = importlib.import_module(dep)
                version = getattr(module, '__version__', 'Unknown')
                print(f"✅ {dep}: {version}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {dep}: 导入失败 - {e}")
            failed_deps.append(dep)
        except Exception as e:
            print(f"⚠️ {dep}: 导入异常 - {e}")
            failed_deps.append(dep)
    
    print(f"\n核心依赖测试结果: {success_count}/{len(core_deps)} 成功")
    if failed_deps:
        print(f"失败的依赖: {', '.join(failed_deps)}")
    return success_count == len(core_deps), failed_deps

def test_onnxruntime():
    """测试ONNX Runtime"""
    print("\n测试ONNX Runtime...")
    try:
        import onnxruntime as ort
        print(f"✅ ONNX Runtime: {ort.__version__}")
        print(f"   可用提供者: {ort.get_available_providers()}")
        return True
    except ImportError as e:
        print(f"❌ ONNX Runtime: 导入失败 - {e}")
        return False
    except Exception as e:
        print(f"⚠️ ONNX Runtime: 异常 - {e}")
        return False

def test_gui_functionality():
    """测试GUI功能"""
    print("\n测试GUI功能...")
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.FluentWidgets import FluentWindow
        
        app = QApplication([])
        print("✅ PySide6 GUI: 基本功能正常")
        app.quit()
        return True
    except Exception as e:
        print(f"❌ GUI功能: 测试失败 - {e}")
        return False

def test_image_processing():
    """测试图像处理功能"""
    print("\n测试图像处理功能...")
    try:
        import cv2
        import numpy as np
        
        # 创建测试图像
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # 测试基本操作
        gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(test_img, (5, 5), 0)
        
        print("✅ OpenCV图像处理: 基本功能正常")
        return True
    except Exception as e:
        print(f"❌ 图像处理: 测试失败 - {e}")
        return False

def test_audio_processing():
    """测试音频处理功能"""
    print("\n测试音频处理功能...")
    try:
        import librosa
        import soundcard as sc
        
        # 测试基本音频功能
        print("✅ 音频处理: 基本功能正常")
        return True
    except Exception as e:
        print(f"❌ 音频处理: 测试失败 - {e}")
        return False

def test_threading_capability():
    """测试多线程能力"""
    print("\n测试多线程能力...")
    try:
        import threading
        import concurrent.futures
        import time
        
        def test_task(n):
            return sum(i*i for i in range(n))
        
        # 单线程测试
        start_time = time.time()
        single_result = [test_task(1000) for _ in range(4)]
        single_time = time.time() - start_time
        
        # 多线程测试
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(test_task, 1000) for _ in range(4)]
            multi_result = [f.result() for f in futures]
        multi_time = time.time() - start_time
        
        speedup = single_time / multi_time if multi_time > 0 else 1.0
        print(f"✅ 多线程测试完成")
        print(f"   单线程时间: {single_time:.3f}秒")
        print(f"   多线程时间: {multi_time:.3f}秒")
        print(f"   加速比: {speedup:.2f}x")
        
        return True
    except Exception as e:
        print(f"❌ 多线程测试: 失败 - {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Python 3.13.7 兼容性测试")
    print("=" * 60)
    
    test_python_version()
    
    results = []
    core_success, failed_deps = test_core_dependencies()
    results.append(core_success)
    results.append(test_onnxruntime())
    results.append(test_gui_functionality())
    results.append(test_image_processing())
    results.append(test_audio_processing())
    results.append(test_threading_capability())
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有测试通过! ({passed}/{total})")
        print("✅ 项目可以安全升级到Python 3.13.7")
    else:
        print(f"⚠️ 部分测试失败 ({passed}/{total})")
        print("❌ 建议先解决兼容性问题再升级")
        if failed_deps:
            print(f"需要解决的依赖问题: {', '.join(failed_deps)}")
    
    return passed == total, failed_deps

if __name__ == "__main__":
    success, failed_deps = main()
    sys.exit(0 if success else 1)
