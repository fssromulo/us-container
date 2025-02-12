# Python imports
import os

# Pip imports
import phonenumbers
from loguru import logger
from mailersend import sms_sending
from twilio.rest import Client

# Internal imports
from src.crud.account_crud import account_crud


def validatePhoneNumber(phone):
    try:
        num = phonenumbers.parse(phone, "US")
        if not phonenumbers.is_possible_number(num) or not (phonenumbers.is_valid_number(num)):
            return False
        else:
            return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return False


async def send_sms_invite(toNumber, account_id):
    if os.environ.get("STAGE", "dev"):
        logger.info("not sending sms invite in dev")
        return
    if not toNumber:
        return False
    account_sid = ""
    auth_token = ""

    account = await account_crud.get_one(account_id)
    attributes = account.cms_attributes
    body = attributes["delivered_sms_text"]

    client = Client(account_sid, auth_token)
    try:
        fromNumber = "+"
        message = client.messages.create(validatePhoneNumber(toNumber), body=body, from_=fromNumber)
        message = client.messages(message.sid).fetch()
        if message.status == "undelivered":
            return False
    except Exception as e:
        logger.info(e)
        return False
    return True


def send_sms_mailer_send(toNumber, message, api_key):
    if not toNumber:
        return False
    if validatePhoneNumber(toNumber) is False:
        return False

    mailer = sms_sending.NewSmsSending(api_key)

    # Number belonging to your account in E164 format
    number_from = "+18332552485"

    # You can add up to 50 recipient numbers
    numbers_to = [
        toNumber,
    ]

    mailer.send_sms(number_from, numbers_to, message)
