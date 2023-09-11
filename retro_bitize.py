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

@invocation("retro_bitize", title = "Bitize", tags = ["retro", "image", "color", "pixel", "bit", "dither"], category = "image")
class RetroBitizeInvocation(BaseInvocation):
    ''' Crush an image to one-bit pixels '''

    #   Inputs
    image:  ImageField  = InputField(description = "Input image for pixelization")
    dither: bool        = InputField(default = True, description = "Dither the Bitized image")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        
        dither = Image.Dither.NONE

        image = image.convert("RGB") if image.mode != "RGB" else image
        
        dither = Image.Dither.FLOYDSTEINBERG if self.dither else Image.Dither.NONE
        
        image = image.convert("1", dither = dither).convert("RGB")

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