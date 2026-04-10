
#!/usr/bin/env python3
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\memory\database')

try:
    from hybrid_memory import get_memory
    mem = get_memory()
    print("Stats:", mem.get_stats())
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()

