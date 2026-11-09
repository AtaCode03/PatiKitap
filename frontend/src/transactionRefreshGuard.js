export function isCurrentTransactionRefresh({
  requestGeneration,
  currentGeneration,
  requestId,
  currentRequestId,
  requestUserId,
  currentUserId
}) {
  return (
    requestGeneration === currentGeneration &&
    requestId === currentRequestId &&
    requestUserId === currentUserId
  );
}
