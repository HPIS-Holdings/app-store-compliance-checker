import * as MediaLibrary from 'expo-media-library';
export const save = (uri) => MediaLibrary.saveToLibraryAsync(uri);
