import { streamText as _streamText, type CoreMessage } from 'ai';
import { getAPIKey } from '~/lib/.server/llm/api-key';
import { getAnthropicModel } from '~/lib/.server/llm/model';
import { MAX_TOKENS } from './constants';
import { getSystemPrompt } from './prompts';
import { getCognitiveIntegration } from './cognitive-integration';

export type Messages = CoreMessage[];

export type StreamingOptions = Omit<Parameters<typeof _streamText>[0], 'model'>;

/**
 * Enhanced streamText with cognitive pipeline integration
 */
export async function streamText(messages: Messages, env: Env, options?: StreamingOptions) {
  // Get cognitive integration instance
  const cognitiveIntegration = getCognitiveIntegration({
    enableCognitivePipeline: true,
    enableOrchestration: true,
    enableMemoryPersistence: false, // Enable when KV store is configured
  });
  
  // Preprocess messages through cognitive architecture
  const { enhancedMessages, shouldOrchestrate, cognitiveContext } = 
    await cognitiveIntegration.preprocessMessages(messages);
  
  // If orchestration is needed, handle it differently
  if (shouldOrchestrate) {
    console.log('🧠 Deep Tree Echo: Activating multi-agent orchestration');
    
    const userMessage = messages[messages.length - 1]?.content as string || '';
    const orchestrationResult = await cognitiveIntegration.executeOrchestration(
      userMessage,
      cognitiveContext
    );
    
    // For now, fall back to standard streaming with orchestration context
    // In future iterations, this would stream orchestration progress
    console.log('Orchestration result:', orchestrationResult);
  }
  
  // Log cognitive state for monitoring
  if (cognitiveContext) {
    console.log('🌊 Cognitive State:', {
      emotion: cognitiveContext.emotionalState?.dominantEmotion,
      confidence: cognitiveContext.metaCognition?.confidenceLevel,
      activatedMemories: cognitiveContext.activatedMemories?.length || 0,
    });
  }
  
  // Stream with enhanced system prompt
  return _streamText({
    model: getAnthropicModel(getAPIKey(env)),
    system: getSystemPrompt(),
    maxTokens: MAX_TOKENS,
    headers: {
      'anthropic-beta': 'max-tokens-3-5-sonnet-2024-07-15',
    },
    messages: enhancedMessages,
    ...options,
  });
}

/**
 * Original streamText for backward compatibility
 */
export function streamTextLegacy(messages: Messages, env: Env, options?: StreamingOptions) {
  return _streamText({
    model: getAnthropicModel(getAPIKey(env)),
    system: getSystemPrompt(),
    maxTokens: MAX_TOKENS,
    headers: {
      'anthropic-beta': 'max-tokens-3-5-sonnet-2024-07-15',
    },
    messages,
    ...options,
  });
}
