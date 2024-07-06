import random
from PIL import Image, ImageDraw

from invokeai.invocation_api import(
    BaseInvocation,
    InputField,
    InvocationContext,
    WithMetadata,
    invocation,
    ImageField,
    ImageOutput,
    ColorField
)

@invocation("retro_scanlines_simple", title="Scan Lines", tags=["retro", "image", "color", "pixel", "line"], category="image", version = "1.0.1")
class RetroScanlinesSimpleInvocation(BaseInvocation, WithMetadata):
    """ Apply a simple scan lines effect to the input image """

    #   Inputs
    image:          ImageField  = InputField(description = "Input image to add scanlines to")
    line_size:      int         = InputField(default = 1, gt = 0, description = "Thickness of scanlines in pixels")
    line_spacing:   int         = InputField(default = 4, gt = 0, description = "Space between lines in pixels")
    line_color:     ColorField  = InputField(default = ColorField(r = 0, g = 0, b = 0, a = 255), description = "Darkness of scanlines, 1.0 being black")
    size_jitter:    int         = InputField(default = 0, ge = 0, description = "Random line position offset")
    space_jitter:   int         = InputField(default = 0, ge = 0, description = "Random line position offset")
    vertical:       bool        = InputField(default = False, description = "Switch scanlines to vertical")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.images.get_pil(self.image.image_name).convert("RGBA")
        width, height = image.size
        line_color = (self.line_color.r, self.line_color.g, self.line_color.b, self.line_color.a)
        
        scanlines_image = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(scanlines_image)

        if self.vertical:  # Create vertical scanlines
            x = 0
            while x < width:
                line_width = self.line_size + random.uniform(-self.size_jitter, self.size_jitter)  # Random size adjustment
                x += int(self.line_spacing + random.uniform(-self.space_jitter, self.space_jitter))  # Random spacing adjustment
                if 0 <= x < width:  # Check if the line is within the image bounds
                    draw.rectangle([(x, 0), (x + int(line_width), height)], fill = line_color)
        else:  # Create horizontal scanlines
            y = 0
            while y < height:
                line_height = self.line_size + random.uniform(-self.size_jitter, self.size_jitter)  # Random size adjustment
                if line_height < 0:
                    line_height = 0  # Ensure line height is not negative
                y += int(self.line_spacing + random.uniform(-self.space_jitter, self.space_jitter))  # Random spacing adjustment
                if 0 <= y < height:  # Check if the line is within the image bounds
                    draw.rectangle([(0, y), (width, y + int(line_height))], fill = line_color)
        
        scanlines_image = Image.alpha_composite(image, scanlines_image).convert("RGB")
        
        dto = context.images.save(image = scanlines_image)

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )