from libs import np , io
import matplotlib.pyplot as plt
from skimage.color import rgb2gray, rgba2rgb
from skimage.filters import gaussian
from skimage.util.shape import view_as_windows

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
   
def gray_image(image):
    gray_scale_image = image
    if(len(image.shape)==3):
        if(image.shape[2]==4):
            gray_scale_image=rgb2gray(rgba2rgb(image))
        else :
            gray_scale_image=rgb2gray(image)
    else :
        gray_scale_image=gray_scale_image/255
    return gray_scale_image

def HistogramEqualization(image,nbins=256):
    image = np.uint8(image*255)
    H = np.zeros(nbins)
    
    m, n = image.shape
    
    H = np.histogram(image, 256, [0,255])
    H_c = np.cumsum(H[0]) 
           
    q = 255*np.array(H_c)/(m*n)
    
    edited_image = np.zeros(image.shape)
    
    edited_image[:, :] = q[image[:, :]]
    return edited_image

def LoGEdgeDetection(img):

    filter = [
        [0,1,0],
        [1,-4,1],
        [0,1,0]
    ]

    img = gaussian(img, sigma = 1)

    sub_matrices = view_as_windows(img, (3,3), 1)
    convoluted = np.einsum('ij,klij->kl', filter, sub_matrices)
    convoluted[convoluted < 0.01] = 0

    return convoluted

# def resize_image(input_path, output_path, new_size):
#     try:
#         # Open the image
#         with Image.open(input_path) as img:
#             # Resize the image
#             resized_img = img.resize(new_size)
#             # Save the resized image
#             resized_img.save(output_path)
#     except Exception as e:
#         print(f"Error processing image: {e}")

def AdaptiveHistogramEqualization(image, nbins=256, tile_size=20):
    # tile_size = int(image.shape[0] / 2)
    
    gray_image = np.uint8(image * 255)
    height, width = gray_image.shape

    # Divide image into tiles
    tiles = [
        gray_image[y : y + tile_size, x : x + tile_size]
        for y in range(0, height, tile_size)
        for x in range(0, width, tile_size)
    ]

    # Equalize each tile individually
    equalized_tiles = []
    for tile in tiles:
        h = np.zeros(nbins)
        h = np.histogram(tile, nbins, [0, 255])[0]
        h_c = np.cumsum(h)
        q = 255 * np.array(h_c) / (tile_size * tile_size)
        equalized_tiles.append(q[tile])

    # Combine equalized tiles back into a single image
    equalized_image = np.empty_like(gray_image)
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            equalized_image[y : y + tile_size, x : x + tile_size] = equalized_tiles.pop(0)

    return equalized_image

def calculate_histogram(img):
    hist, bins = np.histogram(img.flatten(), 256, [0, 256])
    return hist
    
def is_image_dark(hist):
    if np.sum(hist[:128]) > np.sum(hist[128:]): 
        return True  # Image is considered dark
    else:
        return False  # Image is considered bright
    
def apply_gamma_correction(img, c, is_dark):
    if is_dark:
        print("dark")
        gamma = 0.5  # Brighten dark images
    else:
        print("bright")
        gamma = 3    # Darken bright images
    edited_img = c * (img**gamma)
    return edited_img

def Gamma_Correction(img, c):
    hist = calculate_histogram(img)
    # is_dark = is_image_dark(hist)
    is_dark = True
    edited_img = apply_gamma_correction(img, c, is_dark)
    return edited_img

# Example usage

# for i in range(7,12):
#     img = io.imread("./dataset/testcase"+str(i)+".PNG")
#     img = gray_image(img)
#     img = img[:, 2 * (img.shape[1] // 3):]
#     img = img[img.shape[0] // 3: 2 * (img.shape[0] // 3), :]

#     afterGamma = Gamma_Correction(img, 1)
#     LogAfterGamma = LoGEdgeDetection(afterGamma)

#     HistoAfterGamma = HistogramEqualization(afterGamma, 256)
#     LogAfterGammaHisto = LoGEdgeDetection(HistoAfterGamma)

#     Histo = HistogramEqualization(img, 256)
#     LogAfterHisto = LoGEdgeDetection(Histo)

#     show_images([img, afterGamma, Histo, LogAfterGamma, LogAfterHisto, LogAfterGammaHisto], ["original", "after gamma", "after histogram", "log after gamma", "log after histogram", "log after gamma and histogram"])

