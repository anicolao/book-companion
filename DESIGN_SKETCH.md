# Design Sketch for Book Companion

## Architecture Overview

Book Companion consists of several interconnected components that work together to create an interactive audiobook experience.

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  (Playback Controls, Chat Interface, Visual Feedback)       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                    Application Core                          │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Session    │  │ Conversation │  │   Pause      │      │
│  │  Manager     │  │   Handler    │  │  Decision    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└───────┬────────────────────┬────────────────────┬───────────┘
        │                    │                    │
┌───────┴────────┐  ┌────────┴─────────┐  ┌──────┴──────────┐
│   Audiobook    │  │   LLM Service    │  │   Knowledge     │
│   Player       │  │   (GPT-4, etc)   │  │   Store         │
└────────────────┘  └──────────────────┘  └─────────────────┘
```

## Core Components

### 1. Audiobook Player Service

**Responsibilities:**
- Play, pause, and navigate through audiobook files
- Track current position (chapter, timestamp)
- Support multiple audio formats (MP3, M4B, etc.)
- Provide playback events to other components
- Manage audio sources (text-to-speech, pre-recorded, Audible integration)

**Key Technologies:**
- Audio playback libraries (e.g., Web Audio API, ffmpeg)
- Synchronization with text transcripts (when available)
- Buffering and streaming for large files

**Audio Source Strategy:**

*V0/MVP Approach:*
- **Text-to-Speech (TTS) for Audiobook**: Generate audio from Project Gutenberg texts using TTS
- **Distinct Voice for Reading**: Use Voice A (e.g., neutral, clear narrator voice) for book content
- **Distinct Voice for AI Companion**: Use Voice B (e.g., conversational, friendly tone) for discussions
- **Content Source**: Project Gutenberg for copyright-free books
- **Benefits**: Complete control over content, no licensing issues, easy to sync with text

*Long-term Approach:*
- **Audible Integration**: Connect to user's Audible account via API
- **Licensed Audiobooks**: Play professionally narrated content from Audible library
- **Hybrid Model**: Support both TTS (Project Gutenberg) and Audible sources
- **User Choice**: Let users select their preferred audiobook provider
- **Considerations**: DRM compliance, API access negotiation, offline playback

**Interface:**
```
- play()
- pause()
- seek(timestamp)
- getCurrentPosition()
- onPlaybackEvent(callback)
- getChapterInfo()
- setAudioSource(source: 'tts' | 'audible' | 'local')
- setVoiceProfile(profile: 'narrator' | 'companion')
```

### 2. Conversation Handler

**Responsibilities:**
- Manage chat interface and message history
- Route messages between user and LLM
- Maintain conversation context
- Format and present AI responses

**Key Technologies:**
- WebSocket or Server-Sent Events for real-time updates
- Message queue for async processing
- Context window management for LLM

**Interface:**
```
- sendMessage(userMessage)
- receiveResponse(aiMessage)
- getConversationHistory()
- clearConversation()
- exportConversation()
```

### 3. Session Manager

**Responsibilities:**
- Track user's progress through each audiobook
- Maintain state across sessions
- Manage user preferences and settings
- Handle multiple concurrent books

**Data Model:**
```
Session {
  userId: string
  bookId: string
  currentPosition: timestamp
  conversationHistory: Message[]
  bookmarks: Bookmark[]
  notes: Note[]
  lastAccessed: timestamp
  preferences: UserPreferences
}
```

### 4. LLM Service

**Responsibilities:**
- Process user questions and generate responses
- Maintain awareness of book context
- Generate insights and discussion prompts
- Decide when to initiate conversations
- Generate companion voice output using distinct TTS voice

**Key Components:**
- **Context Builder**: Constructs prompts with relevant book content
- **Response Generator**: Interfaces with LLM API
- **Quality Filter**: Ensures responses are relevant and appropriate
- **Voice Synthesizer**: Converts AI responses to speech with companion voice (Voice B)

**Technologies:**
- OpenAI GPT-4 API (or similar)
- Langchain or similar orchestration framework
- Custom prompt templates
- TTS API (e.g., OpenAI TTS, Google Cloud TTS, ElevenLabs) for companion voice

### 5. Pause Decision Engine

**Responsibilities:**
- Analyze audiobook content in real-time
- Identify key learning moments
- Decide when AI should initiate a pause
- Balance interruption with learning value

**Decision Factors:**
- Content complexity (new concepts, technical terms)
- Information density (amount of new information)
- Natural pause points (chapter ends, transitions)
- User engagement patterns (how often they pause)
- Time since last interaction

**Algorithm Sketch:**
```
score = 0
score += contentComplexity * 0.3
score += informationDensity * 0.3
score += isNaturalPause * 0.2
score += timeSinceLastInteraction * 0.2

if score > threshold AND userAllowsAIInitiated:
  suggestPause()
```

### 6. Knowledge Store

**Responsibilities:**
- Store book metadata and content
- Index searchable content
- Maintain semantic embeddings for content retrieval
- Cache frequently accessed information
- Manage book sources (Project Gutenberg, Audible, etc.)

**Data Storage:**
- **Metadata DB**: PostgreSQL or similar for structured data
- **Vector DB**: Pinecone, Weaviate, or Chroma for semantic search
- **Cache**: Redis for frequently accessed data
- **Object Storage**: S3 or similar for audio files (TTS-generated, cached)
- **External Integration**: Audible API integration for licensed content (long-term)

**Book Source Management:**

*V0/MVP:*
- **Project Gutenberg Catalog**: Import and index public domain books
- **Text Storage**: Store full text for TTS generation
- **Generated Audio Cache**: Cache TTS-generated audio segments to avoid regeneration

*Long-term:*
- **Audible Integration**: OAuth connection to user's Audible account
- **Library Sync**: Access user's purchased Audible books
- **Metadata Mapping**: Link Audible books with companion features
- **Hybrid Catalog**: Unified interface for both free (Gutenberg) and licensed (Audible) content

## Key Workflows

### Workflow 1: User-Initiated Conversation

```
1. User presses pause button
2. Audiobook Player Service pauses playback
3. UI transitions to conversation mode
4. User types or speaks a question
5. Conversation Handler receives input
6. Context Builder gathers:
   - Current book position
   - Recent content (last 5 minutes of transcript)
   - Conversation history
   - User profile/preferences
7. LLM Service generates response
8. Response displayed in chat interface
9. User can continue conversation or resume playback
```

### Workflow 2: AI-Initiated Pause

```
1. Audiobook playing normally
2. Pause Decision Engine monitors:
   - Content being played
   - Semantic analysis of concepts
   - Time since last interaction
   - User engagement patterns
3. Engine identifies potential pause moment
4. Score calculated based on multiple factors
5. If score exceeds threshold:
   - Soft notification displayed (non-intrusive)
   - Audio fades slightly
   - Suggestion shown: "I have a thought about this concept"
6. User can:
   - Accept: audiobook pauses, AI shares insight
   - Defer: mark for later discussion
   - Dismiss: continue playing
```

### Workflow 3: Session Restoration

```
1. User opens app/returns to book
2. Session Manager loads last session:
   - Book position
   - Recent conversation history
   - Bookmarks and notes
3. UI displays:
   - "Resume from [position]"
   - Recent conversation preview
   - Option to review notes
4. User resumes listening or reviews past discussions
```

## Data Flow

### Real-Time Audio Processing

```
Audio Source
    ↓
Decoder/Buffer
    ↓
[Playback] → Timeline Events → Content Analyzer
                                      ↓
                              Pause Decision Engine
                                      ↓
                                UI Notifications
```

### Conversation Processing

```
User Input
    ↓
Message Parser
    ↓
Context Builder ← Knowledge Store
    ↓            ← Session Manager
    ↓            ← Current Book Position
    ↓
LLM Service
    ↓
Response Formatter
    ↓
UI Display + Session History
```

## Technical Stack Recommendations

### Frontend
- **Framework**: React or Vue.js for responsive UI
- **Audio**: Howler.js or Web Audio API
- **Chat Interface**: Custom or Stream Chat components
- **State Management**: Redux or Zustand

### Backend
- **API Server**: Node.js/Express or Python/FastAPI
- **Real-time**: WebSockets (Socket.io) or Server-Sent Events
- **LLM Integration**: OpenAI SDK, Langchain
- **TTS Integration**: OpenAI TTS API, Google Cloud TTS, or ElevenLabs
- **Task Queue**: BullMQ or Celery for async processing (TTS generation, caching)

### Data Layer
- **Primary DB**: PostgreSQL for user data and metadata
- **Vector DB**: Pinecone or Weaviate for semantic search
- **Cache**: Redis for session data and TTS audio segments
- **Storage**: S3-compatible for generated audio files and book texts
- **External APIs**: Project Gutenberg API (V0), Audible API (long-term)

### Infrastructure
- **Hosting**: Cloud platform (AWS, GCP, Azure)
- **Container**: Docker for consistent deployment
- **Orchestration**: Kubernetes for scaling (future)
- **CDN**: CloudFlare or similar for audio delivery

## Security Considerations

### Data Protection
- Encrypt audiobook files at rest and in transit
- Secure API keys and credentials with secrets management
- Implement rate limiting to prevent abuse

### User Privacy
- End-to-end encryption for conversations (optional)
- Clear data retention policies
- User control over data export and deletion
- Anonymous usage analytics

### Access Control
- User authentication (OAuth, JWT)
- Authorization for purchased/licensed content
- DRM compliance for commercial audiobooks

## Scalability Considerations

### Performance Targets
- Audio playback start: < 2 seconds
- LLM response time: < 5 seconds for simple queries
- UI responsiveness: 60 FPS during all interactions
- Support 10,000+ concurrent users (future)

### Optimization Strategies
- **Caching**: Aggressive caching of book metadata and common queries
- **Streaming**: Stream audio and LLM responses
- **Batch Processing**: Process multiple AI requests together
- **CDN**: Distribute audio files globally
- **Lazy Loading**: Load content on-demand

### Monitoring
- Track playback quality and errors
- Monitor LLM API usage and costs
- User engagement metrics
- System performance (latency, throughput)

## MVP Scope

For initial prototype (V0), focus on:

1. **TTS-Based Audio Generation**: 
   - Generate audiobook narration from Project Gutenberg texts
   - Use distinct Voice A for book reading (e.g., neural TTS with clear, neutral tone)
   - Use distinct Voice B for AI companion discussions (e.g., warmer, conversational tone)
   - Cache generated audio for performance

2. **Project Gutenberg Integration**:
   - Browse and select from Project Gutenberg catalog
   - Import book text for TTS generation
   - No licensing concerns, fully legal and free

3. **Basic Audio Playback**: Play/pause generated audio with position tracking

4. **Simple Chat Interface**: Text-based conversation UI with voice output option

5. **Manual Pause Only**: User initiates all conversations

6. **Basic Context**: Include last 2 minutes of content in LLM prompts

7. **Single Book**: Support one book at a time per user

8. **Local Storage**: Simple file-based persistence

**Deferred to Post-MVP:**
- AI-initiated pauses
- Multi-book management
- Advanced context retrieval
- Social features
- Analytics dashboard
- Mobile apps
- **Audible integration** (see Long-term Roadmap below)

## Development Phases

### Phase 1: Core Foundation (Weeks 1-4)
- Set up development environment
- Integrate Project Gutenberg API/catalog
- Implement TTS with dual voice profiles (narrator Voice A + companion Voice B)
- Implement basic audio player for TTS-generated content
- Create simple chat interface
- Integrate LLM API with basic prompts

### Phase 2: Context Intelligence (Weeks 5-8)
- Implement efficient TTS caching strategy
- Build context builder using book text
- Enhance prompts with book awareness
- Add session persistence
- Optimize voice generation performance

### Phase 3: Smart Pausing (Weeks 9-12)
- Build pause decision engine
- Implement content analysis
- Create AI-initiated pause UX
- Fine-tune decision thresholds
- Refine voice transitions between reading and discussion modes

### Phase 4: Polish & Test (Weeks 13-16)
- User testing and feedback
- Performance optimization
- Bug fixes and refinement
- Documentation
- Prepare architecture for future Audible integration

## Long-term Roadmap: Audible Integration

### Phase 5: Audible Integration (Post-MVP, 6-12 months)

**Objectives:**
- Allow users to connect their Audible account
- Play professionally narrated audiobooks from Audible library
- Maintain AI companion features with commercial content

**Technical Requirements:**
1. **Audible API Integration**:
   - Negotiate API access with Audible/Amazon
   - Implement OAuth authentication for user accounts
   - Access user's library and playback capabilities

2. **DRM Compliance**:
   - Respect Audible's DRM and content protection
   - Implement secure playback within allowed parameters
   - Ensure AI features don't compromise content security

3. **Audio Synchronization**:
   - Extract or generate timestamps for Audible content
   - Sync AI companion with professional narration
   - Handle chapter markers and navigation

4. **Dual-Source Architecture**:
   - Unified UI for both Project Gutenberg (TTS) and Audible content
   - Seamless switching between content sources
   - User preference management

5. **Transcript Generation**:
   - Use speech-to-text for Audible content if transcripts unavailable
   - Build context for AI companion from audio analysis
   - Cache transcripts for performance

**Challenges:**
- Audible API availability (may be limited or restricted)
- DRM constraints on audio manipulation
- Cost of API access or per-play fees
- Quality of auto-generated transcripts vs. human-created

**Alternatives if Audible API unavailable:**
- Partner with other audiobook platforms (Libro.fm, Kobo, etc.)
- Focus on expanding Project Gutenberg + TTS experience
- Develop user upload feature for personal audiobook files

## Open Questions

1. **Audible API Access**: Is Audible API available for third-party apps? What are the terms?
2. **TTS Voice Quality**: Which TTS provider offers best quality and voice variety for V0?
3. **Voice Customization**: Should users be able to choose narrator and companion voices?
4. **LLM Choice**: Single provider or support multiple LLMs?
5. **Pricing Model**: Freemium, subscription, pay-per-use?
6. **Platform Priority**: Web-first, mobile-first, or desktop app?
7. **Transcript Caching**: How to efficiently cache and manage TTS audio and transcripts?

## Next Steps

1. Build proof-of-concept with single audiobook
2. Test core conversation experience with users
3. Validate technical architecture choices
4. Secure necessary content licenses
5. Refine based on early feedback
6. Plan for production deployment

---

This design sketch provides a starting point for implementation. As we build and learn, we'll iterate on these choices to create the best possible experience for users.
