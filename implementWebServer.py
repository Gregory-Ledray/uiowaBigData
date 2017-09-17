import receiveSQSMessage
import sendSQSMessage

def mlAlgo(image):
    return [('r', 'g', 'b')]


def processInputImage(inDict):
    #to process the image, first retrieve the image
    bucket = inDict['bucket']
    key = inDict['key']
    s3 = boto3.client('s3', region_name='us-east-2')
    response = None
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        
        print("CONTENT TYPE: " + response['ContentType'])
        print(response)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

    #now that we have a response, pull the image data from jpeg and load it for ML
    image = ''

    #run the ML algorithms
    attributes = mlAlgo(image)

    #return classified attributes
    return attributes

def predict(attributes):
    #store all of the attributes locally
    faceColorRGB = attributes[0]

    #poll the database for all classified solutions

    #find the nearest neighbor

    #return the best makeup name and website/link
    return ('name', 'website')

#I assume the input message is of format key=value.key=value.key=value
if __name__ == '__main__':
    inQ = receiveSQSMessage.receiveLoop()
    print inQ
    info = inQ.split('.')
    inData={}
    for entry in info:
        dictReadyEntry = entry.split('=')
        inData[dictReadyEntry[0]] = dictReadyEntry[1]
    
    attributes = processInputMessage(inData)
    
    #print out the attributes we've found by processing the input message
    for i in attributes:
        print attributes

    #make a prediction based on the input attributes
    predict(attributes)

    outMessage='testOutMessage'
    if not sendSQSMessage.sendLoop(outMessage):
        print ('failed to send a message')
