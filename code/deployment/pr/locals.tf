locals { #NAMESPACE
  namespace = "${var.scope}-${var.env}-${var.region}-${var.solution_name}"
  namespace_rg = "${var.scope}-${var.env}-${var.solution_name}"
}

locals { #RESOURCE GROUP
  rg_names = ["${local.namespace_rg}.ip-group-rgp"]
}

locals {
  latest_ip_file_name = trim(file("../../script/latest_ip.txt"), "\n")

  new_json_file_path = "../../script/${local.latest_ip_file_name}"
  new_json_content = file(local.new_json_file_path)

  ip_group_data = jsondecode(local.new_json_content)
}

locals {
  # We load the content of the JSON file
  json_content_ns_pr = file("../../script/rules_north_south_firewall_pr.json")

  # Convert the JSON content to a Terraform data structure
  firewall_data_ns_pr = jsondecode(local.json_content_ns_pr)

  app_rules_ns_pr = lookup(local.firewall_data_ns_pr.rule_collection[0], "application_rule_collection", [])
  network_rules_ns_pr = lookup(local.firewall_data_ns_pr.rule_collection[0], "network_rule_collection", [])
  nat_rules_ns_pr = lookup(local.firewall_data_ns_pr.rule_collection[0], "nat_rule_collection", [])
}

locals {
  # We load the content of the JSON file
  json_content_ew_pr = file("../../script/rules_east_west_firewall_pr.json")

  # Convert the JSON content to a Terraform data structure
  firewall_data_ew_pr = jsondecode(local.json_content_ew_pr)

  app_rules_ew_pr = lookup(local.firewall_data_ew_pr.rule_collection[0], "application_rule_collection", [])
  network_rules_ew_pr = lookup(local.firewall_data_ew_pr.rule_collection[0], "network_rule_collection", [])
  nat_rules_ew_pr = lookup(local.firewall_data_ew_pr.rule_collection[0], "nat_rule_collection", [])
}