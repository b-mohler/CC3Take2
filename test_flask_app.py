import pytest
import requests
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

BASE_URL = 'http://localhost:5000/items'
DYNAMODB_TABLE_NAME = 'ItemsTable'
S3_BUCKET_NAME = 'items-bucket'

# Initialize DynamoDB and S3 clients
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')
s3 = boto3.client('s3', endpoint_url='http://localhost:4566')

# Helper functions
def create_dynamo_table():
    try:
        dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'item_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'item_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            raise

def setup_s3_bucket():
    try:
        s3.create_bucket(Bucket=S3_BUCKET_NAME)
    except ClientError as e:
        if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
            raise

def delete_s3_bucket():
    s3.delete_bucket(Bucket=S3_BUCKET_NAME)

def clear_dynamo_table():
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.scan()
    for item in response.get('Items', []):
        table.delete_item(Key={'item_id': item['item_id']})

def clear_s3_bucket():
    objects = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    for obj in objects.get('Contents', []):
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])

def check_dynamo_item(item_id, expected_data):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.get_item(Key={'item_id': item_id})
    item = response.get('Item')
    assert item == expected_data

def check_s3_object(item_id, expected_data):
    response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=item_id)
    s3_object_data = response['Body'].read().decode('utf-8')
    assert s3_object_data == expected_data

@pytest.fixture(scope='module', autouse=True)
def setup_module():
    create_dynamo_table()
    setup_s3_bucket()
    yield
    clear_dynamo_table()
    clear_s3_bucket()
    delete_s3_bucket()

def test_get_item_existing():
    item_id = 'test_item'
    data = {'name': 'Test Item', 'value': 'Test Value'}
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    table.put_item(Item={'item_id': item_id, **data})
    s3.put_object(Bucket=S3_BUCKET_NAME, Key=item_id, Body=str(data))
    
    response = requests.get(f'{BASE_URL}/{item_id}')
    assert response.status_code == 200
    assert response.json() == data

def test_get_item_not_found():
    response = requests.get(f'{BASE_URL}/non_existing_item')
    assert response.status_code == 404
    assert response.json() == {'error': 'Item not found'}

def test_get_item_no_param():
    response = requests.get(BASE_URL)
    assert response.status_code == 405  # Method Not Allowed

def test_get_item_invalid_param():
    response = requests.get(f'{BASE_URL}/invalid_param/extra')
    assert response.status_code == 404  # Not Found or Bad Request

def test_post_item():
    item_id = 'new_item'
    data = {'name': 'New Item', 'value': 'New Value'}
    response = requests.post(f'{BASE_URL}/{item_id}', json=data)
    assert response.status_code == 201
    assert response.json() == data
    check_dynamo_item(item_id, data)
    check_s3_object(item_id, str(data))

def test_post_item_duplicate():
    item_id = 'duplicate_item'
    data = {'name': 'Duplicate Item', 'value': 'Duplicate Value'}
    requests.post(f'{BASE_URL}/{item_id}', json=data)
    response = requests.post(f'{BASE_URL}/{item_id}', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Item already exists'}

def test_put_item_existing():
    item_id = 'update_item'
    data = {'name': 'Update Item', 'value': 'Update Value'}
    requests.post(f'{BASE_URL}/{item_id}', json=data)
    updated_data = {'name': 'Updated Item', 'value': 'Updated Value'}
    response = requests.put(f'{BASE_URL}/{item_id}', json=updated_data)
    assert response.status_code == 200
    assert response.json() == updated_data
    check_dynamo_item(item_id, updated_data)
    check_s3_object(item_id, str(updated_data))

def test_put_item_not_found():
    item_id = 'non_existing_item'
    updated_data = {'name': 'Non Existing Item', 'value': 'Non Existing Value'}
    response = requests.put(f'{BASE_URL}/{item_id}', json=updated_data)
    assert response.status_code == 404
    assert response.json() == {'error': 'Item not found'}

def test_delete_item_existing():
    item_id = 'delete_item'
    data = {'name': 'Delete Item', 'value': 'Delete Value'}
    requests.post(f'{BASE_URL}/{item_id}', json=data)
    response = requests.delete(f'{BASE_URL}/{item_id}')
    assert response.status_code == 204
    check_dynamo_item(item_id, None)
    s3_objects = s3.list_objects_v2(Bucket=S3_BUCKET_NAME).get('Contents', [])
    assert all(obj['Key'] != item_id for obj in s3_objects)

def test_delete_item_not_found():
    item_id = 'non_existing_item'
    response = requests.delete(f'{BASE_URL}/{item_id}')
    assert response.status_code == 404
    assert response.json() == {'error': 'Item not found'}
