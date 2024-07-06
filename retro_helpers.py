from pathlib import Path
from PIL import Image
from typing import Literal

#   Define Quantize methods list
PIL_QUANTIZE_MODES = Literal[
    "Median Cut",
    "Max Coverage",
    "Fast Octree",
]

#   Define Quantize methods map
PIL_QUANTIZE_MAP = {
    "Median Cut": Image.Quantize.MEDIANCUT,
    "Max Coverage": Image.Quantize.MAXCOVERAGE,
    "Fast Octree": Image.Quantize.FASTOCTREE
}

def get_palette(image):
    #   Get palette from the image
    palette = image.convert("P", palette=Image.ADAPTIVE, colors=256).getpalette()

    #   Create a set to store unique colors
    unique_colors = set()

    new_palette = []

    for i in range(0, len(palette), 3):
        r = palette[i]
        g = palette[i+1]
        b = palette[i+2]

        color = (r,g,b)

        # Add unique colors to set
        if color not in unique_colors:
            unique_colors.add(color)
            new_palette.extend(color)

    num_colors = len(new_palette) // 3

    palette_image = Image.new("P", (num_colors, 1))

    for i in range(num_colors):
        r = new_palette[i*3]
        g = new_palette[i*3+1]
        b = new_palette[i*3+2]
        palette_image.putpixel((i,0), (r,g,b))

    return palette_image

def increment_filename(path, name):
    increment = 0
    while True:
        increment += 1
        new_name = name.split(".png")[0] + str(increment) + ".png"
        if (path / new_name).is_file():
            continue
        else:
            return new_name

def numberize_filename(path, name):
    increment = -1
    if "\\x" in name:
        while True:
            increment +=1
            new_name = name.split(".png")[0].replace("\\x", str(increment)) + ".png"
            if (path / new_name).is_file():
                continue
            else:
                return new_name

def palettize(image, palette_image, prequantize, method, dither):
    palettized = image

    if prequantize:
        palettized = palettized.quantize(colors = 256, method=method, dither=Image.Dither.NONE).convert('RGB')

    if palette_image.mode != 'P':
        palette_image = palette_image.convert('P')

    return palettized.quantize(palette=palette_image, method=method, dither = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE)