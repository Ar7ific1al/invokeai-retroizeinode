# Retroize Nodes
This is a collection of Nodes for InvokeAI to "Retroize". Any image can be given a fresh coat of retro paint with these nodes.

## Nodes
- **Pixelize:** Downsample and upsample images, giving them a pixelated look
- **Palettize:** Apply a color palette to images
- **Quantize:** Reduce colors of an image, giving them that retro feel
- **Ditherize:** Apply Floyd-Steinberg dithering to an image
- **Get Palette:** Get a color palette from an image

NOTE: *ANY* image can be passed as a palette image to Palettize, but this is not the intended behavior.

The following image was used with each of the nodes below.

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/c784e438-8c84-4414-8c7d-2cad62a38f89)


## Pixelize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/d18be520-b871-457a-a856-d3ed92084538)  ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/f8238901-1ffe-4f70-8492-60dc7e28647c)

### Inputs
- Image: Image to Pixelize
- Downsample: Amount to downsample the image. Higher numbers will make the image smaller.
- Upsample: Resize the image back to its original dimensions, giving it the pixelized look.

## Palettize


### Inputs
- Image: Image to Palettize
- Palette Image: A palette image to use for palettizing the input image
- Palette Path: Path to a palette image not in your InvokeAI gallery

## Quantize


### Inputs
- Image: Image to Quantize
- Colors: Number of colors to reduce the image to, up to a max of 256 colors.

## Ditherize


### Inputs
- Image: Image to Ditherize

## Get Palette


### Inputs
- Image: Image to get a palette from
- Export: Whether to export the palette to a user-specified location. If Export is switched off, the palette image will be saved only to the InvokeAI gallery.
- Path: If Export is switched on, the palette will be saved to this location. Expects a full file path, e.g. `C:\Some\Path`
- Name: If Export is switched on, the palette will be saved with this name. Name can be left blank and the palette will be given a name automatically. `.PNG` is not required to be part of the name.


## Thanks and Stuff
[YMGenesis](https://github.com/ymgenesis) for helping figure some things out, providing advice and tips for improvements :)


@dwringer on InvokeAI Discord server for the Image Enhance node. I gutted it and used it as a starting point. lol

## Palette Credit
Since the palette images in the root `palettes` folder are cloned from [Astropulse](https://github.com/Astropulse)'s [sd-palettize](https://github.com/Astropulse/sd-palettize/tree/main) repo, I'll mirror the credit for those palettes here:

`ENDESGA Adigun A. Polack Luis Miguel Maldonado PICO-8 Gabriel C. Nintendo Commodore Microsoft Atari`
