import { z } from 'zod';

// Provider Schemas
export const ProviderInfoSchema = z.object({
  name: z.string(),
  display_name: z.string(),
  enabled: z.boolean(),
  avg_latency_ms: z.number(),
  win_rate: z.number(),
  total_competitions: z.number(),
});

export const ProviderStatsSchema = z.object({
  provider: z.string(),
  total_competitions: z.number(),
  wins: z.number(),
  win_rate: z.number(),
  avg_score: z.number(),
  avg_latency_ms: z.number(),
  total_cost_usd: z.number(),
});

// Competition Schemas
export const EntryScoreSchema = z.object({
  relevance: z.number().default(0),
  quality: z.number().default(0),
  completeness: z.number().default(0),
  efficiency: z.number().default(0),
  brand_alignment: z.number().default(0),
  total: z.number().default(0),
});

export const CompetitionEntrySchema = z.object({
  provider: z.string(),
  rank: z.number(),
  scores: EntryScoreSchema,
  latency_ms: z.number(),
  cost_usd: z.number(),
  response_preview: z.string().default(''),
});

export const CompetitionResponseSchema = z.object({
  id: z.string(),
  task_id: z.string(),
  prompt_preview: z.string(),
  status: z.string(),
  winner: CompetitionEntrySchema.nullable(),
  entries: z.array(CompetitionEntrySchema),
  ab_test_reasoning: z.string().nullable().optional(),
  ab_test_confidence: z.number().nullable().optional(),
  total_duration_ms: z.number(),
  total_cost_usd: z.number(),
  created_at: z.string(),
});

export const HistoryEntrySchema = z.object({
  id: z.string(),
  prompt_preview: z.string(),
  winner_provider: z.string(),
  winner_score: z.number(),
  total_cost_usd: z.number(),
  created_at: z.string(),
});

// Pipeline & 3D Schemas
export const PipelineStatusSchema = z.object({
  status: z.enum(['healthy', 'degraded', 'down']),
  active_jobs: z.number(),
  queued_jobs: z.number(),
  providers_online: z.number(),
  providers_total: z.number(),
});

export const Provider3DSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.enum(['commercial', 'huggingface', 'local']),
  capabilities: z.array(z.string()),
  avg_generation_time_s: z.number(),
  status: z.enum(['online', 'offline', 'busy']),
});

export const Job3DSchema = z.object({
  id: z.string(),
  status: z.enum(['queued', 'processing', 'completed', 'failed']),
  provider: z.string(),
  input_type: z.enum(['text', 'image']),
  input: z.string(),
  output_url: z.string().optional(),
  error: z.string().optional(),
  created_at: z.string(),
  completed_at: z.string().optional(),
});

// Health Schema
export const HealthResponseSchema = z.object({
  status: z.string(),
  version: z.string(),
  uptime: z.number(),
});

// Asset Schemas
export const AssetSchema = z.object({
  id: z.string(),
  name: z.string(),
  url: z.string(),
  collection: z.string(),
  sku: z.string().nullable().optional(),
  tags: z.array(z.string()),
  type: z.enum(['image', '3d_model', 'video', 'texture']),
  size: z.number().nullable().optional(),
  dimensions: z.record(z.string(), z.number()).nullable().optional(),
  uploaded_at: z.string(),
});

export const AssetListResponseSchema = z.object({
  assets: z.array(AssetSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
  has_more: z.boolean(),
});

// QA Review Schemas
export const QAReviewSchema = z.object({
  id: z.string(),
  asset_id: z.string(),
  job_id: z.string(),
  reference_image_url: z.string(),
  generated_model_url: z.string(),
  fidelity_score: z.number().min(0).max(100),
  fidelity_breakdown: z
    .object({
      geometry: z.number(),
      materials: z.number(),
      colors: z.number(),
      proportions: z.number(),
      branding: z.number(),
      texture_detail: z.number(),
    })
    .optional(),
  status: z.enum(['pending', 'approved', 'rejected', 'regenerating']),
  notes: z.string().optional(),
  reviewed_by: z.string().optional(),
  created_at: z.string(),
  reviewed_at: z.string().optional(),
});

export const QAReviewListResponseSchema = z.object({
  reviews: z.array(QAReviewSchema),
  total: z.number(),
  pending_count: z.number(),
  approved_count: z.number(),
  rejected_count: z.number(),
});

// Batch Job Schema
export const BatchJobSchema = z.object({
  id: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed', 'paused']),
  total_assets: z.number(),
  processed_assets: z.number(),
  failed_assets: z.number(),
  current_asset: z.string().optional(),
  progress_percentage: z.number(),
  started_at: z.string().optional(),
  completed_at: z.string().optional(),
  error_log: z.array(z.string()).optional(),
});

// Catalog Schemas
export const CatalogMatchResponseSchema = z.object({
  sku: z.string(),
  name: z.string(),
  collection: z.string(),
  score: z.number(),
  description: z.string().default(''),
  branding_spec: z.string().default(''),
});

export const CatalogSearchResponseSchema = z.object({
  query: z.string(),
  top_k: z.number(),
  collection: z.string().nullable(),
  matches: z.array(CatalogMatchResponseSchema),
  elapsed_ms: z.number(),
});

export const CatalogSimilarResponseSchema = z.object({
  sku: z.string(),
  top_k: z.number(),
  matches: z.array(CatalogMatchResponseSchema),
  elapsed_ms: z.number(),
});

// Settings Schema
export const SettingsSchema = z.object({
  wordpress: z.object({
    url: z.string(),
    consumerKey: z.string(),
    consumerSecret: z.string(),
    autoSync: z.boolean(),
  }),
  vercel: z.object({
    projectId: z.string(),
    apiToken: z.string(),
    orgId: z.string(),
  }),
  autonomous: z.object({
    enabled: z.boolean(),
    circuitBreakerThreshold: z.number(),
    retryAttempts: z.number(),
    retryDelay: z.number(),
  }),
  ui: z.object({
    theme: z.enum(['light', 'dark']),
    typography: z.enum(['playfair', 'inter', 'system']),
    accentColor: z.string(),
  }),
  system: z.object({
    apiTimeout: z.number(),
    maxConcurrentRequests: z.number(),
    logLevel: z.enum(['debug', 'info', 'warn', 'error']),
  }),
});

// Agent Schemas
export const AgentInfoSchema = z.object({
  name: z.string(),
  version: z.string(),
  category: z.string(),
  status: z.string(),
  capabilities: z.array(z.string()),
  endpoints: z.array(z.string()),
  last_execution: z.string().nullable().optional(),
});

export const AgentListResponseSchema = z.object({
  timestamp: z.string(),
  total_agents: z.number(),
  active_agents: z.number(),
  agents_by_category: z.record(z.string(), z.number()),
  agents: z.array(AgentInfoSchema),
});

// Task Schema
export const TaskMetricsSchema = z.object({
  startTime: z.string(),
  endTime: z.string().optional(),
  durationMs: z.number().optional(),
  tokensUsed: z.number().optional(),
  costUsd: z.number().optional(),
  provider: z.string().optional(),
  promptTechnique: z.string().optional(),
});

export const TaskSchema = z.object({
  taskId: z.string(),
  agentType: z.string(),
  prompt: z.string(),
  status: z.enum(['pending', 'running', 'completed', 'failed']),
  result: z.any().optional(),
  error: z.string().optional(),
  createdAt: z.string(),
  metrics: TaskMetricsSchema,
});

// Monitoring Schemas
export const ServiceHealthStatusSchema = z.object({
  name: z.string(),
  status: z.enum(['healthy', 'degraded', 'down']),
  uptime_pct: z.number(),
  response_ms: z.number().nullable().optional(),
  last_check: z.string(),
  circuit_breaker: z.enum(['closed', 'half-open', 'open']),
});

export const SystemStatsSchema = z.object({
  cpu_pct: z.number(),
  memory_pct: z.number(),
  disk_pct: z.number(),
  req_per_min: z.number(),
  success_rate: z.number(),
  avg_latency_ms: z.number(),
});

export const HealthEventSchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  type: z.enum(['success', 'warning', 'error']),
  service: z.string(),
  message: z.string(),
});

export const MonitoringHealthResponseSchema = z.object({
  timestamp: z.string(),
  services: z.array(ServiceHealthStatusSchema),
  system: SystemStatsSchema,
  events: z.array(HealthEventSchema),
});

export const MetricDataPointSchema = z.object({
  timestamp: z.string(),
  value: z.number(),
  labels: z.record(z.string(), z.string()).nullable().optional(),
});

export const MetricSeriesSchema = z.object({
  metric_name: z.string(),
  unit: z.string(),
  data_points: z.array(MetricDataPointSchema),
  aggregation: z.string().nullable().optional(),
});

export const MonitoringMetricsResponseSchema = z.object({
  timestamp: z.string(),
  time_range: z.string(),
  metrics: z.array(MetricSeriesSchema),
  summary: z.record(z.string(), z.unknown()),
});

// Context.dev structured web extraction
export const ContextDevExtractionResponseSchema = z.object({
  data: z.record(z.string(), z.unknown()),
});

// Autonomous Operation Schemas
export const AutonomousOperationSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  status: z.enum(['running', 'stopped', 'error']),
  critical: z.boolean(),
  last_event: z.string().nullable().optional(),
  last_event_at: z.string().nullable().optional(),
});

export const AutonomousHistoryEntrySchema = z.object({
  id: z.string(),
  operation_id: z.string(),
  operation_name: z.string(),
  action: z.enum(['start', 'stop', 'error']),
  timestamp: z.string(),
  message: z.string(),
});

export const AutonomousOperationsResponseSchema = z.object({
  operations: z.array(AutonomousOperationSchema),
  total: z.number(),
});

// Assets — extended schemas
export const SkuImageCountsSchema = z.object({
  counts: z.record(z.string(), z.number()),
  total: z.number(),
  scanned_at: z.string(),
});

export const HfDatasetInfoSchema = z.object({
  id: z.string(),
  private: z.boolean(),
  downloads: z.number(),
  likes: z.number(),
  last_modified: z.string().nullable(),
  created_at: z.string().nullable(),
  tags: z.array(z.string()),
});

export const HfDatasetsResponseSchema = z.object({
  datasets: z.array(HfDatasetInfoSchema),
  count: z.number(),
  author: z.string(),
});

// Training Schemas
export const TrainingProgressSchema = z.object({
  status: z.enum(['idle', 'preparing', 'training', 'completed', 'failed']),
  version: z.string(),
  current_epoch: z.number(),
  total_epochs: z.number(),
  current_step: z.number(),
  total_steps: z.number(),
  progress_percentage: z.number(),
  loss: z.number(),
  learning_rate: z.number(),
  avg_loss: z.number(),
  best_loss: z.number().nullable(),
  started_at: z.string().nullable(),
  updated_at: z.string().nullable(),
  estimated_completion: z.string().nullable(),
  elapsed_seconds: z.number(),
  remaining_seconds: z.number(),
  total_images: z.number(),
  total_products: z.number(),
  collections: z.record(z.string(), z.number()),
  latest_checkpoint: z.string(),
  checkpoint_step: z.number(),
  message: z.string(),
  error: z.string(),
});

export const TrainingJobInfoSchema = z.object({
  job_id: z.string(),
  version: z.string(),
  status: z.enum(['pending', 'running', 'completed', 'failed']),
  started_at: z.string().nullable(),
  completed_at: z.string().nullable(),
  total_epochs: z.number(),
  final_loss: z.number().nullable(),
  total_images: z.number(),
  total_products: z.number(),
  collections: z.record(z.string(), z.number()),
  model_path: z.string().nullable(),
  error: z.string().nullable(),
});

export const TrainingJobsListSchema = z.object({
  total_jobs: z.number(),
  running: z.number(),
  completed: z.number(),
  failed: z.number(),
  jobs: z.array(TrainingJobInfoSchema),
  retrieved_at: z.string(),
});

// Brand Assets Schemas (api/v1/brand_assets.py)
export const BrandAssetCategorySchema = z.enum([
  'product',
  'lifestyle',
  'campaign',
  'mood_board',
  'texture',
  'color_reference',
]);

export const AssetApprovalStatusSchema = z.enum(['pending', 'approved', 'rejected']);

export const IngestionJobStatusSchema = z.enum(['pending', 'processing', 'completed', 'failed', 'partial']);

export const TrainingReadinessStatusSchema = z.enum(['ready', 'not_ready', 'needs_review']);

export const BrandAssetMetadataSchema = z.object({
  campaign: z.string().nullable().optional(),
  season: z.string().nullable().optional(),
  photographer: z.string().nullable().optional(),
  location: z.string().nullable().optional(),
  shoot_date: z.string().nullable().optional(),
  tags: z.array(z.string()).default([]),
  notes: z.string().nullable().optional(),
});

export const ColorPaletteSchema = z.object({
  primary: z.string(),
  secondary: z.array(z.string()).default([]),
  accent: z.string().nullable().optional(),
});

export const CompositionAnalysisSchema = z.object({
  type: z.string(),
  focal_point: z.string().nullable().optional(),
  balance: z.string(),
});

export const LightingProfileSchema = z.object({
  type: z.string(),
  direction: z.string().nullable().optional(),
  mood: z.string().nullable().optional(),
});

export const VisualFeaturesSchema = z.object({
  color_palette: ColorPaletteSchema.nullable().optional(),
  composition: CompositionAnalysisSchema.nullable().optional(),
  lighting: LightingProfileSchema.nullable().optional(),
  style_tags: z.array(z.string()).default([]),
  quality_score: z.number(),
});

export const BrandAssetSchema = z.object({
  id: z.string(),
  url: z.string(),
  category: BrandAssetCategorySchema,
  approval_status: AssetApprovalStatusSchema,
  metadata: BrandAssetMetadataSchema,
  visual_features: VisualFeaturesSchema.nullable().optional(),
  file_size_bytes: z.number(),
  width: z.number().nullable().optional(),
  height: z.number().nullable().optional(),
  mime_type: z.string().nullable().optional(),
  r2_key: z.string().nullable().optional(),
  created_at: z.string(),
  created_by: z.string().nullable().optional(),
});

export const BrandAssetsListResponseSchema = z.object({
  assets: z.array(BrandAssetSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
  has_more: z.boolean(),
});

export const CategoryStatsSchema = z.object({
  category: BrandAssetCategorySchema,
  total: z.number(),
  approved: z.number(),
  pending: z.number(),
  rejected: z.number(),
});

export const TrainingReadinessResponseSchema = z.object({
  status: TrainingReadinessStatusSchema,
  total_assets: z.number(),
  approved_assets: z.number(),
  minimum_required: z.number(),
  categories: z.array(CategoryStatsSchema),
  recommendations: z.array(z.string()).default([]),
  estimated_training_time: z.string().nullable().optional(),
});

export const IngestionJobResultSchema = z.object({
  url: z.string(),
  success: z.boolean(),
  asset_id: z.string().nullable().optional(),
  error: z.string().nullable().optional(),
});

export const BulkIngestionJobSchema = z.object({
  id: z.string(),
  status: IngestionJobStatusSchema,
  total: z.number(),
  processed: z.number(),
  succeeded: z.number(),
  failed: z.number(),
  results: z.array(IngestionJobResultSchema).default([]),
  created_at: z.string(),
  completed_at: z.string().nullable().optional(),
  created_by: z.string().nullable().optional(),
});

// Asset Ingestion + Job Tracking Schemas (api/v1/assets.py — distinct from BatchJob/3D pipeline jobs)
export const AssetIngestResponseSchema = z.object({
  job_id: z.string(),
  status: z.string(),
  message: z.string(),
  original_url: z.string(),
  created_at: z.string(),
  correlation_id: z.string(),
});

export const AssetProcessingStageSchema = z.object({
  name: z.string(),
  status: z.string(),
  started_at: z.string().nullable().optional(),
  completed_at: z.string().nullable().optional(),
  duration_ms: z.number().nullable().optional(),
  output_url: z.string().nullable().optional(),
});

export const AssetJobResponseSchema = z.object({
  job_id: z.string(),
  status: z.string(),
  current_stage: z.string(),
  progress_percent: z.number(),
  stages: z.array(AssetProcessingStageSchema),
  input_url: z.string(),
  output_urls: z.record(z.string(), z.string()),
  product_id: z.string().nullable().optional(),
  source: z.string(),
  created_at: z.string(),
  started_at: z.string().nullable().optional(),
  completed_at: z.string().nullable().optional(),
  error_message: z.string().nullable().optional(),
  total_duration_ms: z.number(),
  correlation_id: z.string(),
});

// Competitor Analysis Schemas (api/v1/competitors.py + services/competitive/schemas.py)
export const CompetitorCategorySchema = z.enum(['direct', 'indirect', 'aspirational', 'emerging']);

export const PricePositioningSchema = z.enum(['budget', 'mid_range', 'premium', 'luxury', 'ultra_luxury']);

export const CompositionTypeSchema = z.enum([
  'flat_lay',
  'on_model',
  'ghost_mannequin',
  'still_life',
  'lifestyle',
  'detail_shot',
  'other',
]);

export const StyleCategorySchema = z.enum([
  'minimalist',
  'bold',
  'classic',
  'avant_garde',
  'streetwear',
  'bohemian',
  'romantic',
  'edgy',
  'sporty',
  'other',
]);

export const CompetitorSchema = z.object({
  id: z.string(),
  name: z.string(),
  category: CompetitorCategorySchema,
  price_positioning: PricePositioningSchema,
  website: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  created_at: z.string(),
  created_by: z.string().nullable().optional(),
});

export const CompetitorListResponseSchema = z.object({
  total: z.number().default(0),
  competitors: z.array(CompetitorSchema).default([]),
});

export const ExtractedAttributesSchema = z.object({
  composition_type: CompositionTypeSchema,
  style_category: StyleCategorySchema,
  primary_colors: z.array(z.string()).default([]),
  detected_materials: z.array(z.string()).default([]),
  mood_tags: z.array(z.string()).default([]),
  quality_assessment: z.string().nullable().optional(),
  confidence_score: z.number(),
});

export const CompetitorAssetSchema = z.object({
  id: z.string(),
  competitor_id: z.string(),
  url: z.string(),
  product_type: z.string().nullable().optional(),
  product_name: z.string().nullable().optional(),
  estimated_price: z.number().nullable().optional(),
  currency: z.string(),
  extracted_attributes: ExtractedAttributesSchema.nullable().optional(),
  manual_tags: z.array(z.string()).default([]),
  notes: z.string().nullable().optional(),
  created_at: z.string(),
  created_by: z.string().nullable().optional(),
  source_url: z.string().nullable().optional(),
});

export const CompetitorAssetListResponseSchema = z.object({
  total: z.number().default(0),
  page: z.number().default(1),
  page_size: z.number().default(20),
  assets: z.array(CompetitorAssetSchema).default([]),
});

export const StyleDistributionSchema = z.object({
  style: StyleCategorySchema,
  count: z.number(),
  percentage: z.number(),
});

export const CompositionDistributionSchema = z.object({
  composition: CompositionTypeSchema,
  count: z.number(),
  percentage: z.number(),
});

export const TopColorSchema = z.object({
  color: z.string(),
  count: z.number(),
});

export const TopMaterialSchema = z.object({
  material: z.string(),
  count: z.number(),
});

export const PriceAnalyticsSchema = z.object({
  competitor_id: z.string(),
  competitor_name: z.string(),
  average_price: z.number().nullable(),
  min_price: z.number().nullable(),
  max_price: z.number().nullable(),
  asset_count: z.number(),
});

export const StyleAnalyticsResponseSchema = z.object({
  total_assets: z.number().default(0),
  style_distribution: z.array(StyleDistributionSchema).default([]),
  composition_distribution: z.array(CompositionDistributionSchema).default([]),
  top_colors: z.array(TopColorSchema).default([]),
  top_materials: z.array(TopMaterialSchema).default([]),
  price_by_competitor: z.array(PriceAnalyticsSchema).default([]),
});

export const CompetitorAnalyticsSummarySchema = z.object({
  total_competitors: z.number(),
  total_assets: z.number(),
  competitors_by_category: z.record(z.string(), z.number()),
  competitors_by_price_positioning: z.record(z.string(), z.number()),
  assets_per_competitor: z.record(z.string(), z.number()),
});

// Dynamic Pricing Schemas (api/v1/commerce.py)
export const PriceOptimizationSchema = z.object({
  product_id: z.string(),
  current_price: z.number(),
  optimized_price: z.number(),
  price_change: z.number(),
  price_change_pct: z.number(),
  estimated_revenue_impact: z.number().nullable().optional(),
  confidence: z.number(),
});

export const DynamicPricingResponseSchema = z.object({
  optimization_id: z.string(),
  status: z.string(),
  timestamp: z.string(),
  strategy: z.string(),
  total_products: z.number(),
  optimizations: z.array(PriceOptimizationSchema),
  aggregate_metrics: z.record(z.string(), z.unknown()),
});
