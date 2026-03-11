
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.app import app

if __name__ == '__main__':
    print("=" * 50)
    print("   今日头条自动化脚本 - Web 控制面板")
    print("=" * 50)
    print("\n请在浏览器中打开: http://localhost:5000")
    print("\n按 Ctrl+C 停止服务器\n")
    app.run(host='0.0.0.0', port=5000, debug=False)

