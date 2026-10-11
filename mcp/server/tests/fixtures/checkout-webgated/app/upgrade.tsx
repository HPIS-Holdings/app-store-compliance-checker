import { Platform } from 'react-native';
import * as Linking from 'expo-linking';
import { requestPurchase } from 'react-native-iap';
export async function upgrade(checkoutUrl) {
  if (Platform.OS === 'web') {
    await Linking.openURL(checkoutUrl);
    return;
  }
  await requestPurchase({ sku: 'pro' });
}
