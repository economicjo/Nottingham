module "firewall_policy_rule_collection_group_north_south_pr" {
  source = "module-network-firewall-rules"

  rule_collection_group_names = var.policy_fw_config.firewall_north_south_pr.rule_collection_group_names
  policy_id = var.policy_fw_config.firewall_north_south_pr.policy_id
  priority  = var.policy_fw_config.firewall_north_south_pr.priority

  app_rules = local.app_rules_ns_pr
  network_rules = local.network_rules_ns_pr
  nat_rules = local.nat_rules_ns_pr
}

module "firewall_policy_rule_collection_group_east_west_pr" {
  source = "module-network-firewall-rules" 

  rule_collection_group_names = var.policy_fw_config.firewall_east_west_pr.rule_collection_group_names
  policy_id = var.policy_fw_config.firewall_east_west_pr.policy_id
  priority  = var.policy_fw_config.firewall_east_west_pr.priority

  app_rules = local.app_rules_ew_pr
  network_rules = local.network_rules_ew_pr
  nat_rules = local.nat_rules_ew_pr
}

module "ip-groups-resource-group" {
  source         = "module-iam-resource-group.git"
  az_rg_name     = local.rg_names
  az_rg_location = var.location_rg
  az_tags        = var.az_tags
}

module "ip_group_firewall_rules" {
  source                = "module-network-ip-groups"
  location              = module.ip-groups-resource-group.az-rg-location[0]
  resource_group_name   = module.ip-groups-resource-group.az-rg-name[0]
  ip_addresses          = local.ip_group_data
}