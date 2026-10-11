import { supabase } from './client';
export async function signUpUser(email, password) { return supabase.auth.signUp({ email, password }); }
async function invokeDeletion(body) {
  return supabase.functions.invoke('delete-account', { body });
}
export async function deleteMyAccountNow() {
  await invokeDeletion({ confirm: true });
}
