locals {
  # We load the content of the JSON file
  json_content_ns_np = file("../../script/rules_north_south_firewall_np.json")

  # Convert the JSON content to a Terraform data structure
  firewall_data_ns_np = jsondecode(local.json_content_ns_np)

  app_rules_ns_np = lookup(local.firewall_data_ns_np.rule_collection[0], "application_rule_collection", [])
  network_rules_ns_np = lookup(local.firewall_data_ns_np.rule_collection[0], "network_rule_collection", [])
  nat_rules_ns_np = lookup(local.firewall_data_ns_np.rule_collection[0], "nat_rule_collection", [])
}

locals {
  # We load the content of the JSON file
  json_content_ew_np = file("../../script/rules_east_west_firewall_np.json")

  # Convert the JSON content to a Terraform data structure
  firewall_data_ew_np = jsondecode(local.json_content_ew_np)

  app_rules_ew_np = lookup(local.firewall_data_ew_np.rule_collection[0], "application_rule_collection", [])
  network_rules_ew_np = lookup(local.firewall_data_ew_np.rule_collection[0], "network_rule_collection", [])
  nat_rules_ew_np = lookup(local.firewall_data_ew_np.rule_collection[0], "nat_rule_collection", [])
}