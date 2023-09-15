from PIL import Image
from typing import Literal
from .retro_getpalette import get_palette

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

#   Define Quantize methods map
PIL_QUANTIZE_MAP = {
    "Median Cut": Image.Quantize.MEDIANCUT,
    "Max Coverage": Image.Quantize.MAXCOVERAGE,
    "Fast Octree": Image.Quantize.FASTOCTREE
}

@invocation("retro_quantize", title = "Quantize", tags = ["retro", "image", "pixel", "quantize"], category = "image", version = "1.0.0")
class RetroQuantizeInvocation(BaseInvocation):
    """ Quantize an image to 256 or less colors """

    #   Inputs
    image:          ImageField = InputField(description = "Input image for quantizing")
    colors:         int = InputField(default = 64, gt = 0, le = 256, description = "Number of colors the image should be reduced to")
    method:         PIL_QUANTIZE_MODES = InputField(default = "Median Cut", description = "Quantization method")
    kmeans:         int = InputField(default = 0, ge = 0, description = "k_means")
    dither:         bool = InputField(default = True, description = "Dither quantized image")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)

        image = image.convert("RGB") if image.mode != "RGB" else image

        if self.dither:
            palette = get_palette(image.quantize(self.colors, method = PIL_QUANTIZE_MAP[self.method]).convert('RGB'))
            image = image.quantize(colors = self.colors, palette = palette, method = PIL_QUANTIZE_MAP[self.method], kmeans = self.kmeans, dither = Image.FLOYDSTEINBERG).convert('RGB')
        else:
            image = image.quantize(colors = self.colors, method = PIL_QUANTIZE_MAP[self.method], kmeans = self.kmeans).convert('RGB')

        dto = context.services.images.create(
            image = image,
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