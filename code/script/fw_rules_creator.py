import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl')

import pandas as pd
import os
import re
from git import Repo, GitCommandError
import csv
import json

# Normalize column names by removing special characters and extra spaces.
def normalize_column_name(name):
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', name)).strip().lower()

# Determine firewall type and environment from Rulebase value.
def get_firewall_paths(Rulebase):
    Rulebase = Rulebase.lower()
    if "eastwest" in Rulebase:
        firewall_type = "east_west_firewall"
    elif "northsouth" in Rulebase:
        firewall_type = "north_south_firewall"
    else:
        raise ValueError("Unrecognized Rulebase value")

    if "pr" in Rulebase and "np" not in Rulebase:
        firewall_env = "pr"
    elif "np" in Rulebase and "pr" not in Rulebase:
        firewall_env = "np"
    else:
        raise ValueError("Rulebase value not recognized or contains both 'pr' and 'np'")
        

    return firewall_type, firewall_env

# Update priority counters for different rule types.
def update_priority(rule_type, priority_counters):
    current_priority = priority_counters[rule_type]
    priority_counters[rule_type] += 1
    return current_priority

# Process the Excel file and append data to output_dict based on the sheet name and rule types.
def process_excel_and_append_to_csv(excel_file, output_dict, sheet_name, priority_counters):
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1, dtype=str)
    except ValueError as e:
        print(f"Warning: {e}")
        return None, None

    # Normalize column names
    df.columns = [normalize_column_name(col) for col in df.columns]
    print(f"Columns available in {sheet_name}:", df.columns)

    required_columns = {
        'traffic flow': ['rulebase', 'ip address host name group name', 'ip address host name group name1', 
                         'rule collection', 'rule name', 'service', 'port number'],
        'nat rules': ['rulebase', 'source ip address host name group name', 'destination ip address host name group name',
                      'destination ip address host name group name1', 'service', 'port number', 'rule name', 'port number1']
    }

    sheet_name = normalize_column_name(sheet_name)
    
    if sheet_name not in required_columns:
        print(f"Warning: Unknown sheet name {sheet_name}")
        return None, None

    for column in required_columns[sheet_name]:
        if column not in df.columns:
            print(f"Warning: The required column '{column}' not found in excel file on sheet {sheet_name}")
            return None, None

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: x.replace('\n', ' ').replace('\r', ' ') if isinstance(x, str) else x)

    df['rulebase'] = df['rulebase'].astype(str)

    firewall_type = None
    firewall_env = None

    for index, row in df.iterrows():
        Rulebase = row['rulebase']
        rule_name = row['rule name']

        try:
            firewall_type, firewall_env = get_firewall_paths(Rulebase)
        except ValueError as e:
            print(f"Skipping row due to error: {e}")
            continue

        if rule_name.endswith('arl'):
            rule_type = 'app_rules'
        elif rule_name.endswith('nrl'):
            rule_type = 'network_rules'
        elif rule_name.endswith('drl'):
            rule_type = 'nat_rules'
        else:
            print(f"Skipping row with unknown rule name: {rule_name}")
            continue

        base_path = f'../firewall_rules_lists/firewall/{firewall_type}/env/{firewall_env}'
        csv_output = os.path.join(base_path, f'{rule_type}.csv')

        priority = update_priority(rule_type, priority_counters)

        if sheet_name == 'nat rules':
            row_data = {
                'rule_collection': row['rule collection'],
                'action': 'Dnat',
                'rule_name': row['rule name'],
                'source_address': row['source ip address host name group name'],
                'destination_fqdn': row['destination ip address host name group name'],
                'translated_address': row['destination ip address host name group name1'],
                'protocol_type': row['service'],
                'protocol_port': row['port number'],
                'priority': priority,
                'translated_port': row['port number1']
            }
        elif sheet_name == 'traffic flow':
            row_data = {
                'rule_collection': row['rule collection'],
                'action': 'Allow',
                'rule_name': row['rule name'],
                'source_address': row['ip address host name group name'],
                'destination_fqdn': row['ip address host name group name1'],
                'protocol_type': row['service'],
                'protocol_port': row['port number'],
                'priority': priority
            }

        if csv_output not in output_dict:
            output_dict[csv_output] = []
        output_dict[csv_output].append(row_data)

    if firewall_type is not None and firewall_env is not None:
        return firewall_type, firewall_env
    else:
        return None, None

# Clone the repository from the given URL or update it if already exists.
def clone_repository(repo_url, repo_dir):
    try:
        if not os.path.exists(repo_dir):
            print(f"Cloning the repository from {repo_url}...")
            Repo.clone_from(repo_url, repo_dir)
            print("Repository cloned successfully.")
        else:
            print("The repository already exists. Updating the repository...")
            repo = Repo(repo_dir)
            origin = repo.remotes.origin
            try:
                origin.pull('master')
                print("Repository successfully updated.")
            except GitCommandError as e:
                print(f"Error updating repository: {e}")
    except GitCommandError as e:
        print(f"Error cloning or updating the repository: {e}")

# Verify and correct priorities in JSON files.
def verify_and_correct_json_priorities(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    rule_collections = data.get('rule_collection', [])
    if not rule_collections:
        return False

    rule_collections.sort(key=lambda x: x['priority'])
    current_priority = rule_collections[0]['priority']
    corrected = False

    for rule_collection in rule_collections:
        if rule_collection['priority'] != current_priority:
            rule_collection['priority'] = current_priority
            corrected = True
        current_priority += 1

    if corrected:
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Priorities corrected in '{json_file}'")
        return True
    return False

# Correct priorities in all JSON files in the specified directory.
def correct_priorities_in_all_jsons(json_dir):
    corrections_needed = False
    for root, _, files in os.walk(json_dir):
        for file in files:
            if file.endswith(".json"):
                json_file_path = os.path.join(root, file)
                if verify_and_correct_json_priorities(json_file_path):
                    corrections_needed = True
    return corrections_needed

# Generate firewall rules for a given set of rule collection group names and policy ID.
def generate_firewall_rules(rule_collection_group_names, policy_id, priority_start, app_rules, network_rules, nat_rules):
    firewall_rules = {
        "resource": "azurerm_firewall_policy_rule_collection_group",
        "rule_collection": []
    }

    current_priority = priority_start

    for name in rule_collection_group_names:
        rule_collection = {
            "name": name,
            "firewall_policy_id": policy_id,
            "priority": current_priority,
            "nat_rule_collection": nat_rules if nat_rules else None,
            "network_rule_collection": network_rules if network_rules else None,
            "application_rule_collection": app_rules if app_rules else None
        }
        rule_collection = {k: v for k, v in rule_collection.items() if v is not None}
        firewall_rules["rule_collection"].append(rule_collection)
        current_priority += 1

    return firewall_rules

# Split and clean addresses by removing spaces and splitting by comma.
def split_and_clean_addresses(addresses):
    return [addr.strip() for addr in addresses.split(',')]

# Classify addresses into IP addresses, IP groups, and FQDN tags.
def classify_addresses(addresses):
    ip_addresses = []
    ip_groups = []
    fqdn_tags = []
    fqdn_pattern = re.compile(r'.*\.(io|dev|net|com|eu|org|edu|gov|mil|int|co|us|biz|info|mobi|name|aero|jobs|museum|qa|uk|ac\.uk|gov\.uk|org\.uk|me\.uk|ltd\.uk|plc\.uk|net\.uk|sch\.uk|co\.uk|nz|co\.nz|ac\.nz|gov\.nz|org\.nz|net\.nz|au|com\.au|edu\.au|gov\.au|net\.au|org\.au|br|com\.br|org\.br|gov\.br|edu\.br|net\.br|mx|com\.mx|org\.mx|edu\.mx|gob\.mx|net\.mx|jp|co\.jp|ne\.jp|or\.jp|ac\.jp|go\.jp|gr\.jp|za|co\.za|org\.za|gov\.za|ac\.za|edu\.za|net\.za|af|al|dz|as|ad|ao|ai|aq|ag|ar|am|aw|at|az|bs|bh|bd|bb|by|be|bz|bj|bm|bt|bo|ba|bw|bv|bn|bg|bf|bi|kh|cm|ca|cv|ky|cf|td|cl|cn|cx|cc|km|cg|cd|ck|cr|ci|hr|cu|cy|cz|dk|dj|dm|do|ec|eg|sv|gq|er|ee|et|fk|fo|fj|fi|fr|gf|pf|tf|ga|gm|ge|de|gh|gi|gr|gl|gd|gp|gu|gt|gg|gn|gw|gy|ht|hm|hn|hk|hu|is|in|id|ir|iq|ie|im|il|it|jm|je|jo|kz|ke|ki|kp|kr|kw|kg|la|lv|lb|ls|lr|ly|li|lt|lu|mo|mk|mg|mw|my|mv|ml|mt|mh|mq|mr|mu|yt|mx|fm|md|mc|mn|ms|ma|mz|mm|na|nr|np|nl|an|nc|nz|ni|ne|ng|nu|nf|mp|no|om|pk|pw|pa|pg|py|pe|ph|pn|pl|pt|pr|qa|re|ro|ru|rw|sh|kn|lc|pm|vc|ws|sm|st|sa|sn|sc|sl|sg|sk|si|sb|so|za|gs|es|lk|sd|sr|sj|sz|se|ch|sy|tw|tj|tz|th|tl|tg|tk|to|tt|tn|tr|tm|tc|tv|ug|ua|ae|gb|us|um|uy|uz|vu|va|ve|vn|vg|vi|wf|eh|ye|zm|zw)$')


    for addr in addresses:
        if addr.startswith("nesp_ipg"):
            ip_groups.append(f"/subscriptions/052085ce-1c15-489c-9a9f-9fc29729dfd2/resourceGroups/nesp-pr-hub.ip-group-rgp/providers/Microsoft.Network/ipGroups/{addr}")
        elif addr.startswith("tag:"):
            fqdn_tags.append(addr)
        elif fqdn_pattern.match(addr):
            fqdn_tags.append(addr)
        else:
            ip_addresses.append(addr)

    return ip_addresses, ip_groups, fqdn_tags

# Read rules from a CSV file based on rule type (nat, network, app).
def read_rules_from_csv(filename, rule_type):
    rules = {}
    if not os.path.exists(filename):
        print(f"Warning: The file {filename} does not exist.")
        return rules
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rule_collection = row["rule_collection"]
            if rule_collection not in rules:
                rules[rule_collection] = {
                    "name": rule_collection,
                    "priority": int(row["priority"]),
                    "action": row["action"],
                    "rules": []
                }

            if rule_type == "nat":
                destination_ports = ["*"] if row["protocol_port"] in ["*"] else [port if port.isdigit() else port for port in row["protocol_port"].split(', ')]
                translated_port = row["translated_port"] if row["translated_port"] is not None else "443"
                src_addresses, src_ip_groups, _ = classify_addresses(split_and_clean_addresses(row["source_address"]))
                dest_addresses, dest_ip_groups, _ = classify_addresses(split_and_clean_addresses(row["destination_fqdn"]))
                translated_address = row["translated_address"]
                protocol_types = row["protocol_type"].split(',')
                protocol_list = [protocol.strip() for protocol in protocol_types]

                rule = {
                    "name": row["rule_name"],
                    "protocols": protocol_list,
                    "source_addresses": src_addresses,
                    "destination_address": dest_addresses[0] if dest_addresses else None,
                    "destination_ports": destination_ports,
                    "translated_address": translated_address,
                    "translated_port": translated_port  
                }
                rule = {k: v for k, v in rule.items() if v is not None}

            elif rule_type == "network":
                destination_ports = ["*"] if row["protocol_port"] in ["Any", "*"] else [port if port.isdigit() else port for port in row["protocol_port"].split(', ')]
                protocol_types = row["protocol_type"].split(',')
                protocol_list = [protocol.strip() for protocol in protocol_types]
                src_addresses, src_ip_groups, _ = classify_addresses(split_and_clean_addresses(row["source_address"]))
                dest_addresses, dest_ip_groups, _ = classify_addresses(split_and_clean_addresses(row["destination_fqdn"]))
                rule = {
                    "name": row["rule_name"],
                    "source_addresses": src_addresses or None,
                    "source_ip_groups": src_ip_groups or None,
                    "destination_addresses": dest_addresses or None,
                    "destination_ip_groups": dest_ip_groups or None,
                    "destination_ports": destination_ports or None,
                    "protocols": protocol_list or None
                }
                rule = {k: v for k, v in rule.items() if v}

            elif rule_type == "app":
                ports = row["protocol_port"].split(', ')
                protocol_list = []
                for port in ports:
                    if port == "80":
                        protocol_list.append({"type": "Http", "port": int(port)})  
                    elif port == "443":
                        protocol_list.append({"type": "Https", "port": int(port)})  
                    else:
                        protocol_types = row["protocol_type"].split(',')
                        for protocol in protocol_types:
                            protocol_list.append({"type": protocol.strip(), "port": int(port)})

                src_addresses, src_ip_groups, _ = classify_addresses(split_and_clean_addresses(row["source_address"]))
                dest_fqdns, dest_ip_groups, destination_fqdn_tags = classify_addresses(split_and_clean_addresses(row["destination_fqdn"]))

                # Transform IPs to a valid FQDN format (with dots)
                fqdn_list = []
                for addr in dest_fqdns:
                    # Check if the address is an IP and convert it to FQDN
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", addr):  # Check if it's an IP address
                        fqdn_list.append(f"{addr}")  # Keep the IP as is (with dots, not converting to hyphens)
                    else:
                        fqdn_list.append(addr)  # If it's already FQDN, keep it as is

                rule = {
                    "name": row["rule_name"],
                    "source_addresses": src_addresses or None,
                    "source_ip_groups": src_ip_groups or None,
                    "destination_fqdn": fqdn_list or None,  # Use destination_fqdn field
                    "destination_fqdn_tags": destination_fqdn_tags or None,
                    "destination_ip_groups": dest_ip_groups or None,
                    "protocols": protocol_list or None
                }
                rule = {k: v for k, v in rule.items() if v}
            rules[rule_collection]["rules"].append(rule)
    return list(rules.values())

# Generate and save firewall rules as JSON files.
def generate_and_save_firewall_rules(firewall_type, firewall_env, output_dir, priority_counters):
    rule_collection_group_names = ["example_group_name"]
    policy_id = "example_policy_id"
    
    base_path = os.path.join(output_dir, f'firewall/{firewall_type}/env/{firewall_env}')
    
    app_rules = read_rules_from_csv(os.path.join(base_path, 'app_rules.csv'), "app")
    network_rules = read_rules_from_csv(os.path.join(base_path, 'network_rules.csv'), "network")
    nat_rules = read_rules_from_csv(os.path.join(base_path, 'nat_rules.csv'), "nat")

    # Adjust priorities to ensure continuity
    priority_counters['network_rules'] += priority_counters['nat_rules']
    priority_counters['app_rules'] += priority_counters['network_rules']

    rules = generate_firewall_rules(rule_collection_group_names, policy_id, priority_counters['nat_rules'], app_rules, network_rules, nat_rules)

    filename = f'rules_{firewall_type}_{firewall_env}.json'

    with open(filename, 'w') as file:
        json.dump(rules, file, indent=4)

    print(f"Rules have been saved at '{filename}'")

# Main function to clone the repository, process Excel files, and generate firewall rules.
def main():
    repo_url = "ssh://git@52.166.71.39:7999/nnap/global-hub-firewall-commatrix.git"
    repo_dir = "global-hub-firewall-commatrix"
    application_commatrix_dir = os.path.join(repo_dir, "application_commatrix")
    json_output_dir = '../firewall_rules_lists'

    clone_repository(repo_url, repo_dir)

    output_dict = {}
    firewall_types_env = set()

    priority_counters = {
        'app_rules': 501,
        'network_rules': 301,
        'nat_rules': 100  
    }

    for root, dirs, files in os.walk(application_commatrix_dir):
        for file in files:
            if file.endswith(".xlsx"):
                excel_file_path = os.path.join(root, file)
                print(f"Processing file: {excel_file_path}")
                for sheet_name in ['Traffic Flow', 'NAT Rules']:
                    firewall_type, firewall_env = process_excel_and_append_to_csv(excel_file_path, output_dict, sheet_name, priority_counters)
                    if firewall_type and firewall_env:
                        firewall_types_env.add((firewall_type, firewall_env))

    for csv_output, rows in output_dict.items():
        df_final = pd.DataFrame(rows)
        os.makedirs(os.path.dirname(csv_output), exist_ok=True)
        df_final.to_csv(csv_output, mode='w', header=True, index=False)
        print(f"File successfully updated to: {csv_output}")

    required_firewall_types_env = [
        ('east_west_firewall', 'pr'),
        ('east_west_firewall', 'np'),
        ('north_south_firewall', 'pr'),
        ('north_south_firewall', 'np')
    ]

    for firewall_type, firewall_env in required_firewall_types_env:
        if (firewall_type, firewall_env) not in firewall_types_env:
            os.makedirs(os.path.join(json_output_dir, f'firewall/{firewall_type}/env/{firewall_env}'), exist_ok=True)
        generate_and_save_firewall_rules(firewall_type, firewall_env, output_dir=json_output_dir, priority_counters=priority_counters)

# Check and correct priorities in all generated JSON
    if correct_priorities_in_all_jsons(json_output_dir):
        # If corrections were made, regenerate the JSON
        for firewall_type, firewall_env in required_firewall_types_env:
            generate_and_save_firewall_rules(firewall_type, firewall_env, output_dir=json_output_dir, priority_counters=priority_counters)

if __name__ == "__main__":
    main()

# Adjust priorities in the specified JSON file.
def adjust_priorities(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    new_priority = 100

    if 'rule_collection' in data and isinstance(data['rule_collection'], list):
        for rule_group in data['rule_collection']:
            if 'nat_rule_collection' in rule_group:
                for nat_rule in rule_group['nat_rule_collection']:
                    nat_rule['priority'] = new_priority
                    new_priority += 1

            if 'network_rule_collection' in rule_group:
                for net_rule in rule_group['network_rule_collection']:
                    net_rule['priority'] = new_priority
                    new_priority += 1

            if 'application_rule_collection' in rule_group:
                for app_rule in rule_group['application_rule_collection']:
                    app_rule['priority'] = new_priority
                    new_priority += 1

    with open(file_path, 'w') as output_file:
        json.dump(data, output_file, indent=4)

json_files = [
    'rules_east_west_firewall_np.json',
    'rules_east_west_firewall_pr.json',
    'rules_north_south_firewall_np.json',
    'rules_north_south_firewall_pr.json'
]

for json_file in json_files:
    adjust_priorities(json_file)

print("Adjusted priorities and overwritten files.")