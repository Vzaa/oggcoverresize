# oggcoverresize

Resize large cover art images in .ogg audio files. Depends on mutagen and
PIL/Pillow.

## On a Single File

```
./oggcoverresize.py test.ogg
````

## Using fd to Run on All .ogg Files Recursively

```
fd -e ogg -x ./oggcoverresize.py
```

## Parameters
Default parameters can be modified in the script:

```python
SIZE = (256, 256)      # Target size
SIZE_MIN = (512, 512)  # Don't touch images smaller than this
JPEG_QUALITY = 90
```
