from typing import Literal, Optional
from PIL import Image
from .retro_helpers import palettize
from .retro_helpers import PIL_QUANTIZE_MAP as QMap
from .retro_helpers import PIL_QUANTIZE_MODES as QMode
import os

from invokeai.invocation_api import(
    BaseInvocation,
    InputField,
    ImageField,
    ImageOutput,
    InvocationContext,
    WithMetadata,
    invocation
)


#   Palette cache
palettes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "palettes")

os.makedirs(palettes_dir, exist_ok = True)

print(f"palettes_dir = {palettes_dir}")

def list_palettes() -> list:
    if not os.path.exists(palettes_dir):
        return []
    palettes = [f for f in os.listdir(palettes_dir) if f.lower().endswith((".png"))]
    return sorted(palettes, key = lambda x: x.lower())

available_palettes = list_palettes()

if available_palettes:
    palettes_str = ", ".join([repr(f) for f in available_palettes])
    PaletteLiteral = eval(f'Literal["None", {palettes_str}]')
else:
    PaletteLiteral = Literal["None"]


def UpdatePalettes():
    def list_palettes() -> list:
        if not os.path.exists(palettes_dir):
            return []
        palettes = [f for f in os.listdir(palettes_dir) if f.lower().endswith((".png"))]
        return sorted(palettes, key = lambda x: x.lower())

    available_palettes = list_palettes()

    if available_palettes:
        palettes_str = ", ".join([repr(f) for f in available_palettes])
        PaletteLiteral = eval(f'Literal["None", {palettes_str}]')
    else:
        PaletteLiteral = Literal["None"]


@invocation("retro_palettize_adv", title = "Palettize Advanced", tags = ["retro", "image", "color", "palette"], category = "image", version = "1.0.1")
class RetroPalettizeAdvInvocation(BaseInvocation, WithMetadata):
    ''' Palettize an image by applying a color palette '''

    #   Inputs
    image:          ImageField = InputField(default = None, description = "Input image for pixelization")
    palette_image:  PaletteLiteral = InputField(default = None, description = "Palette image")
    dither:         bool = InputField(default = False, description = "Apply dithering to image when palettizing")
    prequantize:    bool = InputField(default = False, description = "Apply 256-color quantization with specified method prior to applying the color palette")
    quantizer:      QMode = InputField(default = "Fast Octree", description = "Palettizer quantization method")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.images.get_pil(self.image.image_name)
        
        palettized_image = image
        if palettized_image.mode != 'RGB':
            palettized_image = palettized_image.convert('RGB')

        if self.palette_image == None:
                raise ValueError("No palette image or path was specified.")
        else:
            # print("Using input image as palette.")
            palette_image = Image.open(os.path.join(palettes_dir, self.palette_image))
            palettized_image = palettize(palettized_image, palette_image, self.prequantize, QMap[self.quantizer], self.dither)

        palettized_image = palettized_image.convert('RGB')

        dto = context.images.save(image = palettized_image)
        
        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )


@invocation("retro_palettize", title = "Palettize", tags = ["retro", "image", "color", "palette"], category = "image", version = "1.0.1")
class RetroPalettizeInvocation(BaseInvocation, WithMetadata):
    ''' Palettize an image by applying a color palette '''

    #   Inputs
    image:          ImageField = InputField(default = None, description = "Input image for pixelization")
    palette_image:  ImageField = InputField(default = None, description = "Palette image")
    palette_path:   str = InputField(default = "", description = "Palette image path, including \".png\" extension")
    dither:         bool = InputField(default = False, description = "Apply dithering to image when palettizing")
    prequantize:    bool = InputField(default = False, description = "Apply 256-color quantization with specified method prior to applying the color palette")
    quantizer:      QMode = InputField(default = "Fast Octree", description = "Palettizer quantization method")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.images.get_pil(self.image.image_name)
        
        palettized_image = image
        if palettized_image.mode != 'RGB':
            palettized_image = palettized_image.convert('RGB')

        if self.palette_path == '':
            # print("Palette path is empty.")
            if self.palette_image == None:
                raise ValueError("No palette image or path was specified.")
            else:
                # print("Using input image as palette.")
                palette_image = context.images.get_pil(self.palette_image.image_name)
                palettized_image = palettize(palettized_image, palette_image, self.prequantize, QMap[self.quantizer], self.dither)
        else:
            # print("Palette path is " + self.palette_path)
            palette = self.palette_path
            #   Trim " from file path for lazy users like me (:
            palette = palette.replace('"', '')
            palette_image = Image.open(palette)
            palettized_image = palettize(palettized_image, palette_image, self.prequantize, QMap[self.quantizer], self.dither)

        palettized_image = palettized_image.convert('RGB')

        dto = context.images.save(image = palettized_image)

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )