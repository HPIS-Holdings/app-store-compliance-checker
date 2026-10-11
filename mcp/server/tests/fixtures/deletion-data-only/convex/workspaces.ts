import { mutation } from './_generated/server';
export const requestDeletion = mutation({ args: {}, handler: async (ctx, args) => {
  const rows = await ctx.db.query('items').collect();
  for (const row of rows) await ctx.db.delete(row._id);
} });
