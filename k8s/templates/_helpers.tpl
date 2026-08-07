{{- define "cloud-storage.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "cloud-storage.auth.fullname" -}}
{{- printf "%s-auth" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.file.fullname" -}}
{{- printf "%s-file" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.gateway.fullname" -}}
{{- printf "%s-gateway" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.mail.fullname" -}}
{{- printf "%s-mail" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.kafka.fullname" -}}
{{- printf "%s-kafka" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.minio.fullname" -}}
{{- printf "%s-minio" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.prometheus.fullname" -}}
{{- printf "%s-prometheus" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.loki.fullname" -}}
{{- printf "%s-loki" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.promtail.fullname" -}}
{{- printf "%s-promtail" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.grafana.fullname" -}}
{{- printf "%s-grafana" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.ingress.scheme" -}}
{{- if .Values.ingress.tls.enabled }}https{{ else }}http{{ end }}
{{- end }}
