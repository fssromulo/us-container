# Pip imports
import requests
from loguru import logger


def post_to_webhook(
    phone: str,
    email: str,
    first_name: str,
    last_name: str,
    order_id: str,
    created_at: str,
    referral_source: str,
    campaign_url: str,
):
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IkhKUHdNUG5YSHVJOHl4d0hGQ1BaIiwiY29tcGFueV9pZCI6ImJLbXlTd3BrNllJZTNQVXdLUkdNIiwidmVyc2lvbiI6MSwiaWF0IjoxNjc1MTgyMzY4MzA2LCJzdWIiOiJ1c2VyX2lkIn0.6C47imkMYjUDDwNf8kWpT0N0fZCxAO00mVZC8s1_Yto"
    url = "https://services.leadconnectorhq.com/hooks/HJPwMPnXHuI8yxwHFCPZ/webhook-trigger/03ee98f2-0063-4ed9-acf9-933fdf0004ce"

    body = {
        "phone": phone,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "order_id": order_id,
        "created_at": created_at,
        "referral_source": referral_source,
        "campaign_url": campaign_url,
    }

    logger.info(body)

    result = requests.post(
        url,
        json=body,
        headers={'Authorization': api_key},
    )

    logger.info(result.status_code)
    logger.info(result.text)
    logger.info(result.json())
    # id like to see the body I sent to this endpoint
    logger.info("REQUEST BODY")
    logger.info(result.request.body)
    return result


def long_horn_post_to_webhook(data):
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6ImxEZWYxM3FLR3Z1WjBoR3E1MnVMIiwiY29tcGFueV9pZCI6Ijl2cjl3aHd4RllTM2lXQ2FEcGp0IiwidmVyc2lvbiI6MSwiaWF0IjoxNjk5MjExODI4MzYyLCJzdWIiOiJ1c2VyX2lkIn0.D0WssyhRmkcsyyfSPEybIy66gc7Ds90ZslDv77EzYhg"
    url = "https://backend.leadconnectorhq.com/hooks/lDef13qKGvuZ0hGq52uL/webhook-trigger/ad88fa72-ed9a-4ac2-b3a2-171fb719676c"

    result = requests.post(
        url,
        json=data,
        headers={'Authorization': api_key},
    )

    logger.info(result.status_code)
    logger.info(result.text)
    logger.info(result.json())
    # id like to see the body I sent to this endpoint
    logger.info("REQUEST BODY")
    logger.info(result.request.body)
    return result
