"""
简单启动可视化网站的脚本
"""

import os
import sys
import socket
import subprocess


def start_server():
    """启动可视化网站"""
    os.chdir('/workspace/50-layer-visual')
    
    print("="*60)
    print("🚀 50层系统 - 启动可视化网站")
    print("="*60)
    
    PORT = 8080
    
    # 检查端口
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', PORT))
    sock.close()
    
    if result == 0:
        print(f"\n✅ 服务器已在运行！")
        print(f"📊 请访问: http://localhost:{PORT}")
    else:
        print(f"\n🔧 启动 HTTP 服务器...")
        try:
            # Python 简单服务器
            import http.server
            import socketserver
            
            class Handler(http.server.SimpleHTTPRequestHandler):
                def end_headers(self):
                    self.send_header('Access-Control-Allow-Origin', '*')
                    super().end_headers()
            
            httpd = socketserver.TCPServer(('', PORT), Handler)
            
            print(f"✅ 可视化网站已启动！")
            print(f"🌐 请访问: http://localhost:{PORT}")
            print("\n按 Ctrl+C 停止服务器")
            
            httpd.serve_forever()
            
        except KeyboardInterrupt:
            print(f"\n🛑 服务器已停止")
        except Exception as e:
            print(f"❌ 启动失败: {e}")


if __name__ == "__main__":
    start_server()
