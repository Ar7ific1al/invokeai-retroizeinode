from typing import Literal
from PIL import Image
import numpy as np
import cv2
import random

from invokeai.app.invocations.primitives import ImageField, ImageOutput
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

SHAPES = Literal[
    "Circle",
    "Square",
    "Triangle",
]

@invocation("retro_halftone", title = "Halftone", tags = ["retro", "image", "color"], category = "image")
class RetroHalftoneInvocation(BaseInvocation):
    ''' Apply a halftone-like effect to images '''

    #   Inputs
    image:          ImageField = InputField(default = None, description = "Input image for pixelization")
    shape:          SHAPES = InputField(default = "Circle", description = "Halftone shape")
    size:           int = InputField(default = 16, description = "Size of halftone shape")
    rotation:       int = InputField(default = 0, description = "Rotation in degrees of the halftone shape when Shape != Circle")
    random_rotation: bool = InputField(default = False, description = "Rotate the shape with randomly with a threshold")
    rotation_threshold: int = InputField(default = 0, description = "Threshold for random rotation of the halftone shape")
    jitter:         int = InputField(default = 0, description = "Random size jitter threshold for the halftone shape")
    overlay:        bool = InputField(default = False, description = "Overlay the halftone on the original image, creating a color halftone image")
    #fmt: on

    def invoke(self, context: InvocationContext) -> ImageOutput:
        image = context.services.images.get_pil_image(self.image.image_name)
        
        image = image.convert("RGB")
        
        np_image = np.array(image)
        
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)
        
        jitter = self.jitter
        shape_size = self.size
        rotation = self.rotation
        rotation_threshold = self.rotation_threshold
        
        halftone_overlay = np.zeros_like(gray)

        for i in range(0, gray.shape[0], shape_size):
          for j in range(0, gray.shape[1], shape_size):
            
            # Adjust size randomly if jitter is enabled
            if jitter > 0:
              jitter_amount = random.randint(-jitter, jitter)
              shape_size_adjusted = max(shape_size + jitter_amount, 0)
            else:
              shape_size_adjusted = shape_size
              
            # Skip iteration if shape size ended up 0
            if shape_size_adjusted == 0:
              continue 
            
            x1 = i
            x2 = min(i + shape_size_adjusted, gray.shape[0])
            y1 = j
            y2 = min(j + shape_size_adjusted, gray.shape[1])
            
            roi = gray[x1:x2, y1:y2]
            color = np.mean(roi)

            if self.shape == "Circle":
              cv2.circle(halftone_overlay, (j+shape_size//2, i+shape_size//2),  
                         shape_size_adjusted//2, color, -1)
                         
            elif self.shape == "Square":
              if self.random_rotation:
                angle = random.randint(-rotation_threshold, rotation_threshold)
                M = cv2.getRotationMatrix2D((j+shape_size/2, i+shape_size/2), angle, 1)
                cv2.fillPoly(halftone_overlay, cv2.transform(np.array([[[j,i], [j+shape_size_adjusted, i], [j+shape_size_adjusted, i+shape_size_adjusted], [j, i+shape_size_adjusted]]]), M), color)
              else:
                M = cv2.getRotationMatrix2D((j+shape_size/2, i+shape_size/2), rotation, 1)
                cv2.fillPoly(halftone_overlay, cv2.transform(np.array([[[j,i], [j+shape_size_adjusted, i], [j+shape_size_adjusted, i+shape_size_adjusted], [j, i+shape_size_adjusted]]]), M), color)
                
            elif self.shape == "Triangle":
              if self.random_rotation:
                angle = random.randint(-rotation_threshold, rotation_threshold)
                M = cv2.getRotationMatrix2D((j+shape_size/2, i+shape_size/2), angle, 1)
                cv2.fillPoly(halftone_overlay, cv2.transform(np.array([[[j, i], [j+shape_size_adjusted, i], [j, i+shape_size_adjusted]]]), M), color)
              else:
                M = cv2.getRotationMatrix2D((j+shape_size/2, i+shape_size/2), rotation, 1)
                cv2.fillPoly(halftone_overlay, cv2.transform(np.array([[[j, i], [j+shape_size_adjusted, i], [j, i+shape_size_adjusted]]]), M), color)
                
        # Convert overlay to 3 channels         
        halftone_overlay = cv2.cvtColor(halftone_overlay, cv2.COLOR_GRAY2BGR)

        # Apply overlay on original image
        if self.overlay:
          halftone = cv2.addWeighted(np_image, 0.5, halftone_overlay, 0.5, 0)   
        else:
          halftone = halftone_overlay

        # Convert back to RGB for Pillow 
        halftone = cv2.cvtColor(halftone, cv2.COLOR_BGR2RGB)
        
        halftone_image = Image.fromarray(halftone)

        dto = context.services.images.create(
            image = halftone_image,
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