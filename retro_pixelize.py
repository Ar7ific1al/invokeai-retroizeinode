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

class PixelizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Pixelize an image. Downsample, upsample. '''
    #fmt: off
    type:   Literal["retro_pixelize"] = "retro_pixelize"

    #   Inputs
    image:              Optional[ImageField] = Field(default = None, description = "Input image for pixelization")
    downsample_factor:  int = Field(default = 4, description = "Image resizing factor. Higher = smaller image.")
    upsample:           bool = Field(default=True, description = "Upsample to original resolution")
    #fmt: on

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Retro Pixelize",
                "tags": ["image", "retro", "pixel"]
            },
        }

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        width, height = image.size
        factor = self.downsample_factor

        pixelize_image = image
        if pixelize_image.mode != 'RGB':
            pixelize_image = pixelize_image.convert('RGB')

        if factor < 1:
            factor = 1
        elif factor > 20:
            factor = 20
        
        pixelize_image = pixelize_image.resize((width // factor, height // factor), Image.BOX)
        if self.upsample:
            pixelize_image = pixelize_image.resize((width, height), Image.NEAREST)
        
        
        dto = context.services.images.create(
            image = pixelize_image,
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