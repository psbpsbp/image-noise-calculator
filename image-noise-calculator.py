import numpy as np
from PIL import Image
from scipy.signal import convolve2d
import matplotlib.cm as cm



distribution_size=15
sigma=1

img = Image.open('image.png').convert('RGBA') #load image



def srgb_to_linear(srgb):

    mask = srgb <= 0.04045
    linear = np.where(mask, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)
    return linear

def rgb_to_oklab(img_rgb):

    img_float = img_rgb.astype(np.float32) / 255.0
    linear_rgb = srgb_to_linear(img_float)

    matrix1 = np.array([
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005]
    ])

    original_shape = linear_rgb.shape
    pixels = linear_rgb.reshape((-1, 3))
    lms = np.dot(pixels, matrix1.T)

    lms_prime = np.cbrt(lms)

    matrix2 = np.array([
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660]
    ])

    oklab = np.dot(lms_prime, matrix2.T)
    return oklab.reshape(original_shape)


def weighted_differences(array,distribution,modifier):

    array=array*modifier
    average=convolve2d(array,distribution,'same','fill',0)
    normalization=convolve2d(np.ones_like(array)*modifier,distribution,'same','fill',0)

    return np.abs(average/normalization-array)

def noisemap(image,distribution):

    image=np.array(image.convert('RGBA'))
    A=image[...,-1]/255
    RGB=image[...,:-1]
    oklab=rgb_to_oklab(RGB)
#    oklab=RGB
    L=oklab[...,0]
    a=oklab[...,1]
    b=oklab[...,2]

    L=weighted_differences(L,distribution,A)
    a=weighted_differences(a,distribution,A)
    b=weighted_differences(b,distribution,A)

    noisemap=(L+a+b)/3
    noisemap=((noisemap-noisemap.min())/(noisemap.max()-noisemap.min())*255).astype(np.uint8)

    noisemap=(cm.viridis(noisemap)*255).astype(np.uint8)
    noisemap[...,3]=(A*255).astype(np.uint8)

    return Image.fromarray(noisemap,'RGBA')

normal=lambda pos: round((np.e**(-(pos[0]**2+pos[1]**2)/(2*sigma**2)))/(2*np.pi*sigma**2)**0.5,7)


n=distribution_size//2
distribution=np.apply_along_axis(normal,-1,np.stack((np.meshgrid(np.arange(-n,n+1),np.arange(-n,n+1))),-1))
for _ in range(np.sum(distribution[n]==0)//2):
    distribution=distribution[1:-1,1:-1]
distribution[n,n]=0


noisemap=noisemap(img,distribution).save('noisemap.png') #save image
