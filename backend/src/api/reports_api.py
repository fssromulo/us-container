# Python imports
import os
from typing import List

# Pip imports
from fastapi import APIRouter, Depends
from loguru import logger

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import reports
from src.dependencies import auth
from src.schemas.reports import FilterObject, ReportsOut


STAGE = os.environ.get("STAGE", "dev")

router = APIRouter(tags=["reports"], dependencies=[Depends(auth.implicit_scheme)])


@router.get("/reports", response_model=List[ReportsOut])
async def get_reports(auth_user: Auth0User = Depends(auth.get_user)) -> List[ReportsOut]:
    return await reports.get_reports(auth_user)


@router.get("/reports/{id}", response_model=ReportsOut)
async def get_report(id: str, auth_user: Auth0User = Depends(auth.get_user)) -> ReportsOut:
    return await reports.get_report(id, auth_user)


@router.get("/reports/by_name/{name}", response_model=List[ReportsOut])
async def get_report_by_name(name: str, auth_user: Auth0User = Depends(auth.get_user)) -> List[ReportsOut]:
    return await reports.get_reports_by_name(name, auth_user)


@router.post("/reports/by_name/{name}")
async def run_reports_by_name(name: str, data: FilterObject, auth_user: Auth0User = Depends(auth.get_user)):
    if STAGE == 'dev':
        return await reports.run_reports_by_name_without_lambda(name, data, auth_user)
    else:
        return reports.run_reports_by_name(name, data, auth_user)


@router.post("/reports/retrieve_by_name/{name}")
async def retrieve_by_name(name: str, data: FilterObject):
    return await reports.retrieve_by_name(name, data)


@router.get("/reports/clear_by_name/{name}/{account_id}")
async def clear_by_name(name: str, account_id: str):
    return await reports.clear_by_name(name, account_id)


@router.get("/product_types")
async def get_product_types():
    return await reports.get_product_types()


@router.get("/vendors/{account_id}")
async def get_vendors(account_id: str):
    return await reports.get_vendors(account_id)


@router.post("/reports/close_commissions")
async def close_commissions(data: FilterObject, auth_user: Auth0User = Depends(auth.get_user)):
    await reports.run_reports_by_name_without_lambda("commissions_report_full", data, auth_user)
    data = await reports.retrieve_by_name("commissions_report_full", data)
    logger.info(data)

    await reports.save_commissions(data, auth_user.app_metadata["account_id"])
