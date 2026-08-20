# XYZ-AI

### Role-Aware, Multilingual AI School Assistant

XYZ-AI is a modular AI-powered school assistant that provides personalized, secure, and actionable assistance to Students, Parents, Teachers, and Principals through a text and voice interface.

**Scope note:** This submission implements the XYZ AI application layer only. The four ERP portals referenced in the assignment (student-portal, parent-portal, management-portal, staff-portal) are represented here as mock backend services (`backend/app/services/`) backed by PostgreSQL, standing in for those external systems. XYZ AI's own responsibility — intent understanding, RBAC, tool orchestration, confirmation, persona-aware response generation — is what this repo implements.

Core architectural principle:

> The AI understands the request, but the backend remains the final authority over authentication, authorization, business logic, and tool execution.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [User Roles and Personas](#user-roles-and-personas)
- [System Architecture](#system-architecture)
- [Text Pipeline](#text-pipeline)
- [Voice Pipeline](#voice-pipeline)
- [Multilingual Support](#multilingual-support)
- [AI and ML Architecture](#ai-and-ml-architecture)
- [Confirmation Workflow](#confirmation-workflow)
- [Human Escalation](#human-escalation)
- [Security Architecture](#security-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Services vs Tools](#services-vs-tools)
- [Testing and Evaluation Data](#testing-and-evaluation-data)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Current Implementation Status](#current-implementation-status)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Overview

```
User
 ↓
Understanding (intent + entities)
 ↓
Identity (JWT)
 ↓
Authorization (RBAC)
 ↓
Tool (mock service call)
 ↓
Verified Result
 ↓
Persona-aware response (Grok)
 ↓
User
```

The frontend is presentation-only. The backend owns authentication, authorization, RBAC, tool execution, and confirmation.

### High-Level Architecture Diagram

```mermaid
flowchart TD
    U[User - Text or Voice] --> FE[Next.js Frontend]
    FE --> API[FastAPI API Layer]
    API --> AUTH[Auth: JWT Validation]
    AUTH --> CONV[Conversation Manager]
    CONV --> NLU[Intent Classification + Entity Extraction<br/>ML models]
    NLU --> RBAC[RBAC Check]
    RBAC -->|Denied| DENY[403 Forbidden]
    RBAC -->|Allowed| TOOL[Tool Layer]
    TOOL --> SVC[Service Layer<br/>Mock ERP APIs]
    SVC --> DB[(PostgreSQL)]
    SVC --> RESULT[Verified Result]
    RESULT --> PERSONA[Persona Service]
    PERSONA --> GROK[Grok - Response Generation]
    GROK --> FE
    FE --> U

    style RBAC fill:#7c3aed,color:#fff
    style AUTH fill:#7c3aed,color:#fff
    style DENY fill:#dc2626,color:#fff
    style GROK fill:#059669,color:#fff
```

---

## Key Features

- Multi-role assistant: Student, Parent, Teacher, Principal
- JWT authentication with backend-enforced RBAC
- Text and voice interaction
- Semantic intent classification and entity extraction
- Persona-aware response generation via Grok
- Confirmation workflow for state-changing actions
- Human escalation with backend-verified completion
- Conversational context and follow-ups

---

## User Roles and Personas

Each role is paired with a defined AI persona used for response generation:

| Role | Persona | Access |
|---|---|---|
| Student | Friendly and supportive Academic Assistant | Own attendance, timetable, assignments, exams, academic performance, fees |
| Parent | Caring and patient Parent Support Assistant | Linked child's attendance, academic info, fees; escalation |
| Teacher | Professional Teaching Assistant | Student attendance lookup and updates (confirmation-gated), escalation |
| Principal | Professional Management Assistant | School-wide analytics, attendance, fees, administrative info |

```
Teacher: "Mark Rahul absent today."
AI:      "Please confirm marking Rahul absent today."
Teacher: "Yes."
AI:      "Rahul was marked absent today."
```

Authorization is enforced by the backend (`backend/app/security/rbac.py`), never by prompt instruction.

---

## System Architecture

See the [High-Level Architecture Diagram](#high-level-architecture-diagram) above. Component-to-folder mapping:

| Stage | Folder |
|---|---|
| API layer | `backend/app/api` |
| Authentication | `backend/app/auth`, `backend/app/security` |
| Conversation management | `backend/app/conversation` |
| Intent + entity understanding | `backend/app/ML`, `backend/app/llm` |
| RBAC | `backend/app/security/rbac.py` |
| Tool execution | `backend/app/tools` → `backend/app/services` |
| Persona-aware response | `backend/app/persona` |

---

## Text Pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as /ai/act
    participant CM as ConversationManager
    participant ML as Intent + Entity ML
    participant RBAC as RBAC
    participant T as Tool
    participant S as Service (Mock API)
    participant P as PersonaService
    participant G as Grok

    U->>FE: "What is my attendance?"
    FE->>API: POST /ai/act (JWT)
    API->>CM: process(message, user)
    CM->>ML: classify intent + extract entities
    ML-->>CM: intent=ATTENDANCE, entities={}
    CM->>RBAC: check(user.role, intent)
    RBAC-->>CM: allowed
    CM->>T: execute(user_id)
    T->>S: get_attendance(user_id)
    S-->>T: verified data
    T-->>CM: result
    CM->>P: build_response(result, persona)
    P->>G: generate natural language
    G-->>P: response text
    P-->>API: final response
    API-->>FE: response
    FE-->>U: "Your attendance is 88%"
```

The LLM does not directly execute backend tools. It handles understanding and response generation only; the backend handles authorization and execution.

---

## Voice Pipeline

```mermaid
flowchart LR
    MIC[Microphone] --> REC[Browser MediaRecorder]
    REC --> UP[Upload audio<br/>/voice/process]
    UP --> STT[Faster-Whisper<br/>STT + Language Detection]
    STT --> TXT[Transcribed Text]
    TXT --> PIPE[Text Pipeline<br/>Intent → RBAC → Tool → Persona → Grok]
    PIPE --> TTS[Edge TTS]
    TTS --> AUD[Generated Audio]
    AUD --> PLAY[Frontend Playback]

    style STT fill:#0891b2,color:#fff
    style TTS fill:#0891b2,color:#fff
    style PIPE fill:#7c3aed,color:#fff
```

Voice reuses the same backend orchestration and authorization pipeline as text, no separate business logic path for voice.

Current dev STT config:

```python
WhisperModel("tiny", device="cpu", compute_type="int8")
```

**Note on avatar:** the frontend currently plays back generated audio; there is no avatar or facial-expression component implemented in this submission. This is listed under Known Limitations rather than claimed as complete.

---

## Multilingual Support

Semantic understanding uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Language | Status |
|---|---|
| English | ✅ Tested |
| Hindi | ✅ Tested |
| Tamil | 🟠 Supported, not fully verified |
| Telugu | 🟠 Supported, not fully verified |
| Marathi | 🟠 Supported, not fully verified |
| Bengali | 🟠 Supported, not fully verified |
| Gujarati | 🟠 Supported, not fully verified |
| Punjabi | 🟠 Supported, not fully verified |
| Kannada | 🟠 Supported, not fully verified |
| Malayalam | 🟠 Supported, not fully verified |
| Urdu | 🟠 Supported, not fully verified |

Evaluation data for code-mixed and multilingual voice input is tracked in `Data/multilingual_code_mixed_voice_eval.csv`.

---

## AI and ML Architecture

- **Intent classification** — trained classifier, `ML/models/intent/intent_classifier.joblib`, trained via `ML/training/intent/train.py`
- **Intent embeddings model** — `ML/models/intent/intent_embeddings_classifier.joblib`, trained via `ML/training/intent/train_embeddings.py` (semantic backup/ensemble for the primary classifier)
- **Entity extraction** — `ML/training/entities/extractor.py`
- **Runtime inference** — `ML/inference/understand.py`, called from the conversation layer
- **Response generation** — Grok, via OpenAI-compatible SDK (`backend/app/llm`)

Grok generates language; it does not access the database directly and cannot grant permissions.

---

## Confirmation Workflow

```mermaid
sequenceDiagram
    participant U as User (Teacher)
    participant CM as ConversationManager
    participant RBAC as RBAC
    participant C as ConfirmationService
    participant T as Tool

    U->>CM: "Mark Rahul absent today"
    CM->>RBAC: check(role=TEACHER, action=MARK_ATTENDANCE)
    RBAC-->>CM: allowed
    CM->>C: create_pending_action(user, action, entities)
    C-->>CM: pending_action_id
    CM-->>U: "Please confirm marking Rahul absent today."

    U->>CM: "Yes"
    CM->>C: resolve(pending_action_id, user)
    C->>C: validate ownership
    C->>C: check expiry
    C->>C: consume (one-time use)
    C-->>CM: confirmed
    CM->>T: execute(action, entities)
    T-->>CM: result
    CM-->>U: "Rahul was marked absent today."
```

Implemented in `backend/app/core/confirmation.py`. Test cases: `Data/action_confirmation_cases.csv`.

---

## Human Escalation

```
User: "I want to talk to my teacher."
AI:   "Would you like me to submit the request?"
User: "Yes."
AI:   "Your request has been submitted."
```

Escalation is executed via `backend/app/tools/escalation.py` → `backend/app/services/escalation.py`. The confirmation message is only returned after the underlying service call succeeds — it is not an optimistic response.

---

## Security Architecture

- **Authentication** — JWT (`backend/app/security/jwt.py`)
- **Authorization** — `backend/app/security/rbac.py`, enforced independent of LLM output
- **Password handling** — `backend/app/security/password.py`
- **Role isolation** — a user cannot claim a different role in natural language and gain access; the backend uses the authenticated user's actual role from the JWT
- **Confirmation security** — ownership validation, expiry, one-time consumption

Security and adversarial test case data (prompt injection, RBAC edge cases, hard negatives) is tracked in:

- `Data/prompt_injection_security_cases.csv`
- `Data/rbac_policy.csv`
- `Data/hard_negative_pairs.csv`
- `Data/mock_api_contract_tests.csv`

---

## Technology Stack

### Frontend
Next.js, TypeScript, Tailwind CSS

### Backend
Python, FastAPI, SQLAlchemy, PostgreSQL, Alembic, JWT, Pydantic

### AI / ML
Sentence Transformers (multilingual MiniLM), scikit-learn/Joblib classifiers, Grok (OpenAI-compatible SDK)

### Voice
Faster-Whisper (STT), Edge TTS (TTS)

---

## Project Structure

```
XYZ-AI/
├── backend/
│   ├── alembic/                  # DB migrations
│   └── app/
│       ├── ai/                   # parent_lookup.py, student_lookup.py
│       ├── api/                  # ai.py, auth.py, fees.py, voice.py
│       ├── auth/                 # service.py
│       ├── config/               # settings.py
│       ├── conversation/         # context.py, manager.py
│       ├── core/                 # confirmation.py, logging.py
│       ├── db/                   # session.py, seeds/
│       ├── llm/                  # base.py, provider.py, response_generator.py
│       ├── models/               # user.py, role.py, permission.py
│       ├── persona/              # service.py
│       ├── schemas/              # ai.py, auth.py
│       ├── security/             # deps.py, jwt.py, password.py, rbac.py
│       ├── services/             # mock ERP layer: attendance, fees, exam,
│       │                         # timetable, assignment, escalation,
│       │                         # academic_performance
│       ├── tools/                # LLM-callable wrappers over services/
│       ├── utils/
│       └── voice/                # stt/, tts/, service.py
│
├── ML/
│   ├── inference/                # understand.py
│   ├── models/intent/            # intent_classifier.joblib,
│   │                             # intent_embeddings_classifier.joblib
│   └── training/
│       ├── entities/             # extractor.py
│       └── intent/               # train.py, train_embeddings.py
│
├── Data/                         # catalogs + evaluation/test case CSVs
│   ├── rbac_policy.csv
│   ├── tool_catalog.csv
│   ├── intent_catalog.csv
│   ├── entity_catalog.csv
│   ├── entity_extraction_gold.csv
│   ├── persona_catalog.csv
│   ├── prompt_injection_security_cases.csv
│   ├── mock_api_contract_tests.csv
│   ├── multilingual_code_mixed_voice_eval.csv
│   ├── hard_negative_pairs.csv
│   ├── conversation_context_cases.csv
│   ├── action_confirmation_cases.csv
│   ├── assessment_coverage_matrix.csv
│   └── intent_ml_{train,test,validation,master}.csv
│
├── tests/
│   ├── unit/                     # test_attendance, test_confirmation,
│   │                             # test_conversation, test_fees,
│   │                             # test_persona, test_rbac
│   └── integration/               # scaffolded, not yet populated
│
├── frontend/
│   └── app/
│       ├── chat/                 # page.tsx
│       └── login/                # page.tsx
│
├── generated_audio/               # TTS output (runtime)
├── temp_audio/                    # STT input staging (runtime)
├── alembic.ini
├── requirements.txt
└── .env.example
```

---

## Services vs Tools

Each domain (attendance, fees, exams, timetable, assignments, escalation, academic performance) has two files:

- **`services/<domain>.py`** — the mock ERP/API layer. Pure data logic, no LLM awareness, no authorization decisions.
- **`tools/<domain>.py`** — a thin wrapper exposing the service to the AI orchestration layer as a callable tool.

```python
# services/academic_performance.py
class AcademicPerformanceService:
    """Mock academic performance service — represents the school ERP/mock API.
    No LLM logic, no authorization decisions."""

    @staticmethod
    def get_performance(user_id: int) -> dict:
        ...

# tools/academic_performance.py
class AcademicPerformanceTool:
    """Exposes academic performance to the AI orchestration layer."""
    name = "academic_performance"

    @staticmethod
    def execute(user_id: int) -> dict:
        return AcademicPerformanceService.get_performance(user_id)
```

This keeps the mock-API boundary explicit: `services/` never knows it's being called by an LLM-driven tool, and `tools/` never contains business logic itself.

---

## Testing and Evaluation Data

Unit tests (`tests/unit/`): attendance, confirmation, conversation, fees, persona, RBAC.

`tests/integration/` is scaffolded but not yet populated as of this submission.

Structured evaluation data (`Data/`) covers: RBAC policy matrix, intent/entity/tool/persona catalogs, prompt injection cases, mock API contract tests, multilingual and code-mixed voice evaluation, hard negative pairs, conversation context cases, confirmation cases, and an assessment coverage matrix. These represent authored test scenarios; not all have been executed as automated regression tests at time of submission.

---

## Environment Variables

```
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:PORT/DATABASE
JWT_SECRET_KEY=your-secret-key
XAI_API_KEY=your-xai-api-key
XAI_MODEL=grok-4.1-fast
```

Use `.env.example` as the template. Never commit `.env`.

---

## Local Development

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000` · Docs: `http://127.0.0.1:8000/docs`

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

---

## Current Implementation Status

| Feature | Status |
|---|---|
| FastAPI backend, Next.js frontend, PostgreSQL | ✅ |
| JWT authentication + RBAC | ✅ |
| Four roles with distinct personas | ✅ |
| Attendance, timetable, fees, exams, assignments, academic performance (mock services) | ✅ |
| Confirmation workflow (ownership, expiry, one-time use) | ✅ |
| Human escalation | ✅ |
| Conversation context / follow-ups | ✅ |
| Intent classification + entity extraction (ML) | ✅ |
| Grok response generation | ✅ |
| Voice STT + TTS pipeline | ✅ |
| Multilingual embeddings | ✅ (English/Hindi verified, others supported not fully verified) |


---


---

---

## Author

**Santhosh Teja**
Computer Science & Engineering, NIT Agartala
