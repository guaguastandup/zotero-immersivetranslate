#!/usr/bin/env python3
"""
本地测试服务器：内置 PDF 生成功能
用途：
1. 模拟网络卡顿（等待15秒）
2. 即使没有外部链接，也能返回一个合法的测试用 PDF 文件
"""

import json
import sys
import os
import time
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

# 配置端口
SERVER_PORT = 8765

# 一个极简的 PDF 文件二进制数据 (包含 "Test PDF" 文字)
# 这样不需要依赖任何外部文件或网络
MINIMAL_PDF_BYTES = (
    b'%PDF-1.1\n'
    b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
    b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
    b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
    b'/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> '
    b'/Contents 4 0 R >>\nendobj\n'
    b'4 0 obj\n<< /Length 21 >>\nstream\n'
    b'BT /F1 24 Tf 100 700 Td (Test PDF Content) Tj ET\n'
    b'endstream\nendobj\n'
    b'xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n'
    b'0000000115 00000 n \n0000000300 00000 n \n'
    b'trailer\n<< /Size 5 /Root 1 0 R >>\n'
    b'startxref\n370\n%%EOF\n'
)

class DownloadTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理下载请求"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # 即使前端没传 url 参数，我们也默认处理
        original_url = query_params.get('url', ['(内置测试PDF)'])[0]

        print(f"\n=== 收到请求 ===")
        print(f"路径: {self.path}")
        
        # 无论如何，都进入慢速模拟模式
        self.handle_slow_response()

    def do_HEAD(self):
        self.do_GET()

    def handle_slow_response(self):
        """模拟：先睡15秒，然后返回内置的PDF文件"""
        print(f"⏳ 模拟网络拥堵中...")
        print(f"   - 将暂停 15 秒 (触发前端10秒超时警告)")
        print(f"   - 然后返回内置 PDF 文件")
        
        # 1. 模拟卡顿
        time.sleep(15) 
        
        print("⏰ 15秒结束，开始发送 PDF 数据...")

        # 2. 发送响应头
        self.send_response(200)
        self.send_header('Content-type', 'application/pdf')
        self.send_header('Content-length', str(len(MINIMAL_PDF_BYTES)))
        # 加上文件名，方便浏览器下载识别
        self.send_header('Content-Disposition', 'attachment; filename="test_delay.pdf"')
        self.end_headers()

        # 3. 发送内置的 PDF 二进制数据
        self.wfile.write(MINIMAL_PDF_BYTES)
        print("✅ PDF 发送完毕")

def main():
    print(f"🚀 测试服务器启动: http://localhost:{SERVER_PORT}")
    print(f"💡 说明: 任何请求都会卡顿15秒，然后返回一个测试用PDF。")
    print("-" * 50)

    server = HTTPServer(('localhost', SERVER_PORT), DownloadTestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 停止")

if __name__ == '__main__':
    main()