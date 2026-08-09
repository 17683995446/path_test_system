"""
快速启动可视化网站
"""

import subprocess
import os
import time

def start_web_server():
    """启动Web服务器"""
    os.chdir('/workspace/50-layer-visual')
    
    print("="*80)
    print("🚀 50层系统可视化网站 - 快速启动")
    print("="*80)
    
    # 检查是否有Python可用
    try:
        import http.server
        import socketserver
        
        PORT = 8080
        Handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"\n✅ 服务器已启动！")
            print(f"\n📊 请在浏览器中访问:")
            print(f"   http://localhost:{PORT}")
            print("\n" + "="*80)
            print("按 Ctrl+C 停止服务器")
            print("="*80)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")


if __name__ == "__main__":
    start_web_server()
