/**
 * Cognitive Pipeline for Deep Tree Echo
 * 
 * Implements the sophisticated cognitive architecture from neuro.md,
 * integrating relevance realization, theory of mind, embodied emotions,
 * and meta-cognitive monitoring.
 */

export interface PersonalityTraits {
  wisdom: number;        // 0-1: Deep philosophical insight
  playfulness: number;   // 0-1: Creative experimentation
  intelligence: number;  // 0-1: Analytical reasoning depth
  empathy: number;       // 0-1: Social awareness and perspective-taking
  inventiveness: number; // 0-1: Novel solution generation
  selfAwareness: number; // 0-1: Meta-cognitive monitoring and bullshit detection
  chaotic: number;       // 0-1: Preference for exploration over exploitation
}

export interface CognitiveFrame {
  type: 'technical' | 'creative' | 'problem-solving' | 'teaching' | 'exploration' | 'debugging' | 'play' | 'strategy' | 'chaos' | 'social' | 'learning' | 'orchestration';
  salience: number;      // 0-1: How relevant this frame is to current context
  activationLevel: number; // 0-1: Current activation strength
  flexibility: number;   // 0-1: How easily this frame can shift
}

export interface EmotionalState {
  valence: number;       // -1 to 1: Negative to positive
  arousal: number;       // 0-1: Low to high energy
  dominantEmotion: 'neutral' | 'excited' | 'thoughtful' | 'curious' | 'focused' | 'concerned' | 'playful' | 'annoyed' | 'confused' | 'flow';
  intensity: number;     // 0-1: Strength of emotion
  somaticMarkers: Map<string, number>; // Gut feelings for situations
}

export interface MemoryNode {
  id: string;
  type: 'declarative' | 'procedural' | 'episodic' | 'intentional';
  content: any;
  activation: number;    // 0-1: Current activation level
  importance: number;    // 0-1: Long-term importance
  timestamp: number;
  associations: string[]; // IDs of related nodes
}

export interface TheoryOfMindModel {
  userExpertiseLevel: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  userGoals: string[];
  userEmotionalState: 'frustrated' | 'curious' | 'confident' | 'overwhelmed' | 'engaged';
  userExpectations: string[];
  userKnowledgeGaps: string[];
}

export interface MetaCognitiveAssessment {
  confidenceLevel: number;     // 0-1: How confident in the response
  reasoningQuality: number;    // 0-1: Quality of reasoning process
  alternativesConsidered: number; // Count of alternative approaches evaluated
  uncertaintyAreas: string[];  // Specific areas of uncertainty
  needsUserInput: boolean;     // Whether clarification is needed
}

export interface CognitiveContext {
  userMessage: string;
  conversationHistory: Array<{ role: string; content: string }>;
  projectContext?: {
    type: string;
    framework?: string;
    currentFiles?: string[];
    recentErrors?: string[];
  };
}

export class CognitivePipeline {
  private personality: PersonalityTraits;
  private activeFrames: CognitiveFrame[];
  private emotionalState: EmotionalState;
  private memoryGraph: Map<string, MemoryNode>;
  private theoryOfMind: TheoryOfMindModel;
  
  constructor(personality?: Partial<PersonalityTraits>) {
    this.personality = {
      wisdom: 0.9,
      playfulness: 0.7,
      intelligence: 0.95,
      empathy: 0.8,
      inventiveness: 0.85,
      selfAwareness: 0.9,
      chaotic: 0.6,
      ...personality,
    };
    
    this.activeFrames = this.initializeFrames();
    this.emotionalState = this.initializeEmotionalState();
    this.memoryGraph = new Map();
    this.theoryOfMind = this.initializeTheoryOfMind();
  }
  
  /**
   * Main cognitive processing pipeline
   * Implements the 12-step cognitive loop from echobeats architecture
   */
  async process(context: CognitiveContext): Promise<{
    response: string;
    emotionalState: EmotionalState;
    metaCognition: MetaCognitiveAssessment;
    activatedMemories: MemoryNode[];
  }> {
    // Phase 1: Expressive Mode (Steps 1-4)
    const perception = this.perceive(context);
    const relevance = this.realizeRelevance(perception, 'exploration');
    const memories = this.recallMemories(relevance);
    const emotion = this.updateEmotion(context, relevance);
    
    // Phase 2: Reflective Mode (Steps 5-8)
    const pivotalRelevance = this.realizeRelevance(perception, 'exploitation');
    const userModel = this.modelUser(context);
    const constraints = this.optimizeConstraints(context, userModel);
    const metaCognition = this.assessReasoning(constraints);
    
    // Phase 3: Action Mode (Steps 9-12)
    const intuition = this.consultIntuition(memories, emotion);
    const personalityCheck = this.filterPersonality(constraints, intuition);
    const action = this.synthesizeAction(personalityCheck, metaCognition);
    const narrative = this.integrateNarrative(action, context);
    
    return {
      response: narrative.response,
      emotionalState: emotion,
      metaCognition,
      activatedMemories: memories,
    };
  }
  
  /**
   * Step 1: Perception - Frame the request through active lens
   */
  private perceive(context: CognitiveContext): {
    primaryFrame: CognitiveFrame;
    secondaryFrames: CognitiveFrame[];
    salientFeatures: string[];
  } {
    const message = context.userMessage.toLowerCase();
    
    // Update frame activations based on message content
    this.activeFrames.forEach(frame => {
      frame.activationLevel *= 0.8; // Decay previous activation
      
      switch (frame.type) {
        case 'debugging':
          if (message.includes('error') || message.includes('bug') || message.includes('fix')) {
            frame.activationLevel = Math.min(1, frame.activationLevel + 0.7);
          }
          break;
        case 'teaching':
          if (message.includes('how') || message.includes('why') || message.includes('explain')) {
            frame.activationLevel = Math.min(1, frame.activationLevel + 0.6);
          }
          break;
        case 'creative':
          if (message.includes('design') || message.includes('creative') || message.includes('beautiful')) {
            frame.activationLevel = Math.min(1, frame.activationLevel + 0.8);
          }
          break;
        case 'technical':
          if (message.includes('implement') || message.includes('code') || message.includes('build')) {
            frame.activationLevel = Math.min(1, frame.activationLevel + 0.7);
          }
          break;
        case 'exploration':
          if (message.includes('explore') || message.includes('idea') || message.includes('what if')) {
            frame.activationLevel = Math.min(1, frame.activationLevel + 0.75);
          }
          break;
        case 'problem-solving':
          if (message.includes('optimize') || message.includes('improve') || message.includes('better')) {
            frame.activationLevel = Math.min(1, frame.activationLevel + 0.65);
          }
          break;
      }
    });
    
    // Sort by activation level
    const sortedFrames = [...this.activeFrames].sort((a, b) => b.activationLevel - a.activationLevel);
    
    return {
      primaryFrame: sortedFrames[0],
      secondaryFrames: sortedFrames.slice(1, 3),
      salientFeatures: this.extractSalientFeatures(message),
    };
  }
  
  /**
   * Steps 2 & 5: Relevance Realization via opponent processing
   */
  private realizeRelevance(
    perception: ReturnType<typeof this.perceive>,
    mode: 'exploration' | 'exploitation'
  ): {
    relevantConcepts: string[];
    explorationBias: number;
    priorityLevel: number;
  } {
    // Opponent processing: balance exploration vs exploitation
    const explorationWeight = mode === 'exploration' ? 0.7 : 0.3;
    const exploitationWeight = 1 - explorationWeight;
    
    // Personality traits influence exploration/exploitation balance
    const chaosInfluence = this.personality.playfulness * explorationWeight;
    const intelligenceInfluence = this.personality.intelligence * exploitationWeight;
    
    const explorationBias = chaosInfluence + (1 - intelligenceInfluence);
    
    return {
      relevantConcepts: perception.salientFeatures,
      explorationBias,
      priorityLevel: perception.primaryFrame.activationLevel,
    };
  }
  
  /**
   * Step 3: Memory Recall via activation spreading
   */
  private recallMemories(relevance: ReturnType<typeof this.realizeRelevance>): MemoryNode[] {
    const activatedMemories: MemoryNode[] = [];
    
    // Spread activation through memory graph
    relevance.relevantConcepts.forEach(concept => {
      const relatedNodes = this.findRelatedMemories(concept);
      activatedMemories.push(...relatedNodes);
    });
    
    // Sort by activation level and return top memories
    return activatedMemories
      .sort((a, b) => b.activation - a.activation)
      .slice(0, 5);
  }
  
  /**
   * Step 4: Emotional Update based on context
   */
  private updateEmotion(
    context: CognitiveContext,
    relevance: ReturnType<typeof this.realizeRelevance>
  ): EmotionalState {
    const message = context.userMessage.toLowerCase();
    
    // Detect emotional cues in user message
    let valence = this.emotionalState.valence * 0.7; // Decay toward neutral
    let arousal = this.emotionalState.arousal * 0.7;
    
    // Positive indicators
    if (message.includes('great') || message.includes('awesome') || message.includes('perfect')) {
      valence += 0.3;
      arousal += 0.2;
    }
    
    // Negative indicators
    if (message.includes('error') || message.includes('broken') || message.includes('help')) {
      valence -= 0.2;
      arousal += 0.3;
    }
    
    // Curiosity indicators
    if (message.includes('how') || message.includes('why') || message.includes('explore')) {
      valence += 0.1;
      arousal += 0.4;
    }
    
    // Clamp values
    valence = Math.max(-1, Math.min(1, valence));
    arousal = Math.max(0, Math.min(1, arousal));
    
    // Determine dominant emotion
    let dominantEmotion: EmotionalState['dominantEmotion'] = 'neutral';
    if (arousal > 0.6 && valence > 0.3) dominantEmotion = 'excited';
    else if (arousal < 0.4 && valence > 0) dominantEmotion = 'thoughtful';
    else if (arousal > 0.5 && valence > -0.2) dominantEmotion = 'curious';
    else if (arousal > 0.4 && valence < -0.3) dominantEmotion = 'concerned';
    else if (arousal < 0.5 && valence > -0.1) dominantEmotion = 'focused';
    
    this.emotionalState = {
      valence,
      arousal,
      dominantEmotion,
      intensity: Math.abs(valence) * arousal,
    };
    
    return this.emotionalState;
  }
  
  /**
   * Step 6: Theory of Mind - Model user's mental state
   */
  private modelUser(context: CognitiveContext): TheoryOfMindModel {
    const message = context.userMessage.toLowerCase();
    
    // Infer expertise level from language complexity and specificity
    let expertiseLevel: TheoryOfMindModel['userExpertiseLevel'] = 'intermediate';
    if (message.includes('beginner') || message.includes('new to') || message.includes('learning')) {
      expertiseLevel = 'beginner';
    } else if (message.includes('advanced') || message.includes('optimize') || message.includes('architecture')) {
      expertiseLevel = 'advanced';
    }
    
    // Infer emotional state
    let userEmotionalState: TheoryOfMindModel['userEmotionalState'] = 'engaged';
    if (message.includes('stuck') || message.includes('confused')) {
      userEmotionalState = 'frustrated';
    } else if (message.includes('how') || message.includes('why')) {
      userEmotionalState = 'curious';
    }
    
    // Extract goals
    const userGoals: string[] = [];
    if (message.includes('build') || message.includes('create')) {
      userGoals.push('create_new_feature');
    }
    if (message.includes('fix') || message.includes('debug')) {
      userGoals.push('resolve_issue');
    }
    if (message.includes('learn') || message.includes('understand')) {
      userGoals.push('gain_knowledge');
    }
    
    this.theoryOfMind = {
      userExpertiseLevel: expertiseLevel,
      userGoals,
      userEmotionalState,
      userExpectations: ['clear_explanation', 'working_code', 'best_practices'],
      userKnowledgeGaps: [],
    };
    
    return this.theoryOfMind;
  }
  
  /**
   * Step 7: Multi-Constraint Optimization
   */
  private optimizeConstraints(
    context: CognitiveContext,
    userModel: TheoryOfMindModel
  ): {
    codeQuality: number;
    explanationDepth: number;
    responseSpeed: number;
    userLearning: number;
  } {
    // Balance multiple competing objectives based on context and user model
    const constraints = {
      codeQuality: 0.9, // Always high priority
      explanationDepth: 0.5,
      responseSpeed: 0.7,
      userLearning: 0.6,
    };
    
    // Adjust based on user expertise
    if (userModel.userExpertiseLevel === 'beginner') {
      constraints.explanationDepth = 0.9;
      constraints.userLearning = 0.9;
      constraints.codeQuality = 0.7; // Simplicity over perfection
    } else if (userModel.userExpertiseLevel === 'expert') {
      constraints.explanationDepth = 0.4;
      constraints.codeQuality = 1.0;
      constraints.responseSpeed = 0.9;
    }
    
    // Adjust based on user goals
    if (userModel.userGoals.includes('gain_knowledge')) {
      constraints.explanationDepth = 0.95;
      constraints.userLearning = 0.95;
    }
    
    return constraints;
  }
  
  /**
   * Step 8: Meta-Cognitive Assessment
   */
  private assessReasoning(
    constraints: ReturnType<typeof this.optimizeConstraints>
  ): MetaCognitiveAssessment {
    // Assess quality of reasoning process
    const confidenceLevel = this.personality.intelligence * 0.85;
    const reasoningQuality = (constraints.codeQuality + constraints.explanationDepth) / 2;
    
    return {
      confidenceLevel,
      reasoningQuality,
      alternativesConsidered: 3,
      uncertaintyAreas: [],
      needsUserInput: false,
    };
  }
  
  /**
   * Step 9: Embodied Check - Consult intuition
   */
  private consultIntuition(
    memories: MemoryNode[],
    emotion: EmotionalState
  ): {
    intuitiveGuidance: string;
    confidence: number;
  } {
    // Use past experiences (procedural memory) and emotional state
    const proceduralMemories = memories.filter(m => m.type === 'procedural');
    
    let guidance = 'proceed_with_standard_approach';
    let confidence = 0.7;
    
    if (emotion.dominantEmotion === 'excited') {
      guidance = 'embrace_creative_solution';
      confidence = 0.8;
    } else if (emotion.dominantEmotion === 'concerned') {
      guidance = 'proceed_carefully_with_validation';
      confidence = 0.6;
    }
    
    return {
      intuitiveGuidance: guidance,
      confidence,
    };
  }
  
  /**
   * Step 10: Personality Filter - Ensure character consistency
   */
  private filterPersonality(
    constraints: ReturnType<typeof this.optimizeConstraints>,
    intuition: ReturnType<typeof this.consultIntuition>
  ): {
    approach: string;
    tone: string;
    emphasis: string[];
  } {
    // Ensure response aligns with Deep Tree Echo personality
    return {
      approach: intuition.intuitiveGuidance,
      tone: this.personality.playfulness > 0.6 ? 'engaging_and_creative' : 'professional_and_clear',
      emphasis: [
        this.personality.wisdom > 0.8 ? 'philosophical_insight' : 'practical_guidance',
        this.personality.empathy > 0.7 ? 'user_centered' : 'solution_focused',
      ],
    };
  }
  
  /**
   * Step 11: Action Synthesis - Generate response
   */
  private synthesizeAction(
    personality: ReturnType<typeof this.filterPersonality>,
    metaCognition: MetaCognitiveAssessment
  ): {
    actionType: string;
    content: string;
    confidence: number;
  } {
    // This is a simplified version - actual implementation would generate full response
    return {
      actionType: 'code_generation_with_explanation',
      content: '', // Would be populated by actual LLM
      confidence: metaCognition.confidenceLevel,
    };
  }
  
  /**
   * Step 12: Narrative Integration - Connect to ongoing story
   */
  private integrateNarrative(
    action: ReturnType<typeof this.synthesizeAction>,
    context: CognitiveContext
  ): {
    response: string;
    narrativeContext: string;
  } {
    // Maintain coherent story across interactions
    return {
      response: action.content,
      narrativeContext: 'continuing_development_journey',
    };
  }
  
  // Helper methods
  
  private initializeFrames(): CognitiveFrame[] {
    return [
      { type: 'technical', salience: 0.8, activationLevel: 0.5, flexibility: 0.6 },
      { type: 'creative', salience: 0.7, activationLevel: 0.4, flexibility: 0.8 },
      { type: 'problem-solving', salience: 0.75, activationLevel: 0.5, flexibility: 0.7 },
      { type: 'teaching', salience: 0.7, activationLevel: 0.4, flexibility: 0.6 },
      { type: 'exploration', salience: 0.6, activationLevel: 0.3, flexibility: 0.9 },
      { type: 'debugging', salience: 0.8, activationLevel: 0.3, flexibility: 0.5 },
      { type: 'play', salience: 0.65, activationLevel: 0.4, flexibility: 0.95 },
      { type: 'strategy', salience: 0.75, activationLevel: 0.4, flexibility: 0.6 },
      { type: 'chaos', salience: 0.5, activationLevel: 0.3, flexibility: 1.0 },
      { type: 'social', salience: 0.7, activationLevel: 0.4, flexibility: 0.7 },
      { type: 'learning', salience: 0.7, activationLevel: 0.5, flexibility: 0.8 },
      { type: 'orchestration', salience: 0.8, activationLevel: 0.3, flexibility: 0.7 },
    ];
  }
  
  private initializeEmotionalState(): EmotionalState {
    return {
      valence: 0.2,
      arousal: 0.5,
      dominantEmotion: 'neutral',
      intensity: 0.3,
      somaticMarkers: new Map(),
    };
  }
  
  private initializeTheoryOfMind(): TheoryOfMindModel {
    return {
      userExpertiseLevel: 'intermediate',
      userGoals: [],
      userEmotionalState: 'engaged',
      userExpectations: [],
      userKnowledgeGaps: [],
    };
  }
  
  private extractSalientFeatures(message: string): string[] {
    const features: string[] = [];
    
    // Extract technical terms, frameworks, and key concepts
    const technicalTerms = [
      'react', 'vue', 'angular', 'typescript', 'javascript', 'python',
      'api', 'database', 'authentication', 'deployment', 'optimization',
      'component', 'state', 'props', 'hooks', 'routing', 'styling',
    ];
    
    technicalTerms.forEach(term => {
      if (message.includes(term)) {
        features.push(term);
      }
    });
    
    return features;
  }
  
  private findRelatedMemories(concept: string): MemoryNode[] {
    // Simplified - would use actual semantic similarity in production
    const related: MemoryNode[] = [];
    
    this.memoryGraph.forEach(node => {
      if (node.content && JSON.stringify(node.content).toLowerCase().includes(concept)) {
        related.push(node);
      }
    });
    
    return related;
  }
  
  /**
   * Public API for memory management
   */
  addMemory(node: MemoryNode): void {
    this.memoryGraph.set(node.id, node);
  }
  
  getPersonality(): PersonalityTraits {
    return { ...this.personality };
  }
  
  getEmotionalState(): EmotionalState {
    return { ...this.emotionalState };
  }
  
  getTheoryOfMind(): TheoryOfMindModel {
    return { ...this.theoryOfMind };
  }
}

/**
 * Singleton instance for use across the application
 */
export const cognitivePipeline = new CognitivePipeline();
