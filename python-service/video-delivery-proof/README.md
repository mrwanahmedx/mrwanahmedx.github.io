# Synthetic video compression and segmentation — verified technical demonstration

**Scope:** reproducible original-preserving video transformation, not legal-forensic certification or evidence authentication.

## Tested on October 9, 2026
- Input synthetic MKV: 18 seconds, 6,357,526 bytes.
- Compressed MP4 (H.264 CRF28 video, AAC 128kbps): 1,125,316 bytes, 18.0 seconds; **82.3% smaller**.
- Segmented: two 9.0-second MP4 clips, both with independent SHA-256s.
- Input SHA-256 unchanged after processing. A JSON manifest records original and output hashes, sizes, planned segment boundaries, and durations.
- Passed actual local execution using FFmpeg via Python `imageio-ffmpeg` under the D: project vendor directory.
- All footage is **synthetic** and audio is a **tone**. No human speech clarity/quality has been tested. The original stays untouched; outputs are re-encodings, **not bit-identical to the original**.

## Usage
Install Python 3.12+, then:

```
python -m pip install imageio-ffmpeg
python compress_and_segment.py
python compress_and_segment.py --input "D:\\authorized\\sample.mov" --segment-seconds 30
```

The second command processes only an input the operator is authorized to use, writes to `demo_output`, and leaves the original file unchanged. The sample mode creates original synthetic footage and a tone if no input argument is given.

## Practical delivery checklist
1. Receive the source using an authorized secure file transfer; record original file hash and make a backup before conversion.
2. Agree on the allowed editing/compression policy, required segment boundaries, codec/container and permitted handling of audio for the specific recipient.
3. Convert, segment, inspect frame boundaries and listen to actual dialogue (speech intelligibility **not** proven by the synthetic test).
4. Record manifests, filenames, hashes, durations and output file sizes. Maintain chain-of-custody records externally where required.
5. Obtain confirmation that the intended recipient accepts the format and transformations. Only qualified legal personnel should assess admissibility or authenticity.

No paid client work is claimed. No real court evidence, private recordings, or customer data were used. No claim is made that reduced video preserves every original visual or audio detail.

Source: `compress_and_segment.py` | Evidence: `demo_output/manifest.json`