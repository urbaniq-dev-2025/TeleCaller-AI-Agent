# Real-Time AI Call Coaching – Local Proof of Concept (PoC)
## Complete Build & Execution Guide for Cursor Agent

---

## 1. Objective

Build a **local Proof of Concept (PoC)** for a **Real-Time AI Call Coaching system** that:

- Attaches an AI coaching agent to a live phone call
- Listens to both the agent and the customer in real time
- Analyzes voice modulation and conversational signals
- Displays **live text-based suggestions** to the agent
- Runs **only for the duration of the call**
- Terminates immediately when the call ends

This PoC is intended for **client demonstration and validation**, not production scale.

---

## 2. Scope Definition

### Included
- Live call handling via Twilio
- Real-time audio streaming (agent + customer)
- Audio feature extraction (pace, volume, silence, interruptions)
- Rule-based decision engine
- Optional AI phrasing for suggestions
- Real-time UI updates via WebSocket
- Session-based lifecycle (no persistence)

### Excluded
- Post-call evaluation
- Call scoring or reports
- Dashboards or analytics
- CRM integration
- Audio whisper coaching
- Long-term storage

---

## 3. High-Level Architecture (Local)

```
Agent UI (Browser)
    ↑ WebSocket (suggestions)
    ↓
Local Backend (FastAPI)
    ↑ WebSocket (audio stream)
    ↓
Twilio Media Streams
    ↑
Live Phone Call (Agent ↔ Customer)
```

Each live call spawns a **temporary coaching agent** that exists only while the call is active.

---

## 4. Technology Stack (Locked)

### Backend
- Python 3.10+
- FastAPI
- WebSockets (fastapi[websockets])
- Async processing
- numpy, scipy (audio processing)
- websockets library

### Frontend
- React (Create React App or Vite)
- Single-page UI
- WebSocket client (native or socket.io-client)
- Tailwind CSS plus shadcn components or Material-UI (for styling)

### External Services
- **Twilio Voice + Media Streams** (Free trial: $15.50 credit)
- **cloudflared** (FREE - Cloudflare Tunnel, replaces ngrok)
- Streaming Speech-to-Text (Deepgram / AssemblyAI) - **SKIP for PoC** (not needed)
- Optional: OpenAI (for suggestion phrasing) - **SKIP for PoC** (use hardcoded messages)

### Local Dev
- **cloudflared** (FREE - recommended) or ngrok (free tier with limitations)
- Python virtual environment

---

## 4.5. COST ANALYSIS - FREE vs PAID SERVICES ⚠️

**IMPORTANT:** This section clarifies what you can do for FREE vs what requires payment.

### ✅ 100% FREE (No Cost Ever)

1. **Python 3.10+** - Completely free, open-source
2. **FastAPI** - Free, open-source framework
3. **React** - Free, open-source
4. **All Python libraries** (numpy, scipy, websockets, etc.) - Free
5. **Node.js & npm** - Free, open-source
6. **Git & GitHub** - Free for public/private repos
7. **VS Code / Cursor** - Free tier available
8. **Local development** - Runs on your machine, no cost

### 🆓 FREE TIER (Sufficient for PoC)

1. **Twilio** ⭐ **CRITICAL FOR THIS PROJECT**
   - **Free Trial:** $15.50 credit when you sign up
   - **What it covers:** 
     - ~100 minutes of voice calls
     - Media Streams included
     - Enough for extensive PoC testing
   - **After trial:** ~$0.013 per minute for voice calls
   - **Recommendation:** Use free trial for PoC. For demo, you may need ~$5-10 in credits
   - **Alternative:** None (Twilio is required for phone calls)

2. **ngrok** (Tunneling Service)
   - **Free Tier:** 
     - Random URLs (changes each restart)
     - 1 tunnel at a time
     - Limited bandwidth
     - Session timeout after inactivity
   - **Cost:** FREE for PoC needs
   - **Better FREE Alternative:** **cloudflared** (Cloudflare Tunnel)
     - Completely free
     - Stable URLs
     - No timeouts
     - Better for PoC
   - **Recommendation:** Use **cloudflared** instead of ngrok

3. **OpenAI API** (Optional - for suggestion phrasing)
   - **Free Tier:** $5 free credit for new accounts
   - **Cost after:** ~$0.002 per 1K tokens
   - **Status:** OPTIONAL - Can skip entirely for PoC
   - **Alternative:** Use hardcoded messages (completely free)

### ❌ PAID SERVICES (Can Be Avoided)

1. **Deepgram / AssemblyAI** (Speech-to-Text)
   - **Status:** OPTIONAL - Not required for PoC
   - **Cost:** Paid service
   - **Alternative:** Skip STT entirely. Use audio features only (volume, VAD, pace estimation)
   - **Recommendation:** Don't use for PoC - we can extract features without STT

### 💰 ESTIMATED TOTAL COST FOR PoC

**Minimum (100% Free Approach):**
- **$0** - Use Twilio free trial ($15.50 credit)
- **$0** - Use cloudflared (free alternative to ngrok)
- **$0** - Skip OpenAI (use hardcoded messages)
- **$0** - Skip STT services
- **Total: $0** ✅

**Recommended (Best Demo Quality):**
- **$0-5** - Twilio (free trial covers most, may need small top-up)
- **$0** - cloudflared (free)
- **$0** - Skip OpenAI (hardcoded messages work fine)
- **$0** - Skip STT
- **Total: $0-5** ✅

**With Premium Features:**
- **$5-10** - Twilio (if you exceed free trial)
- **$0** - cloudflared
- **$2-5** - OpenAI (optional, for better phrasing)
- **$10-20** - STT service (optional, not needed)
- **Total: $7-35** (only if you want premium features)

### 🎯 RECOMMENDED FREE SETUP FOR PoC

1. **Use Twilio Free Trial** - Sign up, get $15.50 credit (enough for PoC)
2. **Use cloudflared** instead of ngrok (completely free, better)
3. **Skip OpenAI** - Use hardcoded suggestion messages
4. **Skip STT** - Extract audio features directly (volume, VAD, pace)
5. **All code/development** - 100% free

### 📝 UPDATED TECHNOLOGY STACK (FREE-FIRST)

**Backend:**
- Python 3.10+ ✅ FREE
- FastAPI ✅ FREE
- numpy, scipy ✅ FREE
- webrtcvad (for VAD) ✅ FREE
- websockets ✅ FREE

**Frontend:**
- React ✅ FREE
- WebSocket client ✅ FREE

**External Services:**
- **Twilio** 🆓 FREE TRIAL ($15.50 credit)
- **cloudflared** ✅ FREE (replaces ngrok)
- **OpenAI** ❌ SKIP (use hardcoded messages)
- **STT Services** ❌ SKIP (not needed for PoC)

### ⚠️ IMPORTANT NOTES

1. **Twilio is the only service that requires payment** after free trial, but it's essential for phone calls. The free trial should cover your PoC.

2. **Everything else can be 100% free** if you:
   - Use cloudflared instead of ngrok
   - Skip OpenAI (hardcoded messages)
   - Skip STT services (use audio features only)

3. **For a client demo PoC**, the free tier approach is perfectly adequate. You only need to pay if:
   - You exceed Twilio free trial credits
   - You want to scale to production
   - You want premium features

4. **Cost-saving tip:** Use Twilio's test credentials and webhook testing tools during development to avoid using credits.

### 🔄 ALTERNATIVE: SIMULATED CALLS (100% FREE)

If you want to test **completely free** without Twilio:
- Simulate audio streams with test data
- Build the entire system
- Test with mock audio chunks
- Add Twilio integration later for real calls

**This allows you to build and test 100% of the code for $0.**

**Implementation:**
- Create a mock audio generator that sends test audio chunks
- Simulate different scenarios (fast speech, loud volume, interruptions)
- Test all coaching rules without using Twilio credits
- Perfect for development and initial testing
- Switch to real Twilio calls only when ready for demo

---

## 5. Implementation Phases (FOLLOW IN ORDER)

### **PHASE 1: Project Setup & Configuration**
**Goal:** Create project structure and configuration files

**Tasks:**
1. Create project root structure
2. Set up Python virtual environment
3. Create `requirements.txt` with all dependencies
4. Create `.env.example` file
5. Create `config.py` for environment variables
6. Create `README.md` with setup instructions

**Files to Create:**
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/config.py`
- `backend/README.md`
- `.gitignore`

**Dependencies for requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-dotenv==1.0.0
numpy==1.24.3
scipy==1.11.4
pydantic==2.5.0
twilio==8.10.0
```

---

### **PHASE 2: Core Backend Infrastructure**
**Goal:** Set up FastAPI server and basic routing

**Tasks:**
1. Create `backend/main.py` with FastAPI app
2. Set up CORS middleware
3. Create health check endpoint
4. Set up WebSocket base structure
5. Create logging configuration

**Files to Create:**
- `backend/main.py`
- `backend/utils/logger.py`

**Key Endpoints:**
- `GET /health` - Health check
- `GET /ws/ui/{session_id}` - UI WebSocket connection
- `POST /webhooks/twilio/voice` - Twilio voice webhook
- `POST /webhooks/twilio/media` - Twilio media stream webhook

---

### **PHASE 3: Session Management**
**Goal:** Implement call session lifecycle

**Tasks:**
1. Create session data model
2. Implement session creation
3. Implement session retrieval
4. Implement session cleanup
5. Add session expiration handling

**Files to Create:**
- `backend/sessions/__init__.py`
- `backend/sessions/session_manager.py`
- `backend/sessions/models.py`

**Session Model Structure:**
```python
{
    "call_session_id": str,
    "call_sid": str,  # Twilio Call SID
    "created_at": datetime,
    "agent_audio_buffer": list,
    "customer_audio_buffer": list,
    "metrics": {
        "agent_wpm": float,
        "agent_volume": float,
        "customer_volume": float,
        "silence_duration": float,
        "interruptions": int
    },
    "last_suggestion_time": float,
    "active_rules": dict,
    "ui_websocket": WebSocket,
    "is_active": bool
}
```

---

### **PHASE 4: Audio Processing Foundation**
**Goal:** Set up audio stream handling and basic feature extraction

**Tasks:**
1. Create audio stream handler
2. Implement audio chunk parsing (Twilio format: base64 mu-law)
3. Convert audio to numpy arrays
4. Implement basic VAD (Voice Activity Detection)
5. Calculate RMS energy (volume)
6. Calculate basic speaking rate estimation

**Files to Create:**
- `backend/audio/__init__.py`
- `backend/audio/stream_handler.py`
- `backend/audio/features.py`
- `backend/audio/vad.py`

**Audio Format:**
- Twilio sends mu-law encoded audio in base64
- Sample rate: 8000 Hz
- Chunk size: 20-50ms
- Two tracks: "inbound" (customer) and "outbound" (agent)

---

### **PHASE 5: Coaching Rules Engine**
**Goal:** Implement rule-based coaching logic

**Tasks:**
1. Define rule structure and types
2. Implement rule evaluation logic
3. Create cooldown/throttling mechanism
4. Implement suggestion message mapping
5. Create coaching engine orchestrator

**Files to Create:**
- `backend/coaching/__init__.py`
- `backend/coaching/rules.py`
- `backend/coaching/engine.py`
- `backend/coaching/messages.py`
- `backend/utils/throttling.py`

**Rule Types to Implement:**
1. **SPEAKING_TOO_FAST**: agent_wpm > 160 for 5 seconds
2. **SPEAKING_TOO_LOUD**: agent_volume > threshold for 3 seconds
3. **INTERRUPTING_CUSTOMER**: agent speaks while customer is speaking
4. **TOO_MUCH_SILENCE**: silence > 3 seconds during agent turn
5. **SPEAKING_TOO_SOFT**: agent_volume < threshold for 5 seconds

**Suggestion Format:**
```python
{
    "type": "SPEAKING_TOO_FAST",
    "message": "Slow down your pace slightly to sound more professional.",
    "severity": "medium",  # low, medium, high
    "timestamp": 1710000000.123
}
```

---

### **PHASE 6: Twilio Webhook Integration**
**Goal:** Handle Twilio call events and media streams

**Tasks:**
1. Implement call status webhook handler
2. Implement media stream start handler
3. Implement media stream data handler (WebSocket from Twilio)
4. Implement call disconnect handler
5. Set up TwiML response for media streams

**Files to Create:**
- `backend/api/__init__.py`
- `backend/api/webhooks.py`

**Webhook Endpoints:**
- `POST /webhooks/twilio/voice/status` - Call status changes
- `POST /webhooks/twilio/media/start` - Media stream started
- `POST /webhooks/twilio/media/stop` - Media stream stopped
- `WS /ws/twilio/media/{stream_sid}` - Media stream data

**TwiML Response (for call initiation):**
```xml
<Response>
    <Start>
        <Stream url="wss://your-cloudflared-url.trycloudflare.com/ws/twilio/media/{stream_sid}" />
    </Start>
    <Say>Your call is being monitored for coaching.</Say>
</Response>
```

---

### **PHASE 7: WebSocket Implementation**
**Goal:** Set up bidirectional WebSocket communication

**Tasks:**
1. Create UI WebSocket endpoint
2. Create Twilio media WebSocket handler
3. Implement message routing
4. Add connection management
5. Implement graceful disconnection

**Files to Create:**
- `backend/api/websocket.py`

**WebSocket Endpoints:**
- `WS /ws/ui/{session_id}` - For frontend to receive suggestions
- `WS /ws/twilio/media/{stream_sid}` - For Twilio to send audio

**Message Types:**
- UI → Backend: `{"type": "subscribe", "session_id": "..."}`
- Backend → UI: `{"type": "suggestion", "data": {...}}`
- Backend → UI: `{"type": "call_ended"}`

---

### **PHASE 8: Real-Time Processing Loop**
**Goal:** Connect all components for live processing

**Tasks:**
1. Create processing loop in session manager
2. Integrate audio feature extraction
3. Integrate coaching engine
4. Implement sliding window aggregation (3-5 seconds)
5. Add suggestion broadcasting to UI

**Integration Points:**
- Audio chunks → Feature extraction → Metrics update
- Metrics → Rule evaluation → Suggestion generation
- Suggestions → Throttling → WebSocket broadcast

**Processing Flow:**
```
Every 100ms:
1. Receive audio chunk from Twilio
2. Extract features (volume, VAD, pace estimate)
3. Update session metrics (sliding window)
4. Run coaching engine rules
5. If rule triggers and cooldown passed:
   - Generate suggestion
   - Broadcast to UI WebSocket
   - Update last_suggestion_time
```

---

### **PHASE 9: Frontend Setup**
**Goal:** Create React frontend application

**Tasks:**
1. Initialize React project (Vite or CRA)
2. Set up WebSocket client
3. Create main UI component
4. Create suggestion display component
5. Add styling and animations
6. Implement auto-fade for suggestions

**Files to Create:**
- `frontend/package.json`
- `frontend/src/App.jsx`
- `frontend/src/components/SuggestionCard.jsx`
- `frontend/src/hooks/useWebSocket.js`
- `frontend/src/styles/App.css`
- `frontend/index.html`

**Frontend Dependencies:**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "vite": "^5.0.0"
}
```

**UI Components:**
- Main container with WebSocket connection status
- Suggestion feed (vertical list)
- Suggestion cards with:
  - Message text
  - Severity indicator (color-coded)
  - Timestamp
  - Auto-fade animation

---

### **PHASE 10: Integration & Testing**
**Goal:** Connect all components and test end-to-end

**Tasks:**
1. Set up cloudflared tunnel (or ngrok)
2. Configure Twilio webhooks
3. Test call initiation
4. Test audio streaming
5. Test suggestion generation
6. Test UI updates
7. Test call termination cleanup

**Testing Checklist:**
- [ ] Backend starts without errors
- [ ] Health check endpoint works
- [ ] WebSocket connections establish
- [ ] Twilio webhook receives call events
- [ ] Audio chunks are received and processed
- [ ] Features are extracted correctly
- [ ] Rules trigger appropriately
- [ ] Suggestions appear in UI
- [ ] Session cleans up on call end
- [ ] Multiple calls can be handled (sequential)

---

## 6. Detailed File Structure

```
TeleCaller-AI-Agent/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variables template
│   ├── api/
│   │   ├── __init__.py
│   │   ├── webhooks.py         # Twilio webhook handlers
│   │   └── websocket.py        # WebSocket endpoints
│   ├── sessions/
│   │   ├── __init__.py
│   │   ├── session_manager.py  # Session lifecycle
│   │   └── models.py           # Session data models
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── stream_handler.py   # Audio stream processing
│   │   ├── features.py         # Feature extraction
│   │   └── vad.py              # Voice activity detection
│   ├── coaching/
│   │   ├── __init__.py
│   │   ├── rules.py            # Coaching rules definitions
│   │   ├── engine.py           # Rule evaluation engine
│   │   └── messages.py         # Suggestion messages
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Logging setup
│       └── throttling.py       # Suggestion throttling
├── frontend/
│   ├── package.json
│   ├── vite.config.js          # or similar
│   ├── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── components/
│   │   │   └── SuggestionCard.jsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   └── styles/
│   │       └── App.css
├── .gitignore
└── README.md
```

---

## 7. Environment Variables (.env)

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Server Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
TUNNEL_URL=https://your-cloudflared-url.trycloudflare.com
# OR if using ngrok: TUNNEL_URL=https://your-ngrok-url.ngrok.io

# Optional: OpenAI for suggestion phrasing
OPENAI_API_KEY=your_openai_key  # Optional

# Logging
LOG_LEVEL=INFO
```

---

## 8. End-to-End Call Flow (Detailed)

### 8.1 Call Initiation
1. Agent makes call via Twilio API or Twilio Console
2. Twilio receives call request
3. Twilio calls webhook: `POST /webhooks/twilio/voice/status` with `CallStatus=ringing`
4. Backend responds with TwiML to start media stream
5. Twilio establishes media stream WebSocket: `WS /ws/twilio/media/{stream_sid}`
6. Backend creates new session with `call_session_id`
7. Backend sends `{"type": "stream_started", "session_id": "..."}` to UI

### 8.2 Live Audio Processing
1. Twilio sends audio chunks every 20-50ms via WebSocket
2. Each chunk contains:
   ```json
   {
     "event": "media",
     "streamSid": "...",
     "media": {
       "payload": "base64_encoded_audio"
     },
     "track": "inbound" | "outbound"
   }
   ```
3. Backend:
   - Decodes base64 audio
   - Converts mu-law to linear PCM
   - Extracts features (volume, VAD, pace)
   - Updates session metrics (sliding window)
   - Runs coaching engine every 500ms
   - If rule triggers: generates suggestion and broadcasts to UI

### 8.3 UI Updates
1. Frontend connects to: `WS /ws/ui/{session_id}`
2. Receives suggestions in real-time
3. Displays suggestion cards with fade-in animation
4. Auto-removes suggestions after 5 seconds or when new one arrives

### 8.4 Call Termination
1. Call ends (hangup)
2. Twilio sends: `POST /webhooks/twilio/voice/status` with `CallStatus=completed`
3. Twilio closes media stream WebSocket
4. Backend:
   - Stops processing loop
   - Closes UI WebSocket
   - Sends `{"type": "call_ended"}` to UI
   - Destroys session after 5 second delay
   - Cleans up all resources

---

## 9. Audio Feature Extraction Details

### 9.1 Volume (RMS Energy)
```python
def calculate_rms(audio_chunk):
    # Convert to numpy array
    # Calculate RMS: sqrt(mean(square(samples)))
    # Return dB value
```

### 9.2 Voice Activity Detection (VAD)
```python
def detect_voice_activity(audio_chunk, threshold=-40):
    # Calculate RMS
    # Compare to threshold
    # Return True/False
```

### 9.3 Speaking Rate (Words Per Minute - WPM)
```python
def estimate_wpm(audio_chunks, time_window=5):
    # Count voice activity periods
    # Estimate syllables based on energy patterns
    # Convert to approximate WPM
    # Note: This is an approximation for PoC
```

### 9.4 Interruption Detection
```python
def detect_interruption(agent_audio, customer_audio):
    # Check if both tracks have voice activity simultaneously
    # If agent speaks while customer is speaking = interruption
```

---

## 10. Coaching Rules Implementation Details

### Rule Structure
```python
class CoachingRule:
    name: str
    condition: Callable  # Function that returns bool
    cooldown_seconds: int
    suggestion_type: str
    severity: str
```

### Rule Examples

**Rule 1: Speaking Too Fast**
```python
if agent_wpm > 160 and duration > 5:
    trigger("SPEAKING_TOO_FAST", cooldown=30)
```

**Rule 2: Speaking Too Loud**
```python
if agent_volume_db > -20 and duration > 3:
    trigger("SPEAKING_TOO_LOUD", cooldown=20)
```

**Rule 3: Interrupting Customer**
```python
if customer_speaking and agent_speaking:
    trigger("INTERRUPTING_CUSTOMER", cooldown=15)
```

**Rule 4: Too Much Silence**
```python
if silence_duration > 3 and agent_turn:
    trigger("TOO_MUCH_SILENCE", cooldown=10)
```

**Rule 5: Speaking Too Soft**
```python
if agent_volume_db < -50 and duration > 5:
    trigger("SPEAKING_TOO_SOFT", cooldown=25)
```

---

## 11. Frontend UI Specifications

### 11.1 Layout
- Full-screen single page
- Connection status indicator (top right)
- Suggestion feed (center, scrollable)
- Call status display (top center)

### 11.2 Suggestion Card Design
- Background color based on severity:
  - Low: Light blue (#E3F2FD)
  - Medium: Light yellow (#FFF9C4)
  - High: Light red (#FFEBEE)
- Border color matching severity
- Message text (large, readable)
- Timestamp (small, gray)
- Fade-in animation (0.3s)
- Auto-fade-out after 5 seconds

### 11.3 WebSocket Connection
- Auto-reconnect on disconnect
- Connection status indicator
- Error handling and display

---

## 12. Twilio Setup Instructions

### 12.1 Prerequisites
1. Twilio account (sign up at twilio.com)
2. Twilio phone number with Voice capability
3. cloudflared installed and configured (or ngrok)

### 12.2 Twilio Configuration Steps
1. Enable Media Streams for your phone number
2. Set webhook URL: `https://your-cloudflared-url.trycloudflare.com/webhooks/twilio/voice/status`
   - (If using ngrok: `https://your-ngrok-url.ngrok.io/webhooks/twilio/voice/status`)
3. Set HTTP method: POST
4. Configure media stream URL: `wss://your-cloudflared-url.trycloudflare.com/ws/twilio/media/{stream_sid}`
   - (If using ngrok: `wss://your-ngrok-url.ngrok.io/ws/twilio/media/{stream_sid}`)

### 12.3 Testing Setup
1. Start backend: `uvicorn main:app --reload`
2. Start cloudflared: `cloudflared tunnel --url http://localhost:8000`
   - (Or ngrok: `ngrok http 8000`)
3. Copy the tunnel URL (e.g., `https://xxxxx.trycloudflare.com`)
4. Update Twilio webhooks with tunnel URL
5. Make test call from Twilio Console (uses free trial credits)
6. Observe logs and UI

---

## 13. Development Workflow

### Step-by-Step Execution Order:

1. **Setup Phase**
   - Create all folder structures
   - Set up virtual environment
   - Install dependencies
   - Create .env file

2. **Backend Development** (Phases 1-8)
   - Build incrementally, test each phase
   - Use Postman/curl to test endpoints
   - Test WebSocket connections with wscat

3. **Frontend Development** (Phase 9)
   - Build UI components
   - Test WebSocket connection to backend
   - Style and polish

4. **Integration** (Phase 10)
   - Connect Twilio
   - Test full flow
   - Debug and fix issues

5. **Demo Preparation**
   - Document known limitations
   - Prepare test scenarios
   - Create demo script

---

## 14. Testing Strategy

### Unit Tests (Optional for PoC)
- Audio feature extraction functions
- Rule evaluation logic
- Session management

### Integration Tests
- WebSocket connections
- Webhook handling
- End-to-end call flow

### Manual Testing Scenarios
1. **Fast Speaking Test**: Speak quickly for 10 seconds → Should trigger "Slow down"
2. **Loud Speaking Test**: Speak loudly → Should trigger "Lower tone"
3. **Interruption Test**: Speak while customer is speaking → Should trigger "Let customer finish"
4. **Silence Test**: Stay silent for 5 seconds → Should trigger suggestion
5. **Call End Test**: Hang up → Session should clean up, UI should show "Call ended"

---

## 15. Troubleshooting Guide

### Common Issues

**Issue: WebSocket connection fails**
- Check CORS settings
- Verify WebSocket URL format (wss:// not https://)
- Check firewall/cloudflared tunnel (or ngrok)

**Issue: No audio received**
- Verify Twilio media stream is enabled
- Check WebSocket connection from Twilio
- Verify audio decoding logic

**Issue: Suggestions not appearing**
- Check rule thresholds (may be too strict)
- Verify WebSocket connection to UI
- Check throttling/cooldown settings
- Review logs for rule evaluation

**Issue: Session not cleaning up**
- Check call disconnect webhook
- Verify session cleanup logic
- Check for WebSocket connection leaks

---

## 16. Success Criteria for PoC

The PoC is considered successful if:

✅ A real call can be placed via Twilio  
✅ Audio streams are received and processed  
✅ At least 3 different rules trigger during a call  
✅ Suggestions appear in UI within 2 seconds of trigger  
✅ Suggestions stop immediately when call ends  
✅ Session cleans up properly  
✅ The demo is understandable to a non-technical client  
✅ No crashes or memory leaks during 10-minute call  

---

## 17. What NOT to Optimize in PoC

- Scalability (single call at a time is fine)
- Load handling
- Perfect accuracy (approximations are acceptable)
- Advanced ML models
- Polished UI (functional is enough)
- Error recovery (basic handling is sufficient)
- Performance optimization (real-time is the goal, not speed)

**Focus on clear demonstration of real-time value.**

---

## 18. Post-PoC Next Steps

1. Improve signal accuracy with better algorithms
2. Add analytics and dashboards
3. Harden infrastructure and error handling
4. Deploy to cloud (AWS/Azure/GCP)
5. Introduce scaling for multiple concurrent calls
6. Add post-call evaluation and reports
7. Integrate with CRM systems
8. Add audio whisper coaching option

---

## 19. Implementation Checklist

Use this checklist to track progress:

### Phase 1: Setup
- [ ] Project structure created
- [ ] Virtual environment set up
- [ ] Dependencies installed
- [ ] .env file configured

### Phase 2: Backend Infrastructure
- [ ] FastAPI app created
- [ ] Health check endpoint works
- [ ] CORS configured
- [ ] Logging set up

### Phase 3: Session Management
- [ ] Session model defined
- [ ] Session creation works
- [ ] Session retrieval works
- [ ] Session cleanup works

### Phase 4: Audio Processing
- [ ] Audio stream handler created
- [ ] Audio decoding works
- [ ] Feature extraction works
- [ ] VAD implemented

### Phase 5: Coaching Engine
- [ ] Rules defined
- [ ] Rule evaluation works
- [ ] Throttling works
- [ ] Messages mapped

### Phase 6: Twilio Integration
- [ ] Webhook handlers created
- [ ] TwiML responses work
- [ ] Media stream handling works

### Phase 7: WebSockets
- [ ] UI WebSocket works
- [ ] Twilio WebSocket works
- [ ] Message routing works

### Phase 8: Processing Loop
- [ ] Real-time loop implemented
- [ ] All components integrated
- [ ] Suggestions broadcast correctly

### Phase 9: Frontend
- [ ] React app created
- [ ] WebSocket client works
- [ ] UI displays suggestions
- [ ] Styling complete

### Phase 10: Integration
- [ ] cloudflared configured (or ngrok)
- [ ] Twilio webhooks set
- [ ] End-to-end test successful
- [ ] Demo ready

---

## 20. Quick Start Commands

```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend Setup
cd frontend
npm install
npm run dev

# cloudflared (separate terminal) - FREE alternative to ngrok
# Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
# Windows: Download from GitHub releases or use: winget install --id Cloudflare.cloudflared
cloudflared tunnel --url http://localhost:8000

# OR if using ngrok (free tier):
# Install: https://ngrok.com/download
ngrok http 8000
```

### 20.1 Installing cloudflared (FREE)

**Windows:**
```powershell
# Option 1: Using winget
winget install --id Cloudflare.cloudflared

# Option 2: Download from GitHub
# Visit: https://github.com/cloudflare/cloudflared/releases
# Download cloudflared-windows-amd64.exe
# Rename to cloudflared.exe and add to PATH
```

**macOS:**
```bash
brew install cloudflared
```

**Linux:**
```bash
# Download from GitHub releases or use package manager
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

**Verify installation:**
```bash
cloudflared --version
```

---

**END OF PLAN - Follow phases sequentially for best results**

