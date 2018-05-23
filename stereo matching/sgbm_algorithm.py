import cv2
from tkinter import filedialog, Tk
import numpy as np

class SGBMParamsHandler:
  def __init__(self):
    self.windowSize = 7
    self.disparity = 160
    self.disp12MaxDiff = 1
    self.uniquenessRatio = 15
    self.speckleWindowSize = 0
    self.speckleRange = 2
    self.preFilterCap = 63

  def setWindowSize(self, windowSize):
    if windowSize > 15 or windowSize < 3:
      cv2.setTrackbarPos("window size", "window", 7)
    elif not (windowSize % 2):
      currentWindowSize = windowSize + 1
      cv2.setTrackbarPos("window size", "window", currentWindowSize)
    else:
      self.windowSize = windowSize

  def setDisparity(self, disparity):
    if disparity % 16:
      currentDisparity = disparity - (disparity % 16)
      cv2.setTrackbarPos("disparity", "window", currentDisparity)
    else:
      self.disparity = disparity


class SGBMSolver:

  def __init__(self, leftImg, rightImg):
    self.sgbmParamsHander = SGBMParamsHandler()
    (self.leftImg, self.rightImg) = self.readImages(leftImg, rightImg)
    self.runMatching()

  def readImages(self, leftImgPath, rightImgPath):
    leftImg = cv2.imread(leftImgPath)
    rightImg = cv2.imread(rightImgPath)
    if leftImg.any() == None or rightImg.any() == None:
      raise Exception('No image provided!')
    else:
      return (leftImg, rightImg)

  def runMatching(self):
    cv2.imshow("Disparity Map", self.leftImg)
    cv2.createTrackbar("window size", "Disparity Map",
    self.sgbmParamsHander.windowSize, 41, self.sgbmParamsHander.setWindowSize)
    cv2.createTrackbar("disparity", "Disparity Map", self.sgbmParamsHander.disparity, 512, self.sgbmParamsHander.setWindowSize)
    keyPressed = None
    while keyPressed != 113 and keyPressed != 27:
      left_matcher = cv2.StereoSGBM_create(
      minDisparity=0,
      numDisparities=self.sgbmParamsHander.disparity,
      blockSize=self.sgbmParamsHander.windowSize,
      P1=8 * 3 * self.sgbmParamsHander.windowSize ** 2,
      P2=32 * 3 * self.sgbmParamsHander.windowSize ** 2,
      disp12MaxDiff=self.sgbmParamsHander.disp12MaxDiff,
      uniquenessRatio=self.sgbmParamsHander.uniquenessRatio,
      speckleWindowSize=self.sgbmParamsHander.speckleWindowSize,
      speckleRange=self.sgbmParamsHander.speckleRange,
      preFilterCap=self.sgbmParamsHander.preFilterCap,
      mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
      )
      right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
      (lambdaF, sigma) = (80000, 1.2)
      wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=left_matcher)
      wls_filter.setLambda(lambdaF)
      wls_filter.setSigmaColor(sigma)
      print('computing disparity...')
      dispL = left_matcher.compute(self.leftImg, self.rightImg)
      dispR = right_matcher.compute(self.leftImg, self.rightImg)
      dispL = np.int16(dispL)
      dispR = np.int16(dispR)
      filteredImg = wls_filter.filter(
      dispL, self.leftImg, None, dispR)
      filteredImg = cv2.normalize(
      src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX)
      filteredImg = np.uint8(filteredImg)
      cv2.imshow("Disparity Map", filteredImg)
      keyPressed = cv2.waitKey(50)
    cv2.destroyWindow("Disparity Map")

if __name__ == "__main__":
  root = Tk()
  root.withdraw()
  leftImg = filedialog.askopenfilename(initialdir=".", title="Select left Image", filetypes=(
  ("png files", "*.png"), ("img files", "*.jpg")))
  rightImg = filedialog.askopenfilename(initialdir=".", title="Select left Image", filetypes=(
  ("png files", "*.png"), ("img files", "*.jpg")))
  sgbm = SGBMSolver(leftImg, rightImg)
