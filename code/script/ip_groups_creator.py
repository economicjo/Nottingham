import csv
import json
import os
import sys
from ipaddress import ip_network
import datetime

def create_ip_list(ip_group_name, ip_list):
    ip_group_name = ip_group_name.strip()
    ip_list = [ip.strip('"') for ip in ip_list.split(",")]
    ip_objects = [str(ip_network(ip, strict=False)) for ip in ip_list]
    return {ip_group_name: ip_objects}

def read_ip_groups_from_csv(file_path):
    ip_data = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ip_data.update(create_ip_list(row['IP Group name'], row['IP List']))
    return ip_data

def save_to_json(ip_data, filename):
    with open(filename, 'w') as json_file:
        json.dump(ip_data, json_file, indent=4)

if __name__ == "__main__":
    # Construct the CSV file path based on the environment
    # Make sure the directory name matches exactly with your folder structure
    csv_file_path = f'../ip_group/ip_group.csv'

    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        sys.exit(1)

    # Read IP groups from CSV
    ip_data = read_ip_groups_from_csv(csv_file_path)

    # Generate JSON file name with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file_name = f'ip_list_{timestamp}.json'

    # Save to JSON
    save_to_json(ip_data, json_file_name)

    # Update latest file
    latest_file_name = f'latest_ip.txt'
    if os.path.exists(latest_file_name):
        with open(latest_file_name, 'r') as f:
            last_file = f.read().strip()
            if os.path.exists(last_file):
                os.remove(last_file)

    with open(latest_file_name, 'w') as f:
        f.write(json_file_name)

    print(f"The IP list has been saved at '{json_file_name}' and registered at '{latest_file_name}'")