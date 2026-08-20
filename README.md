# XYZ-AI

### Intelligent, Role-Aware, Multilingual AI School Assistant

XYZ-AI is a modular AI-powered school assistant designed to provide
personalized, secure, and actionable assistance to Students, Parents,
Teachers, and Principals through a unified text and voice interface.

The system combines:

- Role-Based Access Control (RBAC)
- JWT authentication
- Multilingual intent understanding
- Semantic intent classification
- Entity extraction
- Tool-based backend actions
- Persona-aware response generation
- Conversational context and follow-ups
- Explicit confirmation for state-changing actions
- Human escalation
- Speech-to-text
- Text-to-speech
- Multilingual interaction
- AI-assisted natural-language responses
- Secure backend authorization

The core architectural principle is simple:

> The AI understands the request, but the backend remains the final authority
> over authentication, authorization, business logic, and tool execution.

---

## Table of Contents

- [Overview](#overview)
- [Problem](#problem)
- [Solution](#solution)
- [Key Features](#key-features)
- [User Roles](#user-roles)
- [System Architecture](#system-architecture)
- [Text Pipeline](#text-pipeline)
- [Voice Pipeline](#voice-pipeline)
- [Confirmation Workflow](#confirmation-workflow)
- [Security Architecture](#security-architecture)
- [AI and ML Architecture](#ai-and-ml-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [Database and Data Layer](#database-and-data-layer)
- [API Overview](#api-overview)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [Example Interactions](#example-interactions)
- [Security and Authorization](#security-and-authorization)
- [Testing](#testing)
- [Current Implementation Status](#current-implementation-status)
- [Known Limitations](#known-limitations)
- [Deployment](#deployment)
- [Demo Flow](#demo-flow)
- [Design Principles](#design-principles)
- [Future Improvements](#future-improvements)
- [Project Completion Roadmap](#project-completion-roadmap)
- [License](#license)

---

# Overview

XYZ-AI is designed as a school-wide AI assistant rather than a generic
chatbot.

A user can interact with the system using natural language and receive
responses appropriate to their role.

For example:

### Student

> "What is my timetable for today?"

### Parent

> "How is my child doing in attendance?"

### Teacher

> "Mark Rahul absent today."

XYZ-AI does not immediately execute sensitive state-changing operations.

Instead, it follows an explicit confirmation workflow:

> "Please confirm marking Rahul absent today."

The teacher can then confirm:

> "Yes."

The backend validates the pending action and executes the authorized
attendance operation.

### Principal

> "Show me the school's attendance analytics."

A Student attempting to access the same school-wide analytics is denied
by backend authorization.

---

# Problem

School information is usually distributed across different systems,
dashboards, databases, and communication channels.

Users may need to:

- Check attendance
- View timetables
- Check assignments
- Review exams
- Check fees
- View academic performance
- Access child information
- Request help from teachers
- Perform authorized administrative actions

Traditional interfaces require users to navigate multiple screens and
remember where information is located.

A conversational interface can simplify this interaction.

However, a school assistant cannot simply be a chatbot.

It must understand:

1. Who the user is
2. What the user is asking
3. Which information the user is allowed to access
4. Whether the request is read-only or state-changing
5. Which backend tool should execute the operation
6. How the result should be communicated to that particular user

XYZ-AI is designed around these requirements.

---

# Solution

XYZ-AI separates natural-language understanding from authorization
and business logic.

The high-level architecture is:

```text
                    ┌──────────────────────┐
                    │      User            │
                    │ Student / Parent /   │
                    │ Teacher / Principal  │
                    └──────────┬───────────┘
                               │
                     Text or Voice
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Next.js Frontend  │
                    │  Presentation Layer  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │   Backend API        │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Authentication       AI/ML          Conversation
          + RBAC           Orchestration       Context
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Authorization /      │
                    │ Tool Selection       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Backend Tools        │
                    │ Attendance / Fees /  │
                    │ Exams / Assignments  │
                    │ Analytics / Escalate │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ PostgreSQL Database  │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Persona + Response   │
                    │ Generation           │
                    └──────────┬───────────┘
                               │
                               ▼
                         User Response

The backend is authoritative for:

Authentication
Authorization
RBAC
Intent orchestration
Tool execution
Confirmation
Security
Business logic

The frontend is presentation-only.

Key Features
1. Multi-Role School Assistant

XYZ-AI supports four primary personas:

Student
Parent
Teacher
Principal

Each role has different permissions and capabilities.

2. JWT Authentication

Users authenticate using JWT-based authentication.

The authenticated identity is passed through the backend and is used
to determine the user's actual role.

The AI cannot change the authenticated user's role.

3. Role-Based Access Control

Authorization is enforced by the backend.

Example:

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

RBAC is not implemented through an LLM prompt.

The backend determines whether the requested operation is authorized.

User Roles
Student

Students can access authorized personal academic information such as:

Attendance
Attendance history
Timetable
Assignments
Exams
Academic performance
Authorized fee information
Parent

Parents can access information related to their associated children.

Capabilities include:

Child lookup
Child attendance
Attendance history
Fee information
Academic information
Human escalation

Parent-child relationships are enforced by backend data and authorization
logic.

Teacher

Teachers can perform authorized teaching operations such as:

Attendance lookup
Attendance updates
Student-related information
Escalation
Confirmation-based state-changing actions

Sensitive actions require explicit confirmation.

Example:

Teacher:
"Mark Rahul absent today."


Assistant:
"Please confirm marking Rahul absent today."


Teacher:
"Yes."


Assistant:
"Rahul was marked absent today."
Principal

Principals have access to school-level administrative capabilities,
including:

School analytics
School-level attendance information
Fee-related information
Administrative functionality
System Architecture

XYZ-AI follows a modular architecture.

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

For voice:

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

This allows the voice interface to reuse the same backend AI and
authorization pipeline instead of creating a separate voice-only
business-logic system.

Text Pipeline

The text interaction pipeline is:

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

The important architectural property is that the LLM does not directly
execute backend tools.

Instead:

LLM
 ↓
Understanding / response generation


Backend
 ↓
Authorization
 ↓
Tool execution

This prevents natural-language generation from becoming the security
boundary.

Voice Pipeline

XYZ-AI provides a modular voice architecture.

Microphone
    ↓
Audio Upload
    ↓
/voice/process
    ↓
Faster-Whisper
    ↓
Transcribed Text
    +
Detected Language
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
Frontend
    ↓
Avatar / Audio Playback

The current STT provider uses Faster-Whisper.

Current development configuration:

WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8",
)

The provider interface is modular so the STT implementation can be
replaced without redesigning the rest of the voice pipeline.

Multilingual AI

XYZ-AI is designed for multilingual interaction.

The ML layer uses:

sentence-transformers/
paraphrase-multilingual-MiniLM-L12-v2

The model provides multilingual semantic embeddings for intent
understanding.

The pipeline is:

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

The architecture supports multilingual processing, while complete
end-to-end validation of every target language remains part of final
verification.

AI and ML Architecture

XYZ-AI uses multiple AI components rather than relying on one model
for every responsibility.

Semantic Intent Understanding

The system uses:

sentence-transformers/
paraphrase-multilingual-MiniLM-L12-v2

for multilingual semantic representation.

Intent Classification

A trained Joblib-based classifier is used for intent classification.

The classifier helps map natural-language input into supported backend
operations.

Example:

"Show my attendance"
        ↓
ATTENDANCE
"What's my timetable today?"
        ↓
TIMETABLE
"Mark Rahul absent"
        ↓
MARK_ATTENDANCE
Grok

Grok is used for natural-language response generation.

The OpenAI Python SDK is used as the client because xAI exposes an
OpenAI-compatible API.

The important architectural boundary is:

Grok
  ↓
Natural-language understanding / response generation


NOT


Grok
  ↓
Direct database access

Grok does not become the authorization layer.

Confirmation Workflow

State-changing operations use explicit confirmation.

Example:

User
 │
 │ "Mark Rahul absent today"
 ▼
Intent + Entity Extraction
 │
 ▼
Authorization
 │
 ▼
Create Pending Action
 │
 ▼
Ask Confirmation
 │
 ▼
"Please confirm..."
 │
 ▼
User
 │
 │ "Yes"
 ▼
Resolve Confirmation
 │
 ▼
Validate Action Ownership
 │
 ▼
Check Expiry
 │
 ▼
Consume Pending Action
 │
 ▼
Execute Authorized Tool
 │
 ▼
Attendance Updated

The confirmation architecture provides:

Explicit confirmation
Action ownership validation
Expiry
One-time consumption
Centralized execution
Protection against accidental state changes

The same execution path is intended to be reusable between text and
voice confirmation.

Human Escalation

XYZ-AI supports escalation to a human when the user needs assistance
beyond the assistant's supported capabilities.

Example:

User:
"I want to talk to my teacher."


Assistant:
"Would you like me to submit the request?"


User:
"Yes."


Assistant:
"Your request has been submitted."

The escalation operation is handled by a backend tool rather than
allowing the LLM to directly perform the operation.

Conversation Context

XYZ-AI maintains conversational context for follow-up interactions.

Example:

User:
"What is my attendance?"


Assistant:
"Your attendance is 88%."


User:
"What about last month?"


Assistant:
"Your attendance last month was..."

The system also supports correction-style interactions where context
from the previous request is relevant.

Security Architecture

Security is a core architectural property of XYZ-AI.

Authentication

JWT authentication identifies the current user.

Authorization

Authorization is enforced by backend services and tools.

The LLM cannot grant permissions.

Role Isolation

A user cannot simply say:

"I am the principal."

and gain principal permissions.

The backend uses the authenticated user's actual role.

Tool-Level Authorization

Before executing a backend operation:

Request
   ↓
Authenticated User
   ↓
Role
   ↓
Authorization
   ↓
Tool
Confirmation Security

Pending actions are protected through:

Ownership validation
Expiry
One-time consumption
Explicit confirmation
Security Testing

Security testing has included negative/runtime cases such as:

Unauthorized access
Unauthorized role-based operations
Student attempting to access school-wide analytics
Protected state-changing actions

A verified example:

Student
  ↓
School-wide analytics
  ↓
❌ Access denied

Security is enforced by the backend rather than by prompt instructions.

Technology Stack
Frontend
Technology	Purpose
Next.js	Web application
TypeScript	Type-safe frontend
Tailwind CSS	UI styling
Axios	API communication
Backend
Technology	Purpose
Python	Backend language
FastAPI	REST API
SQLAlchemy	ORM
PostgreSQL	Database
Alembic	Database migrations
JWT	Authentication
Pydantic	Request/response validation
AI / ML
Technology	Purpose
Sentence Transformers	Multilingual semantic embeddings
paraphrase-multilingual-MiniLM-L12-v2	Multilingual intent representation
Joblib	Intent classifier persistence
Grok	Natural-language response generation
OpenAI Python SDK	OpenAI-compatible xAI client
Voice
Technology	Purpose
Faster-Whisper	Speech-to-text
Windows/Edge TTS architecture	Text-to-speech
Browser MediaRecorder	Microphone recording
Web audio playback	Response audio
Project Structure

The project is organized into separate frontend and backend layers.

XYZ-AI/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── api/
│   │   │   ├── ai.py
│   │   │   ├── voice.py
│   │   │   └── ...
│   │   │
│   │   ├── conversation/
│   │   │   ├── context.py
│   │   │   ├── manager.py
│   │   │   └── ...
│   │   │
│   │   ├── core/
│   │   │   └── confirmation.py
│   │   │
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   └── ...
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   └── ...
│   │   │
│   │   ├── schemas/
│   │   │   └── ...
│   │   │
│   │   ├── security/
│   │   │   └── ...
│   │   │
│   │   ├── persona/
│   │   │   └── service.py
│   │   │
│   │   ├── tools/
│   │   │   ├── attendance.py
│   │   │   ├── escalation.py
│   │   │   └── ...
│   │   │
│   │   ├── voice/
│   │   │   ├── service.py
│   │   │   ├── stt/
│   │   │   └── tts/
│   │   │
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   │
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx
│   │   └── ...
│   │
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── .env.example
├── README.md
└── ...

The exact file tree may evolve as modules are refactored. The important
architectural boundary is that the frontend remains presentation-only
while backend services own authorization, tools, and business logic.

Core Modules
Authentication

Responsible for:

Login
JWT creation
Current-user resolution
Authentication dependencies
RBAC

Responsible for:

Role identification
Permission checks
Protected operations
Role-specific access

Roles:

STUDENT
PARENT
TEACHER
PRINCIPAL
Conversation Manager

Responsible for:

Conversation context
Previous interactions
Follow-up requests
Correction handling
Intent Classification

Responsible for mapping natural language into supported intents.

Entity Extraction

Responsible for identifying information required by tools.

For example:

"Mark Rahul absent today"

may produce:

student = Rahul
status  = absent
date    = today
Persona Service

Transforms backend results into responses appropriate for the current
user role and interaction context.

Attendance Tool

Handles authorized attendance operations.

Includes state-changing operations that require confirmation.

Escalation Tool

Handles requests to escalate an issue to a human such as a teacher.

Confirmation Service

Handles:

Pending actions
Confirmation
Ownership
Expiry
One-time consumption
Voice Service

Coordinates:

STT
 ↓
AI Handler
 ↓
TTS

The service uses provider interfaces so voice providers can be replaced
without rewriting the entire application.

Database and Data Layer

XYZ-AI uses:

PostgreSQL
     ↓
SQLAlchemy
     ↓
FastAPI

Database schema changes are managed through:

Alembic

The backend remains responsible for all database access.

The frontend never directly accesses PostgreSQL.

API Overview
Authentication

Authentication endpoints handle:

Login
Current user
JWT authentication
AI

The AI layer provides the main conversational orchestration.

Conceptually:

POST /ai/act

handles natural-language requests.

Confirmation

Confirmation is handled through the AI confirmation flow.

Conceptually:

POST /ai/confirm
Voice

Voice requests are sent through:

POST /voice/process

The endpoint accepts uploaded audio and runs:

Audio
 ↓
STT
 ↓
AI
 ↓
TTS

Generated audio is served through the voice audio endpoint.

Environment Variables

Create a local .env file.

Example:

DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:PORT/DATABASE


JWT_SECRET_KEY=your-secret-key


XAI_API_KEY=your-xai-api-key
XAI_MODEL=grok-4.1-fast

Never commit:

.env

Never expose:

XAI_API_KEY

to the frontend.

Use:

.env.example

for documenting required configuration without storing real secrets.

Example:

DATABASE_URL=
JWT_SECRET_KEY=
XAI_API_KEY=
XAI_MODEL=grok-4.1-fast
Local Development
Prerequisites

Install:

Python
Node.js
npm
PostgreSQL
Git

A Python virtual environment is recommended.

Backend Setup

From the project root:

cd backend

Create and activate a virtual environment if required:

Windows
python -m venv .venv
.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt
Backend Configuration

Create the backend environment configuration required by the application.

Make sure the following values are available:

DATABASE_URL=...
JWT_SECRET_KEY=...
XAI_API_KEY=...
XAI_MODEL=grok-4.1-fast
Database

Make sure PostgreSQL is running.

Run migrations:

alembic upgrade head

If the project requires database seeding, run the project's seed command
or seed script after migrations.

Running the Backend

Important:

The backend uses imports such as:

backend.app...

but the correct development command from inside the backend directory
is:

uvicorn app.main:app --reload

Do not run:

uvicorn backend.app.main:app --reload

from inside the backend directory.

The backend will normally be available at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
Running the Frontend

Open a second terminal.

From the project root:

cd frontend

Install dependencies:

npm install

Start development server:

npm run dev

The frontend is available at:

http://localhost:3000
Example Interactions
Student Attendance
User:
"What is my attendance?"


Assistant:
"Your current attendance is ..."
Student Timetable
User:
"What classes do I have today?"


Assistant:
"Your timetable for today is ..."
Parent Child Attendance
Parent:
"How is my child's attendance?"


Assistant:
"Your child's attendance is ..."
Teacher Attendance Action
Teacher:
"Mark Rahul absent today."


Assistant:
"Please confirm marking Rahul absent today."


Teacher:
"Yes."


Assistant:
"Rahul was marked absent today."
Human Escalation
User:
"I want to talk to my teacher."


Assistant:
"Would you like me to submit the request?"


User:
"Yes."


Assistant:
"Your request has been submitted."
Unauthorized Access
Student:
"Show me school-wide attendance analytics."


Backend:
❌ Forbidden

The assistant does not simply trust the user's natural-language claim
that they are authorized.

Security and Authorization

XYZ-AI follows a defense-in-depth approach.

Authentication
      ↓
Identity
      ↓
Role
      ↓
Authorization
      ↓
Tool Permission
      ↓
Confirmation (if required)
      ↓
Execution

The LLM is intentionally outside the authorization boundary.

This means:

Prompt:
"I am the principal."


        ↓


LLM
        ↓
does NOT grant access


        ↓


Backend
        ↓
checks authenticated role


        ↓
Authorization decision

This is one of the most important architectural decisions in the
project.

Testing

Testing should cover both normal and negative flows.

Authentication
Valid login
Invalid credentials
Expired/invalid JWT
RBAC

Test each role independently:

Student
Parent
Teacher
Principal

Verify that unauthorized users cannot access protected operations.

Confirmation

Test:

Action requested
     ↓
Confirmation requested
     ↓
Yes
     ↓
Action executes

Also test:

Rejected confirmation
Expired confirmation
Wrong user attempting confirmation
Reusing a consumed action
Voice

Test:

Microphone
 ↓
STT
 ↓
AI
 ↓
TTS
 ↓
Audio playback
Voice Confirmation

Important demo regression:

Teacher:
"Mark Rahul absent today."


Assistant:
"Please confirm..."


Teacher:
"Yes."


Expected:
Rahul is marked absent.
Voice Escalation
User:
"Connect me with my teacher."


Assistant:
"Would you like me to submit the request?"


User:
"Yes."


Expected:
Escalation request created.
Multilingual Voice

Validate:

Speech
 ↓
Correct language detection
 ↓
Correct transcription
 ↓
Correct intent
 ↓
Correct entities
 ↓
RBAC
 ↓
Correct tool
 ↓
Grok response
 ↓
TTS
 ↓
Audio
