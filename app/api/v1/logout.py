from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/logout")
async def logout(response: Response):
    redirect = RedirectResponse(url="/login", status_code=303)
    redirect.delete_cookie("access_token")
    return redirect