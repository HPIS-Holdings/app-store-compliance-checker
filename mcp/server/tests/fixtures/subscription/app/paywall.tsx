import Purchases from 'react-native-purchases';
export const buy = (p) => Purchases.purchasePackage(p);
