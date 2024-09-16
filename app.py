from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
import os

app = Flask(__name__)

# Configure DynamoDB and S3
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localstack:4566', region='us-east-1')
s3 = boto3.client('s3', endpoint_url='http://localstack:4566', region='us-east-1')

# Set up table and bucket names
TABLE_NAME = 'ItemsTable'
BUCKET_NAME = 'items-bucket'

# Create DynamoDB table and S3 bucket
def setup_resources():
    # Create DynamoDB table
    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'item_id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'item_id',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            raise

    # Create S3 bucket
    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
            raise

setup_resources()

@app.route('/items/<item_id>', methods=['GET'])
def get_item(item_id):
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={'item_id': item_id})
    item = response.get('Item')
    if item is None:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(item), 200

@app.route('/items/<item_id>', methods=['POST'])
def create_item(item_id):
    table = dynamodb.Table(TABLE_NAME)
    if table.get_item(Key={'item_id': item_id}).get('Item'):
        return jsonify({'error': 'Item already exists'}), 400
    data_store = request.json
    table.put_item(Item={'item_id': item_id, **data_store})
    return jsonify(data_store), 201

@app.route('/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    table = dynamodb.Table(TABLE_NAME)
    if not table.get_item(Key={'item_id': item_id}).get('Item'):
        return jsonify({'error': 'Item not found'}), 404
    data_store = request.json
    table.put_item(Item={'item_id': item_id, **data_store})
    return jsonify(data_store), 200

@app.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    table = dynamodb.Table(TABLE_NAME)
    if not table.get_item(Key={'item_id': item_id}).get('Item'):
        return jsonify({'error': 'Item not found'}), 404
    table.delete_item(Key={'item_id': item_id})
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
