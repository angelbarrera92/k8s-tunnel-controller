{{/*
Expand the name of the chart.
*/}}
{{- define "k8s-tunnel-controller.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "k8s-tunnel-controller.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "k8s-tunnel-controller.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "k8s-tunnel-controller.labels" -}}
helm.sh/chart: {{ include "k8s-tunnel-controller.chart" . }}
{{ include "k8s-tunnel-controller.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "k8s-tunnel-controller.selectorLabels" -}}
app.kubernetes.io/name: {{ include "k8s-tunnel-controller.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "k8s-tunnel-controller.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "k8s-tunnel-controller.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Check .Values.token.existingSecret or .Values.token.tokenValue is set, but not both
TODO: This is not working as I expect
*/}}
{{- define "k8s-tunnel-controller.token" -}}
{{- if and .Values.token.existingSecret .Values.token.tokenValue }}
{{- fail "Values.token.existingSecret and Values.token.tokenValue are mutually exclusive" }}
{{- else if .Values.token.existingSecret }}
{{ printf "" }}
{{- else if .Values.token.tokenValue }}
{{- include "k8s-tunnel-controller.tokenValue" . }}
{{- else }}
{{- fail "Values.token.existingSecret or Values.token.tokenValue is required" }}
{{- end }}
{{- end }}

{{/*
Calculate secret name
*/}}
{{- define "k8s-tunnel-controller.secretName" -}}
{{- default (include "k8s-tunnel-controller.fullname" .) .Values.token.existingSecret }}
{{- end }}

{{/*
Validate Values.secret.tokenKey is not empty
*/}}
{{- define "k8s-tunnel-controller.tokenKey" -}}
{{- if .Values.token.tokenKey }}
{{- default "token" .Values.token.tokenKey }}
{{- else }}
{{- fail "Values.token.tokenKey is required" }}
{{- end }}
{{- end }}
