from typing import Literal, Optional

from PIL import Image, ImageOps, ImageDraw, ImagePalette
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

import numpy as np
from itertools import product
from sklearn.cluster import KMeans
from pathlib import Path

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
def pixelize_image(image, pixel_size):
    width, height = image.size
    image = image.resize((width//pixel_size, height//pixel_size), Image.BOX)
    return image

#   Upsample image nearest neighbor
def upsample(image, ow, oh):
    width, height = image.size
    image = image.resize((ow, oh), Image.NEAREST)
    return image

def quantize_colors(image, max_colors):
    image = convert_rgb(image)
    
    # Use PIL.Image.quantize() method 
    quantized = image.quantize(max_colors)
    
    # Convert back to RGB if needed
    #quantized = convert_rgb(image)
    
    return quantized

def dither_colors(image):
    image = image.convert('P', dither=Image.FLOYDSTEINBERG)
    return image

def apply_palette(image, palette_img):  
    quantized = image.quantize(palette=palette_img, dither=Image.Dither.NONE)    
    return quantized

class RetroizeInvocation(BaseInvocation, PILInvocationConfig):
    ''' Pixelize an image. Optionally upsample to original size, and palettize the image to max_colors '''
    # fmt: off
    type: Literal["retroize"] = "retroize"
    
    # Inputs
    image:          Optional[ImageField] = Field(default=None, description="Input image for pixelization/palettization")
    downsample:     int = Field(default=10, description="Amount to downsample image; larger = smaller image")
    upsample:       bool = Field(default=True, description="Upsample image back to original resolution")
    use_palette:    bool = Field(default=False, description="Apply a color palette to the image")
    color_palette:  PALETTE = Field(default="atari-8-bit.png", description="Color palette to apply to the image")
    custom_palette: str = Field(default="", description="Custom palette image name")
    quantize:       bool = Field(default=False, description="Palettize image based on max colors, if Palette = false")
    max_colors:     int = Field(default=128, description="Max colors for quantized image; more = slower")
    dither:         bool = Field(default=False, description="Apply dithering to image to preserve details")
    # fmt: on

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {
                "title": "Retroize",
                "tags": ["image", "enhance", "pixel", "quantize", "palette", "retro"]
            },
        }

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image_out = context.services.images.get_pil_image(self.image.image_name)
        width, height = image_out.size
        size = self.downsample
        palettes_path = ".venv/Lib/site-packages/invokeai/app/invocations/palettes"
                
        if size < 1:
            size = 1
        elif size > 30:
            size = 30
        
        if size > 1:
            image_out = pixelize_image(image_out, size)
            
        if self.upsample:
            image_out = upsample(image_out, width, height)
        
        if self.use_palette:
            palette_path = Path().resolve() / palettes_path
            palette = self.color_palette
            if palette == "Custom":
                palette = self.custom_palette
            palette_img = Image.open(palette_path / palette)
            image_out = apply_palette(image_out, palette_img)
            
        if self.quantize:
            image_out = quantize_colors(image_out, self.max_colors)
        
        if self.dither:
            image_out = dither_colors(image_out)
        

        image_dto = context.services.images.create(
            image=image_out,
            image_origin=ResourceOrigin.INTERNAL,
            image_category=ImageCategory.GENERAL,
            node_id=self.id,
            session_id=context.graph_execution_state_id,
            is_intermediate=self.is_intermediate
        )

        return ImageOutput(image=ImageField(image_name=image_dto.image_name),
                            width=image_dto.width,
                            height=image_dto.height,
        )