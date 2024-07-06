from typing import Literal
from PIL import Image
from .retro_helpers import get_palette
from .retro_helpers import PIL_QUANTIZE_MAP as QMap
from .retro_helpers import PIL_QUANTIZE_MODES as QMode

from invokeai.invocation_api import (
    BaseInvocation,
    InputField,
    InvocationContext,
    WithMetadata,
    invocation,
    ImageField,
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


@invocation("retro_quantize", title = "Quantize", tags = ["retro", "image", "pixel", "quantize"], category = "image", version="1.0.1")
class RetroQuantizeInvocation(BaseInvocation, WithMetadata):
    ''' Quantize an image to 256 or less colors '''

    #   Inputs
    image:          ImageField = InputField(default = None, description = "Input image for quantizing")
    colors:         int = InputField(default = 64, gt = 0, le = 256, description = "Number of colors the image should be reduced to")
    method:         QMode = InputField(default = "Median Cut", description = "Quantization method")
    kmeans:         int = InputField(default = 0, ge = 0, description = "k_means")
    dither:         bool = InputField(default = True, description = "Dither quantized image")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.images.get_pil(self.image.image_name)

        image = image.convert("RGB") if image.mode != "RGB" else image

        if self.dither:
            palette = get_palette(image.quantize(self.colors, method = QMap[self.method]).convert('RGB'))
            image = image.quantize(colors = self.colors, palette = palette, method = QMap[self.method], kmeans = self.kmeans, dither = Image.FLOYDSTEINBERG).convert('RGB')
        else:
            image = image.quantize(colors = self.colors, method = QMap[self.method], kmeans = self.kmeans).convert('RGB')

        dto = context.images.save(image = image)

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )