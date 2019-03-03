import sys, urllib, cv2, numpy, math, time

from pyfy import ClientCreds, Spotify

covers = []

# Load in from text file
in_file = open('rgb.txt', 'r')
lines = in_file.readlines()
for line in lines:
    vals = line.split()
    covers.append([int(vals[0]), int(vals[1]), int(vals[2]), vals[3]])

# Combine arguments into one search string
search_string = ''
for word in sys.argv[1:]:
    search_string += word + ' '
print(search_string.rstrip())

# Connect with Spotify python Web API using credentials
token = tuple(open("token.txt", 'r'))
client = ClientCreds(client_id=token[0].rstrip(), client_secret=token[1].rstrip())
spt = Spotify(client_creds=client)
spt.authorize_client_creds()

# Search using command line argument, get the first result back
results = list(spt.search(search_string, types='album', limit=1).values())

# Get album cover of url and download it to "image.jpg"
for item in results[0]['items']:
    for k, v in item.items():
        if k == 'images':
            print(v[1]['url'])
            file = open("image.jpg", 'wb')
            file.write(urllib.request.urlopen(v[1]['url']).read())
            file.close()

# Function to get average RGB values of seciton of an image
def getAverageRGB(chunk, w, h):
    avR = 0
    avG = 0
    avB = 0
    num = 0
    for i in range(w):
        for j in range(h):
            num += 1
            try:
                avR += chunk[i, j][0]
                avG += chunk[i, j][1]
                avB += chunk[i, j][2]
            except IndexError as exc:
                avR += 50
                avG += 50
                avB += 50
    avR /= num
    avG /= num
    avB /= num
    return round(avR), round(avG), round(avB)

# Get difference between R, G, and B vals, return winner
def getRGBDiffWinner(r, g, b):
    deltaR, deltaG, deltaB = 255, 255, 255
    delta = 1000
    for img in covers:
        if abs(img[0] - r) < deltaR:
            deltaR = abs(img[0] - r)
        if abs(img[1] - r) < deltaR:
            deltaG = abs(img[1] - r)
        if abs(img[2] - r) < deltaR:
            deltaB = abs(img[2] - r)
        if (deltaR + deltaG + deltaB) < delta:
            delta = deltaR + deltaG + deltaB
            winner = img
    covers.remove(winner)
    return winner[3]

# Load image with OpenCV
image = cv2.imread("image.jpg")
copy = cv2.imread("image.jpg")
height, width, _ = image.shape

# Force to be 300x300 if its not already
if not height == 300 or not width == 300:
    image = cv2.resize(image, (300, 300), interpolation = cv2.INTER_AREA)

# Split into squares, 30x30 = 900 squares
div = 50
scaleX, scaleY = int(width/div), int(height/div)

for i in range(div):
    for j in range(div):
        section = image[j*scaleX:(j+1)*scaleX, i*scaleY:(i+1)*scaleY]
        r, g, b = getAverageRGB(section, scaleX, scaleY)
        winner = getRGBDiffWinner(r, g, b)
        winnerFile = cv2.imread('img\\' + winner)
        height, width = winnerFile.shape[:2]
        newW, newH = (j+1)*scaleX - j*scaleX, (i+1)*scaleY - i*scaleY
        winnerOut = cv2.resize(winnerFile, (newW, newH), interpolation = cv2.INTER_AREA)
        try:
            image[j*scaleX:(j+1)*scaleX, i*scaleY:(i+1)*scaleY] = winnerOut
        except ValueError as exc:
            try:
                winnerOut = cv2.resize(winnerFile, (newH, newW), interpolation = cv2.INTER_AREA)
                image[j*scaleX:(j+1)*scaleX, i*scaleY:(i+1)*scaleY] = winnerOut
            except ValueError as exc:
                print("Not placing square at",i,j)

# Display the input and output
cv2.imshow('Output', image)
cv2.imshow('Input', copy)
cv2.waitKey(0)
cv2.destroyAllWindows()