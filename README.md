# GV Video Header Checker (and viewer)

Check the header of gv video file: https://github.com/Ushio/ofxExtremeGpuVideo?tab=readme-ov-file#binary-file-format-gv

## Usage

- Header Checker: `gv-video-header-checker.py`

```txt
usage: gv-video-header-checker.py [-h] video_file

positional arguments:
  video_file  .gv video file

options:
  -h, --help  show this help message and exit
```

and same as:

- Address Checker: `gv-video-address-checker.py`
- Viewer: `gv-video-viewer.py`
- Cutter: `gv-video-cutter.py`

## Requirements for viewer

```bash
pip install lz4
pip install texture2ddecoder
pip install opencv-python
pip install pillow
pip install numpy
pip install matplotlib
```

## Example

### Header Checker

```bash
$ python gv-video-header-checker.py test.gv
```

```txt
width: 6000
height: 3999
frame count: 501
fps: 30.000000
format: DXT5
frame bytes: 24000000
```

### Address Checker

```bash
$ python gv-video-address-checker.py test.gv
```

```txt
width: 1280
height: 720
frame count: 163
fps: 30.000000
format: DXT1
frame bytes: 460800
addresses and sizes:
0: address 24, size 116401
1: address 116425, size 61550
2: address 177975, size 69337
3: address 247312, size 99743
4: address 347055, size 99242
...(print all addresses)
```

### Viewer

- view each frames with `cv2` (press any key to next frame, ESC to exit)
- save to file with `-o` option

```bash
$ python gv-video-viewer.py test.gv

# or skip frames with
# $ python gv-video-viewer.py test.gv -s 10

# or save to file with
# $ python gv-video-viewer.py test.gv -o output.png
```

### Cutter

- cut gv video file with `-s` (skip frames) and `-n` (frame count) option

```bash
$ python gv-video-cutter.py test.gv -s 10 -n 60 -o cut.gv
```
