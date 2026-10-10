/** Public process liveness only. Dependency diagnostics remain authenticated. */
export function GET() {
  return Response.json(
    { status: 'ok' },
    {
      headers: { 'Cache-Control': 'no-store, max-age=0' },
    }
  );
}
