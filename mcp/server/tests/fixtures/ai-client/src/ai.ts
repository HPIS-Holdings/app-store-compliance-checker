import OpenAI from 'openai';
const OPENAI_API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz0123456789";
const client = new OpenAI({ apiKey: OPENAI_API_KEY });
export const ask = (q) => client.responses.create({ model: 'x', input: q });
