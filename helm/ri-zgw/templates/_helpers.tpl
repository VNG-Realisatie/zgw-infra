{{/*
Common labels
*/}}
{{- define "ri.labels" -}}
helm.sh/chart: {{ .Chart.Name }}
{{- if .Values.global.config.environment }}
app.kubernetes.io/env: {{ .Values.global.config.environment }}
{{- end }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels for postgres
*/}}
{{- define "postgres.selectorLabels" -}}
app.kubernetes.io/name: {{ .Values.global.postgres.name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector selector labels for redis
*/}}
{{- define "redis.selectorLabels" -}}
app.kubernetes.io/name: {{ .Values.global.redis.name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

Selector labels
*/}}
{{- define "postgres.selector" -}}
app: postgis
{{- end }}


{{- define "postgres.storageClassName" -}}
  {{- $name := "test" }}
  {{- if eq .Values.global.config.environment "minikube" }}
    {{- $name = "standard" }}
  {{- else if eq .Values.global.config.environment "docker-desktop" -}}
    {{- $name = "hostpath" }}
  {{- else if eq .Values.global.config.environment "test" -}}
    {{- $name = "default" }}
  {{- else if eq .Values.global.config.environment "production" -}}
    {{- $name = "default" }}
  {{- end -}}
  {{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end -}}
