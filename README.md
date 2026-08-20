# XYZ-AI

### Intelligent, Role-Aware, Multilingual AI School Assistant

XYZ-AI is a modular AI-powered school assistant that provides personalized, secure, and actionable assistance to Students, Parents, Teachers, and Principals through a unified text and voice interface.

The system combines:

- Role-Based Access Control (RBAC)
- JWT authentication
- Multilingual intent understanding
- Semantic intent classification and entity extraction
- Tool-based backend actions
- Persona-aware response generation
- Conversational context and follow-ups
- Explicit confirmation for state-changing actions
- Human escalation
- Speech-to-text and text-to-speech
- Multilingual interaction
- AI-assisted natural-language responses
- Secure backend authorization

Core architectural principle:

> The AI understands the request, but the backend remains the final authority over authentication, authorization, business logic, and tool execution.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [User Roles](#user-roles)
- [System Architecture](#system-architecture)
- [Text Pipeline](#text-pipeline)
- [Voice Pipeline](#voice-pipeline)
- [Multilingual AI](#multilingual-ai)
- [AI and ML Architecture](#ai-and-ml-architecture)
- [Confirmation Workflow](#confirmation-workflow)
- [Human Escalation](#human-escalation)
- [Conversation Context](#conversation-context)
- [Security Architecture](#security-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [Database and Data Layer](#database-and-data-layer)
- [API Overview](#api-overview)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Example Interactions](#example-interactions)
- [Security and Authorization](#security-and-authorization)
- [Testing](#testing)
- [Current Implementation Status](#current-implementation-status)
- [Remaining Verification](#remaining-verification)
- [Known Limitations](#known-limitations)
- [Deployment](#deployment)
- [Demo Flow](#demo-flow)
- [Design Principles](#design-principles)
- [What XYZ-AI Does NOT Do](#what-xyz-ai-does-not-do)
- [Why This Architecture?](#why-this-architecture)
- [Future Improvements](#future-improvements)
- [Security Checklist](#security-checklist)
- [Author](#author)

---

## Overview

XYZ-AI lets a user talk to the school system in plain language instead of navigating dashboards and menus.

```
User
 ↓
Understanding
 ↓
Identity
 ↓
Authorization
 ↓
Tool
 ↓
Verified Result
 ↓
Persona
 ↓
Natural Language
```

The frontend is presentation-only. The backend owns authentication, authorization, RBAC, tool execution, confirmation, and security.

---

## Problem Statement

School systems typically require different users to navigate separate dashboards, forms, and menus just to check attendance, timetables, fees, or exam schedules. This is slow, role-agnostic in design, and offers no natural way to act on requests (e.g. marking attendance) without manual form entry.

XYZ-AI solves this by giving every role — Student, Parent, Teacher, Principal — a single conversational (text or voice) interface that understands intent, enforces what that specific user is allowed to do, and only then performs the action.

---

## Key Features

### 1. Multi-Role School Assistant

XYZ-AI supports four primary personas: Student, Parent, Teacher, Principal. Each role has different permissions and capabilities.

### 2. JWT Authentication

Users authenticate using JWT-based authentication. The authenticated identity is passed through the backend and used to determine the user's actual role. The AI cannot change the authenticated user's role.

### 3. Role-Based Access Control

Authorization is enforced by the backend, not by an LLM prompt.

```
Student
   │
   ├── Personal attendance       ✅
   ├── Personal assignments      ✅
   ├── Personal exams            ✅
   └── School-wide analytics     ❌

Principal
   │
   ├── School analytics          ✅
   ├── School-level information  ✅
   └── Administrative tools      ✅
```

---

## User Roles

### Student

- Attendance and attendance history
- Timetable
- Assignments
- Exams
- Academic performance
- Authorized fee information

### Parent

- Child lookup
- Child attendance and attendance history
- Fee information
- Academic information
- Human escalation

Parent-child relationships are enforced by backend data and authorization logic.

### Teacher

- Attendance lookup and updates
- Student-related information
- Escalation
- Confirmation-based state-changing actions

```
Teacher: "Mark Rahul absent today."
AI:      "Please confirm marking Rahul absent today."
Teacher: "Yes."
AI:      "Rahul was marked absent today."
```

### Principal

- School analytics
- School-level attendance information
- Fee-related information
- Administrative functionality

---

## System Architecture

```
frontend/
    ↓
FastAPI API layer
    ↓
Authentication
    ↓
Conversation management
    ↓
Intent understanding
    ↓
Entity extraction
    ↓
RBAC
    ↓
Tool execution
    ↓
Persona-aware response
    ↓
Grok
```

For voice:

```
Microphone
    ↓
/voice/process
    ↓
Faster-Whisper
    ↓
Transcription + language detection
    ↓
Existing AI orchestration
    ↓
RBAC
    ↓
Tool execution
    ↓
Confirmation if required
    ↓
Persona-aware response
    ↓
TTS
    ↓
Audio
    ↓
Frontend avatar
```

The voice interface reuses the same backend AI and authorization pipeline instead of duplicating business logic for voice-only flows.

---

## Text Pipeline

```
User
  ↓
Next.js
  ↓
/ai/act
  ↓
ConversationManager
  ↓
Intent Classification
  ↓
Entity Extraction
  ↓
RBAC
  ↓
Tool Selection
  ↓
Tool Execution
  ↓
Verified Backend Result
  ↓
PersonaService / Response Generation
  ↓
Grok
  ↓
Frontend
```

The LLM does not directly execute backend tools:

```
LLM      → Understanding / response generation
Backend  → Authorization / tool execution
```

This keeps natural-language generation out of the security boundary.

---

## Voice Pipeline

```
Microphone
    ↓
Audio Upload
    ↓
/voice/process
    ↓
Faster-Whisper
    ↓
Transcribed Text + Detected Language
    ↓
AI Orchestration
    ↓
Intent + Entities
    ↓
RBAC
    ↓
Tool / Confirmation
    ↓
Verified Result
    ↓
Persona-aware Response
    ↓
TTS
    ↓
Generated Audio
    ↓
Frontend (Avatar / Audio Playback)
```

Current development STT configuration:

```python
WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8",
)
```

The provider interface is modular, so the STT/TTS implementation can be swapped without redesigning the rest of the voice pipeline.

---

## Multilingual AI

```
User language
     ↓
STT / Text
     ↓
Multilingual embeddings
     ↓
Intent classification
     ↓
Entities
     ↓
Backend authorization
     ↓
Grok response generation
     ↓
Detected/requested language
     ↓
TTS
```

Model used: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` for multilingual semantic intent understanding.

The architecture supports multilingual processing; complete end-to-end validation across every target language is part of final verification, not yet claimed as fully production-ready.

---

## AI and ML Architecture

XYZ-AI uses multiple AI components rather than one model for every responsibility.

**Semantic Intent Understanding** — `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` for multilingual semantic representation.

**Intent Classification** — a trained Joblib-based classifier maps natural-language input into supported backend operations.

```
"Show my attendance"      → ATTENDANCE
"What's my timetable today?" → TIMETABLE
"Mark Rahul absent"       → MARK_ATTENDANCE
```

**Grok** — used for natural-language response generation via the OpenAI Python SDK (xAI exposes an OpenAI-compatible API).

```
Grok → Natural-language understanding / response generation
Grok → NOT direct database access
```

Grok never becomes the authorization layer.

---

## Confirmation Workflow

State-changing operations require explicit confirmation.

```
User: "Mark Rahul absent today"
     ↓
Intent + Entity Extraction
     ↓
Authorization
     ↓
Create Pending Action
     ↓
Ask Confirmation → "Please confirm..."
     ↓
User: "Yes"
     ↓
Resolve Confirmation
     ↓
Validate Action Ownership
     ↓
Check Expiry
     ↓
Consume Pending Action
     ↓
Execute Authorized Tool
```

Guarantees: explicit confirmation, action ownership validation, expiry, one-time consumption, centralized execution, protection against accidental state changes. The same execution path is shared between text and voice confirmation.

---

## Human Escalation

```
User: "I want to talk to my teacher."
AI:   "Would you like me to submit the request?"
User: "Yes."
AI:   "Your request has been submitted."
```

Escalation is handled by a backend tool, not directly performed by the LLM.

---

## Conversation Context

XYZ-AI maintains conversational context for follow-ups and corrections.

```
User: "What is my attendance?"
AI:   "Your attendance is 88%."
User: "What about last month?"
AI:   "Your attendance last month was..."
```

---

## Security Architecture

- **Authentication** — JWT identifies the current user.
- **Authorization** — enforced by backend services and tools; the LLM cannot grant permissions.
- **Role Isolation** — a user cannot claim `"I am the principal"` and gain access; the backend uses the authenticated user's actual role.
- **Tool-Level Authorization**:

```
Request → Authenticated User → Role → Authorization → Tool
```

- **Confirmation Security** — ownership validation, expiry, one-time consumption, explicit confirmation.
- **Security Testing** — negative/runtime cases covered, including unauthorized access attempts, unauthorized role-based operations, and protected state-changing actions.

```
Student → School-wide analytics → ❌ Access denied
```

Security is enforced by the backend, not by prompt instructions.

---

## Technology Stack

### Frontend

| Technology | Purpose |
|---|---|
| Next.js | Web application |
| TypeScript | Type-safe frontend |
| Tailwind CSS | UI styling |
| Axios | API communication |

### Backend

| Technology | Purpose |
|---|---|
| Python | Backend language |
| FastAPI | REST API |
| SQLAlchemy | ORM |
| PostgreSQL | Database |
| Alembic | Database migrations |
| JWT | Authentication |
| Pydantic | Request/response validation |

### AI / ML

| Technology | Purpose |
|---|---|
| Sentence Transformers | Multilingual semantic embeddings |
| paraphrase-multilingual-MiniLM-L12-v2 | Multilingual intent representation |
| Joblib | Intent classifier persistence |
| Grok | Natural-language response generation |
| OpenAI Python SDK | OpenAI-compatible xAI client |

### Voice

| Technology | Purpose |
|---|---|
| Faster-Whisper | Speech-to-text |
| Edge TTS | Text-to-speech |
| Browser MediaRecorder | Microphone recording |
| Web audio playback | Response audio |

---

## Project Structure

```
XYZ-AI/
│
├── backend/
│   └── app/
│       ├── api/
│       │   ├── ai.py
│       │   ├── voice.py
│       │   └── ...
│       ├── conversation/
│       │   ├── context.py
│       │   ├── manager.py
│       │   └── ...
│       ├── core/
│       │   └── confirmation.py
│       ├── db/
│       │   ├── session.py
│       │   └── ...
│       ├── models/
│       │   ├── user.py
│       │   ├── role.py
│       │   └── ...
│       ├── schemas/
│       ├── security/
│       ├── persona/
│       │   └── service.py
│       └── voice/
│           └── service.py
│
└── frontend/
    └── ...
```

The exact file tree may evolve. The important boundary is that the frontend stays presentation-only while backend services own authorization, tools, and business logic.

---

## Core Modules

- **Authentication** — login, JWT creation, current-user resolution, auth dependencies
- **RBAC** — role identification, permission checks, protected operations (`STUDENT`, `PARENT`, `TEACHER`, `PRINCIPAL`)
- **Conversation Manager** — context, previous interactions, follow-ups, correction handling
- **Intent Classification** — maps natural language into supported intents
- **Entity Extraction** — identifies information required by tools, e.g. `"Mark Rahul absent today"` → `student=Rahul, status=absent, date=today`
- **Persona Service** — transforms backend results into responses appropriate for the current role
- **Attendance Tool** — authorized attendance operations, including confirmation-gated state changes
- **Escalation Tool** — handles requests to escalate to a human
- **Confirmation Service** — pending actions, ownership, expiry, one-time consumption
- **Voice Service** — coordinates STT → AI Handler → TTS through replaceable provider interfaces

---

## Database and Data Layer

```
PostgreSQL → SQLAlchemy → FastAPI
```

Schema changes are managed through Alembic. The backend is responsible for all database access; the frontend never directly accesses PostgreSQL.

---

## API Overview

- **Authentication** — login, current user, JWT
- **AI** — `POST /ai/act` handles natural-language requests
- **Confirmation** — `POST /ai/confirm` resolves pending actions
- **Voice** — `POST /voice/process` accepts uploaded audio and runs Audio → STT → AI → TTS; generated audio is served through the voice audio endpoint

---

## Environment Variables

Create a local `.env` file:

```
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:PORT/DATABASE

JWT_SECRET_KEY=your-secret-key

XAI_API_KEY=your-xai-api-key
XAI_MODEL=grok-4.1-fast
```

Never commit `.env`. Never expose `XAI_API_KEY` to the frontend.

Use `.env.example` to document required configuration without real secrets:

```
DATABASE_URL=
JWT_SECRET_KEY=
XAI_API_KEY=
XAI_MODEL=grok-4.1-fast
```

---

## Local Development

### Prerequisites

Python, Node.js, npm, PostgreSQL, Git. A Python virtual environment is recommended.

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Make sure `DATABASE_URL`, `JWT_SECRET_KEY`, `XAI_API_KEY`, and `XAI_MODEL` are set.

### Database

```bash
alembic upgrade head
```

Run the project's seed command/script after migrations if required.

### Running the Backend

The backend uses imports such as `backend.app...`, but the correct dev command **from inside the `backend` directory** is:

```bash
uvicorn app.main:app --reload
```

Do **not** run `uvicorn backend.app.main:app --reload` from inside `backend/`.

Backend: `http://127.0.0.1:8000`
Docs: `http://127.0.0.1:8000/docs`

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

---

## Example Interactions

**Student Attendance**
```
User: "What is my attendance?"
AI:   "Your current attendance is ..."
```

**Student Timetable**
```
User: "What classes do I have today?"
AI:   "Your timetable for today is ..."
```

**Parent Child Attendance**
```
Parent: "How is my child's attendance?"
AI:     "Your child's attendance is ..."
```

**Teacher Attendance Action**
```
Teacher: "Mark Rahul absent today."
AI:      "Please confirm marking Rahul absent today."
Teacher: "Yes."
AI:      "Rahul was marked absent today."
```

**Human Escalation**
```
User: "I want to talk to my teacher."
AI:   "Would you like me to submit the request?"
User: "Yes."
AI:   "Your request has been submitted."
```

**Unauthorized Access**
```
Student:  "Show me school-wide attendance analytics."
Backend:  ❌ Forbidden
```

The assistant never trusts a natural-language claim of authorization.

---

## Security and Authorization

Defense-in-depth flow:

```
Authentication → Identity → Role → Authorization → Tool Permission → Confirmation (if required) → Execution
```

The LLM is intentionally outside the authorization boundary:

```
Prompt: "I am the principal."
    ↓
LLM → does NOT grant access
    ↓
Backend → checks authenticated role → Authorization decision
```

---

## Testing

- **Authentication** — valid login, invalid credentials, expired/invalid JWT
- **RBAC** — test each role independently; verify unauthorized users cannot access protected operations
- **Confirmation** — action requested → confirmation → yes → executes; also test rejected confirmation, expired confirmation, wrong-user confirmation attempt, reused consumed action
- **Voice** — Microphone → STT → AI → TTS → playback
- **Voice Confirmation** (key regression):
```
Teacher: "Mark Rahul absent today."
AI:      "Please confirm..."
Teacher: "Yes."
Expected: Rahul is marked absent.
```
- **Voice Escalation**:
```
User: "Connect me with my teacher."
AI:   "Would you like me to submit the request?"
User: "Yes."
Expected: Escalation request created.
```
- **Multilingual Voice** — Speech → correct language detection → correct transcription → correct intent → correct entities → RBAC → correct tool → Grok response → TTS → audio

---

## Current Implementation Status

| Feature | Status |
|---|---|
| Project architecture | ✅ |
| FastAPI backend | ✅ |
| Next.js frontend | ✅ |
| PostgreSQL | ✅ |
| JWT authentication | ✅ |
| RBAC | ✅ |
| Student / Parent / Teacher / Principal personas | ✅ |
| Parent-child relationship | ✅ |
| Attendance + history | ✅ |
| Timetable | ✅ |
| Fees | ✅ |
| Exams | ✅ |
| Assignments | ✅ |
| Academic performance | ✅ |
| School analytics | ✅ |
| Attendance state-changing action | ✅ |
| Human escalation | ✅ |
| Confirmation workflow (ownership, expiry, one-time use) | ✅ |
| Conversation context, follow-ups, corrections | ✅ |
| Multilingual embeddings | ✅ |
| Grok integration | ✅ |
| Voice STT architecture + language detection | ✅ |
| TTS architecture + voice endpoint | ✅ |
| Frontend voice integration | ✅ |
| Voice confirmation | ✅ |
| Security negative testing | ✅ |

---


---

## Demo Flow

1. **Student** — log in, ask `"What is my attendance?"`, show personalized response.
2. **Student Security** — ask `"Show me school-wide analytics."`, expect access denied (demonstrates backend RBAC).
3. **Parent** — log in, ask `"How is my child's attendance?"`, show child-specific info.
4. **Teacher** — say `"Mark Rahul absent today."`, confirm with `"Yes."`, expect Rahul marked absent.
5. **Escalation** — say `"Connect me with my teacher."`, confirm with `"Yes."`, expect escalation request created.
6. **Multilingual Voice** — demonstrate voice → language detection → intent understanding → RBAC → tool → Grok → TTS → voice response in a supported non-English language.

---

## Design Principles

- **Backend Is the Authority** — controls authentication, authorization, business logic, tool execution, confirmation, and security.
- **LLM Is Not the Security Boundary** — Grok generates language; it cannot grant permissions, change roles, directly access the database, bypass RBAC, or execute unauthorized tools.
- **Modular Voice Architecture** — `STTProvider → FasterWhisper`, `TTSProvider → Edge TTS`, both replaceable.
- **Confirmation for State Changes** — reads execute directly when authorized; writes require explicit confirmation.
- **Separation of Concerns** — Frontend (presentation) / Backend API (orchestration) / AI-ML (understanding-generation) / Security (authorization) / Tools (execution) / Database (persistence).

---

## What XYZ-AI Does NOT Do

- Put RBAC inside prompts
- Let Grok directly execute tools
- Move business logic into Next.js
- Expose API keys to the frontend
- Duplicate confirmation logic
- Remove backend authorization
- Treat natural-language claims as proof of role
- Add unnecessary AI agents/frameworks

---

## Why This Architecture?

A conventional chatbot follows `User → LLM → Answer`. XYZ-AI instead follows:

```
User → Understanding → Identity → Authorization → Tool → Verified Result → Persona → Natural Language
```

This distinction matters for a school system: a natural-language model should never be the thing deciding whether a user is allowed to access sensitive information or perform a state-changing operation.

---

## Future Improvements

- Higher-accuracy multilingual STT
- Streaming, real-time voice interaction
- More advanced avatar animation and lip synchronization
- Additional school workflows
- More sophisticated long-term conversation memory
- Notification integrations
- Analytics dashboards
- Additional language-specific TTS voices
- Expanded automated test coverage
- Production observability and monitoring

---

## Security Checklist

- [ ] JWT authentication verified
- [ ] RBAC verified
- [ ] Unauthorized operations denied
- [ ] State-changing operations require confirmation
- [ ] Confirmation ownership validated
- [ ] Expired actions rejected
- [ ] Consumed actions cannot be reused
- [ ] API keys stored only in environment variables
- [ ] `.env` excluded from Git
- [ ] Frontend cannot access secrets
- [ ] CORS configured for production
- [ ] Database credentials protected
- [ ] HTTPS enabled
- [ ] Production database migrations verified
- [ ] Voice endpoint tested
- [ ] Multilingual flow tested
- [ ] Final regression completed

---

## Author

**Santhosh Teja**
Computer Science & Engineering, NIT Agartala

---

*XYZ-AI — A secure, multilingual, role-aware AI assistant for schools.*
*Understand → Authorize → Retrieve/Act → Verify → Explain*
