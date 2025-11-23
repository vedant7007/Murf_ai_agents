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
  companyName: "Prashant's Coffee Shop",
  pageTitle: "Prashant's Coffee Shop - AI Barista",
  pageDescription: 'Order coffee from your friendly AI barista Prashant',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#6F4E37',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#A67C52',
  startButtonText: 'Talk to Prashant',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: 'Prashant',
};
