import numpy as np
import cv2
import scipy.spatial.distance as distance 
from xlrd import open_workbook

#this file (image recognition)
#input called 'image' in format cv2.imread ???
#output [('r', 'g', 'b')]

#input as faceColor = ('r', 'g', 'b')
#output [productName, websiteLink]

def skinToneFind(selfie):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    
    #outimg = cv2.imread('messi.jpg', cv2.IMREAD_COLOR)
    img = cv2.imread(selfie)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    xmin = 10000
    ymin = 10000
    ymax = 0
    xmax = 0

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        if x < xmin:
            xmin = x
        if y < ymin:
            ymin = y
        if (x+w) > xmax:
            xmax = (x+w)
        if (y+h) > ymax:
            ymax = (y+h)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes: 
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    xmed = (xmin+xmax)//2
    ymed = (ymin+ymax)//2 
    px = img[ymed, xmed]
    #print (px)
    #print (xmed)
    #print (ymed)
    pxlist = px.tolist()
    pxlist.reverse()
    cv2.imshow('img',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #print (pxlist)
    return pxlist
    
def RGB_distance(skin, activeness, acne):
    if activeness == 0: 
        if acne == 0:
            wb= open_workbook('fenty.xls')
        else:
            wb = open_workbook('acne.xls')
    if activeness == 1:
        if acne == 0:
            wb = open_workbook('active.xls')
        else:
            wb = open_workbook('hourglass.xls')
    sheet = wb.sheet_by_name('Sheet1')
    makeup_rgb = [[sheet.cell_value(r, c) for c in range(0,3)] for r in range(1,sheet.nrows)]
    test=[]
    holder=1000000
    y=-1
    for x in range(0,sheet.nrows-1):
        d= distance.euclidean(skin,makeup_rgb[x])
        test.append(distance.euclidean(skin,makeup_rgb[x]))
        if d<holder:
            holder=d
            y=x
    
    r=y+1
    makeup = sheet.cell_value(r,3)
    website = sheet.cell_value(r,4)
    return [makeup, website]

tone = skinToneFind('me.jpg')
output = RGB_distance(tone,0,0)
print (output)