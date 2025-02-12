# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.crud.payment_method_crud import payment_method_crud
from src.dependencies import auth
from src.schemas.payment_method import PaymentMethodInSchema, PaymentMethodOutSchema, CreateUpdatePaymentMethodZone
from src.schemas.token import Status


router = APIRouter(
    tags=["payment_methods"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/payment_methods", response_model=list[PaymentMethodOutSchema])
async def get_logistics_zones(user: Auth0User = Depends(auth.get_user)):
    return await payment_method_crud.get_all(account_id=user.app_metadata['account_id'])


@router.patch("/payment_methods/{id}")
async def update_logistics_zones(id: str, dataReq: CreateUpdatePaymentMethodZone, user: Auth0User = Depends(auth.get_user)):
    reqDict = dataReq.dict()
    reqDict['account_id'] = user.app_metadata['account_id']
    return await payment_method_crud.update(user.app_metadata['account_id'], id, PaymentMethodInSchema(**reqDict))


@router.post("/payment_methods/{id}")
async def create_logistics_zones(id: str, dataReq: CreateUpdatePaymentMethodZone, user: Auth0User = Depends(auth.get_user)):
    reqDict = dataReq.dict()
    reqDict['account_id'] = user.app_metadata['account_id']
    await payment_method_crud.create(PaymentMethodInSchema(**reqDict))
    return Status(message="Successfully created logistiscs zone")


@router.delete("/payment_methods/{id}")
async def delete_logistics_zones(id: str, user: Auth0User = Depends(auth.get_user)):
    await payment_method_crud.delete_one(user.app_metadata['account_id'], id)
    return Status(message="Successfully deleted logistics zone.")
