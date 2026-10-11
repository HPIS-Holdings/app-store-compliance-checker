import { useAudioRecorder, RecordingPresets } from 'expo-audio';
import { ExpoSpeechRecognitionModule } from 'expo-speech-recognition';
export function useVoice() { ExpoSpeechRecognitionModule.start({ lang: 'en-US' }); return useAudioRecorder(RecordingPresets.HIGH_QUALITY); }
