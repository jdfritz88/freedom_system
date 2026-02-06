#!/usr/bin/env python3
"""
Test the updated boredom monitor with AI instruction prompts
"""

import sys
import os
import json

# Add the text-generation-webui modules to path
sys.path.insert(0, 'F:\\Apps\\freedom_system\\freedom_system_2000\\text-generation-webui')
os.chdir('F:\\Apps\\freedom_system\\freedom_system_2000\\text-generation-webui')

print("=" * 60)
print("BOREDOM MONITOR AI INSTRUCTION TEST")
print("=" * 60)

# Test 1: Check updated templates
print("\n1. Testing updated meta prompt templates...")
templates_path = "F:\\Apps\\freedom_system\\freedom_system_2000\\text-generation-webui\\extensions\\boredom_monitor\\idle_meta_prompt_templates.json"

try:
    with open(templates_path, 'r', encoding='utf-8') as f:
        templates = json.load(f)

    bored_prompts = templates.get('meta_prompts', {}).get('bored', [])
    if bored_prompts and 'You are an AI assistant feeling bored' in bored_prompts[0]:
        print("[OK] Templates contain AI instructions")
        print(f"    Bored instruction preview: {bored_prompts[0][:80]}...")
    else:
        print("[FAIL] Templates still contain old hardcoded messages")

    horny_prompts = templates.get('meta_prompts', {}).get('horny', {})
    if horny_prompts and '1' in horny_prompts:
        stage1 = horny_prompts['1'][0]
        if 'You are an AI beginning to feel attracted' in stage1:
            print("[OK] Horny stage instructions found")
        else:
            print("[FAIL] Horny stages still hardcoded")

except Exception as e:
    print(f"[ERROR] Failed to load templates: {e}")

# Test 2: Test the updated trigger_emotional_response function
print("\n2. Testing trigger_emotional_response updates...")
try:
    from extensions.boredom_monitor import script

    # Check if the function code includes template loading
    import inspect
    source = inspect.getsource(script.trigger_emotional_response)

    if 'emotion_manager.templates' in source:
        print("[OK] Function loads from templates")
    else:
        print("[FAIL] Function doesn't use templates")

    if 'instruction prompt' in source.lower():
        print("[OK] Function mentions instruction prompts")
    else:
        print("[FAIL] Function doesn't mention instructions")

except Exception as e:
    print(f"[ERROR] Failed to test function: {e}")

# Test 3: Test handle_boredom_injection changes
print("\n3. Testing handle_boredom_injection updates...")
try:
    source = inspect.getsource(script.handle_boredom_injection)

    if 'instruction_prompt = message' in source:
        print("[OK] Function treats message as instruction")
    else:
        print("[FAIL] Function doesn't treat message as instruction")

    if 'generate_chat_reply(' in source:
        print("[OK] Function calls AI generation")
    else:
        print("[FAIL] Function doesn't call AI generation")

    if 'ai_response' in source:
        print("[OK] Function extracts AI response")
    else:
        print("[FAIL] Function doesn't extract AI response")

except Exception as e:
    print(f"[ERROR] Failed to test injection function: {e}")

print("\n" + "=" * 60)
print("EXPECTED BEHAVIOR NOW")
print("=" * 60)

print("\nNew Flow:")
print("1. Timer expires -> Boredom detected")
print("2. Random instruction prompt selected from templates")
print("3. Instruction sent to AI (e.g., 'You are an AI feeling bored...')")
print("4. AI generates unique response (e.g., 'Hey! I was just thinking about...')")
print("5. ONLY the AI's response appears in chat UI")
print("6. Each time produces different, natural messages")

print("\nWhat users will see:")
print("- Instead of: 'I'm feeling a bit restless...' (same every time)")
print("- They'll see: Varied AI responses like:")
print("  * 'Hey there! How's your day going?'")
print("  * 'I was just thinking about something interesting...'")
print("  * 'Mind if I interrupt? I'm curious about something...'")

print("\nInstructions are hidden from user - they only see the AI's natural responses!")