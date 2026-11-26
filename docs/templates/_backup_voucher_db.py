import sqlite3, sys
src, dst = sys.argv[1], sys.argv[2]
with sqlite3.connect(src) as source:
    with sqlite3.connect(dst) as target:
        source.backup(target)
        target.commit()
print("Backup created:", dst)
