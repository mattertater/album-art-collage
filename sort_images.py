import sys, urllib, cv2, numpy, os

def getAverageRGB(chunk, w, h):
    avR, avG, avB, num = 0, 0, 0, 0
    for i in range(h):
        for j in range(w):
            num += 1
            avR += chunk[i, j][0]
            avG += chunk[i, j][1]
            avB += chunk[i, j][2]
    avR /= num
    avG /= num
    avB /= num
    return int(avR), int(avG), int(avB)

output = open("rgb.txt", 'a')

# Open every image
for file in os.listdir('img'):
    image = cv2.imread('img\\'+file)
    height, width, _ = image.shape
    avR, avB, avG = getAverageRGB(image, width, height)
    print(avR, avG, avB, file)
    output.write("%d %d %d %s\n" % (avR, avG, avB, file))