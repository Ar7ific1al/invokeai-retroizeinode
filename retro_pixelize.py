from PIL import Image

from invokeai.invocation_api import(
    BaseInvocation,
    InputField,
    InvocationContext,
    WithMetadata,
    invocation,
    ImageField,
    ImageOutput
)


@invocation("retro_pixelize", title = "Pixelize", tags = ["retro", "image", "pixel", "scale", "resize"], category = "image", version="1.0.1")
class PixelizeInvocation(BaseInvocation, WithMetadata):
    ''' Pixelize an image. Downsample, upsample. '''

    #   Inputs
    image:              ImageField  = InputField(default = None, description = "Input image for pixelization")
    downsample_factor:  int         = InputField(default = 4, gt = 0, le = 30, description = "Image resizing factor. Higher = smaller image.")
    upsample:           bool        = InputField(default = True, description = "Upsample to original resolution")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.images.get_pil(self.image.image_name)
        width, height = image.size
        factor = self.downsample_factor

        image = image.convert("RGB") if image.mode != "RGB" else image

        image = image.resize((width // factor, height // factor), Image.BOX)

        image = image.resize((width, height), Image.NEAREST) if self.upsample else image
        dto = context.images.save(image = image)

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )