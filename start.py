#!/usr/bin/env python3

from backend.app import app
from backend.constants import DEFAULT_HOST, DEFAULT_PORT


def main():
    print("=" * 50)
    print("拣货路线游戏服务器")
    print("=" * 50)
    print(f"\n启动服务器...")
    print(f"请在浏览器中打开: http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=True)


if __name__ == "__main__":
    main()
