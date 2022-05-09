import argparse
import time 
import cv2
import os 

ap = argparse.ArgumentParser(description='opencv lab for super resolution')
ap.add_argument('-m','--model',required=True, help='path to super resolution model')
ap.add_argument('-i','--image',required=True, help='paht to input image') 

args = vars(ap.parse_args())

modelName = args["model"].split(os.path.sep)[-1].split("_")[0].lower()
modelScale = args["model"].split("_x")[-1]
modelScale = int(modelScale[:modelScale.find(".")])

sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel(args["model"])
sr.setModel(modelName, modelScale)


image = cv2.imread(args['image'])
print("[INFO] w: {}, h: {}".format(image.shape[1], image.shape[0]))

start = time.time()
upscaled = sr.upsample(image)
end = time.time()
print("[INFO] super resolution took {:.6f} seconds".format(
	end - start))

# show the spatial dimensions of the super resolution image
print("[INFO] w: {}, h: {}".format(upscaled.shape[1],
	upscaled.shape[0]))

# resize the image using standard bicubic interpolation
start = time.time()
bicubic = cv2.resize(image, (upscaled.shape[1], upscaled.shape[0]),
interpolation=cv2.INTER_CUBIC)
end = time.time()
print("[INFO] bicubic interpolation took {:.6f} seconds".format(
end - start))

# show the original input image, bicubic interpolation image, and
# super resolution deep learning output
# cv2.imshow("Original", image)
# cv2.imshow("Bicubic", bicubic)
# cv2.imshow("Super Resolution", upscaled)
# cv2.waitKey(0)

cv2.imwrite('bicubic.jpg', bicubic)
cv2.imwrite('super.jpg', upscaled)