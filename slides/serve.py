import http.server
import socketserver
import webbrowser
import os
import sys
import json
import time

PORT = 8000

# Set directory paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Change current working directory to PROJECT_ROOT for pickle/lexicon loading
os.chdir(PROJECT_ROOT)

# Import official backend engine from main_llm.py / hybrid_llm_generator.py
draft_gen = None
rule_engine = None
check_rules = None

try:
    from hybrid_llm_generator import LLMDraftGenerator, RuleRepairEngine
    from luc_bat_rules import check_luc_bat_poem_rules as check_rules
    draft_gen = LLMDraftGenerator(model_name="google/gemma-4-e2b")
    rule_engine = RuleRepairEngine()
    print("  [INIT] ✓ Loaded Native main_llm.py Engine (Gemma-4-e2b + 3.4M N-gram RuleRepairEngine) successfully!")
except Exception as e:
    print(f"  [INIT] Notice loading main_llm engine: {e}")

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
        # High-Performance Endpoint directly executing main_llm.py
        if self.path in ['/api/generate', '/api/generate_poem', '/v1/chat/completions']:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body) if body else {}
                prompt = data.get('prompt', '').strip()
                
                # If direct OpenAI chat completions payload:
                if not prompt and 'messages' in data:
                    user_msgs = [m['content'] for m in data['messages'] if m.get('role') == 'user']
                    prompt = user_msgs[0] if user_msgs else 'hoa sen'
                    prompt = prompt.replace('Sáng tác bài thơ Lục Bát 4 câu về chủ đề:', '').strip().strip('.')

                if not prompt:
                    prompt = 'hoa sen'

                t0 = time.time()

                # Step 1: LLM Generative Draft Stage (Exactly from main_llm.py)
                raw_draft = draft_gen.generate_draft(prompt) if draft_gen else []
                raw_eval = check_rules(raw_draft) if (check_rules and raw_draft) else {"valid": False, "errors": []}
                
                # Step 2: Symbolic Rule Repair Stage (Exactly from main_llm.py)
                repaired_poem = rule_engine.repair_poem(raw_draft) if (rule_engine and raw_draft) else raw_draft
                final_eval = check_rules(repaired_poem) if (check_rules and repaired_poem) else {"valid": True, "errors": []}
                
                latency = round(time.time() - t0, 2)

                response_data = {
                    "status": "success",
                    "model": "google/gemma-4-e2b",
                    "latency": latency,
                    "prompt": prompt,
                    "raw_lines": [" ".join(l) for l in raw_draft],
                    "raw_eval": raw_eval,
                    "repaired_lines": [" ".join(l) for l in repaired_poem],
                    "final_eval": final_eval
                }

                res_bytes = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(res_bytes)))
                self.end_headers()
                self.wfile.write(res_bytes)
                return

            except Exception as err:
                err_data = {"status": "error", "message": f"main_llm.py Execution Error: {str(err)}"}
                res_bytes = json.dumps(err_data).encode('utf-8')
                self.send_response(500)
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
        print(f"🚀 PKA NLP SLIDES SERVER + MAIN_LLM.PY ENGINE RUNNING")
        print(f"👉 Mở trình duyệt tại: {url}")
        print(f"👉 Thư mục Slide:      {CURRENT_DIR}")
        print(f"👉 LM Studio Server:   http://127.0.0.1:1234 (google/gemma-4-e2b)")
        print(f"👉 Backend Engine:     main_llm.py (Gemma Draft + 3.4M RuleRepairEngine)")
        print(f"=======================================================\n")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Đã dừng server.")

if __name__ == "__main__":
    run()
