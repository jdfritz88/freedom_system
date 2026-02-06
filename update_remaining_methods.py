"""
Script to update remaining methods 5-11 to use injection bridge
"""

updates = [
    # Method 5
    (
        'def method_5_gradio_client(message):\n'
        '    """\n'
        '    Method 5: Official Gradio Client Library\n'
        '    Uses gradio_client to connect and inject message\n'
        '    WITH UI refresh mechanism (client call + display update)\n'
        '    """',

        'def method_5_gradio_client(message):\n'
        '    """\n'
        '    Method 5: Official Gradio Client Library\n'
        '    Queues message via injection bridge\n'
        '    """'
    ),
    # Method 6
    (
        'def method_6_apscheduler(message):\n'
        '    """\n'
        '    Method 6: Server-Side State Management with APScheduler\n'
        '    Schedules background injection via APScheduler\n'
        '    WITH UI refresh mechanism (new chat greeting pattern)\n'
        '    """',

        'def method_6_apscheduler(message):\n'
        '    """\n'
        '    Method 6: Server-Side State Management with APScheduler\n'
        '    Queues message via injection bridge\n'
        '    """'
    ),
    # Method 7
    (
        'def method_7_websocket_sse(message):\n'
        '    """\n'
        '    Method 7: WebSocket/SSE Protocol\n'
        '    Uses streaming to inject message\n'
        '    WITH UI refresh mechanism (new chat greeting pattern)\n'
        '    """',

        'def method_7_websocket_sse(message):\n'
        '    """\n'
        '    Method 7: WebSocket/SSE Protocol\n'
        '    Queues message via injection bridge\n'
        '    """'
    ),
    # Method 8
    (
        'def method_8_selenium(message):\n'
        '    """\n'
        '    Method 8: Selenium Automation\n'
        '    Uses Selenium WebDriver to automate browser interaction\n'
        '    WITH UI refresh mechanism (Selenium triggers normal UI flow which includes display update)\n'
        '    """',

        'def method_8_selenium(message):\n'
        '    """\n'
        '    Method 8: Selenium Automation\n'
        '    Queues message via injection bridge\n'
        '    """'
    ),
    # Method 9
    (
        'def method_9_blocks_custom(message):\n'
        '    """\n'
        '    Method 9: Blocks-Based Custom Implementation\n'
        '    Direct manipulation of Gradio Blocks components\n'
        '    WITH UI refresh mechanism (updates history + display)\n'
        '    """',

        'def method_9_blocks_custom(message):\n'
        '    """\n'
        '    Method 9: Blocks-Based Custom Implementation\n'
        '    Queues message via injection bridge\n'
        '    """'
    ),
    # Method 10
    (
        'def method_10_idle_monitor(message):\n'
        '    """\n'
        '    Method 10: Generic Idle Monitor with External Threading\n'
        '    Uses threading to monitor and inject during idle periods\n'
        '    WITH UI refresh mechanism (new chat greeting pattern)\n'
        '    """',

        'def method_10_idle_monitor(message):\n'
        '    """\n'
        '    Method 10: Generic Idle Monitor with External Threading\n'
        '    Queues message via injection bridge\n'
        '    """'
    ),
    # Method 11
    (
        'def method_11_direct_ui_manipulation(message):\n'
        '    """\n'
        '    Method 11: Direct UI Component Manipulation\n'
        '    Directly manipulates Gradio component values\n'
        '    WITH UI refresh mechanism (new chat greeting pattern)\n'
        '    """',

        'def method_11_direct_ui_manipulation(message):\n'
        '    """\n'
        '    Method 11: Direct UI Component Manipulation\n'
        '    Queues message via injection bridge\n'
        '    """'
    ),
]

# Read file
filepath = r'F:\Apps\freedom_system\freedom_system_2000\text-generation-webui\extensions\boredom_monitor\all_injection_methods.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Apply updates
for old, new in updates:
    content = content.replace(old, new)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated method docstrings 5-11")
