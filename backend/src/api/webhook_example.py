# Python imports
from typing import Any, Dict

# Pip imports
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError


router = APIRouter(
    tags=["webhooks"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# Define the request model
class Webhook(BaseModel):
    instance: Any
    instance_id: str
    object: str
    operation: str


@router.get("/webhook")
async def get_all_webhook():
    logger.info("get_all_webhook")
    return []


@router.post("/webhook", status_code=status.HTTP_201_CREATED)
async def create_webhook(webhook: Webhook):
    logger.info("create_webhook")
    logger.info(webhook)
    return webhook


@router.patch(
    "/webhook/{webhook_id}",
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def update_webhook(webhook_id: str):
    logger.info("update_webhook")
    logger.info(webhook_id)
    return {}


@router.delete("/webhook/{webhook_id}", responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}})
async def delete_webhook(webhook_id: str):
    logger.info("delete_webhook")
    logger.info(webhook_id)
    return {}
