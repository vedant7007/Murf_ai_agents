export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;
  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;
  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;
  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}
export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'WellBot Health',
  pageTitle: 'WellBot - Your AI Health Companion',
  pageDescription: 'Your personal voice assistant for fitness, nutrition, and wellness',
  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,
  logo: '/lk-logo.svg',
  accent: '#00D563',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#00FF7F',
  startButtonText: 'Start Wellness Session',
  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: 'WellBot',
};
