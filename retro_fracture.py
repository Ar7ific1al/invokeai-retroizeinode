from pydantic import BaseModel, Field
from typing import Literal, Optional
from PIL import Image, ImageDraw, ImageOps
from scipy.spatial import Voronoi, cKDTree
import numpy as np

from invokeai.app.invocations.primitives import ImageField, ImageOutput, ColorField
from invokeai.app.models.image import (
    ImageCategory,
    ResourceOrigin
)

from invokeai.app.invocations.baseinvocation import(
    BaseInvocation,
    BaseInvocationOutput,
    FieldDescriptions,
    InvocationContext,
    InputField,
    OutputField,
    invocation,
    invocation_output
)

BORDER_STYLE = Literal[
    "Black",
    "White",
    "Color",
    "RGB",
    "BGR",
    "Inverse",
    "Average",
    "Grayscale",
]

CELL_STYLE = Literal[
    "Color",
    "White",
    "Grayscale",
]

def trim_dims(*args):
    return tuple((x - x % 8) for x in args)

def get_border_color(image, vertex, average_color, style = "Black"):
    width, height = image.size
    if style == "White":
        return (255, 255, 255)
    elif style == "Black":
        return (0, 0, 0)
    elif style == "Average":
        return tuple(average_color)
    elif style == "Inverse":
        x = np.clip(int(vertex[0]), 0, width - 1)
        y = np.clip(int(vertex[1]), 0, height - 1)
        inverted_color = tuple(np.subtract((255, 255, 255), image.getpixel((x, y))[:3]))
        return inverted_color
    elif style == "RGB":
        x = np.clip(int(vertex[0]), 0, width - 1)
        y = np.clip(int(vertex[1]), 0, height - 1)
        return image.getpixel((x, y))
    elif style == "BGR":
        x = np.clip(int(vertex[0]), 0, width - 1)
        y = np.clip(int(vertex[1]), 0, height - 1)
        return image.getpixel((x, y))[2], image.getpixel((x, y))[1], image.getpixel((x, y))[0]
    elif style == "Grayscale":
        x = np.clip(int(vertex[0]), 0, width - 1)
        y = np.clip(int(vertex[1]), 0, height - 1)
        grayscale = int(np.mean(image.getpixel((x, y))[:3]))
        return (grayscale, grayscale, grayscale)
    elif style == "Hex":
        return (r, g, b)

@invocation_output("cell_fracture_output")
class CellFractureOutput(BaseInvocationOutput):
    """ Base class for Cell Fracture output """
    
    image:      ImageField = InputField(default = None, description = "The output image")
    width:      int = InputField(description = "The width of the image in pixels")
    height:     int = InputField(description = "The height of the image in pixels")
    mask:       ImageField = InputField(default = None, description = "Voronoi cell mask")
    
    class Config:
        schema_extra = {"required": ["type", "image", "width", "height", "mask"]}


@invocation("voronoi_cell", title = "Voronoi Cells", tags = ["cell", "voronoi", "image", "color"], category = "image")
class VoronoiCellImageInvocation(BaseInvocation):
    ''' Generate a voronoi cell image '''
    
    #   Inputs
    width:              int = InputField(default = 512, description = "Width of the output image")
    height:             int = InputField(default = 512, description = "Height of the output image")
    size:               float = InputField(default = 0.1, gt = 0, description = "Size of cells for fracturing")
    interstice_width:   int = InputField(default = 3, ge = 0, description = "Width of cell interstice in pixels")
    cell_style:         CELL_STYLE = InputField(default = "Grayscale", description = "Style of voronoi cells to generate")
    invert:             bool = InputField(default = False, description = "Invert the voronoi cells image")
    #fmt: on
    
        
    def invoke(self, context: InvocationContext) -> ImageOutput:
        width, height = trim_dims(self.width, self.height)
        
        #   Generate Voronoi cells
        num_cells = int((1 / self.size) * 1000)
        points = np.random.rand(num_cells, 2) * np.array([width, height])
        vor = Voronoi(points)
        tree = cKDTree(vor.vertices)
        
        #   Create voronoi cells
        voronoi_image = Image.new("RGBA", (width, height), color = (0, 0, 0))
        cells = ImageDraw.Draw(voronoi_image)
        cell_color = (255, 255, 255)
        interstice_color = (0, 0, 0)
        
        for region in vor.regions:
            if not -1 in region and len(region) > 0:
                polygon = [tuple(vor.vertices[i]) for i in region]
                if self.cell_style == "White":
                    cells.polygon(polygon, outline = interstice_color, fill = cell_color)
                else:
                    cell_color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
                    cells.polygon(polygon, outline = interstice_color, fill = (cell_color[0], cell_color[1], cell_color[2], 255))
                centroid = np.mean(polygon, axis = 0)
                
                centroid[0] = np.clip(centroid[0], 0, width - 1)
                centroid[1] = np.clip(centroid[1], 0, height - 1)
            
            # Draw the interstice (border) between cells
                for i in range(len(polygon)):
                    p1 = polygon[i]
                    p2 = polygon[(i + 1) % len(polygon)]
                    cells.line((p1[0], p1[1], p2[0], p2[1]), fill = interstice_color, width = self.interstice_width)
        
        voronoi_image = voronoi_image.convert("RGB")
        
        if self.cell_style == "Grayscale":
            voronoi_image = voronoi_image.convert("L")
        
        if self.invert:
            voronoi_image = ImageOps.invert(voronoi_image)
        
        if voronoi_image.mode != "RGB":
            voronoi_image = voronoi_image.convert("RGB")
        
        dto = context.services.images.create(
            image = voronoi_image,
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


@invocation("cell_fracture", title = "Cell Fracture", tags = ["cell", "voronoi", "image", "color"], category = "image")
class CellFractureInvocation(BaseInvocation):
    ''' Fracture an image using Voronoi '''

    #   Inputs
    image:              ImageField = InputField(default = None, description = "Input image to fracture")
    size:               float = InputField(default = 0.1, gt = 0, description = "Size of cells for fracturing")
    interstice_width:   int = InputField(default = 3, ge = 0, description = "Width of cell interstice in pixels")
    interstice_color:   BORDER_STYLE = InputField(default = "Black", description = "Color of cell interstice")
    custom_color:       ColorField = InputField(default = ColorField(r = 0, g = 0, b = 0, a = 255), description = "Custom color of cell interstice")
    fill_border:        bool = InputField(default = True, description = "Fill cells beyond the border with the same color as interstice")
    invert_mask:        bool = InputField(default = False, description = "Invert the cell mask output by this node")
    #fmt: on

    def invoke(self, context: InvocationContext) -> CellFractureOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        width, height = image.size
        style = self.interstice_color
        
        #   Voronoi cell generation
        #   Cell size multiplier
        num_cells = int((1 / self.size) * 1000)
        points = np.random.rand(num_cells, 2) * np.array([width, height])
        vor = Voronoi(points)
        tree = cKDTree(vor.vertices)
        
        #   Set average color based on the image, if border style = average
        average_color = None
        if style == "Average":
            average_color = np.mean(image, axis = (0, 1)).astype(int)
        
        voronoi_image = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(voronoi_image)
        
        #   Create voronoi cell mask
        voronoi_cell_mask = Image.new("RGB", image.size, color = (255, 255, 255) if self.invert_mask else (0, 0, 0))
        mask_cells = ImageDraw.Draw(voronoi_cell_mask)
        mask_cell_color = (0, 0, 0) if self.invert_mask else (255, 255, 255)
        mask_interstice_color = (255, 255, 255) if self.invert_mask else (0, 0, 0)
        
        #   Set RGB from hex color if border style = hex
        r = self.custom_color.r
        g = self.custom_color.g
        b = self.custom_color.b
        # hex = self.hex_color
            
        for region in vor.regions:
            if not -1 in region and len(region) > 0:
                polygon = [tuple(vor.vertices[i]) for i in region]
                
                mask_cells.polygon(polygon, outline = mask_interstice_color, fill = mask_cell_color)
                
                # Calculate the centroid of the Voronoi region
                centroid = np.mean(polygon, axis=0)
                
                # Fill cells outside image bounds with the selected border color
                if centroid[0] < 0 or centroid[0] >= width or centroid[1] < 0 or centroid[1] >= height:
                    if style == "Color":
                        color = self.custom_color.tuple()
                        # color = (r, g, b)
                    else:
                        color = get_border_color(image, centroid, average_color, style)
                else:
                    # Ensure that the centroid coordinates stay within the image bounds
                    centroid[0] = np.clip(centroid[0], 0, width - 1)
                    centroid[1] = np.clip(centroid[1], 0, height - 1)
                    color = image.getpixel((int(centroid[0]), int(centroid[1])))

                draw.polygon(polygon, fill=color)
                
                # Draw the interstice (border) between cells
                for i in range(len(polygon)):
                    p1 = polygon[i]
                    p2 = polygon[(i + 1) % len(polygon)]
                    draw.line((p1[0], p1[1], p2[0], p2[1]), fill=get_border_color(image, (0.5 * (p1[0] + p2[0]), 0.5 * (p1[1] + p2[1])), average_color, style) if style != "Color" else (r, g, b), width=self.interstice_width)
                    mask_cells.line((p1[0], p1[1], p2[0], p2[1]), fill = mask_interstice_color, width = self.interstice_width)
        
        voronoi_image = voronoi_image.convert("RGB")
        
        dto = context.services.images.create(
            image = voronoi_image,
            image_origin = ResourceOrigin.INTERNAL,
            image_category = ImageCategory.GENERAL,
            node_id = self.id,
            session_id = context.graph_execution_state_id,
            is_intermediate = self.is_intermediate,
            workflow = self.workflow
        )
        
        mask_dto = context.services.images.create(
            image = voronoi_cell_mask,
            image_origin = ResourceOrigin.INTERNAL,
            image_category = ImageCategory.MASK,
            node_id = self.id,
            session_id = context.graph_execution_state_id,
            is_intermediate = self.is_intermediate,
            workflow = self.workflow
        )

        return CellFractureOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
            mask = ImageField(image_name = mask_dto.image_name),
        )