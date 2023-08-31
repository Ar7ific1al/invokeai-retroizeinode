# Retroize Nodes
This is a collection of Nodes for InvokeAI to "Retroize" images. Any image can be given a fresh coat of retro paint with these nodes, either from your gallery or from within the graph itself.

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/8988f990-f20a-4331-ada2-bd28ec99169e)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/da1ec440-f325-4477-bdf7-003ddaef59ae)


## Nodes
- **Get Palette:** Get a color palette from an image
- **Get Palette (Advanced):** Get a color palette from an image, with some advanced output options
- **Bitize:** Convert the image to pure one-bit pixels (black and white)
- **Halftone:** Give the image a halftone-like effect, either colored or grayscale
- **Palettize:** Apply a color palette to images
- **Pixelize:** Downsample and upsample images, giving them a pixelated look
- **Quantize:** Reduce colors of an image, giving them that retro feel

NOTE: **_ANY_** image can be passed as a palette image to Palettize, but this is not the intended behavior, and may not work as as expected. _You've been warned_.

All nodes can be found in Nodes search under the "retro" tag!

The following image was used with each of the nodes below.

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/c784e438-8c84-4414-8c7d-2cad62a38f89)

## Get Palette
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/5b0fc04c-6ad0-40c0-a39f-7683b696ee74)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/f0038f80-c667-4b5e-925e-d47daf9ce50a)

### Inputs
- Image: Image to get a peltte from

## Get Palette (Advanced)
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/b88537a6-53e9-4731-a78a-d64e8bde7a28)

The advanced Get Palette node offers advanced users the ability to export the palette to a specific location on their system, optionally with a specific file name. This is useful for instance if you would rather have your palettes exported to a central location rather than to your InvokeAI gallery, for example to a dedicated palettes folder which you use for other applications such as Photoshop, Aseprite, or other applications which can make use of indexed palette images.

### Inputs
- Image: Image to get a palette from
- Export: Whether to export the palette to a user-specified location. If Export is switched off, the palette image will be saved only to the InvokeAI gallery.
- Path: If Export is switched on, the palette will be saved to this location. Expects a full file path, e.g. `C:\Some\Path`
- Name: If Export is switched on, the palette will be saved with this name. Name can be left blank and the palette will be given a name automatically. `.PNG` is not required to be part of the name.

## Bitize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/abce10bc-c203-4cc7-ab19-a4411a18fc79)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/8f90294c-cbaa-4191-a566-3445b9334923)

### Inputs
- Image: Image to Bitize.
- Dither: Dither the image.

## Palettize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/75ea039a-2f3c-4d8e-ac78-70724a21416d)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/da211ec0-5d1e-4f34-8a52-24f41271431a)

## Halftone
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/94a58569-29a6-4757-9f71-ecb0da85d430)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/6a592fad-33ca-473e-bd0f-916630a94da4)

### Inputs
- Image: Image to apply halftone to
- Shape: Shape of the halftone effect. Circle, square, or triangle. (Default: Circle)
- Size: The diameter, in pixels, of the shape.
- Rotation: The rotation, in degrees, of the shape. Not important for circles. **Ignored if Random Rotation is on!**
- Random Rotation: Apply a random rotation within `Rotation Threshold` degrees. **Ignores Rotation parameter!**
- Rotation Threshold: Amount to rotate the shape when `Random Rotation` is switched on. E.g. if set to 90, the shape will be rotated randomly between 0 and 90 degrees.
- Jitter: Threshold for random size of the shape. E.g. if `Size` is 8, and `Jitter` is 3, the size of each shape will vary between 5 and 11 pixels in diameter.
- Overlay: Overlay the halftone image on the color image, producing a colored halftone image.

### Inputs
- Image: Image to Palettize
- Palette Image: A palette image to use for palettizing the input image. **Will be ignored if a palette image is specified via Palette Path.**
- Palette Path: Path to a palette image not in your InvokeAI gallery. **Will bypass the Palete Image input and use the file specified by this path.**
- Dither: Apply dithering. (Operates differently from Ditherize node) (Effect may not work as expected while `Prequantize` is switched on)
- Prequantize: Quantize using a different method prior to applying a palette. This crushes the image to 256 colors _before_ palettizing, and quantizes using the select3ed method. Note: Disables dither effect.
- Quantizer: The method for prequantizing.
### Palettes
Palettes should be indexed PNG images, otherwise they may not work as expected. The images should be one pixel tall and up to 256 pixels wide.

Additional palettes can either be created yourself, obtained from images using the Get Palette node, or retrieved from various online sources. One such online source is [lospec](https://lospec.com/palette-list), which has a ton of palettes available for download.

## Pixelize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/f8238901-1ffe-4f70-8492-60dc7e28647c)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/d18be520-b871-457a-a856-d3ed92084538)

### Inputs
- Image: Image to Pixelize.
- Downsample: Amount to downsample the image. Higher numbers will make the image smaller.
- Upsample: Resize the image back to its original dimensions, giving it the pixelized look.

## Quantize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/ae472c40-4ae2-4c4f-b6ca-9b7bd461afdf)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/9816c0c3-aef6-48cb-a8b2-b1d05e398f24)

### Inputs
- Image: Image to Quantize
- Colors: Number of colors to reduce the image to, up to a max of 256 colors.
- Method: How to quantize the image.
- Kmeans: I'm not sure what this does but have fun with it I guess.

## Thanks and Stuff
- [YMGenesis](https://github.com/ymgenesis) for helping figure some things out, providing advice and tips for improvements :)
- @dwringer on InvokeAI Discord server for the Image Enhance node. I gutted it and used it as a starting point. lol It also served as some inspiration for these nodes.
- [Astropulse](https://github.com/Astropulse) for their [sd-palettize](https://github.com/Astropulse/sd-palettize/tree/main) and [pixeldetector](https://github.com/Astropulse/pixeldetector) projects which served as direct inspiration for this project.

## Palette Credit
Since the palette images in the root `palettes` folder are cloned from Astropulse's sd-palettize repo, I'll mirror the credit for those palettes here:

`ENDESGA Adigun A. Polack Luis Miguel Maldonado PICO-8 Gabriel C. Nintendo Commodore Microsoft Atari`
