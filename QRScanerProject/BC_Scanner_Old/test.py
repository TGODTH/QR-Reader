# import computer vision library(cv2) in this code
import cv2

# main code
if __name__ == "__main__":
    # mentioning absolute path of the image
    img_path = "58-12606-V.tif"

    # read/load an image
    image = cv2.imread(img_path)

    # show the input image on the newly created window
    cv2.imshow('input image', image)

    # convert image from BGR color space to GRAY color space
    convert_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # show the output image on the newly created window
    cv2.imshow('output image', convert_image)