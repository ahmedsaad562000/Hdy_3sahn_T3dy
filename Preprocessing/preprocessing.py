from skimage.color import rgb2gray
from skimage import io
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import convolve2d
from PIL import Image
from skimage.filters import gaussian

def show_images(images,titles=None):
    #This function is used to show image(s) with titles by sending an array of images and an array of associated titles.
    # images[0] will be drawn with the title titles[0] if exists
    # You aren't required to understand this function, use it as-is.
    n_ims = len(images)
    if titles is None: titles = ['(%d)' % i for i in range(1,n_ims + 1)]
    fig = plt.figure()
    n = 1
    for image,title in zip(images,titles):
        a = fig.add_subplot(1,n_ims,n)
        if image.ndim == 2: 
            plt.gray()
        plt.imshow(image)
        a.set_title(title)
        plt.axis('off')
        n += 1
    fig.set_size_inches(np.array(fig.get_size_inches()) * n_ims)
    plt.show() 
   
def gray_image(imagePath):
    image = io.imread(imagePath)
    gray_scale_image = image
    if(len(image.shape)==3):
        if(image.shape[2]==4):
            gray_scale_image=rgb2gray(rgba2rgb(image))
        else :
            gray_scale_image=rgb2gray(image)
    else :
        gray_scale_image=gray_scale_image/255
    return gray_scale_image

def HistogramEqualization(imagePath):
    img = io.imread(imagePath)
    if(len(img.shape)==2):
        img=img
    elif(img.shape[2]==4):
        img=rgb2gray(rgba2rgb(img))
        img=img*255
    elif(img.shape[2]==3):
        img=rgb2gray(img)
        img=img*255
    
    width,height=img.shape
    # Flattning the image and converting it into a histogram
    histOrig, bins = np.histogram(img, 256, [0, 255])
   
    cdf = histOrig.cumsum()  # Calculating the cumsum of pixels of the histogram
    
    cdf = np.round(cdf * 255 / (height *width))  # Histogram Equalization
    imgEq=cdf[img.astype('uint8')]

    return imgEq

def LoGEdgeDetection(imagePath, sigma, filter, threshold):

    if(filter == None):
        filter= np.array([
            [-1,-1,-1],
            [-1,8,-1],
            [-1,-1,-1]
        ])

    img = io.imread(imagePath)

    img=gaussian(img,sigma=sigma)
    img=img*255

    img_convolved=abs(convolve2d(img,filter))
    img_convolved=img_convolved.astype(np.uint8)

    final_image = []
    final_image = np.zeros((img_convolved.shape[0],img_convolved.shape[1]))
    final_image = np.where(abs(img_convolved)>threshold,255,0)

    return final_image

def resize_image(input_path, output_path, new_size):
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Resize the image
            resized_img = img.resize(new_size)
            # Save the resized image
            resized_img.save(output_path)
    except Exception as e:
        print(f"Error processing image: {e}")

# Example usage for image resizing
# input_image_path = "./preprocessing/image.jpeg"
# output_image_path = "./preprocessing/output.jpeg"
# new_size = (4320, 7680)

# output = io.imread(output_image_path)
# ut.show_images(images=[output],titles=['Resized'])

# resize_image(input_image_path, output_image_path, new_size)

