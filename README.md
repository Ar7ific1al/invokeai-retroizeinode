# Retroize Nodes
This is a collection of Nodes for InvokeAI to "Retroize" images. Any image can be given a fresh coat of retro paint with these nodes, either from your gallery or from within the graph itself.

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/8988f990-f20a-4331-ada2-bd28ec99169e)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/da1ec440-f325-4477-bdf7-003ddaef59ae)


## Nodes
- **Get Palette:** Get a color palette from an image
- **Get Palette (Advanced):** Get a color palette from an image, with some advanced output options
- **Retro Bitize:** Convert the image to pure one-bit pixels (black and white)
- **Retro Ditherize:** Apply Floyd-Steinberg dithering to an image. **!Deprecated!** This node is more or less deprecated by the Dither switch on Quantize, but it's left here just in case someone might want to use it.
- **Retro Palettize:** Apply a color palette to images
- **Retro Pixelize:** Downsample and upsample images, giving them a pixelated look
- **Retro Quantize:** Reduce colors of an image, giving them that retro feel

NOTE: **_ANY_** image can be passed as a palette image to Palettize, but this is not the intended behavior, and may not work as as expected. _You've been warned_.

The following image was used with each of the nodes below.

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/c784e438-8c84-4414-8c7d-2cad62a38f89)

## Get Palette
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/b487aeea-ad3d-48d4-ada5-6a48cbe7f531)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/f0038f80-c667-4b5e-925e-d47daf9ce50a)

### Inputs
- Image: Image to get a peltte from
- Intermediate: If Intermediate is switched on, the palette will not be saved to the gallery. **!!This switch will be removed once InvokeAI is updated to allow image output nodes to bypass the gallery!!**

## Get Palette (Advanced)
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/b88537a6-53e9-4731-a78a-d64e8bde7a28)

The advanced Get Palette node offers advanced users the ability to export the palette to a specific location on their system, optionally with a specific file name. This is useful for instance if you would rather have your palettes exported to a central location rather than to your InvokeAI gallery, for example to a dedicated palettes folder which you use for other applications such as Photoshop, Aseprite, or other applications which can make use of indexed palette images.

### Inputs
- Image: Image to get a palette from
- Export: Whether to export the palette to a user-specified location. If Export is switched off, the palette image will be saved only to the InvokeAI gallery.
- Path: If Export is switched on, the palette will be saved to this location. Expects a full file path, e.g. `C:\Some\Path`
- Name: If Export is switched on, the palette will be saved with this name. Name can be left blank and the palette will be given a name automatically. `.PNG` is not required to be part of the name.

## Retro Bitize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/abce10bc-c203-4cc7-ab19-a4411a18fc79)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/8f90294c-cbaa-4191-a566-3445b9334923)

### Inputs
- Image: Image to Bitize.
- Dither: Dither the image.

## Retro Ditherize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/8a7ea0f7-605c-46e2-8f83-ff1add680db9)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/307974d7-6f0f-4866-9352-507ebed0e6f1)

### Inputs
- Image: Image to Ditherize
NOTE: This node doesn't achieve the same appearance as using Quantize with Dither. It does provide a different look, however, so it is left here as is.

## Retro Palettize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/75ea039a-2f3c-4d8e-ac78-70724a21416d)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/da211ec0-5d1e-4f34-8a52-24f41271431a)

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

## Retro Pixelize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/f8238901-1ffe-4f70-8492-60dc7e28647c)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/d18be520-b871-457a-a856-d3ed92084538)

### Inputs
- Image: Image to Pixelize.
- Downsample: Amount to downsample the image. Higher numbers will make the image smaller.
- Upsample: Resize the image back to its original dimensions, giving it the pixelized look.


## Retro Quantize
![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/2a47f086-9b10-4e5a-be4a-81bc6aaa8cfe)

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/9816c0c3-aef6-48cb-a8b2-b1d05e398f24)

### Inputs
- Image: Image to Quantize
- Colors: Number of colors to reduce the image to, up to a max of 256 colors.
- Method: How to quantize the image.
- Kmeans: I'm not sure what this does but have fun with it I guess.
- Dither: Dither the image when quantizing. This will use the Quantizing method for this process, as well.

## Thanks and Stuff
- [YMGenesis](https://github.com/ymgenesis) for helping figure some things out, providing advice and tips for improvements :)
- @dwringer on InvokeAI Discord server for the Image Enhance node. I gutted it and used it as a starting point. lol It also served as some inspiration for these nodes.
- [Astropulse](https://github.com/Astropulse) for their [sd-palettize](https://github.com/Astropulse/sd-palettize/tree/main) and [pixeldetector](https://github.com/Astropulse/pixeldetector) projects which served as direct inspiration for this project.

## Palette Credit
Since the palette images in the root `palettes` folder are cloned from Astropulse's sd-palettize repo, I'll mirror the credit for those palettes here:

`ENDESGA Adigun A. Polack Luis Miguel Maldonado PICO-8 Gabriel C. Nintendo Commodore Microsoft Atari`
