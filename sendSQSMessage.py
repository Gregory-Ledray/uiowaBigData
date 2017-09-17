import boto3

# Send message to SQS queue
def sendMessage(sqs, queueURL, message):
    response = sqs.send_message(
    QueueUrl=queueURL,
    DelaySeconds=5,
    MessageBody=(message)
    )

    return response

if __name__ == '__main__':
    sendLoop('testMessage')
def sendLoop(message):
    if not isinstance(message, str):
        return False
    # Create SQS client
    sqs = boto3.client('sqs', region_name='us-east-2')

    queue_url = 'https://sqs.us-east-2.amazonaws.com/910880444892/makeupAttributeQueue'
    ret = None
    try:
        ret = sendMessage(sqs, queue_url, message)
        return True
    except:
        raise
