export interface ModelOption {
  label: string;
  value: string;
}

export interface ProviderConfig {
  models: ModelOption[];
  sizes: ModelOption[];
  qualities: ModelOption[];
  formats: ModelOption[];
  defaultModel: string;
  defaultSize: string;
  defaultQuality: string;
  defaultFormat: string;
}

export const PROVIDER_CONFIGS: Record<string, ProviderConfig> = {
  "gpt-image": {
    models: [
      { label: "GPT Image 2", value: "gpt-image-2" },
    ],
    sizes: [
      { label: "Square 1024×1024", value: "square" },
      { label: "Landscape 1792×1024", value: "landscape" },
      { label: "Portrait 1024×1792", value: "portrait" },
      { label: "Wide 2048×1024", value: "wide" },
      { label: "Tall 1024×2048", value: "tall" },
    ],
    qualities: [
      { label: "Auto", value: "auto" },
      { label: "Low", value: "low" },
      { label: "Medium", value: "medium" },
      { label: "High", value: "high" },
    ],
    formats: [
      { label: "PNG", value: "png" },
      { label: "JPEG", value: "jpeg" },
      { label: "WebP", value: "webp" },
    ],
    defaultModel: "gpt-image-2",
    defaultSize: "landscape",
    defaultQuality: "high",
    defaultFormat: "png",
  },
  openai: {
    models: [
      { label: "DALL-E 3", value: "dall-e-3" },
      { label: "DALL-E 2", value: "dall-e-2" },
    ],
    sizes: [
      { label: "1024×1024", value: "1024x1024" },
      { label: "1792×1024", value: "1792x1024" },
      { label: "1024×1792", value: "1024x1792" },
    ],
    qualities: [
      { label: "Standard", value: "standard" },
      { label: "HD", value: "hd" },
    ],
    formats: [
      { label: "PNG", value: "png" },
      { label: "JPEG", value: "jpeg" },
    ],
    defaultModel: "dall-e-3",
    defaultSize: "1792x1024",
    defaultQuality: "standard",
    defaultFormat: "jpeg",
  },
  stability: {
    models: [
      { label: "SD 3.5 Large", value: "stable-diffusion-3-5-large" },
      { label: "SD 3.5 Large Turbo", value: "stable-diffusion-3-5-large-turbo" },
      { label: "SD 3.5 Medium", value: "stable-diffusion-3-5-medium" },
    ],
    sizes: [
      { label: "1024×1024", value: "1024x1024" },
      { label: "2048×2048", value: "2048x2048" },
      { label: "2048×1024", value: "2048x1024" },
      { label: "1024×2048", value: "1024x2048" },
    ],
    qualities: [
      { label: "Standard", value: "standard" },
    ],
    formats: [
      { label: "PNG", value: "png" },
      { label: "JPEG", value: "jpeg" },
    ],
    defaultModel: "stable-diffusion-3-5-large",
    defaultSize: "1024x1024",
    defaultQuality: "standard",
    defaultFormat: "jpeg",
  },
  replicate: {
    models: [
      { label: "SD 3.5", value: "stability-ai/stable-diffusion-3.5" },
      { label: "SD 3", value: "stability-ai/stable-diffusion-3" },
    ],
    sizes: [
      { label: "1024×1024", value: "1024x1024" },
      { label: "2048×2048", value: "2048x2048" },
    ],
    qualities: [
      { label: "Standard", value: "standard" },
    ],
    formats: [
      { label: "PNG", value: "png" },
      { label: "JPEG", value: "jpeg" },
    ],
    defaultModel: "stability-ai/stable-diffusion-3.5",
    defaultSize: "1024x1024",
    defaultQuality: "standard",
    defaultFormat: "jpeg",
  },
  local: {
    models: [
      { label: "SD 3.5 Large Turbo", value: "stabilityai/stable-diffusion-3-5-large-turbo" },
      { label: "SD 3.5 Large", value: "stabilityai/stable-diffusion-3-5-large" },
    ],
    sizes: [
      { label: "1024×1024", value: "1024x1024" },
      { label: "768×768", value: "768x768" },
    ],
    qualities: [
      { label: "Standard", value: "standard" },
    ],
    formats: [
      { label: "PNG", value: "png" },
      { label: "JPEG", value: "jpeg" },
    ],
    defaultModel: "stabilityai/stable-diffusion-3-5-large-turbo",
    defaultSize: "1024x1024",
    defaultQuality: "standard",
    defaultFormat: "jpeg",
  },
  dummy: {
    models: [
      { label: "Dummy", value: "dummy" },
    ],
    sizes: [
      { label: "4MP (2400×1600)", value: "2400x1600" },
    ],
    qualities: [
      { label: "Standard", value: "standard" },
    ],
    formats: [
      { label: "JPEG", value: "jpeg" },
    ],
    defaultModel: "dummy",
    defaultSize: "2400x1600",
    defaultQuality: "standard",
    defaultFormat: "jpeg",
  },
  codex: {
    models: [
      { label: "GPT Image via Codex", value: "codex" },
    ],
    sizes: [
      { label: "Standard", value: "standard" },
    ],
    qualities: [
      { label: "Auto", value: "auto" },
    ],
    formats: [
      { label: "PNG", value: "png" },
    ],
    defaultModel: "codex",
    defaultSize: "standard",
    defaultQuality: "auto",
    defaultFormat: "png",
  },
};
