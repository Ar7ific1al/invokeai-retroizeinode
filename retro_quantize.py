from typing import Literal, Optional
from PIL import Image
from pydantic import Field
from .retro_getpalette import get_palette

from ..models.image import ImageCategory, ImageField, ResourceOrigin
from .baseinvocation import(
    BaseInvocation,
    BaseInvocationOutput,
    InvocationContext,
    InvocationConfig
)

from .image import(
    PILInvocationConfig,
    ImageOutput
)


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


class RetroQuantizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Quantize an image to 256 or less colors '''
    #fmt: off
    type:   Literal["retro_quantize"] = "retro_quantize"

    #   Inputs
    image:          Optional[ImageField] = Field(default = None, description = "Input image for pixelization")
    colors:         int = Field(default = 64, gt = 0, le = 256, description = "Number of colors the image should be reduced to")
    method:         PIL_QUANTIZE_MODES = Field(default = "Median Cut", description = "Quantization method")
    kmeans:         int = Field(default = 0, ge = 0, description = "k_means")
    dither:         bool = Field(default = True, description = "Dither quantized image")
    #fmt: on

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Retro Quantize",
                "tags": ["image", "retro", "quantize", "pixel"]
            },
        }

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        colors = self.colors

        quantized_image = image
        if quantized_image.mode != 'RGB':
            quantized_image = quantized_image.convert('RGB')

        kmeans = self.kmeans

        # if colors < 1:
            # colors = 1
        # elif colors > 256:
            # colors = 256

        # if kmeans < 0:
            # kmeans = 1
        
        if self.dither:
            palette = get_palette(quantized_image.quantize(colors, method = PIL_QUANTIZE_MAP[self.method]).convert('RGB'))
            quantized_image = quantized_image.quantize(colors = colors, palette = palette, method = PIL_QUANTIZE_MAP[self.method], kmeans = kmeans, dither = Image.FLOYDSTEINBERG).convert('RGB')
        else:
            quantized_image = quantized_image.quantize(colors = colors, method = PIL_QUANTIZE_MAP[self.method], kmeans = kmeans).convert('RGB')

        dto = context.services.images.create(
            image = quantized_image,
            image_origin = ResourceOrigin.INTERNAL,
            image_category = ImageCategory.GENERAL,
            node_id = self.id,
            session_id = context.graph_execution_state_id,
            is_intermediate = self.is_intermediate
        )

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )