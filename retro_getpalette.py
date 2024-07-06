from pathlib import Path
from .retro_helpers import get_palette, numberize_filename, increment_filename
from .retro_palettize import UpdatePalettes

from invokeai.invocation_api import (
    BaseInvocation,
    BaseInvocationOutput,
    InvocationContext,
    ImageField,
    ImageOutput,
    InputField,
    WithMetadata,
    invocation,
    invocation_output,
    )


@invocation_output("get_palette_output")
class PaletteOutput(BaseInvocationOutput):
    """ Base class for Cell Fracture output """
    
    image:      ImageField = InputField(default = None, description = "The palette output")
    
    class Config:
        json_schema_extra = {"required": ["type", "palette"]}

@invocation("get_palette", title = "Get Palette", tags = ["retro", "image", "pixel", "palette"], category = "image", version = "1.0.1")
class RetroGetPaletteInvocation(BaseInvocation, WithMetadata):
    ''' Get palette from an image, 256 colors max. '''

    #   Inputs
    image:          ImageField  = InputField(default = None, description = "Input image to grab a palette from")
    
    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.images.get_pil(self.image.image_name)
        
        if image_out.mode != 'RGB':
            image_out = image_out.convert('RGB')
        
        image_out = get_palette(image_out)
        
        #   Do NOT convert palette image to RGB; it needs to be indexed color, not RGB, to be used as a palette
        dto = context.images.save(image = image_out)

        return PaletteOutput(
            image = ImageField(image_name = dto.image_name)
        )
        
@invocation("get_palette_adv", title = "Get Palette (Advanced)", tags = ["retro", "image", "pixel", "palette"], category = "image", version = "1.0.1")
class RetroGetPaletteAdvInvocation(BaseInvocation, WithMetadata):
    ''' Get palette from an image, 256 colors max. Optionally export to a user-defined location. '''
    #   Inputs
    image:          ImageField = InputField(default = None, description = "Input image to grab a palette from")
    export:         bool = InputField(default = True, description = "Save palette PNG to specified path with optional name")
    subfolder:      str = InputField(default="", description = "Subfolder for the palette in nodes/Retroize/palettes/ folder")
    name:           str = InputField(default="", description = "Name for the palette image")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.images.get_pil(self.image.image_name)
        
        if image_out.mode != 'RGB':
            image_out = image_out.convert('RGB')
        
        if self.export:
            palettes_dir = "nodes/Retroize/palettes/"
            out_path = palettes_dir
            if self.subfolder != "":
                out_path = palettes_dir + self.subfolder
            out_path = Path(out_path).resolve()
            print(f"out_path = {out_path}")
            Path(out_path).mkdir(parents=True, exist_ok=True)
            
            palette_image = get_palette(image_out)
            name = self.name
            if name == "":
                    name = self.image.image_name
            if ".png" not in name:
                name = name + ".png"
            #   Replace "\x" in string with 0 to begin incremental palettes
            if "\\x" in name:
                name = numberize_filename(out_path, name)
            if (out_path / name).is_file():
                name = increment_filename(out_path, name)
            palette_image.save(out_path / name)
            image_out = palette_image
                
        else:
            image_out = get_palette(image_out)

        #   Do NOT convert palette image to RGB; it needs to be indexed color, not RGB, to be used as a palette
        dto = context.images.save(image = image_out)

        return PaletteOutput(
            image = ImageField(image_name = dto.image_name)
        )