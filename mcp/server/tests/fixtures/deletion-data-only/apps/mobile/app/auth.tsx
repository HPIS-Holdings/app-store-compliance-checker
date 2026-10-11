import { useAuthActions } from '@convex-dev/auth/react';
export function useAuth() { const { signIn } = useAuthActions(); return () => signIn('password', { flow: 'signUp' }); }
