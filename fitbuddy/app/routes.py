from pathlib import Path
import os

from dotenv import load_dotenv

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .database import (
    delete_user,
    get_all_users_with_plans,
    get_latest_plan,
    get_user,
    init_db,
    save_plan,
    save_user,
    update_plan,
)

from .gemini_generator import generate_workout_gemini

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)

from .updated_plan import update_workout_plan

from .schemas import (
    FeedbackRequest,
    UserInput,
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------
# Templates
# --------------------------------------------------

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# --------------------------------------------------
# Router
# --------------------------------------------------

router = APIRouter()


# --------------------------------------------------
# Admin
# --------------------------------------------------

ADMIN_TOKEN = os.getenv(
    "ADMIN_TOKEN",
    "fitbuddy-admin",
)


# --------------------------------------------------
# Home
# --------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    init_db()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None,
        },
    )


# --------------------------------------------------
# Generate workout
# --------------------------------------------------

@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):

    try:

        user_data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Please check your input: {exc}"
            },
            status_code=400,
        )

    user = save_user(
        user_data.model_dump()
    )

    workout_plan = generate_workout_gemini(
        user
    )

    nutrition_tip = (
        generate_nutrition_tip_with_flash(
            user.goal
        )
    )

    plan = save_plan(
        user_id=user.user_id,
        original_plan=workout_plan,
        nutrition_tip=nutrition_tip,
    )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": plan,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "message": None,
        },
    )


# --------------------------------------------------
# Feedback
# --------------------------------------------------

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):

    try:

        feedback_data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Invalid feedback: {exc}"
            },
            status_code=400,
        )

    user = get_user(
        feedback_data.user_id
    )

    if user is None:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "User ID was not found."
            },
            status_code=404,
        )

    plan = get_latest_plan(
        feedback_data.user_id
    )

    if plan is None:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "No workout plan was found."
            },
            status_code=404,
        )

    current_plan = (
        plan.updated_plan
        if plan.updated_plan
        else plan.original_plan
    )

    revised_plan = update_workout_plan(
        user=user,
        original_plan=current_plan,
        feedback=feedback_data.feedback,
    )

    nutrition_tip = (
        generate_nutrition_tip_with_flash(
            user.goal
        )
    )

    updated_plan = update_plan(
        plan_id=plan.id,
        updated_plan=revised_plan,
        feedback=feedback_data.feedback,
        nutrition_tip=nutrition_tip,
    )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": updated_plan or plan,
            "workout_plan": revised_plan,
            "nutrition_tip": nutrition_tip,
            "message": "Your workout plan was updated successfully.",
        },
    )


# --------------------------------------------------
# Admin dashboard
# --------------------------------------------------

@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    token: str | None = None,
):

    authorized = token == ADMIN_TOKEN

    users_with_plans = []

    if authorized:
        users_with_plans = get_all_users_with_plans()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "authorized": authorized,
            "users_with_plans": users_with_plans,
            "token": token or "",
            "error": None,
        },
    )


# --------------------------------------------------
# Delete user
# --------------------------------------------------

@router.post(
    "/admin/delete",
    response_class=HTMLResponse,
)
def admin_delete_user(
    request: Request,
    token: str = Form(...),
    user_id: str = Form(...),
):

    if token != ADMIN_TOKEN:

        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={
                "authorized": False,
                "users_with_plans": [],
                "token": "",
                "error": "Invalid admin token.",
            },
            status_code=401,
        )

    delete_user(user_id)

    return RedirectResponse(
        url=f"/view-all-users?token={token}",
        status_code=303,
    )


# --------------------------------------------------
# API
# --------------------------------------------------

@router.get("/api/users")
def api_users(
    token: str | None = None,
):

    if token != ADMIN_TOKEN:

        return {
            "error": "Unauthorized"
        }

    users_with_plans = (
        get_all_users_with_plans()
    )

    result = []

    for user, plan in users_with_plans:

        result.append(
            {
                "user_id": user.user_id,
                "username": user.username,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "created_at": user.created_at.isoformat(),
                "latest_plan": (
                    {
                        "id": plan.id,
                        "original_plan": plan.original_plan,
                        "updated_plan": plan.updated_plan,
                        "feedback": plan.feedback,
                        "nutrition_tip": plan.nutrition_tip,
                    }
                    if plan
                    else None
                ),
            }
        )

    return {
        "users": result
    }