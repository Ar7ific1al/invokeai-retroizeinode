from typing import Literal, Optional
from PIL import Image
from pydantic import BaseModel, Field

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

@invocation("retro_pixelize", title = "Pixelize", tags = ["retro", "image", "pixel", "scale", "resize"], category = "image")
class PixelizeInvocation(BaseInvocation):
    ''' Pixelize an image. Downsample, upsample. '''

    #   Inputs
    image:              ImageField = InputField(default = None, description = "Input image for pixelization")
    downsample_factor:  int = InputField(default = 4, description = "Image resizing factor. Higher = smaller image.")
    upsample:           bool = InputField(default=True, description = "Upsample to original resolution")

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
            is_intermediate = self.is_intermediate,
            workflow = self.workflow
        )

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )