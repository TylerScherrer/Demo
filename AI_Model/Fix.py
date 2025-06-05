from pathlib import Path

cache_dir = Path(r"C:\Users\Tyler\.cache\huggingface\hub\models--microsoft--phi-2\snapshots")

for snapshot in cache_dir.iterdir():
    if snapshot.is_dir():
        files = list(snapshot.glob("*"))
        print(f"\nSnapshot: {snapshot}")
        for file in files:
            print("-", file.name)
