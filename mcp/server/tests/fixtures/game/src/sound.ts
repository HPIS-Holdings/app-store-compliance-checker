import { Audio } from 'expo-av';
export async function boom() { const { sound } = await Audio.Sound.createAsync(require('./boom.mp3')); await sound.playAsync(); }
