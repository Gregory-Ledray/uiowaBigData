import boto3

# Send message to SQS queue
def receiveMessage(sqs, queueURL):
    response = sqs.receive_message(
    QueueUrl=queueURL,
    MaxNumberOfMessages=1,
    VisibilityTimeout=0,
    WaitTimeSeconds=5
    )
    
    try:
        message = response['Messages'][0]
    except:
        return None

    sqs.delete_message(QueueUrl=queueURL, ReceiptHandle=message['ReceiptHandle'])

    return response 


def receiveLoop():
    # Create SQS client
    sqs = boto3.client('sqs', region_name='us-east-2')

    queue_url = 'https://sqs.us-east-2.amazonaws.com/910880444892/makeupImageQueue'
    rec = None
    while True:
        rec = receiveMessage(sqs, queue_url)
        if rec is not None:
            break
        else:
            print('no message received')
    return rec['Messages'][0]['Body']

if __name__ == '__main__':
    receiveLoop()
