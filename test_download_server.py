#!/usr/bin/env python3
"""
多功能本地测试服务器
功能：
1. /health/missing -> 模拟 434 状态码，无 ext1 字段 (测试通过的情况)
2. /health/block   -> 模拟 434 状态码，ext1=true (测试拦截的情况)
3. 其他路径        -> 模拟网络卡顿15秒后返回 PDF
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# 配置端口
SERVER_PORT = 8765

# 极简 PDF 数据
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

class MultiUseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """根据路径分发请求"""
        print(f"\n=== 收到请求: {self.path} ===")

        # 场景 1: 模拟缺少 ext1 字段 (你应该能通过检查)
        if self.path.startswith('/health/missing'):
            self.send_response(434) # 模拟特定状态码
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # 返回空 JSON 或者其他无关字段
            response_data = {"msg": "No ext1 field here", "other": 123}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            print("✅ 已发送 434 响应 (无 ext1)")
            return

        # 场景 2: 模拟存在 ext1=true (你应该被拦截)
        if self.path.startswith('/health/block'):
            self.send_response(434)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # 返回包含 ext1: true 的 JSON
            response_data = {"ext1": True, "msg": "You shall not pass"}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            print("🚫 已发送 434 响应 (ext1=true)")
            return

        # 场景 3: 默认行为 (模拟慢速 PDF 下载)
        self.handle_slow_pdf()

    def do_HEAD(self):
        self.do_GET()

    def handle_slow_pdf(self):
        """模拟：先睡15秒，然后返回内置的PDF文件"""
        print(f"⏳ 模拟网络拥堵中... (15s)")
        time.sleep(15) 
        
        self.send_response(200)
        self.send_header('Content-type', 'application/pdf')
        self.send_header('Content-length', str(len(MINIMAL_PDF_BYTES)))
        self.send_header('Content-Disposition', 'attachment; filename="test_delay.pdf"')
        self.end_headers()

        self.wfile.write(MINIMAL_PDF_BYTES)
        print("✅ PDF 发送完毕")

def main():
    print(f"🚀 全能测试服务器启动: http://localhost:{SERVER_PORT}")
    print(f"1. 测试无 ext1:  http://localhost:{SERVER_PORT}/health/missing")
    print(f"2. 测试有 ext1:  http://localhost:{SERVER_PORT}/health/block")
    print(f"3. 测试慢速PDF:  http://localhost:{SERVER_PORT}/any-other-path")
    print("-" * 50)

    server = HTTPServer(('localhost', SERVER_PORT), MultiUseHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 停止")

if __name__ == '__main__':
    main()