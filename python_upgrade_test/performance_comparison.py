"""
Python 3.13.7 性能对比测试脚本
比较普通版本和freethreaded版本的性能差异
"""

import time
import threading
import concurrent.futures
import numpy as np
import sys
import platform

def cpu_intensive_task(n):
    """CPU密集型任务"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

def image_processing_task():
    """图像处理任务"""
    try:
        import cv2
        # 创建测试图像
        img = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        
        # 执行多个图像处理操作
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(img, (15, 15), 0)
        edges = cv2.Canny(gray, 50, 150)
        
        return len(edges)
    except ImportError:
        # 如果没有OpenCV，使用numpy模拟
        img = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        gray = np.mean(img, axis=2)
        return np.sum(gray > 128)

def matrix_operations_task():
    """矩阵运算任务"""
    # 创建大矩阵进行运算
    a = np.random.rand(1000, 1000)
    b = np.random.rand(1000, 1000)
    
    # 矩阵乘法
    c = np.dot(a, b)
    
    # 特征值分解
    eigenvals = np.linalg.eigvals(c[:100, :100])
    
    return np.sum(eigenvals)

def test_single_threaded():
    """单线程测试"""
    print("执行单线程测试...")
    start_time = time.time()
    
    # 执行CPU密集型任务
    for i in range(4):
        cpu_intensive_task(50000)
    
    # 执行图像处理任务
    for i in range(4):
        image_processing_task()
    
    # 执行矩阵运算任务
    for i in range(2):
        matrix_operations_task()
    
    end_time = time.time()
    return end_time - start_time

def test_multi_threaded():
    """多线程测试"""
    print("执行多线程测试...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # 提交CPU密集型任务
        cpu_futures = [executor.submit(cpu_intensive_task, 50000) for _ in range(4)]
        
        # 提交图像处理任务
        img_futures = [executor.submit(image_processing_task) for _ in range(4)]
        
        # 提交矩阵运算任务
        matrix_futures = [executor.submit(matrix_operations_task) for _ in range(2)]
        
        # 等待所有任务完成
        all_futures = cpu_futures + img_futures + matrix_futures
        concurrent.futures.wait(all_futures)
        
        # 获取结果（确保任务完成）
        for future in all_futures:
            future.result()
    
    end_time = time.time()
    return end_time - start_time

def test_memory_intensive():
    """内存密集型测试"""
    print("执行内存密集型测试...")
    start_time = time.time()
    
    # 创建大数组
    arrays = []
    for i in range(10):
        arr = np.random.rand(1000, 1000)
        arrays.append(arr)
    
    # 执行数组操作
    results = []
    for arr in arrays:
        result = np.sum(arr * arr)
        results.append(result)
    
    end_time = time.time()
    return end_time - start_time, sum(results)

def benchmark_test():
    """基准测试"""
    print("执行基准测试...")
    iterations = 1000000
    
    # 简单循环测试
    start_time = time.time()
    total = 0
    for i in range(iterations):
        total += i
    loop_time = time.time() - start_time
    
    # 列表推导式测试
    start_time = time.time()
    squares = [i*i for i in range(iterations//10)]
    list_comp_time = time.time() - start_time
    
    return loop_time, list_comp_time, total

def main():
    """主测试函数"""
    print("=" * 60)
    print("Python 3.13.7 性能测试")
    print("=" * 60)
    
    # 显示Python信息
    print(f"Python版本: {sys.version}")
    print(f"Python实现: {platform.python_implementation()}")
    print(f"是否为freethreaded: {'freethreaded' in sys.version}")
    print("-" * 60)
    
    # 运行各种测试
    tests = []
    
    # 单线程测试
    single_time = test_single_threaded()
    tests.append(("单线程测试", single_time))
    print(f"单线程执行时间: {single_time:.2f}秒")
    
    # 多线程测试
    multi_time = test_multi_threaded()
    tests.append(("多线程测试", multi_time))
    print(f"多线程执行时间: {multi_time:.2f}秒")
    
    # 计算多线程加速比
    speedup = single_time / multi_time if multi_time > 0 else 1.0
    print(f"多线程加速比: {speedup:.2f}x")
    
    # 内存密集型测试
    memory_time, memory_result = test_memory_intensive()
    tests.append(("内存密集型测试", memory_time))
    print(f"内存密集型测试时间: {memory_time:.2f}秒")
    
    # 基准测试
    loop_time, list_comp_time, loop_result = benchmark_test()
    tests.append(("循环基准测试", loop_time))
    tests.append(("列表推导式测试", list_comp_time))
    print(f"循环基准测试时间: {loop_time:.2f}秒")
    print(f"列表推导式测试时间: {list_comp_time:.2f}秒")
    
    # 性能评估
    print("\n" + "=" * 60)
    print("性能评估")
    print("=" * 60)
    
    if speedup > 2.0:
        print("🚀 多线程性能优秀！freethreaded版本可能带来显著提升")
    elif speedup > 1.5:
        print("✅ 多线程性能良好，freethreaded版本有优势")
    elif speedup > 1.1:
        print("⚠️ 多线程性能一般，freethreaded版本有轻微优势")
    else:
        print("❌ 多线程性能不佳，可能不需要freethreaded版本")
    
    # 保存测试结果
    with open('performance_results.txt', 'w', encoding='utf-8') as f:
        f.write(f"Python版本: {sys.version}\n")
        f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        for test_name, test_time in tests:
            f.write(f"{test_name}: {test_time:.2f}秒\n")
        f.write(f"多线程加速比: {speedup:.2f}x\n")
    
    print(f"\n测试结果已保存到 performance_results.txt")
    
    return {
        'single_threaded': single_time,
        'multi_threaded': multi_time,
        'speedup': speedup,
        'memory_test': memory_time,
        'loop_benchmark': loop_time,
        'list_comp_benchmark': list_comp_time
    }

if __name__ == "__main__":
    results = main()
