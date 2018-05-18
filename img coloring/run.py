import numpy as np
import sys
import cv2
import random

class ImagePainter:
    R_CHANNEL, G_CHANNEL, B_CHANNEL = (0, 1, 2)
    DEV_MODE, LOGGING = (0, 0)
    CLUSTERING = 1

    def __init__(self, color, gray, outPath, N, saveGray):
        self.colorImg = cv2.cvtColor(cv2.imread(color), cv2.COLOR_BGR2RGB)
        self.grayImg = cv2.imread(gray)
        self.outImgPath = outPath
        grayHeight, grayWidth, grayChannels = self.grayImg.shape
        if grayChannels == 3:
            self.grayImg = cv2.cvtColor(self.grayImg, cv2.COLOR_BGR2GRAY)
        if saveGray:
            cv2.imwrite('gray.jpg', self.grayImg)
        self.outImg = np.zeros([grayHeight, grayWidth, 3])
        self.clusters = int(N)
        self.estimatedColors = np.zeros([self.clusters,3])
        self.grayThresholds = np.zeros(self.clusters)
        if not self.CLUSTERING:
            colorHeight, colorWidth = (self.colorImg.shape[0], self.colorImg.shape[1])
            self.blurImg = None
            self.samples = int(0.01 * colorHeight * colorWidth)
            self.colorThresholds = np.zeros(self.clusters)

    def findColorsByClusterirng(self):
        centers = None
        processingImage = self.colorImg
        processingImage = processingImage.reshape((-1,3))
        processingImage = np.float32(processingImage)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = self.clusters
        if cv2.__version__.startswith("2."):
            centers = cv2.kmeans(processingImage,K,criteria,10, 0)[2]
        else:
            centers = cv2.kmeans(processingImage,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)[2]
        self.estimatedColors = centers
        if self.DEV_MODE:
            print(self.estimatedColors)

    def findColorThresholds(self, useBlur=False):
        heigth, width = (self.colorImg.shape[0], self.colorImg.shape[1])
        processingImage = self.colorImg
        if useBlur:
            processingImage = cv2.blur(self.colorImg, (10, 10))
            self.blurImg = processingImage
        cumHist = np.zeros([heigth, width])
        for x in range(0, heigth):
            for y in range(0, width):
                R_value = int(processingImage[x, y, self.B_CHANNEL])
                G_value = int(processingImage[x, y, self.G_CHANNEL])
                B_value = int(processingImage[x, y, self.R_CHANNEL])
                cumHist[[x], [y]] = R_value + B_value + G_value

        cumHistVecSort = np.sort(cumHist.flatten())
        self.colorThresholds = self.calculateColorIndividuals(cumHistVecSort)
        if self.DEV_MODE:
            print('color thresholds {}'.format(self.colorThresholds))

    # think about minimal variance spread
    def calculateColorIndividuals(self, sortedHist, useMean=False):
        spread = int(len(sortedHist) / self.clusters)
        thresholds = np.zeros(self.clusters)
        for i in range(0, self.clusters):
            lowerBand = i * spread
            upperBand = (i+1) * spread
            if useMean:
                thresholds[i] = int(np.mean(sortedHist[lowerBand:upperBand]))
            else:
                thresholds[i] = np.median(sortedHist[lowerBand:upperBand])
        return thresholds

    # randomly pick samples to estimate color being equivalent to threshold - quasi Monte Carlo method
    def findColorTriples(self):
        if not (self.blurImg is None):
            img = self.blurImg
        else:
            img = self.colorImg
        heigth, width = (img.shape[0], img.shape[1])
        # r,g,b + clusterId
        classifiedPixels = np.zeros((self.samples, 4))
        for sample in range(0, self.samples):
            r = img[random.randint(0, heigth - 1), random.randint(0, width - 1), self.R_CHANNEL]
            b = img[random.randint(0, heigth - 1), random.randint(0, width - 1), self.B_CHANNEL]
            g = img[random.randint(0, heigth - 1), random.randint(0, width - 1), self.G_CHANNEL]
            color = int(r) + int(g) + int(b)
            clusterId = np.argmin([abs(threshold - color) for threshold in self.colorThresholds ])
            classifiedPixels[(sample)] = [r,g,b,clusterId]

        self.estimatedColors = self.findColorIndividuals(classifiedPixels)
        if self.DEV_MODE:
            # print(classifiedPixels)
            print('estimated Colors: \n{}'.format(self.estimatedColors))

    def findColorIndividuals(self, classifiedPixels, useMean=False):
        CLUSTER_INDEX = 3
        colors = np.zeros([self.clusters,3])
        for index in range(0, self.clusters):
            if useMean:
                triple = np.mean(classifiedPixels[classifiedPixels[:, CLUSTER_INDEX] == index], axis=0)
            else:
                triple = np.median(classifiedPixels[classifiedPixels[:, CLUSTER_INDEX] == index], axis=0)
            colors[(index)] = triple[:CLUSTER_INDEX]
        return colors

    def colorGrayImage(self, save=True):
        height, width = (self.grayImg.shape[0], self.grayImg.shape[1])
        outImg = np.zeros([height, width, 3])
        self.grayThresholds = np.arange(int(255 / self.clusters), 256, int(255 / self.clusters))
        if self.LOGGING:
            file = open('logs.txt','w')
            self.grayThresholds.tofile(file," ")
        for x in range(0,height):
            for y in range(0,width):
                intensity = self.grayImg[x,y]
                idx = self.clusters - 1
                for index in range(0, self.clusters):
                    if self.grayThresholds[index] - intensity >= 0:
                        idx = index
                        break
                if self.LOGGING:
                    file.write("intensity {}\tclass {}\t diffs\t".format(intensity, idx))
                    # diffs.tofile(file,sep=", ")
                    file.write("\n")
                outImg[[x], [y], self.B_CHANNEL] = self.estimatedColors[idx, 0]
                outImg[[x], [y], self.G_CHANNEL] = self.estimatedColors[idx, 1]
                outImg[[x], [y], self.R_CHANNEL] = self.estimatedColors[idx, 2]
        if self.DEV_MODE:
            file.close()
        self.outImg = outImg
        if save:
            cv2.imwrite(self.outImgPath, self.outImg)
            print("image saved")

def main(**kwargs):
    inputColor, inputGray, clusters = (None, None, 10)
    for key, value in kwargs.items():
        if key == 'inputColor':
            inputColor = value
        elif key == 'inputGray':
            inputGray = value
        elif key == 'N':
            clusters = value
        elif key == 'outImg':
            outImg = value
    # explicity show we want to use clustering
    ImagePainter.CLUSTERING = 1
    ImagePainter.DEV_MODE = 0
    imagePainter = ImagePainter(inputColor, inputGray, outImg, clusters, False)
    if 1 == ImagePainter.CLUSTERING:
        imagePainter.findColorsByClusterirng()
        imagePainter.colorGrayImage()
    else:
        imagePainter.findColorThresholds()
        imagePainter.findColorTriples()
        imagePainter.colorGrayImage()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SyntaxError("Insufficient arguments")
    else:
        main(**dict(arg.split('=') for arg in sys.argv[1:]))
