export default ({ config }) => ({
  ...config,
  ios: { infoPlist: {
    NSMicrophoneUsageDescription: 'Records voice notes you dictate.',
    NSCameraUsageDescription: process.env.CAMERA_TEXT,
  } },
});
