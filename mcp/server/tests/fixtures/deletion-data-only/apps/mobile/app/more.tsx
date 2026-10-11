import { useMutation } from 'convex/react';
import { makeFunctionReference } from 'convex/server';
const requestDeletionRef = makeFunctionReference<'mutation'>('workspaces:requestDeletion');
export function More() {
  const requestDeletion = useMutation(requestDeletionRef);
  function deleteRemoteWorkspace() {
    void requestDeletion({ workspaceId: 'w' });
  }
  return deleteRemoteWorkspace;
}
