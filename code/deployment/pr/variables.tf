##ENVIRONMENT

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

##NAMING CONVENTIONS

variable "scope" {
  description = "The scope for the deployment"
  type        = string
}

variable "env" {
  description = "The environment (e.g. prod, nonprod, test)"
  type        = string
}

variable "region" {
  description = "The region for deployment"
  type        = string
}

variable "solution_name" {
  description = "A description for the deployment"
  type        = string
}

#RESOURCE GROUP

variable "az_tags" {
  description = "A mapping of tags which should be assigned to all resources"
  type        = map(any)
  default     = {}
}

variable "location_rg" {
  description = "Available region"
  type        = list(string)
}


variable "policy_fw_config" {
  description = "Configuration for fw policy rules"
  type        = map(any)
  default     = {}
}
