# invokeai-retroizeinode
This is a Python script for InvokeAI Nodes to "Retroize" images in the node graph.

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/c2abe8ff-fc8b-4e42-9f83-5c2ada82181b)

## Features
- Downsample and upsample to "pixelize" the image
- Apply a color palette provided from the `/palettes/` folder
  - Alternatively, apply a custom color palette with the `Custom` palette selection, and provide the name of the image located in the `/palettes/` folder. For example, create a new palette image called `new-palette.png` and place it in `/palettes/` and enter the name `new-palette.png` in the `Custom Palette` field on the node to use that custom palette.
- Quantize the image to the desired number of colors
- Apply Floyd-Steinberg dithering
All options are executed in the order displayed on the node (Downsample -> Upsample -> Palettize -> Quantize -> Dither)

NOTE: Palette images should be PNG images saved with indexed color, NOT RGB or RGBA images.
