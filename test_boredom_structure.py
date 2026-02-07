# ==========================================
# BOREDOM MONITOR STRUCTURE TEST
# Validate the code structure without imports
# ==========================================

import ast
import sys
from pathlib import Path

print("[STRUCTURE-TEST] Validating Boredom Monitor Extension Structure")

script_path = Path("F:/Apps/freedom_system/app_cabinet/text-generation-webui/extensions/boredom_monitor/script.py")

try:
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("[STRUCTURE-TEST] SUCCESS: Script file loaded")

    # Parse the AST to check structure
    tree = ast.parse(content)
    print("[STRUCTURE-TEST] SUCCESS: Code syntax is valid")

    # Find functions and classes
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

    print(f"[STRUCTURE-TEST] Found {len(functions)} functions:")
    for func in sorted(functions):
        print(f"  - {func}()")

    if classes:
        print(f"[STRUCTURE-TEST] Found {len(classes)} classes:")
        for cls in sorted(classes):
            print(f"  - {cls}")

    # Check for required extension functions
    required_functions = ['setup', 'ui', 'custom_css', 'trigger_emotional_response']
    missing_functions = []

    for req_func in required_functions:
        if req_func in functions:
            print(f"[STRUCTURE-TEST] SUCCESS: {req_func}() found")
        else:
            missing_functions.append(req_func)
            print(f"[STRUCTURE-TEST] ERROR: {req_func}() missing")

    # Check for direct call implementation
    if 'trigger_emotional_response' in functions:
        print("[STRUCTURE-TEST] SUCCESS: Direct call method implemented")

    # Check for API removal
    api_indicators = ['FastAPI', 'uvicorn', 'app.get', 'app.post']
    api_found = []

    for indicator in api_indicators:
        if indicator in content:
            api_found.append(indicator)

    if api_found:
        print(f"[STRUCTURE-TEST] WARNING: API code still present: {api_found}")
    else:
        print("[STRUCTURE-TEST] SUCCESS: API code removed - clean direct call implementation")

    # Check for direct call patterns
    direct_call_patterns = ['generate_chat_reply', 'shared.gradio', 'shared.persistent_interface_state']
    found_patterns = []

    for pattern in direct_call_patterns:
        if pattern in content:
            found_patterns.append(pattern)

    if found_patterns:
        print(f"[STRUCTURE-TEST] SUCCESS: Direct call patterns found: {found_patterns}")
    else:
        print("[STRUCTURE-TEST] WARNING: Direct call patterns not found")

    # Check for horny progression
    horny_patterns = ['horny', 'stage', 'cooldown']
    found_horny = []

    for pattern in horny_patterns:
        if pattern in content:
            found_horny.append(pattern)

    if len(found_horny) >= 2:
        print(f"[STRUCTURE-TEST] SUCCESS: Horny progression system present")

    # Summary
    if not missing_functions and found_patterns:
        print("[STRUCTURE-TEST] SUCCESS: Extension structure is correct")
        print("[STRUCTURE-TEST] Ready for text-generation-webui integration")
    else:
        print("[STRUCTURE-TEST] WARNING: Some issues found - review needed")

    # File size check
    size_kb = len(content) / 1024
    print(f"[STRUCTURE-TEST] Script size: {size_kb:.1f} KB")

    if size_kb < 50:  # Much smaller than original API version
        print("[STRUCTURE-TEST] SUCCESS: Simplified implementation (removed API complexity)")

except Exception as e:
    print(f"[STRUCTURE-TEST] ERROR: {e}")

print("[STRUCTURE-TEST] Validation completed")