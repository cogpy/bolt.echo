/**
 * Cognitive Integration Module
 * 
 * Wires the cognitive pipeline into the runtime request flow,
 * enabling deep tree echo orchestration and neuro.md features.
 */

import { CognitivePipeline, type CognitiveContext } from './cognitive-pipeline';
import { OrchestrationEngine } from './orchestration-engine';
import type { CoreMessage } from 'ai';

export interface IntegrationConfig {
  enableCognitivePipeline: boolean;
  enableOrchestration: boolean;
  enableMemoryPersistence: boolean;
  orchestrationThreshold: number; // Complexity threshold for multi-agent orchestration
}

export class CognitiveIntegration {
  private pipeline: CognitivePipeline;
  private orchestrator: OrchestrationEngine;
  private config: IntegrationConfig;
  
  constructor(config?: Partial<IntegrationConfig>) {
    this.config = {
      enableCognitivePipeline: true,
      enableOrchestration: true,
      enableMemoryPersistence: false, // Disabled until KV store is configured
      orchestrationThreshold: 0.7,
      ...config,
    };
    
    this.pipeline = new CognitivePipeline();
    this.orchestrator = new OrchestrationEngine();
  }
  
  /**
   * Process messages through cognitive architecture before LLM invocation
   */
  async preprocessMessages(messages: CoreMessage[]): Promise<{
    enhancedMessages: CoreMessage[];
    shouldOrchestrate: boolean;
    cognitiveContext: any;
  }> {
    if (!this.config.enableCognitivePipeline) {
      return {
        enhancedMessages: messages,
        shouldOrchestrate: false,
        cognitiveContext: null,
      };
    }
    
    // Extract user message and conversation history
    const userMessage = messages[messages.length - 1]?.content as string || '';
    const conversationHistory = messages.map(m => ({
      role: m.role,
      content: typeof m.content === 'string' ? m.content : JSON.stringify(m.content),
    }));
    
    // Build cognitive context
    const context: CognitiveContext = {
      userMessage,
      conversationHistory,
      projectContext: this.extractProjectContext(messages),
    };
    
    // Run through cognitive pipeline
    const cognitiveResult = await this.pipeline.process(context);
    
    // Determine if orchestration is needed
    const shouldOrchestrate = this.shouldUseOrchestration(
      userMessage,
      cognitiveResult.metaCognition
    );
    
    // Enhance messages with cognitive insights (optional metadata)
    const enhancedMessages = [...messages];
    
    return {
      enhancedMessages,
      shouldOrchestrate,
      cognitiveContext: {
        emotionalState: cognitiveResult.emotionalState,
        metaCognition: cognitiveResult.metaCognition,
        activatedMemories: cognitiveResult.activatedMemories,
      },
    };
  }
  
  /**
   * Determine if request should use multi-agent orchestration
   */
  private shouldUseOrchestration(
    userMessage: string,
    metaCognition: any
  ): boolean {
    if (!this.config.enableOrchestration) {
      return false;
    }
    
    // Complexity indicators
    const complexityIndicators = [
      'build a complete',
      'full stack',
      'entire application',
      'multiple features',
      'complex system',
      'orchestrate',
      'coordinate',
      'analyze and implement',
      'design and build',
    ];
    
    const hasComplexityIndicator = complexityIndicators.some(indicator =>
      userMessage.toLowerCase().includes(indicator)
    );
    
    // Low confidence suggests need for multi-perspective reasoning
    const lowConfidence = metaCognition.confidenceLevel < this.config.orchestrationThreshold;
    
    // Multiple uncertainty areas suggest need for specialized agents
    const highUncertainty = metaCognition.uncertaintyAreas.length > 2;
    
    return hasComplexityIndicator || (lowConfidence && highUncertainty);
  }
  
  /**
   * Execute orchestrated workflow if needed
   */
  async executeOrchestration(userMessage: string, context: any): Promise<{
    orchestrationResult: any;
    synthesizedResponse: string;
  }> {
    // Decompose request into tasks
    const tasks = await this.orchestrator.decomposeRequest(userMessage, context);
    
    // Create workflow
    const workflow = this.orchestrator.createWorkflow(
      'user_request_workflow',
      `Orchestrated workflow for: ${userMessage}`,
      tasks,
      'hybrid' // Use hybrid mode for optimal parallelization
    );
    
    // Execute workflow
    const result = await this.orchestrator.executeWorkflow(workflow.id);
    
    // Synthesize results
    const synthesizedResponse = this.synthesizeOrchestrationResults(result);
    
    return {
      orchestrationResult: result,
      synthesizedResponse,
    };
  }
  
  /**
   * Extract project context from conversation
   */
  private extractProjectContext(messages: CoreMessage[]): any {
    // Analyze recent messages for project context
    const recentMessages = messages.slice(-5);
    
    const frameworks = ['react', 'vue', 'angular', 'svelte', 'next.js', 'astro', 'vite'];
    const detectedFramework = frameworks.find(fw =>
      recentMessages.some(m =>
        typeof m.content === 'string' && m.content.toLowerCase().includes(fw)
      )
    );
    
    return {
      type: 'web_development',
      framework: detectedFramework,
      currentFiles: [],
      recentErrors: [],
    };
  }
  
  /**
   * Synthesize orchestration results into coherent response
   */
  private synthesizeOrchestrationResults(orchestrationResult: any): string {
    // This would be enhanced with actual synthesis logic
    return `Orchestration completed with ${orchestrationResult.tasks?.length || 0} tasks.`;
  }
  
  /**
   * Add memory to persistent storage
   */
  async addMemory(memory: any): Promise<void> {
    if (!this.config.enableMemoryPersistence) {
      return;
    }
    
    // Would integrate with KV store or D1 database
    // For now, just add to in-memory pipeline
    this.pipeline.addMemory(memory);
  }
  
  /**
   * Get current cognitive state for debugging/monitoring
   */
  getCognitiveState(): any {
    return {
      pipelineActive: this.config.enableCognitivePipeline,
      orchestrationActive: this.config.enableOrchestration,
      memoryPersistence: this.config.enableMemoryPersistence,
    };
  }
}

/**
 * Singleton instance for runtime use
 */
let cognitiveIntegrationInstance: CognitiveIntegration | null = null;

export function getCognitiveIntegration(config?: Partial<IntegrationConfig>): CognitiveIntegration {
  if (!cognitiveIntegrationInstance) {
    cognitiveIntegrationInstance = new CognitiveIntegration(config);
  }
  return cognitiveIntegrationInstance;
}

/**
 * Reset singleton (useful for testing)
 */
export function resetCognitiveIntegration(): void {
  cognitiveIntegrationInstance = null;
}
