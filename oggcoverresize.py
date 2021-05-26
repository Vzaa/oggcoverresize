#!/bin/env python3

import io
import sys
import base64
import PIL
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import Picture, error as FLACError
from PIL import Image

SIZE = (256, 256)      # Target size
SIZE_MIN = (512, 512)  # Don't touch images smaller than this
JPEG_QUALITY = 90
# Using lower case key has issues for some reason?
MBP_KEY = "METADATA_BLOCK_PICTURE"


def main():
    filename = sys.argv[1]
    ogg_file = OggVorbis(filename)

    mbps = ogg_file.get(MBP_KEY, [])
    if len(mbps) == 0:
        print(f"No img found in {filename}")
        return

    modified = False

    del ogg_file[MBP_KEY]

    for b64_data in mbps:
        try:
            data = base64.b64decode(b64_data)
        except (TypeError, ValueError):
            continue

        try:
            picture_org = Picture(data)
        except FLACError:
            continue

        with Image.open(io.BytesIO(picture_org.data)) as img:
            if img.width <= SIZE_MIN[0] and img.height <= SIZE_MIN[1]:
                print(f"{filename}: Skip img with type {picture_org.type}, "
                      f"{img.width}x{img.height} is smaller than limit "
                      f"{SIZE_MIN[0]}x{SIZE_MIN[1]}")
                continue
            with io.BytesIO() as of:
                print(f"{filename}: Resize img with type {picture_org.type}, "
                      f"{img.width}x{img.height} to {SIZE[0]}x{SIZE[1]}")
                img.thumbnail(SIZE, PIL.Image.LANCZOS)
                img = img.convert('RGB')
                img.save(of, "JPEG", quality=JPEG_QUALITY)
                of.seek(0)
                buf = of.read()
                w = img.width
                h = img.height
                bpp = 24

        modified = True

        picture = Picture()
        picture.data = buf
        picture.type = picture_org.type
        picture.desc = picture_org.desc
        picture.mime = u"image/jpeg"
        picture.width = w
        picture.height = h
        picture.depth = bpp

        picture_data = picture.write()
        encoded_data = base64.b64encode(picture_data)
        vcomment_value = encoded_data.decode("ascii")
        mbpl = ogg_file.get(MBP_KEY, [])
        mbpl.append(vcomment_value)
        ogg_file[MBP_KEY] = mbpl

    if modified:
        print(f"Modifying {filename}")
        ogg_file.save()
    else:
        print(f"Did not modify {filename}")


if __name__ == "__main__":
    main()
