{{- define "cloud-storage.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "cloud-storage.labels" -}}
helm.sh/chart: {{ include "cloud-storage.name" . }}-{{ .Chart.Version | replace "+" "_" }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "cloud-storage.auth.fullname" -}}
{{- printf "%s-auth" .Release.Name }}
{{- end }}
