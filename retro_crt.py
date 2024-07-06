from PIL import Image
import numpy as np

from invokeai.invocation_api import(
    BaseInvocation,
    InputField,
    InvocationContext,
    WithMetadata,
    invocation,
    ImageField,
    ImageOutput
)


@invocation("retro_crt_curvature", title = "CRT", tags = ["retro", "image", "distort"], category = "image", version = "1.0.1")
class RetroCRTCurvatureInvocation(BaseInvocation, WithMetadata):
    """ Distort the input image, simulating CRT display curvature """

    #   Inputs
    image:              ImageField  = InputField(description = "Input image for pixelization")
    crt_width:          int         = InputField(default = 240, description = "Horizontal resolution of the CRT; smaller = more noticeable")
    crt_height:         int         = InputField(default = 160, description = "Vertical resolution of the CRT; smaller = more noticeable")
    crt_curvature:      float       = InputField(default = 3.0, description = "Curvature factor; smaller = stronger inward curve")
    scanlines_opacity:  float       = InputField(default = 1.0, description = "Opacity of CRT scan lines")
    vignette_opacity:   float       = InputField(default = 0.5, description = "Vignette opacity")
    vignette_roundness: float       = InputField(default = 5.0, description = "Vignette opacity")
    crt_brightness:     float       = InputField(default = 1.2, description = "Factor by which to brighten the image if using scan lines")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        
        def scanline_intensity(uv, resolution, opacity):
            #   Calculate intensity
            intensity = np.sin(uv * resolution * np.pi * 2.0)
    
            #   Remap intensity to the range (0.1, 1.0)
            intensity = ((0.5 * intensity) + 0.5) * 0.9 + 0.1
    
            return intensity**opacity

        def vignette_intensity(uv, resolution, opacity, roundness):
            uvX = uv[..., 0]    #   Extract the x-coordinates
            uvY = uv[..., 1]    #   Extract the y-coordinates
    
            #   Calculate the intensity for all pixels using vectorized operations
            intensity = uvX * uvY * (1.0 - uvX) * (1.0 - uvY)
    
            #   Clip the intensity values to be in the range [0, 1]
            intensity = np.clip((resolution[0] / roundness) * intensity, 0.0, 1.0)
    
            #   Apply opacity to the intensity for all pixels
            intensity = intensity ** opacity
    
            return intensity
        
        image = context.images.get_pil(self.image.image_name).convert("RGB")
        width, height = image.size
        
        #   Create normalized numpy array from input image
        image_array = np.array(image) / 255.0
        
        #   Define virtual CRT screen resolution and curvature factor
        crt_resolution = (self.crt_width, self.crt_height)

        #   Create UV grid
        x, y = np.meshgrid(np.linspace(0, 1, width), np.linspace(0, 1, height))
        uv = np.stack((x, y), axis = -1)
        
        #   Remap UVs
        uv = uv * 2 - 1
        offset = np.abs(uv[..., [1, 0]]) / self.crt_curvature
        uv = uv + uv * offset * offset
        uv = uv * 0.5 + 0.5
        
        #   Map UV coords to original image
        remapped_uvs = (
            (uv[..., 0] * (width - 1)).clip(0, width - 1).astype(int),
            (uv[..., 1] * (height - 1)).clip(0, height - 1).astype(int)
        )

        #   Precompute vignette and scanlines
        vignette_effect = vignette_intensity(uv, crt_resolution, self.vignette_opacity, self.vignette_roundness) if self.vignette_opacity > 0 else 0
        scanline_x_intensity = scanline_intensity(uv[..., 0], crt_resolution[1], self.scanlines_opacity) if self.scanlines_opacity > 0 else 0
        scanline_y_intensity = scanline_intensity(uv[..., 1], crt_resolution[0], self.scanlines_opacity) if self.scanlines_opacity > 0 else 0        

        #   Create an array for manipulation of pixels using the input image's dimensions
        crt_array = np.zeros((height, width, 3), dtype=np.float32)
        
        # Iterate over each pixel and apply the GLSL shader operations
        for y in range(height):
            for x in range(width):
                # Fetch pixel color from the original image_array
                base_color = image_array[remapped_uvs[1][y, x], remapped_uvs[0][y, x]]
        
                # Apply vignetteIntensity as a scaling factor
                if self.vignette_opacity > 0:
                    base_color *= vignette_effect[y, x]

                # Apply scanLineIntensity separately to x and y components
                if self.scanlines_opacity > 0:
                    base_color[0] *= scanline_x_intensity[y, x]
                    base_color[1] *= scanline_y_intensity[y, x]
                    base_color[2] *= scanline_y_intensity[y, x]

                #   Adjust brightness
                if self.crt_brightness > 0:
                    base_color *= self.crt_brightness

                #   Clip pixels outside UV range
                if any(uv[y, x] < 0.0) or any(uv[y, x] > 1.0):
                    final_color = np.array([0.0, 0.0, 0.0])
                else:
                    final_color = np.clip(base_color, 0.0, 1.0)

                crt_array[y, x] = final_color

        image = Image.fromarray((crt_array * 255).astype(np.uint8)).convert("RGB")
        
        dto = context.images.save(image = image)

        return ImageOutput(
            image = ImageField(image_name = dto.image_name),
            width = dto.width,
            height = dto.height,
        )