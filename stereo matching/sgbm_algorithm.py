import cv2 
from tkinter import filedialog
from tkinter import *

class SGBMSolver:
  
  def __init__(self, leftImg, rightImg):
    self.blockSize = 5
    self.disparity = 64
    self.P1 = 200
    self.P2 = 800
    self.filterCap = 1

    (self.leftImg, self.rightImg) = self.readImages(leftImg, rightImg)
    self.runMatching()

  def readImages(self,leftImgPath, rightImgPath):
    leftImg = cv2.imread(leftImgPath)
    rightImg = cv2.imread(rightImgPath)
    if leftImg.any() == None or rightImg.any() == None:
      raise Exception('No image provided!')
    else:
      return (leftImg, rightImg)
      
  def runMatching(self):
    cv2.imshow("window",self.leftImg)
    cv2.createTrackbar("window size","window",self.windowSize,41, self.setWindowSize)
    cv2.createTrackbar("disparity","window",self.disparity,400, self.setDisparity)
    keyPressed = None
    while keyPressed != 113 and keyPressed != 27:
      cv2.SGBM
      keyPressed = cv2.waitKey(50)
    cv2.destroyWindow("window")

  def setWindowSize(self, windowSize):
    if windowSize > 255 or windowSize < 255:
      cv2.setTrackbarPos("window size","window", 100)
    elif not (windowSize % 2):
      currentWindowSize = windowSize + 1
      cv2.setTrackbarPos("window size","window", currentWindowSize)
    else:
      self.windowSize = windowSize

  def setDisparity(self, disparity):
    if disparity % 16:
      currentDisparity = disparity - (disparity % 16)
      cv2.setTrackbarPos("disparity","window", currentDisparity)
    else:
      self.disparity = disparity

if __name__ == "__main__":
  root = Tk()
  root.withdraw()
  leftImg =  filedialog.askopenfilename(initialdir = ".",title = "Select left Image",filetypes = (("png files","*.png"),("img files","*.jpg")))
  rightImg = filedialog.askopenfilename(initialdir = ".",title = "Select left Image",filetypes = (("png files","*.png"),("img files","*.jpg")))
  sgbm = SGBMSolver(leftImg, rightImg)