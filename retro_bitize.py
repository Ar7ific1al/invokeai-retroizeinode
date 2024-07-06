from PIL import Image


from invokeai.invocation_api import (
    BaseInvocation,
    InputField,
    InvocationContext,
    WithMetadata,
    invocation,
    ImageOutput,
    ImageField
    )

@invocation("retro_bitize", title = "Bitize", tags = ["retro", "image", "color", "pixel", "bit", "dither"], category = "image", version = "1.0.1")
class RetroBitizeInvocation(BaseInvocation, WithMetadata):
    ''' Crush an image to one-bit pixels '''

    #   Inputs
    image:  ImageField  = InputField(description = "Input image for pixelization")
    dither: bool        = InputField(default = True, description = "Dither the Bitized image")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.images.get_pil(self.image.image_name)
        
        dither = Image.Dither.NONE

        image = image.convert("RGB") if image.mode != "RGB" else image
        
        dither = Image.Dither.FLOYDSTEINBERG if self.dither else Image.Dither.NONE
        
        image = image.convert("1", dither = dither).convert("RGB")

        dto = context.images.save(image = image)

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )