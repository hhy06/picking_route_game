#!/usr/bin/env python3

import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("拣货路线游戏")
    print("=" * 50)
    
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    
    print("\n启动后端服务器 (Flask)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--host=127.0.0.1", "--port=5000"],
        cwd=os.path.dirname(__file__),
        env={**os.environ, "FLASK_APP": "backend.app"}
    )
    
    print("启动前端服务器 (Vite)...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir
    )
    
    print("\n" + "=" * 50)
    print("服务器已启动！")
    print("请在浏览器中打开: http://localhost:3000")
    print("=" * 50)
    print("\n按 Ctrl+C 停止所有服务器")
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n正在停止服务器...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("服务器已停止")

if __name__ == "__main__":
    main()
