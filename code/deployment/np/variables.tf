##ENVIRONMENT

variable "policy_fw_config" {

  description = "Configuration for fw policy rules"
  type        = map(any)
  default     = {}

}

variable "ip_groups_config" {

  description = "Configuration for ip groups"
  type        = map(any)
  default     = {}

}

/*variable "app_rules" {
  description = "List of application rule collections."
  type = list(object({
    name     = string
    priority = number
    action   = string
    rules = list(object({
      name                = string
      source_addresses    = list(string)
      destination_fqdns   = list(string)
      protocols = list(object({
        type = string
        port = number
      }))
    }))
  }))
}



variable "network_rules" {
  description = "List of network rule collections."
  type = list(object({
    name     = string
    priority = number
    action   = string
    rules = list(object({
      name                  = string
      protocols             = list(string)
      source_addresses      = list(string)
      destination_addresses = list(string)
      destination_ports     = list(string)
    }))
  }))
}

variable "nat_rules" {
  description = "List of NAT rule collections."
  type = list(object({
    name     = string
    priority = number
    action   = string
    rules = list(object({
      name                = string
      protocols           = list(string)
      source_addresses    = list(string)
      destination_address = string
      destination_ports   = list(string)
      translated_address  = string
      translated_port     = string
    }))
  }))
}*/

variable "subscription_id" {
  description = "Define the environment: np or pr."
  type = string
}

variable "tenant_id" {
  description = "Define Tenant Id"
  type = string
}

variable "client_id" {
  description = "Define Client Id"
  type = string
}

variable "client_secret" {
  description = "Define client secret"
  type = string
}