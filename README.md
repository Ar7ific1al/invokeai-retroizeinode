# invokeai-retroizeinode
This is a Python script for InvokeAI Nodes to "Retroize" images in the node graph.

![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/0b3797cd-83eb-469c-b60e-852148bf6582)

## Features
- Downsample and upsample image
- Palettize images (palette transfer/enforce color palette)
- Quantize images (reduce colors)
- Apply dithering

All options are executed in the order displayed on the node (Downsample -> Upsample -> Palettize -> Quantize -> Dither)

NOTE: Palette images should be PNG images saved with indexed color, NOT RGB or RGBA images.

## Usage & Tips
- `Downsample`: Higher values will downsample the image more. A value of 1 will not downsample the image at all. 4 is a pretty decent starting point. There's no limit to how high this value can go, but be reasonable; I'm not responsible for disasters if you set this value to 50. :)
- `Upsample`: If switched on (default), the image will be upsampled back to its original size (assuming `Downsample` > 1). Otherwise, the image will be downsampled to a smaller size.
- `Use Palette`: If switched on (default: off), the image will use the specified color palette to palettize the image.
- `Custom Palette`: The full file path to a palette image. Palettes can be stored anywhere.
  - Ths path and filename is ***CaSe SeNsItIvE!***
- `Quantize`: If switched on (default: off), the image will be quantized (reduced in color) to the specified number of colors.
- `Max Colors`: The number of colorse for quantization of the image. This can be used together with `Use Palette` to further reduce the colors of the image. Keep in mind you likely won't notice a difference if your Color Palette already has fewer colors than Max Colors.
- `Dither`: If switched on (default: off), the image will have Floyd-Steinberg dithering applied.

## Example Images
The following images are arranged thusly: Original Image -> Retroized Images
| OG  | Retroized |
| :-------------: | :-------------: |
| ![4ed79609-dfbb-4444-96e8-bc2243880774](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/3e79e757-56db-4aba-ac00-7532a97cac9a)  | ![9ba63ca0-49f1-4f8b-81fb-21b28e9ef79a](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/8ef6f794-eb8f-4de4-91ec-0ace4f48cf23)  |
| ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/4fbe12c5-972d-4af8-bfd1-f0cc837d3c9d)  | ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/a639216c-96a2-40cc-8e0e-8ac69ffeb293)  |
| ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/5737b133-69b9-448c-83b3-a39501e855fc)  | ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/e9dcfe34-fc71-48bf-99ac-46e22d2e2f05)  |
| ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/a206a1d3-98d5-49b7-a303-2021ca53320b)  | ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/c6672257-7148-43af-85bf-ce1c165376cb)  |
| ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/b9e64ea3-006f-46ed-8de3-924011402499)  | ![image](https://github.com/Ar7ific1al/invokeai-retroizeinode/assets/2306586/2bc043a5-e2db-4cc4-8044-c1850447a240)  |

## Palette Credit
Since palettes are cloned from [Astropulse](https://github.com/Astropulse)'s [sd-palettize](https://github.com/Astropulse/sd-palettize/tree/main) repo, I'll mirror the credit for those palettes here.

`ENDESGA Adigun A. Polack Luis Miguel Maldonado PICO-8 Gabriel C. Nintendo Commodore Microsoft Atari`
