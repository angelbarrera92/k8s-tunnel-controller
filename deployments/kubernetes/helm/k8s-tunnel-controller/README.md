
K8s-tunnel-controller
===========

A Helm chart for Kubernetes


## Configuration

The following table lists the configurable parameters of the K8s-tunnel-controller chart and their default values.

| Parameter                | Description             | Default        |
| ------------------------ | ----------------------- | -------------- |
| `token.tokenKey` |  | `"token"` |
| `replicaCount` |  | `1` |
| `image.repository` |  | `"ghcr.io/angelbarrera92/k8s-tunnel-controller"` |
| `image.pullPolicy` |  | `"Always"` |
| `image.tag` |  | `"main"` |
| `imagePullSecrets` |  | `[]` |
| `nameOverride` |  | `""` |
| `fullnameOverride` |  | `""` |
| `serviceAccount.create` |  | `true` |
| `serviceAccount.annotations` |  | `{}` |
| `serviceAccount.name` |  | `""` |
| `podAnnotations` |  | `{}` |
| `podSecurityContext` |  | `{}` |
| `securityContext.capabilities.drop` |  | `["ALL"]` |
| `securityContext.readOnlyRootFilesystem` |  | `true` |
| `service.type` |  | `"ClusterIP"` |
| `service.port` |  | `8080` |
| `ingress.enabled` |  | `false` |
| `ingress.className` |  | `""` |
| `ingress.annotations` |  | `{}` |
| `ingress.hosts` |  | `[{"host": "chart-example.local", "paths": [{"path": "/", "pathType": "ImplementationSpecific"}]}]` |
| `ingress.tls` |  | `[]` |
| `resources.limits.cpu` |  | `"100m"` |
| `resources.limits.memory` |  | `"128Mi"` |
| `resources.requests.cpu` |  | `"100m"` |
| `resources.requests.memory` |  | `"128Mi"` |
| `autoscaling.enabled` |  | `false` |
| `autoscaling.minReplicas` |  | `1` |
| `autoscaling.maxReplicas` |  | `100` |
| `autoscaling.targetCPUUtilizationPercentage` |  | `80` |
| `nodeSelector` |  | `{}` |
| `tolerations` |  | `[]` |
| `affinity` |  | `{}` |





