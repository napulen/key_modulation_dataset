import os
import subprocess
import shutil

if __name__ == '__main__':
    for root, _, files in os.walk("."):
        for f in files:
            if not f.endswith(".krn"):
                continue
            path = os.path.join(root, f)
            pathslugified = f"moduton-{path.replace('./', '').replace('/', '-').replace('.krn', '')}"
            print(path)
            subprocess.run(f"python3 -m converter21 -f humdrum -t musicxml {path} mxl/{pathslugified}.musicxml".split())
            # shutil.move(f"{path.replace('.krn', '.musicxml')}", f"mxl/{pathslugified}.musicxml")
