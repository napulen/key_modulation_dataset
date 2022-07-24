import os
import subprocess

if __name__ == '__main__':
    for root, _, files in os.walk("."):
        for f in files:
            if not f.endswith(".krn"):
                continue
            path = os.path.join(root, f)
            pathslugified = f"keymodt-{path.replace('./', '').replace('/', '-').replace('.krn', '')}"
            print(path)
            subprocess.run(f"python3 -m converter21 -f humdrum -t musicxml {path} mxl/{pathslugified}.musicxml".split())
