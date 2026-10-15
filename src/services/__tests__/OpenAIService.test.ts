/**
 * Unit Tests for OpenAIService
 * @vitest-environment node
 */

import { OpenAIService } from '../OpenAIService';

// Mock Logger
vi.mock('../../utils/Logger', () => ({
  Logger: vi.fn(function Logger() {
    return {
      info: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
      debug: vi.fn(),
    };
  }),
}));

// Mock config
vi.mock('../../config/index', () => ({
  openaiConfig: {
    apiKey: 'test-api-key',
    baseURL: 'https://api.openai.com/v1',
    defaultModel: 'gpt-4o',
    maxTokens: 4000,
    temperature: 0.7,
    timeout: 60000,
  },
}));

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('OpenAIService', () => {
  let service: OpenAIService;

  beforeEach(() => {
    vi.clearAllMocks();
    service = new OpenAIService();
  });

  describe('constructor', () => {
    it('should initialize with API key from config', () => {
      expect(service).toBeDefined();
    });

    it('should use API key from config', () => {
      // The service is already initialized with the mocked config
      // This test verifies the service was created successfully with the API key
      expect(service).toBeDefined();
      // The constructor would have thrown if API key was missing
    });

    it('should throw error when API key is missing', async () => {
      // Reset modules to allow re-mocking
      vi.resetModules();

      // Mock config with empty API key
      vi.doMock('../../config/index', () => ({
        openaiConfig: {
          apiKey: '', // Empty API key
          baseURL: 'https://api.openai.com/v1',
          defaultModel: 'gpt-4o',
          maxTokens: 4000,
          temperature: 0.7,
          timeout: 60000,
        },
      }));

      // Mock Logger again since modules were reset
      vi.doMock('../../utils/Logger', () => ({
        Logger: vi.fn(function Logger() {
          return {
            info: vi.fn(),
            warn: vi.fn(),
            error: vi.fn(),
            debug: vi.fn(),
          };
        }),
      }));

      // The module exports a singleton, so importing will throw.
      await expect(import('../OpenAIService')).rejects.toThrow('OpenAI API key is required');
    });
  });

  describe('createCompletion', () => {
    it('should make POST request to /completions endpoint', async () => {
      const mockResponse = {
        id: 'cmpl-123',
        object: 'text_completion',
        created: Date.now(),
        model: 'gpt-4o',
        choices: [{ text: 'Hello!', index: 0, logprobs: null, finishReason: 'stop' }],
        usage: { promptTokens: 5, completionTokens: 10, totalTokens: 15 },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
        headers: new Map([['x-request-id', 'req-123']]),
      });

      const result = await service.createCompletion({ prompt: 'Hello' });

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.openai.com/v1/completions',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer test-api-key',
            'Content-Type': 'application/json',
          }),
        })
      );
      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockResponse);
    });

    it('should use custom model when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Map(),
      });

      await service.createCompletion({ prompt: 'Test', model: 'gpt-3.5-turbo' });

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(callBody.model).toBe('gpt-3.5-turbo');
    });

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ error: { message: 'Invalid API key', code: 'invalid_api_key' } }),
        headers: new Map(),
      });

      await expect(service.createCompletion({ prompt: 'Test' })).rejects.toThrow('Invalid API key');
    });

    it('should handle API errors without error message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({}),
        headers: new Map(),
      });

      await expect(service.createCompletion({ prompt: 'Test' })).rejects.toThrow('HTTP 500');
    });
  });

  describe('createChatCompletion', () => {
    it('should make POST request to /chat/completions endpoint', async () => {
      const mockResponse = {
        id: 'chatcmpl-123',
        object: 'chat.completion',
        created: Date.now(),
        model: 'gpt-4o',
        choices: [{ text: 'Hi there!', index: 0, logprobs: null, finishReason: 'stop' }],
        usage: { promptTokens: 10, completionTokens: 5, totalTokens: 15 },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
        headers: new Map([['x-request-id', 'req-456']]),
      });

      const result = await service.createChatCompletion({
        messages: [{ role: 'user', content: 'Hello' }],
      });

      expect(mockFetch).toHaveBeenCalledWith('https://api.openai.com/v1/chat/completions', expect.any(Object));
      expect(result.success).toBe(true);
    });

    it('should include functions when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Map(),
      });

      await service.createChatCompletion({
        messages: [{ role: 'user', content: 'Test' }],
        functions: [{ name: 'test_fn', description: 'Test function', parameters: {} }],
        functionCall: 'auto',
      });

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(callBody.functions).toBeDefined();
      expect(callBody.function_call).toBe('auto');
    });
  });

  describe('createImage', () => {
    it('should make POST request to /images/generations endpoint', async () => {
      const mockResponse = {
        data: [{ url: 'https://example.com/image.png' }],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
        headers: new Map(),
      });

      const result = await service.createImage({ prompt: 'A beautiful sunset' });

      expect(mockFetch).toHaveBeenCalledWith('https://api.openai.com/v1/images/generations', expect.any(Object));
      expect(result.success).toBe(true);
      expect(result.data.data[0]?.url).toBe('https://example.com/image.png');
    });

    it('should use custom size and quality', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: [] }),
        headers: new Map(),
      });

      await service.createImage({
        prompt: 'Test',
        size: '1792x1024',
        quality: 'hd',
        style: 'natural',
      });

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(callBody.size).toBe('1792x1024');
      expect(callBody.quality).toBe('hd');
      expect(callBody.style).toBe('natural');
    });
  });

  describe('analyzeImage', () => {
    it('should call createChatCompletion with vision model', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            choices: [{ text: 'This is an image of a cat' }],
          }),
        headers: new Map(),
      });

      const result = await service.analyzeImage('https://example.com/cat.jpg', 'What is in this image?');

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(callBody.model).toBe('gpt-4o');
      expect(callBody.messages[0].content).toEqual([
        { type: 'text', text: 'What is in this image?' },
        { type: 'image_url', image_url: { url: 'https://example.com/cat.jpg' } },
      ]);
      expect(callBody.max_tokens).toBe(1000);
      expect(result.success).toBe(true);
    });

    it('should use default prompt when not provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Map(),
      });

      await service.analyzeImage('https://example.com/image.jpg');

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(callBody.messages[0].content[0]).toEqual({ type: 'text', text: 'Describe this image' });
    });
  });

  describe('getModels', () => {
    it('should make GET request to /models endpoint', async () => {
      const mockResponse = {
        data: [
          { id: 'gpt-4o', object: 'model', created: 1234567890 },
          { id: 'gpt-3.5-turbo', object: 'model', created: 1234567890 },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
        headers: new Map(),
      });

      const result = await service.getModels();

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.openai.com/v1/models',
        expect.objectContaining({ method: 'GET' })
      );
      expect(result.success).toBe(true);
      expect(result.data.data).toHaveLength(2);
    });
  });

  describe('createEmbeddings', () => {
    it('should make POST request to /embeddings endpoint', async () => {
      const mockResponse = {
        data: [{ embedding: [0.1, 0.2, 0.3], index: 0 }],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
        headers: new Map(),
      });

      const result = await service.createEmbeddings('Hello world');

      expect(mockFetch).toHaveBeenCalledWith('https://api.openai.com/v1/embeddings', expect.any(Object));
      expect(result.success).toBe(true);
    });

    it('should accept array of strings', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: [] }),
        headers: new Map(),
      });

      await service.createEmbeddings(['Hello', 'World']);

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(callBody.input).toEqual(['Hello', 'World']);
    });

    it('should use custom model', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: [] }),
        headers: new Map(),
      });

      await service.createEmbeddings('Test', 'text-embedding-3-large');

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(callBody.model).toBe('text-embedding-3-large');
    });
  });

  describe('moderateContent', () => {
    it('should make POST request to /moderations endpoint', async () => {
      const mockResponse = {
        results: [
          {
            flagged: false,
            categories: { hate: false, violence: false },
            categoryScores: { hate: 0.001, violence: 0.002 },
          },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
        headers: new Map(),
      });

      const result = await service.moderateContent('Hello, how are you?');

      expect(mockFetch).toHaveBeenCalledWith('https://api.openai.com/v1/moderations', expect.any(Object));
      expect(result.success).toBe(true);
      expect(result.data.results[0]?.flagged).toBe(false);
    });

    it('should detect flagged content', async () => {
      const mockResponse = {
        results: [
          {
            flagged: true,
            categories: { hate: true, violence: false },
            categoryScores: { hate: 0.95, violence: 0.01 },
          },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
        headers: new Map(),
      });

      const result = await service.moderateContent('Some hateful content');

      expect(result.data.results[0]?.flagged).toBe(true);
      expect(result.data.results[0]?.categories['hate']).toBe(true);
    });
  });

  describe('error handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(service.createCompletion({ prompt: 'Test' })).rejects.toThrow('Network error');
    });

    it('should handle timeout errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('The operation was aborted'));

      await expect(service.createCompletion({ prompt: 'Test' })).rejects.toThrow('The operation was aborted');
    });

    it('should handle rate limit errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: () => Promise.resolve({ error: { message: 'Rate limit exceeded', code: 'rate_limit_exceeded' } }),
        headers: new Map(),
      });

      await expect(service.createCompletion({ prompt: 'Test' })).rejects.toThrow('Rate limit exceeded');
    });
  });

  describe('response metadata', () => {
    it('should include execution time in response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        headers: new Map([['x-request-id', 'req-789']]),
      });

      const result = await service.createCompletion({ prompt: 'Test' });

      expect(result.metadata).toBeDefined();
      expect(result.metadata.executionTime).toBeGreaterThanOrEqual(0);
      expect(result.metadata.timestamp).toBeDefined();
    });
  });
});
