## GLOBAL VARIABLES ##
## NAMING CONVENTIONS ##
scope         = ""
env           = ""
region        = ""
solution_name = ""

##ENVIRONMENT
subscription_id = ""
tenant_id       = ""
/*client_id       = "value"
client_secret   = "value"*/

#RESOURCE GROUP
location_rg = ["westeurope"]
az_tags = {
  "apm code"            = ""
  "digipi id"           = ""
  "cost center"         = ""
  "cost plan"           = ""
  "financial owner"     = "djburllaile@gmail.com"
  "billing contact"     = "djburllaile@gmail.com"
  "region"              = ""
  "department"          = "Notthingham"
  "functional owner"    = "djburllaile@gmail.com"
  "technical owner"     = "djburllaile@gmail.com"
  "market"              = "all"
  "network"             = "internal"
  "shared cost"         = "no"
  "solution type"       = "b2b"
  "data classification" = "general use"
  "environment"         = ""
}

policy_fw_config = {
  firewall_north_south = {
    rule_collection_group_names = ["North-South-Firewall-Rules-Collection"]
    policy_id                   = ""
    priority                    = 500
  },
  firewall_east_west = {
    rule_collection_group_names = ["East-West-Firewall-Rules-Collection"]
    policy_id                   = ""
    priority                    = 500
  },



  firewall_north_south_pr = {
    rule_collection_group_names = ["North-South-Firewall-Rules-Collection-Prod"]
    policy_id                   = ""
    priority = 100
  },
  firewall_east_west_pr = {
    rule_collection_group_names = ["East-West-Firewall-Rules-Collection-Prod"]
    policy_id                   = ""
    priority = 100
  }
}
