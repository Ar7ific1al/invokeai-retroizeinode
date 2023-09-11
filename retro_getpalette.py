from pathlib import Path
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
    BaseInvocationOutput,
    InvocationContext,
    InputField,
    invocation,
    invocation_output
)

def get_palette(image):
    #   Get palette from the image
    palette = image.convert("P", palette=Image.ADAPTIVE, colors=256).getpalette()

    #   Create a set to store unique colors
    unique_colors = set()

    new_palette = []

    for i in range(0, len(palette), 3):
        r = palette[i]
        g = palette[i+1]
        b = palette[i+2]

        color = (r,g,b)

        # Add unique colors to set
        if color not in unique_colors:
            unique_colors.add(color)
            new_palette.extend(color)

    num_colors = len(new_palette) // 3

    palette_image = Image.new("P", (num_colors, 1))

    for i in range(num_colors):
        r = new_palette[i*3]
        g = new_palette[i*3+1]
        b = new_palette[i*3+2]
        palette_image.putpixel((i,0), (r,g,b))

    return palette_image

def increment_filename(path, name):
    increment = 0
    while True:
        increment += 1
        new_name = name.split(".png")[0] + str(increment) + ".png"
        if (path / new_name).is_file():
            continue
        else:
            return new_name

def numberize_filename(path, name):
    increment = -1
    if "\\x" in name:
        while True:
            increment +=1
            new_name = name.split(".png")[0].replace("\\x", str(increment)) + ".png"
            if (path / new_name).is_file():
                continue
            else:
                return new_name


@invocation_output("get_palette_output")
class PaletteOutput(BaseInvocationOutput):
    """ Base class for Cell Fracture output """
    
    image:      ImageField = InputField(default = None, description = "The palette output")
    
    class Config:
        schema_extra = {"required": ["type", "palette"]}

@invocation("get_palette", title = "Get Palette", tags = ["retro", "image", "pixel", "palette"], category = "image")
class RetroGetPaletteInvocation(BaseInvocation):
    ''' Get palette from an image, 256 colors max. '''

    #   Inputs
    image:          ImageField  = InputField(default = None, description = "Input image to grab a palette from")
    
    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.services.images.get_pil_image(self.image.image_name)
        
        if image_out.mode != 'RGB':
            image_out = image_out.convert('RGB')
        
        image_out = get_palette(image_out)
        
        #   Do NOT convert palette image to RGB; it needs to be indexed color, not RGB, to be used as a palette
        dto = context.services.images.create(
            image = image_out,
            image_origin = ResourceOrigin.INTERNAL,
            image_category = ImageCategory.GENERAL,
            node_id = self.id,
            session_id = context.graph_execution_state_id,
            is_intermediate = self.is_intermediate,
            workflow = self.workflow
        )

        return PaletteOutput(
            image = ImageField(image_name = dto.image_name)
        )
        
@invocation("get_palette_adv", title = "Get Palette (Advanced)", tags = ["retro", "image", "pixel", "palette"], category = "image")
class RetroGetPaletteAdvInvocation(BaseInvocation):
    ''' Get palette from an image, 256 colors max. Optionally export to a user-defined location. '''
    #   Inputs
    image:          ImageField = InputField(default = None, description = "Input image to grab a palette from")
    export:         bool = InputField(default = True, description = "Save palette PNG to specified path with optional name")
    path:           str = InputField(default="", description = "Path to save the palette image")
    name:           str = InputField(default="", description = "Name for the palette image")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.services.images.get_pil_image(self.image.image_name)
        
        if image_out.mode != 'RGB':
            image_out = image_out.convert('RGB')
        
        if self.export:
            path = self.path
            if path == "":
                raise ValueError("No save path specified.")
            else:
                #   Trim " from path for lazy users like me (:
                path = self.path.replace('"', '')
                path = Path(path).resolve()
                Path(path).mkdir(parents=True, exist_ok=True)
                palette_image = get_palette(image_out)
                name = self.name
                if name == "":
                    name = context.graph_execution_state_id
                if ".png" not in name:
                    name = name + ".png"
                #   Replace "\x" in string with 0 to begin incremental palettes
                if "\\x" in name:
                    name = numberize_filename(path, name)
                if (path / name).is_file():
                    name = increment_filename(path, name)
                palette_image.save(path / name)
                image_out = palette_image
        else:
            image_out = get_palette(image_out)

        #   Do NOT convert palette image to RGB; it needs to be indexed color, not RGB, to be used as a palette
        dto = context.services.images.create(
            image = image_out,
            image_origin = ResourceOrigin.INTERNAL,
            image_category = ImageCategory.GENERAL,
            node_id = self.id,
            session_id = context.graph_execution_state_id,
            is_intermediate = self.is_intermediate,
            workflow = self.workflow
        )

        return PaletteOutput(
            image = ImageField(image_name = dto.image_name)
        )