import { useAudioRecorder, RecordingPresets } from 'expo-audio';
export const useVoice = () => useAudioRecorder(RecordingPresets.HIGH_QUALITY);
