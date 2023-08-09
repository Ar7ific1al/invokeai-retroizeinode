from typing import Literal, Optional
from pathlib import Path
from PIL import Image
from pydantic import Field
import cv2

# from . import ditherlib as Dither

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


# DITHER_METHODS = Literal[
    # "PIL",
    # "simple2D",
    # "floyd-steinberg",
    # "jarvis-judice-ninke",
# ]


def PILDither(image):
    return image.convert('P', dither=Image.FLOYDSTEINBERG)


class RetroDitherizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Apply Floyd-Steinberg dithering to an image '''
    #fmt: off
    type:   Literal["retro_ditherize"] = "retro_ditherize"

    #   Inputs
    image:          Optional[ImageField] = Field(default = None, description = "Input image for dithering")
    # method:         DITHER_METHODS = Field(default = "PIL", description = "Dithering method")
    #fmt: on


    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Retro Ditherize",
                "tags": ["image", "retro", "dither", "pixel"]
            },
        }

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        
        ditherized_image = image
        if ditherized_image.mode != 'RGB':
            ditherized_image = ditherized_image.convert('RGB')
        
        ditherized_image = PILDither(ditherized_image)
        # if self.method == "PIL":
            # ditherized_image = PILDither(ditherized_image)
        # else:
            # ditherized_image = Dither.dither(img = ditherized_image, method = self.method, resize=False)
        # ditherized_image = ditherized_image.convert('RGB')
        
        dto = context.services.images.create(
            image = ditherized_image,
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