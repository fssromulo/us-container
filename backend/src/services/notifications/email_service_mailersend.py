# Python imports
import os
from datetime import datetime
from typing import Any, Dict, List

# Pip imports
# import boto3
import requests
from jinja2 import DictLoader, Environment, select_autoescape
from loguru import logger
from mailersend import emails
from pydantic import BaseModel
from pytz import timezone

# Internal imports
from src.config import settings
from src.controllers import orders as order_controller
from src.crud.account_crud import account_crud
from src.database.models.account import Account  # noqa: E402
from src.database.models.orders.order import Order
from src.database.models.pricing.region import Region
from src.schemas.customer import CustomerDetail
from src.schemas.orders import OrderDetail, OrderOut, OrderTransaction


TIMEOUT = 5

STAGE = os.environ.get('STAGE', 'dev')
EMAIL_TO = os.environ.get('EMAIL_TO', None)
MAILERSEND_API_KEY = os.environ.get('MAILERSEND_API_KEY', None)

ENVIRONMENT: str = settings.STAGE


class EmptyAccount:
    cms_attributes = {}


class ChargedRental(BaseModel):
    date: str = '1970-01-01'
    amount: str = '0.00'
    display_order_id: str = 'default-id'
    is_approved: bool = False


class Data(BaseModel):
    company_name: str = 'Default Company'
    charged_rentals: List[ChargedRental] = []
    total_rentals_charged: str = '0'


class SendChargedRental(BaseModel):
    email: str = 'default@email.com'
    data: Data = Data()


def validate_email(email: str) -> bool:
    response = requests.get(
        f"{settings.EMAIL_BASE_URI}/v4/address/validate",
        auth=("api", settings.EMAIL_AUTH_TOKEN),
        params={"address": email},
    )
    if response.ok:
        return response.json().get("result") == "deliverable"

    return False


def post_email_message(context: Dict[str, str] = None, account=None) -> bool:
    if not account:
        account = EmptyAccount()

    if EMAIL_TO:
        context["email_to"] = [
            {
                "name": "Test User",
                "email": settings.EMAIL_TO,
            }
        ]

    if ENVIRONMENT.lower() == "dev":
        context["email_to"] = [
            {
                "name": "Test User",
                "email": settings.EMAIL_TO,
            }
        ]

        context["personalization"][0]["email"] = settings.EMAIL_TO
    mail_body = {}
    context["personalization"][0]['data']["account_url"] = account.cms_attributes.get("mailer_send_defaults", {}).get(
        "company_url", ""
    )
    if account.cms_attributes.get("mailer_send_defaults", {}).get("facebook", "") != "":
        context["personalization"][0]['data']["fb"] = "Facebook"
        context["personalization"][0]['data']["fb"] = account.cms_attributes.get("mailer_send_defaults", {}).get(
            "facebook", ""
        )
    if account.cms_attributes.get("mailer_send_defaults", {}).get("google", "") != "":
        context["personalization"][0]['data']["google"] = "Google"
        context["personalization"][0]['data']["g_url"] = account.cms_attributes.get("mailer_send_defaults", {}).get(
            "google", ""
        )
    if account.cms_attributes.get("mailer_send_defaults", {}).get("linkedId", "") != "":
        context["personalization"][0]['data']["linkedin"] = "LinkedIn"
        context["personalization"][0]['data']["linkedin_url"] = account.cms_attributes.get(
            "mailer_send_defaults", {}
        ).get("linkedId", "")
    if account.cms_attributes.get("terms_and_conditions_link", "") != "":
        context["personalization"][0]['data']["terms"] = "Terms & Conditions"
        context["personalization"][0]['data']["terms_url"] = account.cms_attributes.get("terms_and_conditions_link", "")

    if "email_from" not in context or context["email_from"] is None or context.get("email_from").get("email") == "":
        context["email_from"] = {
            "name": account.name,
            "email": account.cms_attributes.get("emails", {}).get(
                "quote_contact_email",
                account.integrations.get("mailer_send", {}).get('default_sender', "tanner@mobilestoragetech.com"),
            ),
        }

    if "reply_to" not in context or context["reply_to"] is None or context.get("reply_to").get("email") == "":
        context["reply_to"] = {
            "name": account.name,
            "email": account.cms_attributes.get("emails", {}).get(
                "quote_contact_email", account.cms_attributes.get("mailer_send", {}).get('default_reply_to')
            ),
        }

    if STAGE != 'dev':
        context["cc_recipients"] = [
            {
                "email": account.cms_attributes.get("emails", {}).get("secondary_internal_email", ""),
            }
        ]

    if ENVIRONMENT.lower() != "dev":
        context["cc_recipients"] = [
            {
                "email": account.cms_attributes.get("emails", {}).get("secondary_internal_email", ""),
            }
        ]
    logger.info(context)
    mailer = emails.NewEmail(account.integrations.get("mailer_send", {}).get("api_key", ""))
    mailer.set_mail_from(context.get("email_from"), mail_body)
    mailer.set_mail_to(context.get("email_to"), mail_body)
    # The cc must me an array, so if we dont have them, then we need to not include them
    if STAGE != 'dev':
        if context["cc_recipients"][0]['email'] != '':
            mailer.set_cc_recipients(context.get("cc_recipients"), mail_body)
    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("sales", None)
    mailer.set_subject(context.get('subject'), mail_body)
    if context.get("body"):
        mailer.set_html_content(context['body'], mail_body)
    else:
        mailer.set_template(
            context.get("template", template_defaults.get("template_id") if template_defaults else ""), mail_body
        )

        if hasattr(mailer, "set_advanced_personalization"):
            mailer.set_advanced_personalization(context.get("personalization"), mail_body)
        else:
            mailer.set_personalization(context.get("personalization"), mail_body)

    mailer.set_reply_to(context.get("reply_to"), mail_body)

    try:
        resp: str = mailer.send(mail_body)
        # example error message: "422 {"message":"The cc must be an array.","errors":{"cc":["The cc must be an array."]}}"
        logger.info(resp)
        resp_code: str = resp[:3]
        resp_code_type: int = int(resp_code[0])
        if resp_code_type != 2:
            raise Exception(resp)
        logger.info("Email sent")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")

        return False


def send_submitted_application_email(customer_order: OrderOut, account: Account):
    if account.name.startswith("USA Containers"):
        order_link = f"https://quote.usacontainers.co/#/{customer_order.id}"
    else:
        links = account.cms_attributes.get("links", {})
        order_link = f"{links.get('invoice_email_link', '')}{customer_order.id}"
    cms_attrs = account.cms_attributes
    company_name = cms_attrs.get("account_name", "")

    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": account.cms_attributes.get("emails", {}).get("rental_internal_email"),
            }
        ],
        "email_from": {
            "name": company_name,
            "email": account.cms_attributes.get("emails", {}).get("quote_contact_email", "paul@amobilebox.com"),
        },
        "subject": "Application submitted invoice #" + str(customer_order.display_order_id),
        "body": f"An application has been submitted for {str(customer_order.display_order_id)}, see <a href="
        + order_link
        + "> here </a>",
    }

    mail_body = {}

    mailer = emails.NewEmail("mlsn.89aede0b404c7384993aec6e23eb8e9ac78a0c06b0b91a82e1566a54c655de78")
    mailer.set_mail_to(context.get("email_to"), mail_body)
    mailer.set_mail_from(context.get("email_from"), mail_body)
    mailer.set_html_content(context['body'], mail_body)
    mailer.set_subject(context.get('subject'), mail_body)

    try:
        resp: str = mailer.send(mail_body)
        # example error message: "422 {"message":"The cc must be an array.","errors":{"cc":["The cc must be an array."]}}"
        logger.info(resp)
        resp_code: str = resp[:3]
        resp_code_type: int = int(resp_code[0])
        if resp_code_type != 2:
            raise Exception(resp)
        logger.info("Email sent")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


def send_declined_application_email(customer_order: OrderOut, account: Account):
    # context = {
    #     "email_to": [
    #         {
    #             "name": "Customer",
    #             "email": customer_order.customer.email,
    #         }
    #     ],
    #     "subject": "Declined Application",
    #     "template": "neqvygmrv9dl0p7w",
    #     "personalization": [
    #         {
    #         "email": customer_order.customer.email,
    #          "data": {
    #                         "company": account.name,
    #                         "order_title": customer_order.display_order_id,
    #                         "text": account.cms_attributes.get("emails", {}).get("declined_application","")
    #                     }

    #         }
    #     ],
    # }

    # logger.info(f"Sending declined application email, here's the info: \n{context}")

    # return post_email_message(context=context, account=account)

    if account.name.startswith("USA Containers"):
        order_link = f"https://quote.usacontainers.co/#/{customer_order.id}"
    else:
        links = account.cms_attributes.get("links", {})
        order_link = f"{links.get('invoice_email_link', '')}{customer_order.id}"

    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": customer_order.user.email,
            }
        ],
        "subject": "Your order #" + str(customer_order.display_order_id) + " has been declined.",
        "body": "Your order #"
        + str(customer_order.display_order_id)
        + " has been declined, see <a href="
        + order_link
        + "> here </a>",
    }

    mail_body = {}

    mailer = emails.NewEmail("mlsn.89aede0b404c7384993aec6e23eb8e9ac78a0c06b0b91a82e1566a54c655de78")
    mailer.set_mail_to(context.get("email_to"), mail_body)
    mailer.set_html_content(context['body'], mail_body)
    mailer.set_subject(context.get('subject'), mail_body)

    try:
        resp: str = mailer.send(mail_body)
        # example error message: "422 {"message":"The cc must be an array.","errors":{"cc":["The cc must be an array."]}}"
        logger.info(resp)
        resp_code: str = resp[:3]
        resp_code_type: int = int(resp_code[0])
        if resp_code_type != 2:
            raise Exception(resp)
        logger.info("Email sent")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


def send_driver_email(customer_order: Order, line_item, region: Region, account: Account) -> bool:
    driver = line_item.driver
    company_name = account.name
    if account.name == 'Amobilebox':
        company_name = 'A Mobile Box'
    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("driver_email", None)
    email_info_from_cms = account.cms_attributes.get("emails", {}).get("driver_email", "")
    subject_w_out_order_id = email_info_from_cms.get("subject", "Driver Delivery Email")
    region = f"({region[:1]})" if region else ""
    line_item_id_sub = f"[Line ID {str(customer_order.line_items[0].id)[-5:]}] {region}"
    full_subject = f"{subject_w_out_order_id} - {str(customer_order.display_order_id)} {line_item_id_sub}"

    depot = line_item.inventory.depot
    scheduled_date = line_item.scheduled_date
    scheduled_date = scheduled_date.astimezone(timezone('US/Mountain')) if scheduled_date else None

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=customer_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    data = {
        "order_id": customer_order.display_order_id,
        "shipping_cost": str(line_item.shipping_cost),
        "delivery_company": driver.company_name,
        "delivery_address": customer_order.address.full_address,
        "customer_name": customer_info.get("full_name", ""),
        "customer_phone": customer_info.get("phone", ""),
        "container_size": line_item.title.strip(),
        "door_orientation": line_item.door_orientation,
        "delivery_date": scheduled_date.strftime("%m/%d/%Y") if scheduled_date else "",
        "release_number": line_item.inventory.container_release_number,
        "depot_name": depot.name,
        "depot_phone": depot.primary_phone,
        "depot_address": depot.full_address,
        "container_color": line_item.inventory.container_color,
        "initial_text": account.cms_attributes.get("emails", {}).get("driver_email", {}).get("initial_text", ""),
        "company_name": company_name,
        "company_phone": account.cms_attributes.get("emails", {}).get("quote_contact_phone", ""),
        "display_order_id": customer_order.display_order_id,
        "current_year": str(datetime.now().year),
        "company_email": account.cms_attributes.get("emails", {}).get("quote_contact_email", ""),
        "company_address": account.cms_attributes.get("emails", {}).get("company_mailing_address", ""),
    }

    context = {
        "email_to": [
            {
                "name": "Driver",
                "email": driver.email,
            }
        ],
        "subject": full_subject,
        "template": template_defaults.get("template_id"),
        "personalization": [
            {
                "email": driver.email,
                "data": data,
            }
        ],
    }

    logger.info(f"Sending driver delivery email, here's the info: \n{context}")

    return post_email_message(context=context, account=account)


async def send_customer_pickup_email(item: Dict[str, Any]) -> bool:
    account = await account_crud.get_one(item.get("account_id"))
    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("sales", None)

    context = {
        "email_to": [
            {
                "name": item.get("customer_name"),
                "email": item.get("customer_email"),
            }
        ],
        "subject": "Customer Pickup Email",
        "template": template_defaults.get("template_id"),
        "personalization": [
            {
                "email": item.get("customer_email"),
                "data": {
                    "order_title": item.get("status", "Invoice"),
                    "display_order_id": item.get("display_order_id"),
                    "text": item.get("text"),
                },
            }
        ],
    }

    logger.info(f"Sending customer pickup email, here's the info: \n{context}")

    return post_email_message(context=context, account=account)


async def send_customer_invoice_email(item: Dict[str, Any]) -> bool:

    # subs = [{"var": "order_title", "value": item.get("status", "Invoice")},
    #         {"var": "display_order_id", "value": item.get("display_order_id")},
    #         {"var": "text", "value": item.get("text")}] account_id

    # set invoiced to invoice
    account = await account_crud.get_one(item.get("account_id"))
    if item.get("status") == "Invoiced":
        item["status"] = "Invoice"

    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("sales", None)
    email_from = ""
    reply_to = ""

    if template_defaults is not None and template_defaults.get("default_sender") != "":
        email_from = template_defaults.get("default_sender")
    if template_defaults is not None and template_defaults.get("default_reply_to") != "":
        reply_to = template_defaults.get("default_reply_to")

    personalization = [
        {
            "email": item.get("customer_email"),
            "data": {
                "text": account.cms_attributes.get("emails", {}).get("invoice", ""),
                "order_title": item.get("status", "Invoice"),
                "account_name": item.get("company_name"),
                "display_order_id": item.get("display_order_id"),
                "url": item.get("url"),
            },
        }
    ]

    context = {
        "email_from": {
            "email": email_from,
            "name": account.name,
        },
        "reply_to": {
            "email": reply_to,
            "name": account.name,
        },
        "email_to": [
            {
                "name": item.get("customer_name"),
                "email": item.get("customer_email"),
            }
        ],
        "subject": f"{item.get('order_title', 'Invoice')} #{item.get('display_order_id')} from {item.get('company_name')}",
        "template": template_defaults.get("template_id") if template_defaults else "",
        "personalization": personalization,
    }

    logger.error(f"Sending customer invoice email, here's the info: \n{context}")

    return post_email_message(context=context, account=account)


async def send_rental_receipt(email, url, order_id: str, account: Account) -> bool:
    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("sales", None)
    email_from = ""
    reply_to = ""

    if template_defaults is not None and template_defaults.get("default_sender") != "":
        email_from = template_defaults.get("default_sender")
    if template_defaults is not None and template_defaults.get("default_reply_to") != "":
        reply_to = template_defaults.get("default_reply_to")

    personalization = [
        {
            "email": email,
            "data": {
                "text": "Here's the link to your rental receipt:",
                "order_title": "Rental Receipt",
                "account_name": account.name,
                "display_order_id": order_id,
                "url": url,
            },
        }
    ]

    context = {
        "email_from": {
            "email": email_from,
            "name": account.name,
        },
        "reply_to": {
            "email": reply_to,
            "name": account.name,
        },
        "email_to": [
            {
                "name": "Customer",
                "email": email,
            }
        ],
        "subject": f"Rental Reciept: #{order_id}",
        "template": template_defaults.get("template_id"),
        "personalization": personalization,
    }

    logger.info(f"Rental Receipt Email # {order_id}")

    return post_email_message(context=context, account=account)


async def send_paid_email(order: Dict[str, Any]) -> bool:
    order_id = order.get("display_order_id")
    account = await account_crud.get_one(order.get("account_id"))
    links = account.cms_attributes.get("links", {})
    url = f"{links.get('invoice_email_link', '')}{order.get('id')}"

    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("sales", None)
    email_from = ""
    reply_to = ""

    if template_defaults is not None and template_defaults.get("default_sender") != "":
        email_from = template_defaults.get("default_sender")
    if template_defaults is not None and template_defaults.get("default_reply_to") != "":
        reply_to = template_defaults.get("default_reply_to")
    text = order.get('text').replace("{{ order_id }}", order_id)
    text = text.replace("{{ address }}", order.get("address", {}).get("full_address", ""))
    email = ""
    if order.get("customer", {}) is not None:
        text = text.replace("{{ phone }}", order.get("customer", {}).get("phone", ""))
        text = text.replace("{{ name }}", order.get("customer", {}).get("full_name", ""))
        email = order.get("customer", {}).get("email")
    else:
        contacts = order.get("single_customer", {}).get("customer_contacts", [])
        if len(contacts) > 0:
            text = text.replace("{{ phone }}", contacts[0].get("phone", ""))
            email = contacts[0].get("email", "")
        text = text.replace("{{ name }}", order.get("single_customer", {}).get("full_name", ""))
    if 'questionaire_link' in links:
        url = links.get('questionaire_link')
        order['status'] = "Questionaire"
    personalization = [
        {
            "email": email,
            "data": {
                "text": text,
                "order_title": order.get("status", "Invoice"),
                "account_name": account.name,
                "display_order_id": order.get("display_order_id"),
                "url": url,
            },
        }
    ]

    context = {
        "email_from": {
            "email": email_from,
            "name": account.name,
        },
        "reply_to": {
            "email": reply_to,
            "name": account.name,
        },
        "email_to": [
            {
                "name": "Customer",
                "email": email,
            }
        ],
        "subject": f"Payment Confirmation For Your Order #{order_id}",
        "template": template_defaults.get("template_id") if template_defaults is not None else None,
        "personalization": personalization,
    }

    logger.info(f"Paid Email # {order_id}")

    return post_email_message(context=context, account=account)


async def send_rental_agreement(email_info: dict[str, str]) -> bool:
    order_id = email_info.get("display_order_id")
    account = await account_crud.get_one(email_info.get("account_id"))
    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("rentals", None)

    personalization = [
        {
            "email": email_info.get("customer_email"),
            "data": {
                "text": "You have been approved to rent a shipping container from A Mobile Box. Please click the button below to begin the signing process.",
                "order_title": "Rental Agreement",
                "account_name": email_info.get("company_name"),
                "display_order_id": email_info.get("display_order_id"),
                "url": email_info.get("url"),  # this will need to be the contract link
            },
        }
    ]
    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": email_info.get("customer_email"),
            }
        ],
        "subject": f"{template_defaults.get('subject')}, Order #{order_id}",
        "template": template_defaults.get("template_id"),
        "personalization": personalization,
    }

    return post_email_message(context=context, account=account)


def send_authorization_agreement(email_info: dict[str, str], account: Account) -> bool:
    order_id = email_info.get("display_order_id")

    personalization = [
        {
            "email": email_info.get("customer_email"),
            "data": {
                "text": "In order to move forward with credit card as a payment method, we require an authorization form to be signed.",
                "order_title": "Authorization Form",
                "account_name": email_info.get("company_name"),
                "display_order_id": email_info.get("display_order_id"),
                "url": email_info.get("url"),  # this will need to be the contract link
            },
        }
    ]

    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": email_info.get("customer_email"),
            }
        ],
        "subject": f"Credit Card Authorization w/ A Mobile Box, Order #{order_id}",
        "template": "neqvygmrv9dl0p7w",
        "personalization": personalization,
    }
    return post_email_message(context=context, account=account)


def send_signed_agreement(email_info: dict[str, str]) -> bool:
    order_id = email_info.get("display_order_id")

    personalization = [
        {
            "email": email_info.get("customer_email"),
            "data": {
                "text": email_info.get("text", ""),
                "order_title": email_info.get("title", ""),
                "account_name": email_info.get("company_name"),
                "display_order_id": email_info.get("display_order_id"),
                "url": email_info.get("url"),  # this will need to be the contract link
            },
        }
    ]

    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": email_info.get("customer_email"),
            }
        ],
        "subject": f"{email_info.get('title', '')} PDF From A Mobile Box, Order #{order_id}",
        "template": "neqvygmrv9dl0p7w",
        "personalization": personalization,
    }

    return post_email_message(context=context)


async def send_transaction_failed(order: Dict[str, Any]) -> bool:
    order_id = order.get("display_order_id")
    account = await account_crud.get_one(order.get("account_id"))
    links = account.cms_attributes.get("links", {})
    url = f"{links.get('invoice_email_link', '')}{order.get('id')}"

    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("sales", None)
    email_from = ""
    reply_to = ""

    if template_defaults is not None and template_defaults.get("default_sender") != "":
        email_from = template_defaults.get("default_sender")
    if template_defaults is not None and template_defaults.get("default_reply_to") != "":
        reply_to = template_defaults.get("default_reply_to")

    context = {
        "email_from": {
            "email": email_from,
            "name": account.name,
        },
        "reply_to": {
            "email": reply_to,
            "name": account.name,
        },
        "email_to": [
            {
                "name": "Customer",
                "email": order.get("customer", {}).get("email"),
            }
        ],
        "subject": f"Your Transaction failed for Order #{order_id}",
        "template": template_defaults.get("template_id"),
        "personalization": [
            {
                "email": order.get("customer", {}).get("email"),
                "data": {
                    "url": url,
                    "order_title": f"{order_id}",
                    "text": "Our system tried to card your card and the transaction has failed.",
                    "account_name": order.get("account_name", ""),
                },
            }
        ],
    }

    return post_email_message(context=context, account=account)


def send_charged_rentals(send_charged_rental: SendChargedRental, email_to: str) -> bool:

    context = {
        "email_to": [
            {
                "name": "Admin",
                "email": email_to,
            }
        ],
        "subject": "Charged Rentals",
        "template": "pq3enl62q7842vwr",
        "personalization": [send_charged_rental.dict()],
    }

    return post_email_message(context=context)


async def send_late_fee_email(order: Dict[str, Any]) -> bool:
    order_id = order.get("display_order_id")
    account = await account_crud.get_one(order.get("account_id"))
    links = account.cms_attributes.get("links", {})
    url = f"{links.get('invoice_email_link', '')}{order.get('id')}"

    template_defaults = account.integrations.get("mailer_send", {}).get("templates", {}).get("rentals", None)
    email_from = ""
    reply_to = ""

    if template_defaults is not None and template_defaults.get("default_sender") != "":
        email_from = template_defaults.get("default_sender")
    if template_defaults is not None and template_defaults.get("default_reply_to") != "":
        reply_to = template_defaults.get("default_reply_to")

    context = {
        "email_from": {
            "email": email_from,
            "name": account.name,
        },
        "reply_to": {
            "email": reply_to,
            "name": account.name,
        },
        "email_to": [
            {
                "name": "Customer",
                "email": order.get("customer", {}).get("email"),
            }
        ],
        "subject": f"Late fees for Order #{order_id}",
        "template": template_defaults.get('template_id'),
        "personalization": [
            {
                "email": order.get("customer", {}).get("email"),
                "data": {
                    "url": url,
                    "order_title": f"{order_id}",
                    "text": "Your order has received late fees.",
                    "account_name": order.get("account_name", ""),
                },
            }
        ],
    }

    return post_email_message(context=context, account=account)


def send_change_password_email(info: Dict[str, Any], account: Account) -> bool:
    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": info.get("email", {}),
            }
        ],
        "subject": f"Welcome to {info.get('company_name')} {info.get('first_name')}",
        "template": "jy7zpl9mk75g5vx6",
        "personalization": [
            {
                "email": info.get("email", {}),
                "data": {
                    "account": info.get("company_name"),
                    "url": info.get("url"),
                },
            }
        ],
    }

    return post_email_message(context=context, account=account)

    pass


def send_agent_email(text: str, emails: List[str]) -> bool:
    pass


def send_customer_rental_statement(pdf_url: str, email: str, display_order_id: str, account: Account) -> bool:
    subject = f"Customer rental statement for order #{display_order_id}"
    body = f"Click this <a href=\"{pdf_url}\">link </a> to download the pdf."
    personalization = [
        {
            "email": email,
            "data": {},
        }
    ]
    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": email,
            }
        ],
        "subject": subject,
        "body": body,
        "personalization": personalization,
    }

    return post_email_message(context=context, account=account)


# def send_customer_rental_statement(
#     transaction_details: List[OrderTransaction],
#     customer_detail: CustomerDetail,
#     order_detail: OrderDetail,
#     company_name: str,
#     order_info: dict,
#     subject: str = None,
#     account: Account = None,
# ) -> bool:

#     # [transaction_detail.dict() for transaction_detail in transaction_details]
#     # make each dict convert dates to json serializable

#     personalization = [
#         {
#             "email": customer_detail.email,
#             "data": {
#                 "auto_pay": "Yes",
#                 "order_info": {"paid_thru": order_info['paid_thru'], "first_rent": order_info.get('first_rent', {})},
#                 "companyName": company_name,
#                 "order_status": order_detail.status,
#                 "transactions": [transaction_detail.dict() for transaction_detail in transaction_details],
#                 "customer_name": customer_detail.name,
#                 "container_type": order_detail.container_type,
#                 "customer_email": customer_detail.email,
#                 "late_fees_date": order_detail.late_fee_date,
#                 "customer_address": customer_detail.address,
#                 "order_amount_due": order_detail.amount_due,
#                 "last_four_digits_card": order_detail.last_card_digits,
#             },
#         }
#     ]

#     template = account.cms_attributes.get("rental_statement_mailsend_template", "3vz9dle31eqgkj50")

#     context = {
#         "email_to": [
#             {
#                 "name": customer_detail.name,
#                 "email": customer_detail.email,
#             }
#         ],
#         "subject": "Customer Rental Statement",
#         "template": template,
#         "personalization": personalization,
#     }

#     if subject:
#         context['subject'] = subject

#     logger.info(f"Sending customer rental statment email, here's the info: \n{context}")

#     return post_email_message(context=context, account=account)


def send_application_submitted_email(email: str, display_order_id: str, order_id: str) -> bool:
    order_link = f"https://manage.amobilebox.co/#/{order_id}"

    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": email,
            }
        ],
        "subject": "Application submitted invoice #" + str(display_order_id),
        "body": f"Order {display_order_id} has submitted a rental application, click the link below to view. <br> <a href=\"{order_link}\">{display_order_id}</a>",
    }

    mail_body = {}

    mailer = emails.NewEmail("mlsn.89aede0b404c7384993aec6e23eb8e9ac78a0c06b0b91a82e1566a54c655de78")
    mailer.set_mail_to(context.get("email_to"), mail_body)
    mailer.set_mail_from(context.get("email_from"), mail_body)
    mailer.set_html_content(context['body'], mail_body)
    mailer.set_subject(context.get('subject'), mail_body)

    try:
        resp: str = mailer.send(mail_body)
        # example error message: "422 {"message":"The cc must be an array.","errors":{"cc":["The cc must be an array."]}}"
        logger.info(resp)
        resp_code: str = resp[:3]
        resp_code_type: int = int(resp_code[0])
        if resp_code_type != 2:
            raise Exception(resp)
        logger.info("Email sent")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


def send_application_submitted_email_to_customer(email: str) -> bool:
    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": email,
            }
        ],
        "subject": "Application submitted",
        "body": """&#x2705; You have successfully submitted your application. &#x2705; <br>
                Please watch out for further communication from us within 1-2 business days. <br>
                For any questions, please email paul@amobilebox.com.""",
    }

    mail_body = {}

    mailer = emails.NewEmail("mlsn.89aede0b404c7384993aec6e23eb8e9ac78a0c06b0b91a82e1566a54c655de78")
    mailer.set_mail_to(context.get("email_to"), mail_body)
    mailer.set_mail_from(context.get("email_from"), mail_body)
    mailer.set_html_content(context['body'], mail_body)
    mailer.set_subject(context.get('subject'), mail_body)

    try:
        resp: str = mailer.send(mail_body)
        # example error message: "422 {"message":"The cc must be an array.","errors":{"cc":["The cc must be an array."]}}"
        logger.info(resp)
        resp_code: str = resp[:3]
        resp_code_type: int = int(resp_code[0])
        if resp_code_type != 2:
            raise Exception(resp)
        logger.info("Email sent")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


def send_initial_email_payment_on_delivery(account, email_info):
    STAGE: str = settings.STAGE
    if STAGE.lower() == "dev":
        BASE_URL = "http://localhost:5173/#"
    elif STAGE.lower() == "prod":
        BASE_URL = f"{account.cms_attributes.get('sales_link_base_url')}/#"

    personalization = [
        {
            "email": email_info['customer_email'],
            "data": {
                "contract_url": f"{BASE_URL}/contracts_pay_on_delivery/{email_info['display_order_id']}",
                "contact": account.cms_attributes.get("quote_contact_phone", ""),
                "companyName": account.cms_attributes.get("account_name", ""),
                "companyUrl": account.cms_attributes.get("mailer_send_defaults", {}).get("company_url", ""),
                "companyDomain": account.cms_attributes.get("mailer_send_defaults", {}).get("company_url", ""),
            },
        }
    ]

    template = account.integrations.get("mailer_send", {}).get("templates", {}).get("pod", {}).get("template_id", "")

    context = {
        "email_to": [
            {
                "name": email_info['first_name'] + " " + email_info['last_name'],
                "email": email_info['customer_email'],
            }
        ],
        "subject": "Pay on delivery contract",
        "template": template,
        "personalization": personalization,
    }

    logger.info(f"Sending pay on delivery email, here's the info: \n{context}")

    return post_email_message(context=context, account=account)


def send_container_update_email_to_customer(
    display_order_id: str, is_attach: bool, region_email: str, account: Account
) -> bool:
    subject = f"Order #{display_order_id} Container Attached/Detached Update"
    body = "Container has been " + ("attached" if is_attach else "detached") + "."

    personalization = [
        {
            "email": region_email,
            "data": {},
        }
    ]
    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": region_email,
            }
        ],
        "subject": subject,
        "body": body,
        "personalization": personalization,
    }

    return post_email_message(context=context, account=account)


def send_message_from_customer_twilio(display_order_id: str, body: str, region_email: str, account: Account) -> bool:
    subject = f"Order #{display_order_id} message from customer"

    personalization = [
        {
            "email": region_email,
            "data": {},
        }
    ]
    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": region_email,
            }
        ],
        "subject": subject,
        "body": body,
        "personalization": personalization,
    }

    return post_email_message(context=context, account=account)


def send_incoming_rental_payment_invoice(display_order_id: str, body: str, email: str, account: Account) -> bool:
    subject = f"Order #{display_order_id} incoming payment due date"

    personalization = [
        {
            "email": email,
            "data": {},
        }
    ]
    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": email,
            }
        ],
        "subject": subject,
        "body": body,
        "personalization": personalization,
    }

    return post_email_message(context=context, account=account)


def get_templates_dict_loader(pages: tuple) -> DictLoader:
    file_path = f"{settings.ROOT_DIR}/services/email_templates"
    templates = dict((name, open(f"{file_path}/{name}").read()) for name in pages)
    return DictLoader(templates)


def send_aniversary_email(account: Account, email: str, years: int, notification: object):
    subject = ""
    template = notification.external_id

    personalization = [
        {
            "email": email,
            "data": {},
        }
    ]

    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": email,
            }
        ],
        "subject": notification.subject,
        "template": template,
        "personalization": personalization,
    }

    return post_email_message(context=context, account=account)


def send_check_rentals_admin_email(admin_table: dict, account: Account, accounts: List[Account]) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("adminCheckRentalsEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    subject = "Admin view of check rentals"

    personalization = [
        {
            "email": "tanner@mobilestoragetech.com",
            "data": {},
        }
    ]

    accounts_dict = {}
    for account_item in accounts:
        accounts_dict[account_item.id] = account_item

    data = []
    accounts_with_activity = []
    for account_id in admin_table:
        for display_order_id in admin_table[account_id]:
            if admin_table[account_id][display_order_id].get('customer_paid', '') != "No Attempt" or not admin_table[
                account_id
            ][display_order_id].get('customer_emailed', False):

                account_name = accounts_dict[account_id].cms_attributes['account_name']
                link = f'{accounts_dict[account_id].cms_attributes.get("links", {}).get("base_url", "")}/#/invoices/{display_order_id}'
                data.append(
                    {
                        "account_id": account_name,
                        "display_order_id": link,
                        "customer_paid": admin_table[account_id][display_order_id].get('customer_paid', True),
                        "customer_emailed": admin_table[account_id][display_order_id].get('customer_emailed', False),
                    }
                )
                if account_id not in accounts_with_activity:
                    accounts_with_activity.append(account_id)

    for account_id in admin_table:
        if account_id not in accounts_with_activity:
            account_name = accounts_dict[account_id].cms_attributes['account_name']
            data.append(
                {
                    "account_id": str(account_name) + " No attempt for emails charges",
                    "display_order_id": "",
                    "customer_paid": "",
                    "customer_emailed": "",
                }
            )

    body = ""
    context = {
        "email_to": [
            {
                "name": "Customer",
                "email": "tanner.cordovatech@gmail.com",
            }
        ],
        "email_from": {"name": "Tanner", "email": "tanner@mobilestoragetech.com"},
        "subject": subject,
        "body": env.get_template("adminCheckRentalsEmail.html").render(data=data),
        "personalization": personalization,
    }
    logger.info("Sending email message to tanner@mobilestoragetech.com. " + str(body))
    return post_email_message(context=context, account=account)

async def send_exception_email(lambda_name: str, exception_detail: str) -> bool:
    account = await account_crud.get_one(1)
    context = {
        "email_to": [
            {
                "name": "Developers",
                "email": "developers@mobilestoragetech.com",
            }
        ],
        "subject": lambda_name + " error",
        "body": f"Ran at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Error: {exception_detail}"
    }

    mail_body = {}

    mailer = emails.NewEmail(account.integrations.get("mailer_send", {}).get("api_key", ""))
    mailer.set_mail_to(context.get("email_to"), mail_body)
    mailer.set_mail_from({"name:": "Developers", "email": "tanner@mobilestoragetech.com"}, mail_body)
    mailer.set_html_content(context['body'], mail_body)
    mailer.set_subject(context.get('subject'), mail_body)

    try:
        resp: str = mailer.send(mail_body)
        # example error message: "422 {"message":"The cc must be an array.","errors":{"cc":["The cc must be an array."]}}"
        logger.info(resp)
        resp_code: str = resp[:3]
        resp_code_type: int = int(resp_code[0])
        if resp_code_type != 2:
            raise Exception(resp)
        logger.info("Email sent")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")