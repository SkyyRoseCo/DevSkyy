/**
 * DevSkyy OpenAI Service
 * Integration with OpenAI API for AI capabilities
 */

import { openaiConfig } from '../config/index';
import { Logger } from '../utils/Logger';
import type { ApiResponse } from '../types/index';

export interface OpenAICompletionRequest {
  prompt: string;
  model?: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  stop?: string[];
}

export interface OpenAICompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    text: string;
    index: number;
    logprobs: null | Record<string, unknown>;
    finishReason: string;
  }>;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

export type OpenAIContentPart =
  { type: 'text'; text: string } | { type: 'image_url'; image_url: { url: string; detail?: 'auto' | 'low' | 'high' } };

export interface OpenAIChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string | OpenAIContentPart[];
}

export interface OpenAIChatRequest {
  messages: OpenAIChatMessage[];
  model?: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  stop?: string[];
  functions?: Array<{
    name: string;
    description: string;
    parameters: Record<string, unknown>;
  }>;
  functionCall?: 'auto' | 'none' | { name: string };
}

export interface OpenAIImageRequest {
  prompt: string;
  n?: number;
  size?: '256x256' | '512x512' | '1024x1024' | '1792x1024' | '1024x1792';
  quality?: 'standard' | 'hd';
  style?: 'vivid' | 'natural';
}

export class OpenAIService {
  private logger: Logger;
  private baseURL: string;
  private apiKey: string;

  constructor() {
    this.logger = new Logger('OpenAIService');
    this.baseURL = openaiConfig.baseURL;
    this.apiKey = openaiConfig.apiKey;

    if (!this.apiKey) {
      throw new Error('OpenAI API key is required');
    }
  }

  /**
   * Make HTTP request to OpenAI API
   */
  private async makeRequest<T>(
    endpoint: string,
    method: 'GET' | 'POST' = 'POST',
    body?: Record<string, unknown>
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const startTime = Date.now();

    try {
      const fetchOptions: RequestInit = {
        method,
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
          'User-Agent': 'DevSkyy-SDK/1.0.0',
        },
        signal: AbortSignal.timeout(openaiConfig.timeout),
      };

      if (body) {
        fetchOptions.body = JSON.stringify(body);
      }

      const response = await fetch(url, fetchOptions);

      const executionTime = Date.now() - startTime;
      const data = (await response.json()) as T;

      if (!response.ok) {
        const error = data as { error?: { message: string; code: string } };
        throw new Error(error.error?.message || `HTTP ${response.status}`);
      }

      this.logger.debug(`OpenAI API request completed`, {
        endpoint,
        status: response.status,
        executionTime,
      });

      return {
        success: true,
        data,
        metadata: {
          requestId: response.headers.get('x-request-id') || 'unknown',
          timestamp: new Date().toISOString(),
          version: 'v1',
          executionTime,
        },
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;
      this.logger.error(`OpenAI API request failed`, error, {
        endpoint,
        executionTime,
      });

      throw error;
    }
  }

  /**
   * Create text completion
   */
  public async createCompletion(request: OpenAICompletionRequest): Promise<ApiResponse<OpenAICompletionResponse>> {
    const body = {
      model: request.model || openaiConfig.defaultModel,
      prompt: request.prompt,
      max_tokens: request.maxTokens || openaiConfig.maxTokens,
      temperature: request.temperature ?? openaiConfig.temperature,
      top_p: request.topP,
      frequency_penalty: request.frequencyPenalty,
      presence_penalty: request.presencePenalty,
      stop: request.stop,
    };

    return this.makeRequest<OpenAICompletionResponse>('/completions', 'POST', body);
  }

  /**
   * Create chat completion
   */
  public async createChatCompletion(request: OpenAIChatRequest): Promise<ApiResponse<OpenAICompletionResponse>> {
    const body = {
      model: request.model || openaiConfig.defaultModel,
      messages: request.messages,
      max_tokens: request.maxTokens || openaiConfig.maxTokens,
      temperature: request.temperature ?? openaiConfig.temperature,
      top_p: request.topP,
      frequency_penalty: request.frequencyPenalty,
      presence_penalty: request.presencePenalty,
      stop: request.stop,
      functions: request.functions,
      function_call: request.functionCall,
    };

    return this.makeRequest<OpenAICompletionResponse>('/chat/completions', 'POST', body);
  }

  /**
   * Generate images
   */
  public async createImage(request: OpenAIImageRequest): Promise<ApiResponse<{ data: Array<{ url: string }> }>> {
    const body = {
      prompt: request.prompt,
      n: request.n || 1,
      size: request.size || '1024x1024',
      quality: request.quality || 'standard',
      style: request.style || 'vivid',
    };

    return this.makeRequest<{ data: Array<{ url: string }> }>('/images/generations', 'POST', body);
  }

  /**
   * Analyze image with vision model
   */
  public async analyzeImage(
    imageUrl: string,
    prompt: string = 'Describe this image'
  ): Promise<ApiResponse<OpenAICompletionResponse>> {
    const messages: OpenAIChatMessage[] = [
      {
        role: 'user',
        content: [
          { type: 'text', text: prompt },
          { type: 'image_url', image_url: { url: imageUrl } },
        ],
      },
    ];

    return this.createChatCompletion({
      messages,
      model: 'gpt-4o', // Vision-capable model
      maxTokens: 1000,
    });
  }

  /**
   * Get available models
   */
  public async getModels(): Promise<ApiResponse<{ data: Array<{ id: string; object: string; created: number }> }>> {
    return this.makeRequest<{ data: Array<{ id: string; object: string; created: number }> }>('/models', 'GET');
  }

  /**
   * Create embeddings
   */
  public async createEmbeddings(
    input: string | string[],
    model: string = 'text-embedding-ada-002'
  ): Promise<ApiResponse<{ data: Array<{ embedding: number[]; index: number }> }>> {
    const body = {
      model,
      input,
    };

    return this.makeRequest<{ data: Array<{ embedding: number[]; index: number }> }>('/embeddings', 'POST', body);
  }

  /**
   * Moderate content
   */
  public async moderateContent(input: string): Promise<
    ApiResponse<{
      results: Array<{
        flagged: boolean;
        categories: Record<string, boolean>;
        categoryScores: Record<string, number>;
      }>;
    }>
  > {
    const body = { input };
    return this.makeRequest<{
      results: Array<{
        flagged: boolean;
        categories: Record<string, boolean>;
        categoryScores: Record<string, number>;
      }>;
    }>('/moderations', 'POST', body);
  }
}

// Export singleton instance
export const openaiService = new OpenAIService();
