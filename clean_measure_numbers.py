from operator import mod
import music21
import re
import os


def measureNumberShift(m21Score):
    firstMeasure = m21Score.parts[0].measure(0) or m21Score.parts[0].measure(1)
    isAnacrusis = True if firstMeasure.paddingLeft > 0.0 else False
    return 0 if isAnacrusis else 1


if __name__ == "__main__":
    for root, _, files in os.walk("."):
        for f in files:
            if not f.endswith(".krn"):
                continue
            path = os.path.join(root, f)
            score = music21.converter.parse(path)
            firstMeasureNumber = measureNumberShift(score)
            print(path, firstMeasureNumber)
            with open(path) as fd:
                lines = fd.readlines()
            modified = ""
            measure = firstMeasureNumber
            for idx, line in enumerate(lines):
                is_ts = re.match(r"\*M\d+/\d+", line)
                is_mm_change = re.match(r"(=\d*\t)+", line)
                if is_ts:
                    modified += line
                    nextline = lines[idx + 1]
                    if re.match(r"(=\d*\t)+", nextline):
                        continue
                    spines = len(line.split("\t"))
                    if measure != 0:
                        modified += "\t".join([f"={measure}"] * spines) + "\n"
                    measure += 1
                elif is_mm_change:
                    spines = len(line.split("\t"))
                    if measure != 0:
                        modified += "\t".join([f"={measure}"] * spines) + "\n"
                    measure += 1
                else:
                    modified += line
            with open(path, "w") as fd:
                fd.write(modified)
