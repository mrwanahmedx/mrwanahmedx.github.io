"""Reproducible *technical* video compression/segmentation sample.
Synthetic fixture by default. Not a legal evidence authentication service.
Never alters input. Keeps input + output SHA-256 hashes and transformation records.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "vendor"))
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def run(parts):
    cp = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-threads", "2", *map(str, parts)],
                        cwd=ROOT, text=True, capture_output=True, errors="replace", timeout=150)
    if cp.returncode:
        raise RuntimeError("FFmpeg failed: " + cp.stderr[-1800:])
    return cp.stderr

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def detail(path):
    return {"name": path.name, "bytes":path.stat().st_size, "sha256":digest(path)}

def make_synthetic(path):
    # Frame pattern + tone, not a claim to demonstrate speech intelligibility.
    run(["-y","-f","lavfi","-i","testsrc2=size=640x360:rate=20",
         "-f","lavfi","-i","sine=frequency=440:sample_rate=44100",
         "-t","18","-map","0:v:0","-map","1:a:0",
         "-c:v","libx264","-preset","ultrafast","-crf","16",
         "-c:a","pcm_s16le",path])
    return path

def duration(path):
    cp=subprocess.run([FFMPEG,"-hide_banner","-i",str(path)],
                      capture_output=True,text=True,errors="replace",timeout=20)
    m=re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)",cp.stderr)
    if not m: raise RuntimeError("No readable duration in "+str(path))
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))

def process(source, out_dir, segment=9.0):
    source=Path(source).resolve()
    out_dir=Path(out_dir).resolve()
    out_dir.mkdir(parents=True,exist_ok=True)
    if not source.exists():raise FileNotFoundError(source)
    total=duration(source)
    if total<=0:raise RuntimeError("Zero-length input")
    source_hash=digest(source)
    cleaned=out_dir/"compressed_reference.mp4"
    flags=["-map","0:v:0","-map","0:a:0?","-c:v","libx264","-preset",
           "veryfast","-crf","28","-pix_fmt","yuv420p","-c:a","aac",
           "-b:a","128k","-movflags","+faststart"]
    run(["-y","-i",source,*flags,cleaned])
    segments=[]
    start=0.0
    while start<total-0.1:
        end=min(total,start+segment)
        part=out_dir/("segment_%02d.mp4"%(len(segments)+1))
        run(["-y","-ss",format(start,".3f"),"-i",source,"-t",format(end-start,".3f"),
             *flags,part])
        segments.append({**detail(part),"start_seconds":round(start,3),
                         "planned_end_seconds":round(end,3),
                         "actual_duration_seconds":duration(part)})
        start=end
    manifest={"purpose":"synthetic technical sample / no legal certification",
              "note":"Lossy re-encoding; original hash maintained for traceability; "
                     "do not claim compressed version is byte-identical or forensic original",
              "created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
              "original":{**detail(source),"duration_seconds":total},
              "compressed":{**detail(cleaned),"duration_seconds":duration(cleaned)},
              "segments":segments,"video_codec":"H.264 CRF28",
              "audio_codec":"AAC 128kbps when source contains audio"}
    (out_dir/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    assert digest(source)==source_hash, "INPUT MODIFIED"
    assert cleaned.stat().st_size < source.stat().st_size, "NO SIZE REDUCTION"
    assert len(segments)>=2, "NO SEGMENTS"
    assert abs(manifest["compressed"]["duration_seconds"]-total)<=0.2, "DURATION DRIFT"
    print("PASS: SOURCE_UNCHANGED",source.name,"SHA256",source_hash)
    print("PASS: COMPRESSED",source.stat().st_size,"->",cleaned.stat().st_size)
    print("PASS: SEGMENTS",len(segments),"MANIFEST",out_dir/"manifest.json")
    return manifest

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",default=None,help="Authorized input path (default: generated synthetic)")
    parser.add_argument("--segment-seconds",type=float,default=9)
    args=parser.parse_args()
    if not (1 <= args.segment_seconds <= 600): raise ValueError("segment_seconds invalid")
    source=Path(args.input) if args.input else make_synthetic(ROOT/"synthetic_original.mkv")
    process(source,ROOT/"demo_output",args.segment_seconds)

if __name__=="__main__":
    main()