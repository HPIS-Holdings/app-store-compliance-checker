import * as Linking from 'expo-linking';
export async function buy(createCheckout) {
  const result = await createCheckout({ productId: 'lifetime' });
  await Linking.openURL(result.url);
}
