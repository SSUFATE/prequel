export function isAuthError(err: unknown): boolean {
  if (
    typeof err === "object" &&
    err !== null &&
    "status" in err &&
    (err as { status?: number }).status === 401
  ) {
    return true;
  }
  return err instanceof Error && /not authenticated|unauthorized/i.test(err.message);
}