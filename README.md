# GV Video Header Checker

Check the header of gv video file: https://github.com/Ushio/ofxExtremeGpuVideo?tab=readme-ov-file#binary-file-format-gv

## Usage

```txt
usage: gv-video-header-checker.py [-h] video_file

positional arguments:
  video_file  .gv video file

options:
  -h, --help  show this help message and exit
```

## Example

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