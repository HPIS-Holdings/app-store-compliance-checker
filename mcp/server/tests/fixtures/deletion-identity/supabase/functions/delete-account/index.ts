Deno.serve(async (req) => {
  const admin = createClient();
  const { data } = await admin.auth.getUser();
  await admin.auth.admin.deleteUser(data.user.id);
  return new Response('ok');
});
