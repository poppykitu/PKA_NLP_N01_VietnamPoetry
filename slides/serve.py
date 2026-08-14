import http.server
import socketserver
import webbrowser
import os
import sys
import json
import urllib.request
import time

PORT = 8000

# Set directory paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Change current working directory to PROJECT_ROOT for pickle/lexicon loading
os.chdir(PROJECT_ROOT)

# Try importing native Python RuleRepairEngine for highest accuracy
rule_engine = None
try:
    from hybrid_llm_generator import RuleRepairEngine
    rule_engine = RuleRepairEngine()
    print("  [INIT] ✓ Loaded Native Python 3.4M N-gram RuleRepairEngine successfully!")
except Exception as e:
    print(f"  [INIT] Notice: {e}")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=CURRENT_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        # High-Performance Full Neuro-Symbolic Endpoint
        if self.path in ['/api/generate', '/api/generate_poem', '/v1/chat/completions']:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body) if body else {}
                prompt = data.get('prompt', '')
                
                # If direct OpenAI chat completions payload:
                if not prompt and 'messages' in data:
                    user_msgs = [m['content'] for m in data['messages'] if m.get('role') == 'user']
                    prompt = user_msgs[0] if user_msgs else 'hoa sen'
                    prompt = prompt.replace('Sáng tác bài thơ Lục Bát 4 câu về chủ đề:', '').strip().strip('.')

                # Call LM Studio Google Gemma-4-e2b
                t0 = time.time()
                lm_url = "http://127.0.0.1:1234/v1/chat/completions"
                lm_payload = {
                    "model": "google/gemma-4-e2b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Bạn là nhà thơ Việt Nam kiệt xuất. Hãy sáng tác bài thơ Lục Bát 4 câu (6-8-6-8 từ) mượt mà, giàu cảm xúc về chủ đề được yêu cầu. Trả về đúng 4 câu thơ Tiếng Việt, mỗi câu trên một dòng."
                        },
                        {
                            "role": "user",
                            "content": f"Sáng tác bài thơ Lục Bát 4 câu về chủ đề: {prompt}."
                        }
                    ],
                    "temperature": 0.7
                }

                req = urllib.request.Request(
                    lm_url,
                    data=json.dumps(lm_payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    lm_res = json.loads(resp.read().decode('utf-8'))

                latency = round(time.time() - t0, 2)
                msg_obj = lm_res.get('choices', [{}])[0].get('message', {})
                raw_text = (msg_obj.get('content') or msg_obj.get('reasoning_content') or '').strip()

                # Robust JSON & Text Extractor (Filters out 'poem_lines' metadata key)
                import re
                clean_lines = []
                try:
                    match_json = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if match_json:
                        json_data = json.loads(match_json.group(0))
                        for key in ['poem_lines', 'lines', 'poem']:
                            if key in json_data and isinstance(json_data[key], list):
                                clean_lines = [str(l).strip(".,!?:;\"'()[]{}*`-_/ ") for l in json_data[key] if str(l).strip()]
                                break
                except Exception:
                    pass

                if not clean_lines:
                    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                    ignore_kw = [
                        'poem_lines', 'poemlines', 'json', 'schema', 'prompt', 'draft', 
                        'revision', 'phase', 'constraint', 'dưới đây', 'chắc chắn', 'bài thơ', 
                        'lục bát', 'chủ đề', 'tác giả', '{', '}', '[', ']', '```', "'''"
                    ]
                    for l in lines:
                        cl = l.strip(".,!?:;\"'()[]{}*`-_/ ")
                        cl = re.sub(r'^(?:Line\s*\d+|Draft\s*\d+|\d+|\*|\-|\:|\s)+', '', cl, flags=re.IGNORECASE).strip()
                        low = cl.lower()
                        if any(low.startswith(k) or k == low or k in low for k in ['poem_lines', 'poemlines', '{', '}', '[', ']']):
                            continue
                        if len(cl.split()) < 3:
                            continue
                        if re.search(r'[a-zA-Zà-ỹÀ-Ỹ]', cl):
                            clean_lines.append(cl)

                # Extract word tokens from clean lines
                raw_words = []
                for l in clean_lines[:4]:
                    w_list = [w.strip(".,!?:;\"'()[]*") for w in l.split() if w.strip()]
                    w_list = [w for w in w_list if w.lower() not in ['poem_lines', 'poemlines', 'json']]
                    if w_list:
                        raw_words.append(w_list)

                repaired_poem = []
                if rule_engine and len(raw_words) >= 4:
                    repaired_matrix = rule_engine.repair_poem(raw_words[:4])
                    repaired_poem = [" ".join(line) for line in repaired_matrix]
                else:
                    repaired_poem = [" ".join(w) for w in raw_words[:4]]

                response_data = {
                    "status": "success",
                    "model": "google/gemma-4-e2b",
                    "latency": latency,
                    "prompt": prompt,
                    "raw_lines": [" ".join(w) for w in raw_words[:4]],
                    "repaired_lines": repaired_poem,
                    "choices": lm_res.get('choices', [])
                }

                res_bytes = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(res_bytes)))
                self.end_headers()
                self.wfile.write(res_bytes)
                return

            except Exception as err:
                err_data = {"status": "error", "message": f"LM Studio Proxy Error: {str(err)}"}
                res_bytes = json.dumps(err_data).encode('utf-8')
                self.send_response(502)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(res_bytes)))
                self.end_headers()
                self.wfile.write(res_bytes)
                return

        super().do_POST()

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html#slide-23"
        print(f"\n=======================================================")
        print(f"🚀 PKA NLP SLIDES SERVER + LM STUDIO PROXY RUNNING")
        print(f"👉 Mở trình duyệt tại: {url}")
        print(f"👉 Thư mục Slide:      {CURRENT_DIR}")
        print(f"👉 LM Studio Server:   http://127.0.0.1:1234")
        print(f"👉 Proxy API Endpoint: http://localhost:{PORT}/api/generate")
        print(f"=======================================================\n")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Đã dừng server.")

if __name__ == "__main__":
    run()
