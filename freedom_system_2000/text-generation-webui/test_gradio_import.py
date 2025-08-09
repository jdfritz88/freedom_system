import sys
print("Testing Gradio import order issue...")

# Test 1: Direct import
print("\n1. Testing direct gradio import:")
import gradio as gr
print(f"   Gradio version: {gr.__version__}")
print(f"   Has themes: {hasattr(gr, 'themes')}")

# Test 2: Import through modules
print("\n2. Testing import through modules:")
from modules import shared
print("   shared imported successfully")

# Test 3: Import block_requests (this triggers ui import)
print("\n3. Testing block_requests import (triggers ui import):")
try:
    from modules.block_requests import OpenMonkeyPatch, RequestBlocker
    print("   block_requests imported successfully")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Check gradio themes after all imports
print("\n4. Checking gradio themes after all imports:")
print(f"   Has themes: {hasattr(gr, 'themes')}")
if hasattr(gr, 'themes'):
    try:
        theme = gr.themes.Default()
        print("   Successfully created Default theme")
    except Exception as e:
        print(f"   ERROR creating theme: {e}")