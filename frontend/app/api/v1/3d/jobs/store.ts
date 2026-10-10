// In-memory job store (replaced by database in production)
export const jobStore: Array<{
  id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  provider: string;
  input_type: 'text' | 'image';
  input: string;
  output_url?: string;
  error?: string;
  created_at: string;
  completed_at?: string;
}> = [];
