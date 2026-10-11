import { deleteMyAccountNow } from '../src/account';
export function Settings() {
  const onDelete = () => deleteMyAccountNow();
  return 'Delete account';
}
