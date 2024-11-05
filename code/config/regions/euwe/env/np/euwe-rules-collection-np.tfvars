##ENVIRONMENT
subscription_id = ""
tenant_id       = ""
/*client_id       = "value"
client_secret   = "value"*/

policy_fw_config = {
  firewall_north_south_np = {
    rule_collection_group_names = ["North-South-Firewall-Rules-Collection-NonProd"]
    policy_id = ""
    priority = 100
  },
  firewall_east_west_np = {
    rule_collection_group_names = ["East-West-Firewall-Rules-Collection-NonProd"]
    policy_id = ""
    priority = 100
  }
}