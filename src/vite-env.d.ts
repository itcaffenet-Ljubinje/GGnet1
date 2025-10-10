/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_GGROCK_API_URL: string
  readonly VITE_GGROCK_WS_URL: string
  readonly VITE_GGROCK_VNC_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_ENABLE_VNC: string
  readonly VITE_ENABLE_GRAFANA: string
  readonly VITE_GRAFANA_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

