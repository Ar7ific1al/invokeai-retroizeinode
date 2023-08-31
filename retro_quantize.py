from typing import Literal, Optional
from PIL import Image
from pydantic import BaseModel, Field
from .retro_getpalette import get_palette

from invokeai.app.invocations.primitives import ImageField, ImageOutput
from invokeai.app.models.image import (
    ImageCategory,
    ResourceOrigin
)
from invokeai.app.invocations.baseinvocation import(
    BaseInvocation,
    InputField,
    FieldDescriptions,
    InvocationContext,
    invocation
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

@invocation("retro_quantize", title = "Quantize", tags = ["retro", "image", "pixel", "quantize"], category = "image")
class RetroQuantizeInvocation(BaseInvocation):
    ''' Quantize an image to 256 or less colors '''

    #   Inputs
    image:          ImageField = InputField(default = None, description = "Input image for quantizing")
    colors:         int = InputField(default = 64, gt = 0, le = 256, description = "Number of colors the image should be reduced to")
    method:         PIL_QUANTIZE_MODES = InputField(default = "Median Cut", description = "Quantization method")
    kmeans:         int = InputField(default = 0, ge = 0, description = "k_means")
    dither:         bool = InputField(default = True, description = "Dither quantized image")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        colors = self.colors

        quantized_image = image
        if quantized_image.mode != 'RGB':
            quantized_image = quantized_image.convert('RGB')

        kmeans = self.kmeans
        
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
            is_intermediate = self.is_intermediate,
            workflow = self.workflow
        )

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )