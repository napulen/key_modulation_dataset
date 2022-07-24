from mailbox import MMDFMessage
import music21
import harmalysis
import sys
import os
import pprint
import pandas as pd
import re


def convert_m21key(key):
    k, m = key.split()
    if m == "minor":
        return k.lower()
    return k


def m121fy_rn(rnnum):
    if rnnum in ["iio7", "iio65", "iio43", "iio42", "iio2"]:
        rnnum = rnnum.replace("iio", "iiø")
    return rnnum


def makeRntxtHeader(metadata):
    analyst = (
        "Napoles Lopez et al. See https://github.com/DDMAL/key_modulation_dataset"
    )
    composer = metadata.composer
    title = metadata.title
    movementNumber = metadata.movementNumber
    movementName = metadata.movementName
    header = f"Composer: {composer}\n"
    header += f"Title: {title} - {movementNumber}: {movementName}\n"
    header += f"Analyst: {analyst}\n"
    header += f"Proofreader: Automated translation by Néstor Nápoles López\n"
    return header


def makeRntxtBody(tss, ms):
    body = ""
    allMeasures = list(sorted(set(list(tss.keys()) + list(ms.keys()))))
    for m in allMeasures:
        if m in tss:
            body += f"\nTime Signature: {tss[m]}\n\n"
        if m in ms:
            line = f"m{m} "
            for b, (key, rn) in ms[m].items():
                beat = f"b{b} " if b != 1 else ""
                if key:
                    key = key.replace("-", "b")
                    line += f"{beat}{key}: {rn} "
                else:
                    line += f"{beat}{rn} "
            if re.match(r"m(\d)+ $", line):
                continue
            body += f"{line[:-1]}\n"
    return body


def get_dataframe_from_file(score):
    tss = {}
    mms = {}
    for ts in score.flat.getElementsByClass("TimeSignature"):
        m = ts.measureNumber
        tss[m] = ts.ratioString
    labels = {}
    prevChord = ((), "", "")
    prevKey = ""
    caut67 = music21.roman.Minor67Default.CAUTIONARY
    for n in score.flat.notesAndRests:
        if n.lyric:
            label = harmalysis.parse(n.lyric)
            try:
                chordlabel = harmalysis.parse(str(label.chord), syntax='chordlabel')
            except:
                chordlabel = 'Unknown chord'
                pass
            offset = eval(str(n.offset)) # Resolving triplets (fractions) into floats
            beat = round(float(n.beat), 3)
            beat = int(beat) if beat.is_integer() else beat
            mm = n.measureNumber
            pcset = tuple(sorted(label.chord.get_pitch_classes()))
            local_key = str(label.main_key)
            tonicized_key = str(label.secondary_key) if label.secondary_key else local_key
            inversion = label.chord.inversion
            rnnum = n.lyric.split(":")[-1]
            rnnum = rnnum.split("/", 1)
            tonicizations = ""
            if len(rnnum) > 1:
                rnnum, tonicizations = rnnum
            else:
                rnnum = rnnum[0]
            rnnum = m121fy_rn(rnnum)
            rn = f"{rnnum}{'/' if tonicizations else ''}{tonicizations}"
            if (pcset, local_key, tonicized_key, inversion, "Cad64" in n.lyric) == prevChord:
                continue
            prevChord = (pcset, local_key, tonicized_key, inversion, "Cad64" in n.lyric)
            m21key = convert_m21key(local_key)
            if mm not in mms:
                mms[mm] = {}
            if beat not in mms[mm]:
                key = None if m21key == prevKey else m21key
                mms[mm][beat] = (key, rn)
            m21rn = music21.roman.RomanNumeral(rnnum, convert_m21key(tonicized_key), seventhMinor=caut67)
            m21pcset = tuple(sorted(m21rn.pitchClasses))
            if pcset != m21pcset:
                print(f"{n.lyric} mistranslates in music21: {pcset} != {m21pcset}")
            labels[offset] = {
                "measure": mm,
                "beat": beat,
                'annotation': n.lyric,
                "rn": f"{rnnum}{'/' if tonicizations else ''}{tonicizations}",
                # 'chord_label': chordlabel,
                'pitch_classes': pcset,
                'local_key': local_key,
                # 'tonicized_key': tonicized_key,
                'inversion': inversion,
                # "m21rn": m21rn.figure,
                # "m21pcset": m21pcset,
            }
            prevKey = m21key
    df = pd.DataFrame(labels).transpose()
    return df, tss, mms


if __name__ == '__main__':
    for root, _, files in os.walk("."):
        for f in files:
            if not f.endswith(".krn"):
                continue
            path = os.path.join(root, f)
            pathslugified = f"moduton-{path.replace('./', '').replace('/', '-').replace('.krn', '')}"
            print(path)
            score = music21.converter.parse(path)
            df, tss, mss = get_dataframe_from_file(score)
            header = makeRntxtHeader(score.metadata)
            body = makeRntxtBody(tss, mss)
            with open(f"rntxt/{pathslugified}.rntxt", "w") as f:
                f.write(header)
                f.write(body)
            print(df, tss, mss)
