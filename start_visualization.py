"""
启动可视化网站
=============
"""

import http.server
import socketserver
import os
import socket
import subprocess
import time


def check_port_in_use(port):
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False


def start_visualization_server():
    """启动可视化网站服务器"""
    os.chdir('/workspace/50-layer-visual')
    
    PORT = 8080
    
    print("="*80)
    print("🚀 50层系统 - 启动可视化网站")
    print("="*80)
    
    # 检查端口
    if check_port_in_use(PORT):
        print(f"\n✅ 网站已在运行！")
        print(f"\n📊 请在浏览器中访问:")
        print(f"   http://localhost:{PORT}")
        print("\n" + "="*80)
    else:
        # 启动服务器
        print(f"\n🔧 启动HTTP服务器在端口 {PORT}...")
        
        Handler = http.server.SimpleHTTPRequestHandler
        
        try:
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                print(f"✅ 可视化网站已启动！")
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
    start_visualization_server()
