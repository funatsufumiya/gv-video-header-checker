#!/usr/bin/env python3

## GV Video to Sequence
## Usage: gv-video-to-seq.py <video file> <output directory>
## Output: <output directory>/frame_%05d.png

# NOTE:
# pip install lz4 texture2ddecoder opencv-python pillow numpy matplotlib

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
import gc
import os
import struct
import argparse
import texture2ddecoder
import lz4.frame
import lz4.block
from matplotlib import pyplot as plt
import numpy as np
import cv2
from PIL import Image

def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2RGB)
        # new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

formats = {
    1: 'DXT1',
    3: 'DXT3',
    5: 'DXT5',
    7: 'BC7'
}

def decode_dxt(data, width, height, fmt):
    # lz4_decoded_data = lz4.frame.decompress(data)
    if fmt == 1:
        lz4_decoded_data = lz4.block.decompress(data, uncompressed_size=width * height * 4)
        return texture2ddecoder.decode_bc1(lz4_decoded_data, width, height)
    elif fmt == 3:
        lz4_decoded_data = lz4.block.decompress(data, uncompressed_size=width * height * 4)
        return texture2ddecoder.decode_bc2(lz4_decoded_data, width, height)
    elif fmt == 5:
        lz4_decoded_data = lz4.block.decompress(data, uncompressed_size=width * height * 4)
        return texture2ddecoder.decode_bc3(lz4_decoded_data, width, height)
    elif fmt == 7:
        lz4_decoded_data = lz4.block.decompress(data, uncompressed_size=width * height * 4)
        return texture2ddecoder.decode_bc7(lz4_decoded_data, width, height)
    else:
        print('Error: unknown format')
        return
    
def main():
    parser = argparse.ArgumentParser(description='Convert gv video file to image sequence',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
                                    
    parser.add_argument('video_file', help='.gv video file')
    parser.add_argument('output_dir', help='output directory')
    args = parser.parse_args()

    if not os.path.isfile(args.video_file):
        print('Error: video file not found')
        return
    
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)

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

        print('')
        print('Converting...')

        try:
            for i in range(frame_count):
                f.seek(-frame_count * 16 + i * 16, os.SEEK_END)
                address, size = struct.unpack('QQ', f.read(16))
                # print('%d: address %d, size %d' % (i, address, size))

                f.seek(address, os.SEEK_SET)
                data = f.read(size)
                if len(data) < size:
                    print('Error: video file is too small')
                    return
                decoded_data = decode_dxt(data, width, height, fmt)
                del data
                if fmt == 1:
                    dec_img = Image.frombytes("RGBA", (width, height), decoded_data, 'raw', ("BGRA"))
                else:
                    dec_img = Image.frombytes("RGBA", (width, height), decoded_data, 'raw', ("BGRA"))
                im = pil2cv(dec_img)
                cv2.imwrite(os.path.join(args.output_dir, 'frame_%05d.png' % i), im)
                # print('frame: %d' % i)
                del decoded_data
                del dec_img
                gc.collect()
        except KeyboardInterrupt:
            sys.exit(1)

        print('Done')

if __name__ == '__main__':
    main()