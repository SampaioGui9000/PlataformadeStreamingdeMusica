terraform {
  required_version = ">= 1.6"
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.33" }
    helm       = { source = "hashicorp/helm", version = "~> 2.15" }
  }
}

provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.kube_context
}

provider "helm" {
  kubernetes {
    config_path    = var.kubeconfig_path
    config_context = var.kube_context
  }
}

resource "kubernetes_namespace" "playcatch" {
  metadata {
    name   = var.namespace
    labels = { "istio-injection" = "enabled" }
  }
}

resource "helm_release" "playcatch" {
  name       = "playcatch"
  chart      = "${path.module}/../helm/playcatch"
  namespace  = kubernetes_namespace.playcatch.metadata[0].name
  wait       = true
  timeout    = 300

  set {
    name  = "image.repository"
    value = var.image_repository
  }
  set {
    name  = "image.tag"
    value = var.image_tag
  }
  set {
    name  = "replicaCount"
    value = var.replicas
  }
  set_sensitive {
    name  = "postgres.password"
    value = var.db_password
  }
}
