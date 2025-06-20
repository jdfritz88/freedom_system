try:
    with open("F:/Apps/freedom_system/autosave_test.txt", "w") as f:
        f.write("Autosave test successful.\n")
    print("✅ File written successfully.")
except Exception as e:
    print(f"❌ Write failed: {e}")
