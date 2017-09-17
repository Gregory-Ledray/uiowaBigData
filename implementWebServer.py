from __future__ import print_function
import receiveSQSMessage
import sendSQSMessage
from extraLib import *
import numpy as np
import scipy.spatial.distance as distance
from xlrd import open_workbook
import os, boto3, cv2, urllib.request
import requests

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
    #cv2.imshow('img',img)
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
    return (makeup, website)
def processInputImage(inDict):
    #to process the image, first retrieve the image
    bucket = inDict['bucket']
    key = inDict['key']
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    print ('obj', obj)
    print('starting dumb download')
    print('key', key, 'bucket', bucket)
    basicURL = (('https://'+bucket+'.s3.amazonaws.com/'+str(key)))
    enhanced = basicURL+' -i MakeupMyMind.pem'
    print (enhanced)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
    enhancedReq = urllib.request.Request(enhanced, headers=headers)
    with urllib.request.urlopen(enhancedReq) as response:
        html = response.read()
    print (html)
    print('finished dumb download')
    print (s3.download_file(bucket, key, 'tmpImg.jpg'))
    print(open('tmpImg.jpg').read())
    print ('got here')
    transfer = S3Transfer(s3)
    response = None
    try:
        response = transfer.download_file(str(bucket), str(key), '/tmp/tmpImg.jpg')
        
        print("CONTENT TYPE: " + response['ContentType'])
        print(response)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        if e.response['Error']['Code'] == '404':
            return ['0', '0', '0']

        raise e

    
    #now that we have a response, pull the image data from jpeg and load it for ML
    image = '/tmp/tmpImg.jpg' 

    #run the ML algorithms
    attributes = skinToneFind(image)

    #delete the image from RAM
    os.remove('tmpImg.jpg')

    #return classified attributes with (r,g,b)
    return attributes

def predict(attributes):
    #store all of the attributes locally
    faceColorRGB = attributes[0]
    acne = attributes[1]
    active = attributes[2]

    #find nearest neighbor using a .csv file functioning as a classification database
    output = RGB_distance(faceColorRGB, acne, active)

    #return the best makeup name and website/link
    return output

#I assume the input message is of format key=value.key=value.key=value
if __name__ == '__main__':
    inQ = receiveSQSMessage.receiveLoop()
    print (inQ)
    info = inQ.split('.')
    info2 = []
    inData={}
    c=0
    for entry in info:
        if entry == 'jpg':
            info2[c-1]+='.jpg'
        else:
            c+=1
            info2.append(entry)
    for entry in info2:
        dictReadyEntry = entry.split('=')
        try:
            inData[dictReadyEntry[0]] = dictReadyEntry[1]
        except:
            print (entry, dictReadyEntry)
            raise    
    attributes = processInputImage(inData)
   
    #TODO
    #push the filename, attributes, acne, active to the MySQL database on the image line 

    #print out the attributes we've found by processing the input message
    for i in attributes:
        print (attributes)

    #make a prediction based on the input attributes
    (name, website) = predict(attributes, inData['acne'], inData['active'])
    
    #TODO
    #pull the MySQL database line which contains the file name (now .text)
    
    #TODO FINISH
    #Create a new file with that name and the name, website data
    filename = str(inData['key'])
    filename = filename[:-4]
    filename = filename + '.txt'
    formattedOut = 'Product Name: '+str(name)+' Website: '+str(website)
    open(filename).write(formattedOut)
    #push that new file to the S3 data dump
    s3 = boto3.client('s3')
    s3.upload_file(str(inData['key']), 'make-up-your-mind-response', str(inData['key']))
