#!/usr/bin/env python3

# USAGE:
# - cut gv video file with `-s` (skip frames) and `-n` (frame count) option
#
# ```bash
# $ python gv-video-cutter.py test.gv -s 10 -n 60 -o cut.gv
# ```

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
    parser = argparse.ArgumentParser(description='GV video cutter',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('video_file', help='.gv video file')
    parser.add_argument('-s', '--skip', type=int, default=0, help='skip frames')
    parser.add_argument('-n', '--count', type=int, default=30, help='frame count')
    parser.add_argument('-o', '--output', required=True, help='output file name')

    args = parser.parse_args()
    skip_frames = args.skip
    expected_frame_count = args.count
    output_file = args.output

    if not os.path.isfile(args.video_file):
        print('Error: video file not found')
        return

    with open(args.video_file, 'rb') as f:
        data = f.read(24)
        if len(data) < 24:
            print('Error: video file is too small')
            return

        width, height, frame_count, fps, fmt, frame_bytes = struct.unpack('IIIfII', data)

        # print('addresses and sizes:')

        # eof - (frame count) * 16: address list

        real_frame_count = 0
        frame_infos = []

        f.seek(-frame_count * 16, os.SEEK_END)
        # first, create dictionary
        addr_size_dict = {}
        for i in range(frame_count):
            address, size = struct.unpack('QQ', f.read(16))
            addr_size_dict[address] = size

        for i in range(frame_count):
            if i < skip_frames:
                continue
            if i >= skip_frames + expected_frame_count:
                break

            real_frame_count += 1

            address, size = list(addr_size_dict.items())[i]
            # print('%d: address %d, size %d' % (i, address, size))
            frame_infos.append((address, size))

        print('width: %d' % width)
        print('height: %d' % height)
        print('frame count: %d' % real_frame_count)
        print('fps: %f' % fps)
        print('format: %s' % formats[fmt])
        print('frame bytes: %d' % frame_bytes)

        # write header
        with open(output_file, 'wb') as out:
            out.write(struct.pack('IIIfII', width, height, real_frame_count, fps, fmt, frame_bytes))

            new_frame_infos = []
            # write frame data
            i = 0
            for address, size in frame_infos:
                f.seek(address, os.SEEK_SET)
                data = f.read(size)
                if len(data) < size:
                    print('Error: video file is too small')
                    return
                
                current_address = out.tell()
                out.write(data)

                if i + 1 < len(frame_infos):
                    # write zero till next address
                    next_address = frame_infos[i+1][0]
                    zero_size = next_address - (address + size)
                    out.write(b'\x00' * zero_size)

                new_frame_infos.append((current_address, size))

                i += 1


            # write frame infos
            for address, size in new_frame_infos:
                out.write(struct.pack('QQ', address, size))

if __name__ == '__main__':
    main()