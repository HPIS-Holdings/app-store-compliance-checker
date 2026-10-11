import { action } from './_generated/server';
export const askCoach = action({ args: {}, handler: async (ctx, args) => {
  const body = { weight: args.weight, glucose: args.glucose };
  return fetch('https://api.openai.com/v1/responses', { method: 'POST', body: JSON.stringify(body) });
} });
