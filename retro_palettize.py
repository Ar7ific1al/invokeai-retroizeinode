from typing import Literal
from PIL import Image

from invokeai.app.invocations.primitives import (
    ImageField, ImageOutput
)
from invokeai.app.models.image import (
    ImageCategory,
    ResourceOrigin
)

from invokeai.app.invocations.baseinvocation import(
    BaseInvocation,
    InputField,
    InvocationContext,
    invocation
)

#   Define Quantize methods list
PIL_QUANTIZE_MODES = Literal[
    "Median Cut",
    "Max Coverage",
    "Fast Octree",
]

PIL_QUANTIZE_MAP = {
    "Median Cut": Image.Quantize.MEDIANCUT,
    "Max Coverage": Image.Quantize.MAXCOVERAGE,
    "Fast Octree": Image.Quantize.FASTOCTREE
}

def palettize(image, palette_image, prequantize, method, dither):
    palettized = image

    if prequantize:
        palettized = palettized.quantize(colors = 256, method=method, dither=Image.Dither.NONE).convert('RGB')

    if palette_image.mode != 'P':
        palette_image = palette_image.convert('P')

    return palettized.quantize(palette=palette_image, method=method, dither = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE)

@invocation("retro_palettize", title = "Palettize", tags = ["retro", "image", "color", "palette"], category = "image")
class RetroPalettizeInvocation(BaseInvocation):
    ''' Palettize an image by applying a color palette '''

    #   Inputs
    image:          ImageField = InputField(default = None, description = "Input image for pixelization")
    palette_image:  ImageField = InputField(default = None, description = "Palette image")
    palette_path:   str = InputField(default = "", description = "Palette image path, including \".png\" extension")
    dither:         bool = InputField(default = False, description = "Apply dithering to image when palettizing")
    prequantize:    bool = InputField(default = False, description = "Apply 256-color quantization with specified method prior to applying the color palette")
    quantizer:      PIL_QUANTIZE_MODES = InputField(default = "Fast Octree", description = "Palettizer quantization method")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        
        palettize_image = image
        if palettize_image.mode != 'RGB':
            palettize_image = palettize_image.convert('RGB')

        if self.palette_path == '':
            # print("Palette path is empty.")
            if self.palette_image == None:
                raise ValueError("No palette image or path was specified.")
            else:
                # print("Using input image as palette.")
                palette_image = context.services.images.get_pil_image(self.palette_image.image_name)
                palettize_image = palettize(palettize_image, palette_image, self.prequantize, PIL_QUANTIZE_MAP[self.quantizer], self.dither)
        else:
            # print("Palette path is " + self.palette_path)
            palette = self.palette_path
            #   Trim " from file path for lazy users like me (:
            palette = palette.replace('"', '')
            palette_image = Image.open(palette)
            palettize_image = palettize(palettize_image, palette_image, self.prequantize, PIL_QUANTIZE_MAP[self.quantizer], self.dither)

        palettize_image = palettize_image.convert('RGB')

        dto = context.services.images.create(
            image = palettize_image,
            image_origin = ResourceOrigin.INTERNAL,
            image_category = ImageCategory.GENERAL,
            node_id = self.id,
            session_id = context.graph_execution_state_id,
            is_intermediate = self.is_intermediate,
            workflow = self.workflow
        )

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )