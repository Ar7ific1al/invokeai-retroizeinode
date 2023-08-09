from typing import Literal, Optional
from PIL import Image
from pydantic import Field

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


class RetroBitizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Crush an image to one-bit pixels '''
    #fmt: off
    type:   Literal["retro_bitize"] = "retro_bitize"

    #   Inputs
    image:          Optional[ImageField] = Field(default = None, description = "Input image for pixelization")
    dither:         bool = Field(default = True, description = "Dither the Bitized image")
    #fmt: on

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Retro Bitize",
                "tags": ["image", "retro", "pixel"]
            },
        }

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        
        bitized_image = image
        dither = Image.Dither.NONE
        
        if bitized_image.mode != 'RGB':
            bitized_image = bitized_image.convert('RGB')
        
        if self.dither:
            dither = Image.Dither.FLOYDSTEINBERG
        
        bitized_image = bitized_image.convert('1', dither=dither).convert('RGB')
        

        dto = context.services.images.create(
            image = bitized_image,
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