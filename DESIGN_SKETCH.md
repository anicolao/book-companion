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

**Key Technologies:**
- Audio playback libraries (e.g., Web Audio API, ffmpeg)
- Synchronization with text transcripts (when available)
- Buffering and streaming for large files

**Interface:**
```
- play()
- pause()
- seek(timestamp)
- getCurrentPosition()
- onPlaybackEvent(callback)
- getChapterInfo()
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

**Key Components:**
- **Context Builder**: Constructs prompts with relevant book content
- **Response Generator**: Interfaces with LLM API
- **Quality Filter**: Ensures responses are relevant and appropriate

**Technologies:**
- OpenAI GPT-4 API (or similar)
- Langchain or similar orchestration framework
- Custom prompt templates

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

**Data Storage:**
- **Metadata DB**: PostgreSQL or similar for structured data
- **Vector DB**: Pinecone, Weaviate, or Chroma for semantic search
- **Cache**: Redis for frequently accessed data
- **Object Storage**: S3 or similar for audio files

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
- **Task Queue**: BullMQ or Celery for async processing

### Data Layer
- **Primary DB**: PostgreSQL for user data and metadata
- **Vector DB**: Pinecone or Weaviate for semantic search
- **Cache**: Redis for session data
- **Storage**: S3-compatible for audiobook files

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

For initial prototype, focus on:

1. **Basic Audio Playback**: Play/pause MP3 files with position tracking
2. **Simple Chat Interface**: Text-based conversation UI
3. **Manual Pause Only**: User initiates all conversations
4. **Basic Context**: Include last 2 minutes of content in LLM prompts
5. **Single Book**: Support one book at a time per user
6. **Local Storage**: Simple file-based persistence

**Deferred to Post-MVP:**
- AI-initiated pauses
- Multi-book management
- Advanced context retrieval
- Social features
- Analytics dashboard
- Mobile apps

## Development Phases

### Phase 1: Core Foundation (Weeks 1-4)
- Set up development environment
- Implement basic audio player
- Create simple chat interface
- Integrate LLM API with basic prompts

### Phase 2: Context Intelligence (Weeks 5-8)
- Add transcript/content parsing
- Implement context building
- Enhance prompts with book awareness
- Add session persistence

### Phase 3: Smart Pausing (Weeks 9-12)
- Build pause decision engine
- Implement content analysis
- Create AI-initiated pause UX
- Fine-tune decision thresholds

### Phase 4: Polish & Test (Weeks 13-16)
- User testing and feedback
- Performance optimization
- Bug fixes and refinement
- Documentation

## Open Questions

1. **Content Rights**: How to handle copyrighted audiobook content?
2. **Transcript Source**: Generate from audio or require existing transcripts?
3. **LLM Choice**: Single provider or support multiple LLMs?
4. **Pricing Model**: Freemium, subscription, pay-per-use?
5. **Platform Priority**: Web-first, mobile-first, or desktop app?
6. **Integration**: Build standalone or integrate with existing audiobook apps?

## Next Steps

1. Build proof-of-concept with single audiobook
2. Test core conversation experience with users
3. Validate technical architecture choices
4. Secure necessary content licenses
5. Refine based on early feedback
6. Plan for production deployment

---

This design sketch provides a starting point for implementation. As we build and learn, we'll iterate on these choices to create the best possible experience for users.
