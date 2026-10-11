import { useAction } from 'convex/react';
import { api } from '../../../convex/_generated/api';
export function Coach({ aiConsentGiven }) {
  const ask = useAction(api.coach.askCoach);
  return () => aiConsentGiven && ask({ q: 'hi' });
}
