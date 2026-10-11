import { useAudioRecorder, RecordingPresets } from 'expo-audio';
export function useVoice() { return useAudioRecorder(RecordingPresets.HIGH_QUALITY); }
