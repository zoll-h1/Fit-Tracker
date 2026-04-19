from fastapi import Request

ADMIN_PASSWORD = "admin123"
ADMIN_COOKIE_NAME = "admin_session"
ADMIN_SESSION_TOKEN = "fittracker_admin_secret_2024"


def get_admin_session(request: Request):
    token = request.cookies.get(ADMIN_COOKIE_NAME)
    if token != ADMIN_SESSION_TOKEN:
        return None
    return True


def require_admin_session(request: Request):
    if not get_admin_session(request):
        from fastapi import HTTPException
        from fastapi.responses import RedirectResponse
        raise HTTPException(status_code=302, headers={"Location": "/admin/login"})
    return True
