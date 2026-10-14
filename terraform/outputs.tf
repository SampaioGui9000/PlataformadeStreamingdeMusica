output "namespace" {
  value = kubernetes_namespace.playcatch.metadata[0].name
}
output "release_status" {
  value = helm_release.playcatch.status
}
