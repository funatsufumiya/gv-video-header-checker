#!/usr/bin/env python3

# gv-video-header-checker.py
# Check the header of gv video file
# Usage: gv-video-header-checker.py <video file>

# NOTE:
# gv file format
# 0: uint32_t width
# 4: uint32_t height
# 8: uint32_t frame count
# 12: float fps
# 16: uint32_t fmt (DXT1 = 1, DXT3 = 3, DXT5 = 5, BC7 = 7)
# 20: uint32_t frame bytes
# // 24: raw frame storage (lz4 compressed)
# eof - (frame count) * 16: [(uint64_t, uint64_t)..<frame count] (address, size) of lz4, address is zero based from file head


import sys
import os
import struct
import argparse

formats = {
    1: 'DXT1',
    3: 'DXT3',
    5: 'DXT5',
    7: 'BC7'
}

def main():
    parser = argparse.ArgumentParser(description='Check the header and show addresses list of gv video file: https://github.com/Ushio/ofxExtremeGpuVideo?tab=readme-ov-file#binary-file-format-gv',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('video_file', help='.gv video file')

    args = parser.parse_args()

    if not os.path.isfile(args.video_file):
        print('Error: video file not found')
        return

    with open(args.video_file, 'rb') as f:
        data = f.read(24)
        if len(data) < 24:
            print('Error: video file is too small')
            return

        width, height, frame_count, fps, fmt, frame_bytes = struct.unpack('IIIfII', data)

        print('width: %d' % width)
        print('height: %d' % height)
        print('frame count: %d' % frame_count)
        print('fps: %f' % fps)
        print('format: %s' % formats[fmt])
        print('frame bytes: %d' % frame_bytes)
        print('addresses and sizes:')

        # eof - (frame count) * 16: address list
        f.seek(-frame_count * 16, os.SEEK_END)
        for i in range(frame_count):
            address, size = struct.unpack('QQ', f.read(16))
            print('%d: address %d, size %d' % (i, address, size))





if __name__ == '__main__':
    main()