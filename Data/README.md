# XYZ AI — Complete Data & Evaluation Package v2

This package covers the data/contracts needed by the scalable XYZ AI architecture.

## What is included

### 1. ML
- `intent_ml_master.csv`
- `intent_ml_train.csv`
- `intent_ml_validation.csv`
- `intent_ml_test.csv`
- `hard_negative_pairs.csv`

The classifier input should be ONLY `text` (and optionally language metadata if the
model design explicitly uses it). Do not leak role/tool/permission columns into training.

### 2. Entity extraction
- `entity_catalog.csv`
- `entity_extraction_gold.csv`

### 3. RBAC/security
- `rbac_policy.csv`
- `prompt_injection_security_cases.csv`

Authorization must remain application/tool-side. The LLM must never decide its own role.

### 4. Conversation
- `conversation_context_cases.csv`
- `action_confirmation_cases.csv`

Covers follow-ups, corrections, ambiguity, missing entities, confirmation and escalation.

### 5. Personas
- `persona_catalog.csv`

### 6. Tools/mock APIs
- `tool_catalog.csv`
- `mock_api_contract_tests.csv`

### 7. Multilingual/voice evaluation
- `multilingual_code_mixed_voice_eval.csv`

Includes native-script, code-mixed, conversational and voice-style test cases.

### 8. Architecture completeness
- `assessment_coverage_matrix.csv`

This maps every major requirement in the assessment to a data set or contract.

## Important
The 880 intent utterances are a development seed corpus, not a final human-curated
production corpus. Native-speaker review and additional genuine utterances are still
required. The test set should eventually be locked and reviewed independently.

The avatar itself does not require a separate language dataset; it is a presentation
layer driven by XYZ AI's response/audio state.
