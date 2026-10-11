import Anthropic from '@anthropic-ai/sdk';
export const ask = async (q) => new Anthropic().messages.create({ model: 'x', max_tokens: 100, messages: [{ role: 'user', content: q }] });
