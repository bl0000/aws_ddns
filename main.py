import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

import requests

def read_config(file_path):
    config = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading config file: {e}")
        raise
    return config

def update_route53_record(zone_id, record_name, record_type, new_value, credentials, ttl=300):
    try:
        session = boto3.Session(
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key'],
            region_name=credentials['region']
        )
        client = session.client('route53')

        response = client.list_resource_record_sets(
            HostedZoneId=zone_id,
            StartRecordName=record_name,
            StartRecordType=record_type,
            MaxItems='1'
        )

        for record in response['ResourceRecordSets']:
            if record['Name'] == (record_name + "."):
                print(record)
                if record['ResourceRecords'][0]['Value'] == new_value:
                    print("IP has not changed, no update required")
                else:
                    print("IP has changed, performing update")

                    # Prepare the change batch request
                    change_batch = {
                        'Comment': 'Updating record via script',
                        'Changes': [
                            {
                                'Action': 'UPSERT',
                                'ResourceRecordSet': {
                                    'Name': record_name,
                                    'Type': record_type,
                                    'TTL': ttl,
                                    'ResourceRecords': [{'Value': new_value}],
                                }
                            }
                        ]
                    }
                
                    # Update the record
                    response = client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=change_batch
                    )
                
        return response
    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        ip_info = response.json()
        return ip_info['ip']
    except requests.RequestException as e:
        print(f"Error getting public IP: {e}")
        return None

if __name__ == "__main__":
    config = read_config("config.txt")

    hosted_zone_id = config['hosted_zone_id']
    record_name = config['record_name']
    record_type = config['record_type']
    new_value = get_public_ip()
    ttl = int(config['ttl'])

    response = update_route53_record(hosted_zone_id, record_name, record_type, new_value, config, ttl)
    
    if response:
        print(response)
