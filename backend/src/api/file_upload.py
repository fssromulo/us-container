# Pip imports
from fastapi import APIRouter, Depends, HTTPException, Request, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import file_upload
from src.dependencies import auth

# from src.redis import limiter
from src.schemas.file_upload import GetS3Object


router = APIRouter(tags=["uploads"])


@router.post("/generate_presigned_get_url")
async def generate_presigned_get_url(
    s3_file_data: GetS3Object, request: Request, user: Auth0User = Depends(auth.get_user)
):
    # client_ip = request.client.host
    # ttl: int = 60  # time to live in seconds
    # limit_per_ttl: int = 5  # number of calls that will be allowed per {ttl} seconds

    # res = limiter(client_ip,limit_per_ttl, ttl)
    res = {"call": True, "ttl": 0}
    if res["call"]:
        return await file_upload.generate_presigned_get_url(s3_file_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"message": "call limit reached", "ttl": res["ttl"]}
        )
