import os
import pgpy
import boto3

def lambda_handler(event, context):

    priv_key = 'some_key_path'
    passphrase = 'some_passphrase'

    s3 = boto3.client('s3')

    s3bucket = event['Records'][0]['s3']['bucket']['name']
    s3key = event['Records'][0]['s3']['object']['key']

    print("Bucket is: " + s3bucket)
    print("Key is: " + s3key)

    def remove_gpg_from_name(path):
        return os.path.splitext(path)[0]

    def decrypt_file(filename, priv_key, passphrase):
        ## read it from s3
        response = s3.get_object(Bucket=s3bucket, Key=s3key)
        blob_string = response['Body'].read()

        file_to_blob = open(priv_key, 'r')
        key_string = file_to_blob.read()
        print(key_string)
        ## decrypt it
        emsg = pgpy.PGPMessage.from_blob(blob_string)
        key,_ = pgpy.PGPKey.from_blob(key_string)
        with key.unlock(passphrase):
            decrypted_path = remove_gpg_from_name(filename)
            s3.put_object(Body=key.decrypt(emsg).message.decode("utf-8"), Bucket=s3bucket, Key=decrypted_path)
            print("Decrypted this file: " + filename)
            print("Added this decrypted file: " + decrypted_path)

    decrypt_file(s3key,priv_key)

    return True
