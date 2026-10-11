export default ({ config }) => ({ ...config, name: process.env.APP_NAME, ios: { infoPlist: { NSMicrophoneUsageDescription: process.env.MIC_TEXT } } });
