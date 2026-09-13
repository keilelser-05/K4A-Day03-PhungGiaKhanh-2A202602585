from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
required=['README.md','requirements.txt','.env.example','.gitignore','src/app.py','src/mcp_server.py','src/mcp_client.py','src/tools.py','src/providers.py','config/test_cases.json','docs/trace_eval.md','docs/trace_waterfall.json']
forbidden=['.env','credentials.json','token.json','.venv']
errors=[]
for rel in required:
    if not (ROOT/rel).exists(): errors.append(f'MISSING: {rel}')
for rel in forbidden:
    if (ROOT/rel).exists(): errors.append(f'SECRET/LOCAL FILE PRESENT: {rel}')
try:
    tests=json.loads((ROOT/'config/test_cases.json').read_text(encoding='utf-8'))
    if len(tests)!=5: errors.append(f'Expected 5 test cases, found {len(tests)}')
except Exception as e: errors.append(f'Invalid test_cases.json: {e}')
try:
    trace=json.loads((ROOT/'docs/trace_waterfall.json').read_text(encoding='utf-8'))
    if not trace: errors.append('trace_waterfall.json is empty')
except Exception as e: errors.append(f'Invalid trace_waterfall.json: {e}')
if errors:
    print('SUBMISSION CHECK: FAIL')
    for e in errors: print(' -',e)
    sys.exit(1)
print('SUBMISSION CHECK: PASS')
print('Required artifacts present; secrets/local env absent; 5 tests and trace available.')
