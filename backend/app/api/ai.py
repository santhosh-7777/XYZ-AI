from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ML.inference.understand import understand

from backend.app.ai.parent_lookup import resolve_child
from backend.app.ai.student_lookup import resolve_student_id
from backend.app.tools.fees import FeeTool
from backend.app.tools.exam import ExamTool
from backend.app.tools.assignment import AssignmentTool
from backend.app.tools.academic_performance import AcademicPerformanceTool

from backend.app.conversation.context import ConversationContextStore
from backend.app.conversation.manager import ConversationManager

from backend.app.core.confirmation import ConfirmationService

from backend.app.db.session import get_db

from backend.app.models.role import Role
from backend.app.models.user import User

from backend.app.schemas.ai import (
    ActResponse,
    ConfirmationRequest,
    ConfirmationResponse,
    UnderstandRequest,
    UnderstandResponse,
)

from backend.app.security.deps import get_current_user

from backend.app.services.attendance import AttendanceService

from backend.app.tools.attendance import AttendanceTool
from backend.app.tools.escalation import EscalationTool
from backend.app.tools.timetable import TimetableTool

from backend.app.persona.service import PersonaService


router = APIRouter(prefix="/ai", tags=["AI"])


# =========================================================
# /ai/understand
# =========================================================


@router.post(
    "/understand",
    response_model=UnderstandResponse,
)
def understand_message(
    data: UnderstandRequest,
    user: User = Depends(get_current_user),
):
    """
    Understand a user message.

    This endpoint performs:

        text
          ↓
        intent classification
          ↓
        entity extraction

    No tool execution happens here.
    """

    result = understand(data.text)

    return UnderstandResponse(**result)


# =========================================================
# /ai/act
# =========================================================


@router.post(
    "/act",
    response_model=ActResponse,
)
def act_on_message(
    data: UnderstandRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Main AI orchestration endpoint.

    Flow:

        User message
              ↓
        Conversation handling
              ↓
        Intent + entity extraction
              ↓
        Application-layer RBAC
              ↓
        Tool OR confirmation
              ↓
        Persona response
              ↓
        Conversation state saved
    """

    text = data.text.strip()
    language = data.language.lower().strip()

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty.",
        )

    # ---------------------------------------------------------
    # ROLE
    # ---------------------------------------------------------

    role = db.get(Role, user.role_id)
    role_name = role.name.upper() if role else None

    if role_name is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role could not be determined.",
        )

    # ---------------------------------------------------------
    # CONVERSATION: CONFIRMATION DETECTION
    #
    # IMPORTANT:
    # We DO NOT automatically execute confirmation here.
    #
    # The actual state-changing action must still go through:
    #
    #     POST /ai/confirm
    #
    # This preserves the assignment's explicit confirmation
    # safety boundary.
    # ---------------------------------------------------------

    confirmation = ConversationManager.resolve_confirmation(
        user_id=user.id,
        text=text,
    )

    if confirmation is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Confirmation detected. "
                "Please confirm the pending action using "
                f"/ai/confirm with action_id "
                f"'{confirmation['action_id']}'."
            ),
        )

    # ---------------------------------------------------------
    # CONVERSATION: CORRECTION DETECTION
    #
    # Example:
    #
    #     "No, I meant my timetable."
    #
    # We allow the corrected message to continue through the
    # normal ML pipeline instead of executing the old intent.
    # ---------------------------------------------------------

    correction = ConversationManager.resolve_correction(
        user_id=user.id,
        text=text,
    )

    # ---------------------------------------------------------
    # CONVERSATION: FOLLOW-UP RESOLUTION
    #
    # Example:
    #
    # Previous:
    #     "How much attendance does my child have?"
    #
    # Follow-up:
    #     "How about last month?"
    #
    # The ConversationManager recovers:
    #     previous intent
    #     previous entities
    #     previous student context
    #
    # We automatically map supported read-only follow-ups.
    # ---------------------------------------------------------

    follow_up = None

    if correction is None:
        follow_up = ConversationManager.resolve_follow_up(
            user_id=user.id,
            text=text,
        )

    # ---------------------------------------------------------
    # CONTEXT REQUIRED
    # ---------------------------------------------------------

    if (
        follow_up is not None
        and follow_up["type"] == "CONTEXT_REQUIRED"
    ):
        return ActResponse(
            intent="CONTEXT_REQUIRED",
            entities={},
            result={
                "message": follow_up["message"],
            },
        )

    # ---------------------------------------------------------
    # INTENT + ENTITIES
    # ---------------------------------------------------------

    if (
        follow_up is not None
        and follow_up["type"] == "FOLLOW_UP"
    ):
        previous_intent = follow_up["previous_intent"]
        entities = follow_up["entities"]

        # -----------------------------------------------------
        # Attendance follow-up:
        #
        # OWN_ATTENDANCE
        # CHILD_ATTENDANCE
        # ATTENDANCE_HISTORY
        #
        # + last month
        #
        #       ↓
        #
        # ATTENDANCE_HISTORY
        # -----------------------------------------------------

        if (
            previous_intent
            in {
                "OWN_ATTENDANCE",
                "CHILD_ATTENDANCE",
                "ATTENDANCE_HISTORY",
            }
            and entities.get("period") == "last_month"
        ):
            intent = "ATTENDANCE_HISTORY"

        # -----------------------------------------------------
        # Simple contextual follow-up:
        #
        # "Can you check it?"
        #
        # Reuse only read-only intents.
        #
        # Never automatically reuse a state-changing intent.
        # -----------------------------------------------------

        elif previous_intent in {
            "OWN_ATTENDANCE",
            "CHILD_ATTENDANCE",
            "ATTENDANCE_HISTORY",
            "TIMETABLE",
        }:
            intent = previous_intent

        else:
            # The follow-up cannot be safely mapped to a
            # supported action. Let the normal ML pipeline
            # classify the message instead.
            result = understand(text)

            intent = result["intent"]
            entities = result["entities"]

    else:
        # -----------------------------------------------------
        # NORMAL ML UNDERSTANDING
        # -----------------------------------------------------

        result = understand(text)

        intent = result["intent"]
        entities = result["entities"]

    # ---------------------------------------------------------
    # CORRECTION SAFETY
    #
    # The new ML classification is authoritative for the
    # corrected request.
    #
    # We do NOT reuse the previous intent automatically.
    # ---------------------------------------------------------

    if correction is not None:
        # The normal ML classification above is authoritative.
        pass

    # =========================================================
    # GREETING
    #
    # Human-like chat behavior.
    #
    # This is presentation/conversation behavior only.
    # No tool is called.
    # =========================================================

    if intent == "GREETING":

        if role_name == "STUDENT":
            message = (
                "Hi! I'm your academic assistant. "
                "How can I help you today?"
            )

        elif role_name == "PARENT":
            message = (
                "Hello! I'm here to help you with your "
                "child's school information. How can I help?"
            )

        elif role_name == "TEACHER":
            message = (
                "Hello! I'm your teaching assistant. "
                "What would you like me to help with?"
            )

        elif role_name == "PRINCIPAL":
            message = (
                "Hello! I'm your school management assistant. "
                "How may I assist you today?"
            )

        else:
            message = (
                "Hello! How can I help you today?"
            )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool=None,
            entities=entities,
            result={
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                "message": message,
            },
        )

    # =========================================================
    # GENERAL HELP
    #
    # This explains what XYZ AI can currently help with.
    # It does not execute a tool.
    # =========================================================

    if intent == "GENERAL_HELP":

        message = (
            "I can help you with school-related information such as "
            "attendance, attendance history, timetables, exams, "
            "assignments, academic performance, fees, and other "
            "academic requests available to your role. "
            "You can also ask me to connect you with a teacher "
            "or school management when human assistance is needed."
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool=None,
            entities=entities,
            result={
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                "message": message,
            },
        )

    # =========================================================
    # OUT OF SCOPE
    #
    # Security boundary:
    # Do not execute tools for unsupported requests.
    # =========================================================

    if intent == "OUT_OF_SCOPE":

        message = (
            "I'm sorry, but I can only help with school-related "
            "requests and services available through XYZ AI."
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="blocked",
            entities=entities,
            result={
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                "status": "BLOCKED",
                "message": message,
            },
        )

    # =========================================================
    # OWN ATTENDANCE
    # =========================================================

    if intent == "OWN_ATTENDANCE":

        data_out = AttendanceTool.execute(user.id)

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_my_attendance",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

    # =========================================================
    # CHILD ATTENDANCE
    # =========================================================

    if intent == "CHILD_ATTENDANCE":

        if role_name not in {
            "PARENT",
            "TEACHER",
            "PRINCIPAL",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Your role is not authorized to view "
                    "child attendance."
                ),
            )

        child = resolve_child(user.id)

        if child is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No child record linked to this "
                    "user account."
                ),
            )

        # -----------------------------------------------------
        # Preserve resolved child in conversation context.
        #
        # Important for:
        #
        # "How about last month?"
        # -----------------------------------------------------

        entities = {
            **entities,
            "student_id": child["student_id"],
            "student_name": child["student_name"],
        }

        data_out = AttendanceTool.get_child_attendance(
            parent_user_id=user.id,
            child_id=child["student_id"],
        )

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_child_attendance",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

    # =========================================================
    # ATTENDANCE HISTORY
    # =========================================================

    if intent == "ATTENDANCE_HISTORY":

        # -----------------------------------------------------
        # STUDENT
        #
        # Authenticated student's own ID is authoritative.
        # -----------------------------------------------------

        if role_name == "STUDENT":
            student_id = user.id

        else:
            # -------------------------------------------------
            # Parent / teacher / principal:
            #
            # For follow-up requests, student_id should come
            # from the previously authorized conversation
            # context.
            # -------------------------------------------------

            student_id = entities.get("student_id")

        if student_id is None:
            return ActResponse(
                intent="CONTEXT_REQUIRED",
                entities=entities,
                result={
                    "message": (
                        "I need to know which student's "
                        "attendance history you want."
                    ),
                },
            )

        period = entities.get("period")

        if period is None:
            return ActResponse(
                intent="CLARIFICATION_REQUIRED",
                entities=entities,
                result={
                    "message": (
                        "Which attendance period would "
                        "you like me to check?"
                    ),
                },
            )

        # -----------------------------------------------------
        # Parent safety:
        #
        # Ensure the requested student is still the
        # authenticated parent's authorized child.
        # -----------------------------------------------------

        if role_name == "PARENT":

            child = resolve_child(user.id)

            if child is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "No child record linked to this "
                        "user account."
                    ),
                )

            if student_id != child["student_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "You are not authorized to view "
                        "this student's attendance history."
                    ),
                )

        data_out = AttendanceTool.get_attendance_history(
            student_id=student_id,
            period=period,
        )

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_attendance_history",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

    # =========================================================
    # TIMETABLE
    #
    # Read-only school information.
    #
    # All currently supported roles can access their timetable.
    # =========================================================

    if intent == "TIMETABLE":

        if role_name not in {
            "STUDENT",
            "PARENT",
            "TEACHER",
            "PRINCIPAL",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Your role is not authorized "
                    "to view the timetable."
                ),
            )

        data_out = TimetableTool.execute(user.id)

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_timetable",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

    # =========================================================
    # MARK ATTENDANCE
    #
    # Teacher only.
    #
    # IMPORTANT:
    # RBAC happens BEFORE creating the pending action.
    #
    # Actual mutation happens ONLY inside /ai/confirm.
    # =========================================================

    if intent == "MARK_ATTENDANCE":

        if role_name != "TEACHER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can mark attendance.",
            )

        student_id = resolve_student_id(
            entities.get("student_name")
        )

        if student_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unknown student: "
                    f"{entities.get('student_name')}"
                ),
            )

        if entities.get("date") is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing date in request.",
            )

        if entities.get("status") is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing attendance status in request.",
            )

        # -----------------------------------------------------
        # CREATE PENDING ACTION
        # -----------------------------------------------------

        pending = ConfirmationService.create_pending_action(
            user_id=user.id,
            intent=intent,
            tool="mark_attendance",
            arguments={
                "student_id": student_id,
                "student_name": entities["student_name"],
                "date": entities["date"],
                "status": entities["status"],
            },
        )

        confirmation_result = {
            "status": "CONFIRMATION_REQUIRED",
            "action_id": pending.action_id,
            "message": (
                f"Please confirm marking "
                f"{entities['student_name']} "
                f"{entities['status'].lower()} "
                f"on {entities['date']}."
            ),
            "expires_at": pending.expires_at.isoformat(),
        }

        # -----------------------------------------------------
        # SAVE CONVERSATION STATE
        # -----------------------------------------------------

        ConversationContextStore.update(
            user_id=user.id,
            intent=intent,
            tool="mark_attendance",
            entities=entities,
            result=confirmation_result,
            pending_action_id=pending.action_id,
            pending_action_intent=intent,
        )

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=confirmation_result,
            language=language,
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **confirmation_result,
                "message": message,
            },
        )

    # =========================================================
    # SCHOOL ANALYTICS
    # =========================================================

    if intent == "SCHOOL_ANALYTICS":

        if role_name != "PRINCIPAL":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only principals can view "
                    "school-wide analytics."
                ),
            )

        data_out = AttendanceService.get_school_analytics()

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_school_analytics",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

    # =========================================================
    # ESCALATION
    #
    # State-changing action.
    #
    # /ai/act:
    #     creates CONFIRMATION_REQUIRED
    #
    # /ai/confirm:
    #     performs actual submission
    # =========================================================

    if intent == "ESCALATION":

        if role_name not in {
            "STUDENT",
            "PARENT",
            "TEACHER",
            "PRINCIPAL",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Your role is not authorized "
                    "to create an escalation request."
                ),
            )

        pending = ConfirmationService.create_pending_action(
            user_id=user.id,
            intent=intent,
            tool="create_escalation_request",
            arguments={
                "target": "teacher",
            },
        )

        confirmation_result = {
            "status": "CONFIRMATION_REQUIRED",
            "action_id": pending.action_id,
            "message": (
                "I can submit a request to speak with "
                "your teacher. Would you like me to "
                "submit the request?"
            ),
            "expires_at": pending.expires_at.isoformat(),
        }

        ConversationContextStore.update(
            user_id=user.id,
            intent=intent,
            tool="create_escalation_request",
            entities=entities,
            result=confirmation_result,
            pending_action_id=pending.action_id,
            pending_action_intent=intent,
        )

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=confirmation_result,
            language=language,
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **confirmation_result,
                "message": message,
            },
        )

        # =========================================================
    # FEES
    #
    # Read-only financial information.
    #
    # Only PARENT and PRINCIPAL may access fee information,
    # per the RBAC policy.
    # =========================================================

    if intent == "FEES":

        if role_name not in {
            "PARENT",
            "PRINCIPAL",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Your role is not authorized "
                    "to view fee information."
                ),
            )

        data_out = FeeTool.execute(user.id)

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_fees",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

    # =========================================================
    # EXAM
    #
    # Read-only academic information.
    #
    # All supported roles may access exam information.
    # =========================================================

    if intent == "EXAM":

        if role_name not in {
            "STUDENT",
            "PARENT",
            "TEACHER",
            "PRINCIPAL",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Your role is not authorized "
                    "to view exam information."
                ),
            )

        data_out = ExamTool.execute(user.id)

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_exams",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )


    # =========================================================
    # ASSIGNMENT
    #
    # Read-only academic information.
    #
    # All supported roles may access assignment information.
    # =========================================================

    if intent == "ASSIGNMENT":

        if role_name not in {
            "STUDENT",
            "PARENT",
            "TEACHER",
            "PRINCIPAL",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Your role is not authorized "
                    "to view assignment information."
                ),
            )

        data_out = AssignmentTool.execute(user.id)

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_assignments",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )


    # =========================================================
    # ACADEMIC PERFORMANCE
    #
    # Read-only academic information.
    #
    # All supported roles may access academic performance.
    # =========================================================

    if intent == "ACADEMIC_PERFORMANCE":

        if role_name not in {
            "STUDENT",
            "PARENT",
            "TEACHER",
            "PRINCIPAL",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Your role is not authorized "
                    "to view academic performance."
                ),
            )

        data_out = AcademicPerformanceTool.execute(user.id)

        message = PersonaService.format_response(
            role=role_name,
            intent=intent,
            result=data_out,
            language=language,
        )

        ConversationManager.save_result(
            user_id=user.id,
            intent=intent,
            tool="get_academic_performance",
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )

        return ActResponse(
            intent=intent,
            entities=entities,
            result={
                **data_out,
                "message": message,
            },
        )


    # =========================================================
    # NOT YET IMPLEMENTED
    #
    # We intentionally do NOT pretend unsupported services
    # exist yet.
    #
    # These will be added as independent service + tool
    # modules in subsequent phases:
    #
    #     ANNOUNCEMENT
    #     LEAVE
    #
    # =========================================================

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            f"Intent '{intent}' is recognized "
            "but not yet actionable."
        ),
    )


# =========================================================
# /ai/confirm
# =========================================================


@router.post(
    "/confirm",
    response_model=ConfirmationResponse,
)
def confirm_action(
    data: ConfirmationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Confirm and execute a previously approved
    state-changing action.

    ConfirmationService guarantees:

    - action belongs to authenticated user
    - action has not expired
    - action can only be consumed once
    """

    action = ConfirmationService.consume_pending_action(
        action_id=data.action_id,
        user_id=user.id,
    )

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Confirmation is invalid, expired, "
                "or already used."
            ),
        )

    # =========================================================
    # MARK ATTENDANCE
    # =========================================================

    if action.tool == "mark_attendance":

        result = AttendanceTool.mark_attendance(
            teacher_user_id=user.id,
            student_id=action.arguments["student_id"],
            student_name=action.arguments["student_name"],
            date=action.arguments["date"],
            status=action.arguments["status"],
        )

        ConversationManager.clear_pending_action(
            user.id
        )

        return ConfirmationResponse(
            confirmed=True,
            action_id=action.action_id,
            intent=action.intent,
            result=result,
        )

   
    # =========================================================
    # ESCALATION
    # =========================================================

    if action.tool == "create_escalation_request":

        result = EscalationTool.create_request(
            user_id=user.id,
            target=action.arguments["target"],
        )

        role = db.get(Role, user.role_id)
        role_name = role.name.upper() if role else "STUDENT"

        message = PersonaService.format_response(
            role=role_name,
            intent=action.intent,
            result=result,
            language="en",
        )

        ConversationManager.clear_pending_action(
            user.id
        )

        return ConfirmationResponse(
            confirmed=True,
            action_id=action.action_id,
            intent=action.intent,
            result={
                **result,
                "message": message,
            },
        )

    # =========================================================
    # UNSUPPORTED CONFIRMATION TOOL
    # =========================================================

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"Unsupported confirmation tool: "
            f"{action.tool}"
        ),
    )