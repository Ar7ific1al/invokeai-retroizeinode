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


@invocation("retro_bitize", title = "Bitize", tags = ["retro", "image", "color", "pixel", "bit", "dither"], category = "image")
class RetroBitizeInvocation(BaseInvocation):
    ''' Crush an image to one-bit pixels '''

    #   Inputs
    image:          ImageField  = InputField(description = "Input image for pixelization")
    dither:         bool        = InputField(default = True, description = "Dither the Bitized image")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        
        bitized_image = image
        dither = Image.Dither.NONE
        
        if bitized_image.mode != "RGB":
            bitized_image = bitized_image.convert("RGB")
        
        if self.dither:
            dither = Image.Dither.FLOYDSTEINBERG
        
        bitized_image = bitized_image.convert("1", dither=dither).convert("RGB")
        

        dto = context.services.images.create(
            image = bitized_image,
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