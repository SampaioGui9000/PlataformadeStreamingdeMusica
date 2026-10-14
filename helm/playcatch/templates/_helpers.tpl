{{- define "playcatch.name" -}}{{ .Release.Name }}{{- end -}}
{{- define "playcatch.labels" -}}
app: {{ include "playcatch.name" . }}
app.kubernetes.io/name: playcatch
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
