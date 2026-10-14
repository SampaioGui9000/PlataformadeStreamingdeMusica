variable "kubeconfig_path" {
  type    = string
  default = "~/.kube/config"
}
variable "kube_context" {
  type    = string
  default = "minikube"
}
variable "namespace" {
  type    = string
  default = "playcatch"
}
variable "image_repository" {
  type    = string
  default = "playcatch-api"
}
variable "image_tag" {
  type    = string
  default = "latest"
}
variable "replicas" {
  type    = number
  default = 2
}
variable "db_password" {
  type      = string
  sensitive = true
}
