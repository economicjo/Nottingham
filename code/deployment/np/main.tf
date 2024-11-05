module "firewall_policy_rule_collection_group_north_south_np" {
  source = "git::ssh://git@52.166.71.39:7999/nnap/module-network-firewall-rules.git//firewalls-policy-rule-collection-group?ref=1.4.0"

  rule_collection_group_names = var.policy_fw_config.firewall_north_south_np.rule_collection_group_names
  policy_id = var.policy_fw_config.firewall_north_south_np.policy_id
  priority  = var.policy_fw_config.firewall_north_south_np.priority

  app_rules = local.app_rules_ns_np
  network_rules = local.network_rules_ns_np
  nat_rules = local.nat_rules_ns_np
}

module "firewall_policy_rule_collection_group_east_west_np" {
  source = "git::ssh://git@52.166.71.39:7999/nnap/module-network-firewall-rules.git//firewalls-policy-rule-collection-group?ref=1.4.0" 

  rule_collection_group_names = var.policy_fw_config.firewall_east_west_np.rule_collection_group_names
  policy_id = var.policy_fw_config.firewall_east_west_np.policy_id
  priority  = var.policy_fw_config.firewall_east_west_np.priority

  app_rules = local.app_rules_ew_np
  network_rules = local.network_rules_ew_np
  nat_rules = local.nat_rules_ew_np
}