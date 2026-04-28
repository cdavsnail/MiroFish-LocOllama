"""
MiroFish Backend 启动入口
"""

import os
import sys

# 解决 Windows 控制台中文乱码问题：在所有导入之前设置 UTF-8 编码
if sys.platform == 'win32':
    # 设置环境变量确保 Python 使用 UTF-8
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    # 重新配置标准输出流为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import subprocess
import threading
import time
import webbrowser

from app import create_app
from app.config import Config


def check_ollama_status():
    """检查Ollama状态并在必要时启动及下载模型"""
    print("Checking Ollama status...")

    # Check if Ollama is installed
    try:
        subprocess.run(['ollama', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Ollama is not installed. Please install it from https://ollama.com/")
        # You might want to automatically open the browser to the installation page here
        webbrowser.open('https://ollama.com/')
        sys.exit(1)

    # Check if the server is running, if not try to start it
    # We will run a simple curl to check if it's responding
    # But a simpler way in python is just to use urllib
    import urllib.request
    import urllib.error

    ollama_running = False
    try:
        urllib.request.urlopen('http://localhost:11434', timeout=2)
        ollama_running = True
        print("Ollama server is already running.")
    except (urllib.error.URLError, ConnectionRefusedError):
        print("Starting Ollama server...")
        # Start ollama serve in background
        if sys.platform == 'win32':
            subprocess.Popen(['ollama', 'serve'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for it to start
        for _ in range(15):
            time.sleep(1)
            try:
                urllib.request.urlopen('http://localhost:11434', timeout=2)
                ollama_running = True
                print("Ollama server started successfully.")
                break
            except (urllib.error.URLError, ConnectionRefusedError):
                pass

    if not ollama_running:
        print("Failed to start Ollama server. Please start it manually: `ollama serve`")
        sys.exit(1)

    # Check and pull the llama3 model
    print("Checking for llama3 model...")
    try:
        # Check if model exists
        result = subprocess.run(['ollama', 'list'], stdout=subprocess.PIPE, text=True, check=True)
        if 'llama3' not in result.stdout:
            print("Downloading llama3 model (this may take a while)...")
            # We don't want to capture stdout so the user sees progress
            subprocess.run(['ollama', 'pull', 'llama3'], check=True)
            print("Model downloaded successfully.")
        else:
            print("llama3 model is ready.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking/pulling model: {e}")
        print("You may need to manually run: `ollama pull llama3`")

def open_browser(port):
    """Wait a moment and then open the browser"""
    time.sleep(2)
    url = f"http://localhost:{port}"
    print(f"Opening browser at {url}...")
    webbrowser.open(url)

def main():
    """主函数"""
    # 如果是打包后的环境，不使用debug模式，避免reloader导致两次执行
    is_frozen = getattr(sys, 'frozen', False)
    debug = False if is_frozen else Config.DEBUG

    # 仅在主进程中执行一次性操作，避免在使用reloader时重复执行
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    is_main_execution = not debug or is_reloader_process

    if is_main_execution:
        # Check and setup Ollama automatically
        check_ollama_status()

    # 验证配置
    errors = Config.validate()
    if errors:
        print("配置错误:")
        for err in errors:
            print(f"  - {err}")
        print("\n请检查 .env 文件中的配置")
        sys.exit(1)
    
    # 创建应用
    app = create_app()
    
    # 获取运行配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    # 启动后自动打开浏览器
    if is_main_execution:
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # 启动服务
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    main()

