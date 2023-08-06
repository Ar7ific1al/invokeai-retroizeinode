'''
Thanks to Claude.ai for helping me figure out how to even understand where to begin. I don't know Python at all, and haven't done any programming in a long time.
Thanks to @dwringer from InvokeAI Discord for their Enhance Image node which I gutted to get a skeleton to work with. lol
Credit to Astropulse https://github.com/Astropulse for...
    https://github.com/Astropulse/pixeldetector: Inspired this project; ended up not using any of their code but they still deserve recognition.
    https://github.com/Astropulse/sd-palettize/tree/main: Color palettes included in this repo cloned from sd-palettize.
    
'''

from typing import Literal, Optional
from pathlib import Path
from PIL import Image, ImagePalette
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

PALETTE = Literal[
    "aap-64.png",
    "atari-8-bit.png",
    "commodore64.png",
    "endesga-32.png",
    "fantasy-24.png",
    "microsoft-windows.png",
    "NES.png",
    "nintendo-gameboy.png",
    "pico-8.png",
    "slso8.png",
    "Custom",
]

#   Check color mode and convert to RGB if needed
def convert_rgb(image):
    # Convert back to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB') 
    return image

#   Downsample image box style
def pixelize(image, samples, upsample):
    width, height = image.size
    image = image.resize((width//samples, height//samples), Image.BOX)
    if upsample:
        image = image.resize((width, height), Image.NEAREST)
    return image

def quantize(image, max_colors):
    image = convert_rgb(image)
    # Use PIL.Image.quantize() method 
    quantized = image.quantize(max_colors)    
    return quantized

def ditherize(image):
    image = image.convert('RGB')
    image = image.convert('P', dither=Image.FLOYDSTEINBERG)
    return image

def palettize(image, palette):  
    palettized = image
    palettized = convert_rgb(palettized)
    if palette.mode != 'P':
        palette = palette.convert('P', dither=Image.NONE)
    palettized = image.quantize(palette=palette, dither=Image.Dither.NONE)    
    return palettized

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

def dto(context, image_out, id, intermediate):
    return context.services.images.create(
        image = image_out,
        image_origin = ResourceOrigin.INTERNAL,
        image_category = ImageCategory.GENERAL,
        node_id = id,
        session_id = context.graph_execution_state_id,
        is_intermediate = intermediate
    ) 

class PixelizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Pixelize an image. Downsample, upsample. '''
    #fmt: off
    type:   Literal["pixelize"] = "pixelize"
    
    #   Inputs
    image:          Optional[ImageField] = Field(default = None, description = "Input image for pixelization")
    downsample:     int = Field(default = 4, description = "Amount to downsample image. Larger = smaller image = more pixelization on upsample.")
    upsample:       bool = Field(default=True, description = "Upsample to original resolution")
    #fmt: on
    
    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Pixelize",
                "tags": ["image", "retro", "pixel"]
            },
        }
    
    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.services.images.get_pil_image(self.image.image_name)
        width, height = image_out.size
        samples = self.downsample
        
        image_out = convert_rgb(image_out)
        
        if samples < 1:
            samples = 1
        elif samples > 30:
            samples = 30
        
        image_out = pixelize(image_out, samples, self.upsample)
        image_out = convert_rgb(image_out)
        
        image_dto = dto(context, image_out, self.id, self.is_intermediate)
        
        return ImageOutput(image = ImageField(image_name = image_dto.image_name),
                            width = image_dto.width,
                            height = image_dto.height,
        )


class QuantizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Quantize an image (reduce colors) '''
    #fmt: off
    type:   Literal["quantize"] = "quantize"
    
    #   Inputs
    image:          Optional[ImageField] = Field(default = None, description = "Input image for pixelization")
    colors:         int = Field(default = 64, description = "Number of colors the image should be reduced to")
    #fmt: on
    
    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Quantize",
                "tags": ["image", "retro", "quantize", "pixel"]
            },
        }
    
    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.services.images.get_pil_image(self.image.image_name)
        colors = self.colors
        
        image_out = convert_rgb(image_out)
        
        if colors < 1:
            colors = 1
        elif colors > 256:
            colors = 256
        
        image_out = quantize(image_out, colors)
        image_out = convert_rgb(image_out)
        
        image_dto = dto(context, image_out, self.id, self.is_intermediate)
        
        return ImageOutput(image = ImageField(image_name = image_dto.image_name),
                            width = image_dto.width,
                            height = image_dto.height,
        )


class PalettizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Palettize an image by applying a color palette '''
    #fmt: off
    type:   Literal["palettize"] = "palettize"
    
    #   Inputs
    image:          Optional[ImageField] = Field(default = None, description = "Input image for pixelization")
    palette_image:  Optional[ImageField] = Field(default = None, description = "Palette image")
    palette_path:   str = Field(default="", description="Palette image path, including \".png\" extension")
    #fmt: on
    
    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Palettize",
                "tags": ["image", "retro", "palette", "pixel", "color"]
            },
        }
    
    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.services.images.get_pil_image(self.image.image_name)
        
        image_out = convert_rgb(image_out)
        
        if self.palette_image == None:
            palette = self.palette_path
            if palette == '':
                raise ValueError("No palette file specified.")
            else:
                #   Trim " from file path for lazy users like me (:
                palette = palette.replace('"', '')
                palette_image = Image.open(palette)
                image_out = palettize(image_out, palette_image)
        else:
            palette_image = context.services.images.get_pil_image(self.palette_image.image_name)
            image_out = palettize(image_out, palette_image)
        
        image_out = convert_rgb(image_out)
        
        image_dto = dto(context, image_out, self.id, self.is_intermediate)
        
        return ImageOutput(image = ImageField(image_name = image_dto.image_name),
                            width = image_dto.width,
                            height = image_dto.height,
        )


class DitherizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Apply Floyd-Steinberg dithering to an image '''
    #fmt: off
    type:   Literal["ditherize"] = "ditherize"
    
    #   Inputs
    image:          Optional[ImageField] = Field(default = None, description = "Input image for dithering")
    #fmt: on
    
    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Ditherize",
                "tags": ["image", "retro", "dither", "pixel", "color"]
            },
        }
    
    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.services.images.get_pil_image(self.image.image_name)
        
        image_out = convert_rgb(image_out)
        
        image_out = ditherize(image_out)
        
        image_out = convert_rgb(image_out)
        
        image_dto = dto(context, image_out, self.id, self.is_intermediate)
        
        return ImageOutput(image = ImageField(image_name = image_dto.image_name),
                            width = image_dto.width,
                            height = image_dto.height,
        )


class GetPaletteInvocation(BaseInvocation, PILInvocationConfig):
    ''' Get palette from an image '''
    #fmt: off
    type:   Literal["get_palette"] = "get_palette"
    
    #   Inputs
    image:          Optional[ImageField] = Field(default = None, description = "Input image to grab a palette from")
    export:           bool = Field(default = True, description = "Save palette PNG to specified path with optional name")
    path:           str = Field(default="", description = "Path to save the palette image")
    name:           str = Field(default="", description = "Name for the palette image")
    #fmt: on
    
    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Get Palette",
                "tags": ["image", "retro", "palette"]
            },
        }
    
    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.services.images.get_pil_image(self.image.image_name)
        
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
                palette_image.save(path / name)
                image_out = palette_image
        else:
            image_out = get_palette(image_out)
        
        #   Do NOT convert palette image to RGB; it needs to be indexed color, not RGB, to be used as a palette
        image_dto = dto(context, image_out, self.id, self.export)
        
        return ImageOutput(image = ImageField(image_name = image_dto.image_name),
                            width = image_dto.width,
                            height = image_dto.height,
        )


# class RetroizeInvocation(BaseInvocation, PILInvocationConfig):
    # ''' Retroize an image. Downsample, upsample, palettize, quantize, and dither. '''
    # # fmt: off
    # type: Literal["retroize"] = "retroize"
    
    # # Inputs
    # image:          Optional[ImageField] = Field(default=None, description="Input image for pixelization/palettization")
    # downsample:     int = Field(default=10, description="Amount to downsample image; larger = smaller image")
    # upsample:       bool = Field(default=True, description="Upsample image back to original resolution")
    # use_palette:    bool = Field(default=False, description="Apply a color palette to the image")
    # #palette:        PALETTE = Field(default="atari-8-bit.png", description="Color palette to apply to the image")
    # custom_palette: str = Field(default="", description="Custom palette image path, including \".png\" extension")
    # quantize:       bool = Field(default=False, description="Palettize image based on max colors, if Use Palette = false")
    # max_colors:     int = Field(default=128, description="Max colors for quantized image; more = slower")
    # dither:         bool = Field(default=False, description="Apply dithering to image to preserve details")
    # # fmt: on

    # class Config(InvocationConfig):
        # schema_extra = {
            # "ui": {
                # "title": "Retroize",
                # "tags": ["image", "pixel", "quantize", "palette", "retro"]
            # },
        # }

    # def invoke(self, context: InvocationContext) -> ImageOutput:
        # image_out = context.services.images.get_pil_image(self.image.image_name)
        # width, height = image_out.size
        # size = self.downsample
        # #palettes_path = "some path to palettes to be figured out later lol"
        
        # image_out = convert_rgb(image_out)
        
        # if size < 1:
            # size = 1
        # elif size > 30:
            # size = 30
        
        # if size > 1:
            # image_out = pixelize_image(image_out, size)
            
        # if self.upsample:
            # image_out = upsample(image_out, width, height)
        
        # if self.use_palette:
            # #palette_path = Path().resolve() / palettes_path
            # palette = self.custom_palette
            # if palette == '':
                # raise ValueError("No palette file specified.")
            # else:
                # #if palette == "Custom":
                    # #palette = self.palette
                # #   Remove " from file path for lazy users like me (:
                # palette = self.custom_palette.replace('"', '')
                # #palette_img = Image.open(palette_path / palette)
                # palette_img = Image.open(palette)
                # image_out = apply_palette(image_out, palette_img)
            
        # if self.quantize:
            # image_out = quantize_colors(image_out, self.max_colors)
        
        # if self.dither:
            # image_out = dither_colors(image_out)
        
        # image_out = convert_rgb(image_out)
        
        # image_dto = context.services.images.create(
            # image=image_out,
            # image_origin=ResourceOrigin.INTERNAL,
            # image_category=ImageCategory.GENERAL,
            # node_id=self.id,
            # session_id=context.graph_execution_state_id,
            # is_intermediate=self.is_intermediate
        # )

        # return ImageOutput(image=ImageField(image_name=image_dto.image_name),
                            # width=image_dto.width,
                            # height=image_dto.height,
        # )