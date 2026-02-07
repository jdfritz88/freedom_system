"""
Quick script to replace all direct .value assignments with trigger_ui_update() calls
"""

import re

# Read the file
with open(r'F:\Apps\freedom_system\app_cabinet\text-generation-webui\extensions\boredom_monitor\all_injection_methods.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Replace blocks that set history.value then display.value
pattern1 = re.compile(
    r'shared\.gradio\[\'history\'\]\.value = ([\w_]+)\s*\n\s*'
    r'# UI REFRESH MECHANISM:.*?\n\s*'
    r'html = redraw_html\(([\w_]+),.*?\)\s*\n\s*'
    r'if \'display\' in shared\.gradio:\s*\n\s*'
    r'shared\.gradio\[\'display\'\]\.value = html',
    re.MULTILINE | re.DOTALL
)

replacement1 = r'# UI REFRESH MECHANISM: Use trigger_ui_update()\n                if trigger_ui_update(\1, state)'

content = pattern1.sub(replacement1, content)

# Write back
with open(r'F:\Apps\freedom_system\app_cabinet\text-generation-webui\extensions\boredom_monitor\all_injection_methods.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated all methods to use trigger_ui_update()")
