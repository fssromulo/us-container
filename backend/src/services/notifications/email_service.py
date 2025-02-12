# Python imports
import logging
from datetime import timedelta
from typing import Any, Dict, List

# Pip imports
# import boto3
import sendgrid

# from botocore.exceptions import ClientError
from jinja2 import DictLoader, Environment, select_autoescape
from loguru import logger
from pytz import timezone
from sendgrid.helpers.mail import Cc, Mail

# Internal imports
from src.config import settings
from src.controllers import orders as order_controller
from src.database.models.customer.old_customer import Customer
from src.database.models.customer.order_customer import OrderCustomer
from src.database.models.orders.order import Order
from src.database.models.pricing.location_price import PickupRegion
from src.database.models.pricing.region import Region
from src.schemas.line_items import LineItemOut


# ROOT_DIR = (f"{os.getcwd()}/src/services/email_templates/"
#             if os.environ.get('IS_DEV') else f"{os.environ.get('LAMBDA_TASK_ROOT')}{'/email_templates'}")
TIMEOUT = 5

STAGE: str = settings.STAGE


def post_email_message(context: Dict[str, str] = None) -> bool:
    if STAGE == 'local' or STAGE == 'dev':
        context["email_to"] = [settings.EMAIL_TO]

    # convert list to tuple
    context["email_to"] = [(email, "") for email in context.get("email_to", [])]
    logger.info(context["email_to"])

    message = Mail(
        from_email=context.get("email_from") if context.get("email_from") else settings.EMAIL_FROM,
        to_emails=context.get("email_to", []),
        subject=context.get("subject"),
        plain_text_content=context.get("text", "Please enable HTML on your email."),
        html_content=context.get("html"),
    )

    if context.get("cc"):
        cc_emails = []
        for c in context.get("cc"):
            cc_emails.append(Cc(c, c))
        message.add_cc(cc_emails)

    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code == 202:
            return True

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")

    return False


# def post_email_message(context: Dict[str, str] = None) -> bool:
#     logger.info("post_email_message")
#     logger.debug("post_email_message")

#     if os.environ.get('STAGE') == 'local':
#         context["email_to"] = [settings.EMAIL_TO]

#     # Create a new SES client
#     ses_client = boto3.client('ses', region_name=settings.AWS_REGION)

#     try:
#         response = ses_client.send_email(
#             Source=context.get("email_from") if context.get("email_from") else settings.EMAIL_FROM,
#             Destination={
#                 'ToAddresses': context.get("email_to", [])
#             },
#             Message={
#                 'Subject': {
#                     'Data': context.get("subject")
#                 },
#                 'Body': {
#                     'Text': {
#                         'Data': context.get("text", "Please enable HTML on your email.")
#                     },
#                     'Html': {
#                         'Data': context.get("html")
#                     }
#                 }
#             }
#         )
#         return True

#     except ClientError as e:
#         logger.error(f"Error sending email: {str(e.response['Error']['Message'])}")

#     return False


# def post_email_message(context: Dict[str, str] = None) -> bool:
#     if os.environ.get('STAGE') == 'local':
#         context["email_to"] = [settings.EMAIL_TO]
#     response = requests.post(
#         f"{settings.EMAIL_BASE_URI}/v3/mg.usacontainers.co/messages",
#         auth=("api", settings.EMAIL_AUTH_TOKEN),
#         timeout=TIMEOUT,
#         data={
#             "from": context.get("email_from") if context.get("email_from") else settings.EMAIL_FROM,
#             "to": context.get("email_to", []),
#             "subject": context.get("subject"),
#             "text": context.get("text", "Please enable html on your email."),
#             "html": context.get("html"),
#         },
#     )
#     if response.ok:
#         return response.ok

#     logger.error(f"Error sending email: {response.text}")

#     return False


def get_templates_dict_loader(pages: tuple) -> DictLoader:
    file_path = f"{settings.ROOT_DIR}/services/email_templates"
    templates = dict((name, open(f"{file_path}/{name}").read()) for name in pages)
    return DictLoader(templates)


async def send_driver_paid_email(driver_email: str, logistics_email: str, customer_order: Order):
    context = {
        # "email_from": "USA Containers <rto@usacontainers.co>",
        "email_to": [driver_email, logistics_email],
        "subject": f"Order {customer_order.display_order_id} - *{customer_order.address.city}, {customer_order.address.zip} * is PAID!",
        "text": f"""Order {customer_order.display_order_id} - *{customer_order.address.city}, {customer_order.address.zip} * is PAID! You can drop the container.""",
    }

    return post_email_message(context=context)


def send_driver_email(account, customer_order: Order, line_item, region: Region) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("deliveryEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    driver = line_item.driver
    depot = line_item.inventory.depot
    scheduled_date = line_item.scheduled_date
    scheduled_date = scheduled_date.astimezone(timezone('US/Mountain')) if scheduled_date else None
    STAGE: str = settings.STAGE
    if STAGE.lower() == "dev":
        BASE_URL = "http://localhost:5173/#"
    elif STAGE.lower() == "prod":
        BASE_URL = f"{account.cms_attributes.get('base_pricing_link')}/#"

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=customer_order)
    customer_info: dict[str, Any] = check_is_single_cust_dict.get("customer_info", None)

    email_data = {
        "order_id": customer_order.display_order_id,
        "shipping_cost": line_item.shipping_cost,
        "delivery_company": driver.company_name if driver and driver.company_name else "",
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
        "is_pod": True if customer_order.signed_at and customer_order.status == 'Pod' else False,
        "driver_payment_url": f"{BASE_URL}/driver/customerpayment/{customer_order.id}",
    }
    # delivery_table_img_path = "delivery_table.jpg"  # TODO: Change this to a real image maybe?
    order_id = (
        f"R{customer_order.display_order_id}"
        if customer_order.type == "RENT_TO_OWN"
        else customer_order.display_order_id
    )
    subject = (
        f"USA Containers Delivery - Order #{order_id}, "
        f"[Line ID {str(customer_order.line_items[0].id)[-5:]}] ({region[:1]})"
    )
    if customer_order.signed_at and customer_order.status == 'Pod':
        subject = (
            f"USA Containers PAYMENT ON DELIVERY - Order #{order_id}, "
            f"[Line ID {str(customer_order.line_items[0].id)[-5:]}] ({region[:1]})"
        )

    context = {
        "email_to": [driver.email, 'logistics@usacontainers.co'],
        "subject": subject,
        "html": env.get_template("deliveryEmail.html").render(data=email_data),
    }

    logger.info(f"Sending driver delivery email, here's the info: \n{email_data}")

    return post_email_message(context=context)


async def send_customer_pickup_email(
    customer_order: Order, selected_line_item: LineItemOut, region: Region, pickup_region: PickupRegion
) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("pickupEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    check_is_single_cust_dict: dict[str, Any] = order_controller.check_is_single_customer_order(order=customer_order)
    customer_info: None | OrderCustomer | Customer = check_is_single_cust_dict.get("customer_info", None)

    depot = selected_line_item.inventory.depot

    email_data = {
        "order_id": customer_order.display_order_id,
        "container_size": selected_line_item.title.replace(" Used", " Used ").strip(),
        "release_number": selected_line_item.inventory.container_release_number,
        "depot_name": depot.name,
        "depot_phone": depot.primary_phone,
        "depot_address": depot.full_address,
        "pickup_region": pickup_region,
    }
    order_id = (
        f"R{email_data.get('order_id')}" if email_data.get("is_rent_to_own", None) else email_data.get("order_id")
    )

    subject = (
        f"Pickup information for your container is below - Order #{order_id}, "
        f"[Line ID {str(selected_line_item.id)[-5:]}] ({pickup_region[:1]})"
    )

    context = {
        "email_from": "USA Containers <"
        + ("west.inventory@usacontainers.co>" if pickup_region == 'WEST' else "east.inventory@usacontainers.co>"),
        "email_to": [customer_info.get("email", "")],
        "subject": subject,
        "html": env.get_template("pickupEmail.html").render(data=email_data),
        "cc": ["west.inventory@usacontainers.co"] if pickup_region == 'WEST' else ["east.inventory@usacontainers.co"],
    }

    logger.info(f"Sending pickup email, here's the info: {email_data} {customer_info.get('email', '')}")

    return post_email_message(context=context)


def send_public_notifiction(item: Dict[str, Any]) -> bool:
    logger.info(f"Sending public invoice creation email, here's the info: {item.get('email')}")

    context = {
        "email_from": "A Mobile Box <automated@amobilebox.com>",
        "email_to": [item.get("mail_to")],
        "subject": "Public invoice creation mail",
        "html": f"An invoice/estimate/quote was just created from the public site. See here, <a href='{ item.get('url') }'>{ item.get('url') }</a>",
    }
    logger.info(f"Sending public invoice creation email, here's the info { context }")

    return post_email_message(context=context)


def send_agent_status_email(agent_email: str, display_order_id: str):
    context = {
        "email_from": "USA Containers <rto@usacontainers.co>",
        "email_to": [agent_email],
        "subject": f"RTO Update - Important Update Regarding Your Rent-To-Own Order - Invoice #{display_order_id}",
        "text": """
        Hello!
        We are writing this email to inform you about the progress of your Rent-To-Own order.
        The application has been received and we will be contacting the customer within the next 24 hours.
        Thank you!
        Have a great day!
        """,
    }

    return post_email_message(context=context)


def send_container_invoice_email(item: Dict[str, Any]) -> bool:
    logger.info(f"Sending customer invoice email, here's the info: {item.get('email')}")
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("emailInvoice.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)
    item["quote_title"] = "Quote" if item.get("attributes", {}).get("is_quote_title") else "Invoice"
    item[
        "footer_text"
    ] = "Once the order has been placed, you will receive an email to start the delivery process or if you are picking up please allow up to 5 business days and you will receive an email with the release information and full pick up address for your container."
    if item["type"] == 'RENT':
        item['quote_title'] = "RENTAL"
        item["footer_text"] = "PLEASE VIEW THE AGREEMENT AND THE PRICE BY CLICKING THE LINK ABOVE."
    item["due_date"] = (item.get("created_at") + timedelta(days=5)).strftime("%b %d %Y ")
    item["order_date"] = item.get("created_at").strftime("%b %d %Y ")
    item["pickup"] = any([i.get("shipping_revenue") == 0 for i in item.get("line_items")])
    order_id = f"R{item.get('display_order_id')}" if item.get("is_rent_to_own", None) else item.get("display_order_id")
    context = {
        "email_from": "USA Containers <jack@usacontainers.co>",
        "email_to": [item.get("customer_email")],
        "subject": f"{item.get('quote_title')} #{order_id} from USA Containers",
        "html": env.get_template("emailInvoice.html").render(data=item),
    }
    logger.info(f"Sending customer invoice email {item.get('display_order_id')}")
    return post_email_message(context=context)


def send_accessory_invoice_email(item: Dict[str, Any]) -> bool:
    logger.info(f"Sending customer invoice email, here's the info: {item.get('email')}")
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("accessoryEmailInvoice.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)
    item["quote_title"] = "Quote" if item.get("attributes", {}).get("is_quote_title") else "Invoice"
    item["due_date"] = (item.get("created_at") + timedelta(days=5)).strftime("%b %d %Y ")
    item["order_date"] = item.get("created_at").strftime("%b %d %Y ")
    item["pickup"] = any([i.get("shipping_revenue") == 0 for i in item.get("line_items")])
    order_id = f"R{item.get('display_order_id')}" if item.get("is_rent_to_own", None) else item.get("display_order_id")
    context = {
        "email_from": "USA Containers <parts@usacontainers.co>",
        "email_to": [item.get("customer_email")],
        "subject": f"Accessories {item.get('quote_title')} #{order_id} from USA Containers",
        "html": env.get_template("accessoryEmailInvoice.html").render(data=item),
    }
    logger.info(f"Sending customer invoice email {item.get('display_order_id')}")
    return post_email_message(context=context)


def send_customer_invoice_email(item: Dict[str, Any]) -> bool:
    if item["type"] == "PURCHASE_ACCESSORY":
        return send_accessory_invoice_email(item)
    else:
        return send_container_invoice_email(item)


def send_customer_general_receipt_email(order: Dict[str, Any]) -> bool:
    # if not validate_email(order["customer"]["email"]):
    #     return False

    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("generalReceiptEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    order_id = order.get("display_order_id")
    order["url"] = f"{settings.BASE_INVOICE_URL}/#/{order.get('id')}"
    order["title"] = "View Agreement" if order.get("type") == "RENT_TO_OWN" else "View Receipt"
    subject = f"USA Containers {'Agreement' if order.get('type') == 'RENT_TO_OWN' else 'Receipt'} Order #{order_id}"

    context = {
        "email_from": "USA Containers <jack@usacontainers.co>",
        "email_to": [order.get("customer", {}).get("email")],
        "subject": subject,
        "html": env.get_template("generalReceiptEmail.html").render(data=order),
    }

    logger.info(f"USA Containers General Receipt Order # {order_id}")

    return post_email_message(context=context)


def send_paid_email(order: Dict[str, Any], signature) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("paidConfirmation.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    email_data = {
        "order_id": order.get("display_order_id"),
        "name": order.get("customer", {}).get("full_name"),
        "address": order.get("address", {}).get("full_address"),
        "phone": order.get("customer", {}).get("phone"),
        "is_pod": True if order.get("signed_at", None) is not None and order.get("status", "") == 'Pod' else False,
        "url": f"{settings.BASE_INVOICE_URL}/#/{order.get('id')}",
    }
    order_id = f"R{order.get('order_id')}" if order.get("is_rent_to_own", None) else order.get("display_order_id")

    region = signature['email'][0].upper()

    context = {
        "email_from": f"USA Containers <{signature.get('email')}>",
        "email_to": [order.get("customer", {}).get("email"), signature.get('email')],
        "subject": f"Your Container Delivery Invoice #{order_id} ({region})",
        "html": env.get_template("paidConfirmation.html").render(data=email_data),
    }

    logger.info(f"Sending paid email {order_id}")

    return post_email_message(context=context)


def send_change_password_email(info: Dict[str, Any]) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("changePassword.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    email_data = {
        "first_name": info.get("first_name"),
        "company_name": info.get("company_name"),
        "url": info.get("url"),
    }

    context = {
        "email_from": "USA Containers <jack@usacontainers.co>",
        "email_to": [info.get("email")],
        "subject": f"Welcome to {info.get('company_name')} {info.get('first_name')}",
        "html": env.get_template("changePassword.html").render(data=email_data),
    }

    logger.info("Sending change password email ", info.get("email"))

    return post_email_message(context=context)


def send_agent_email(text: str, emails: List[str]) -> bool:
    context = {
        "email_from": "USA Containers <jack@usacontainers.co>",
        "email_to": emails,
        "subject": text,
        "html": f"{text} Check it out on weare.usacontainers.co.",
    }

    logger.info(f"Sending agent email {emails}")

    return post_email_message(context=context)


def send_discount_applied_email(item: Dict[str, Any]) -> bool:
    env = Environment(autoescape=select_autoescape(enabled_extensions=["html", "xml"]))
    pages = ("discountAppliedEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)
    email_from: str = f"USA Containers <{item.get('email')}>"
    email_to = [item.get('email')]
    context = {
        "email_from": email_from,
        "email_to": email_to,
        "subject": f"Order #{item.get('display_order_id')} Has Been Discounted",
        "html": env.get_template("discountAppliedEmail.html").render(data=item),
    }

    logger.info(f"Sending discount has been applied email: {item.get('display_order_id')}")

    return post_email_message(context=context)


async def send_accessory_paid_email(order_id: str):
    env = Environment(autoescape=select_autoescape(enabled_extensions=["html", "xml"]))
    pages = ("accessoryPaidEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)
    email_from: str = "USA Containers <parts@usacontainers.co>"
    email_to = ['parts@usacontainers.co']
    context = {
        "email_from": email_from,
        "email_to": email_to,
        "subject": f"Order #{order_id} Has Been Paid",
        "html": env.get_template("accessoryPaidEmail.html").render(order_id=order_id),
    }

    logger.info(f"Sending accessory paid email: {order_id}")

    return post_email_message(context=context)


def send_time_frame_email(order: Dict[str, Any], start_date: str, end_date: str, signature: dict) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("timeFrameEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    email_data = {
        "order_id": order.get("display_order_id"),
        "name": order.get("customer", {}).get("first_name"),
        "start_date": start_date,
        "end_date": end_date,
        "signature": signature,
    }
    order_id = f"R{order.get('order_id')}" if order.get("is_rent_to_own", None) else order.get("display_order_id")

    region = signature['email'][0].upper()

    context = {
        "email_from": f"USA Containers <{signature.get('email')}>",
        "email_to": [order.get("customer", {}).get("email"), signature.get("email")],
        "subject": f"Your Container Delivery Invoice #{order_id} ({region})",
        "html": env.get_template("timeFrameEmail.html").render(data=email_data),
    }
    logger.info(f"Sending time frame email {order_id}")
    return post_email_message(context=context)


def send_potential_email(order: Dict[str, Any], potential_date: str, signature: dict) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("potentialDateEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    email_data = {
        "order_id": order.get("display_order_id"),
        "name": order.get("customer", {}).get("first_name"),
        "potential_date": potential_date,
        "signature": signature,
    }
    order_id = f"R{order.get('order_id')}" if order.get("is_rent_to_own", None) else order.get("display_order_id")

    region = signature['email'][0].upper()

    context = {
        "email_from": f"USA Containers <{signature.get('email')}>",
        "email_to": [order.get("customer", {}).get("email"), signature.get("email")],
        "subject": f"Your Container Delivery Invoice #{order_id} ({region})",
        "html": env.get_template("potentialDateEmail.html").render(data=email_data),
    }
    logger.info(f"Sending time frame email {order_id}")
    return post_email_message(context=context)


def send_confirmation_date_email(order: Dict[str, Any], scheduled_date: str, signature: dict) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("confirmationDateEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    email_data = {
        "order_id": order.get("display_order_id"),
        "name": order.get("customer", {}).get("first_name"),
        "scheduled_date": scheduled_date,
        "signature": signature,
    }
    order_id = f"R{order.get('order_id')}" if order.get("is_rent_to_own", None) else order.get("display_order_id")

    region = signature['email'][0].upper()

    context = {
        "email_from": f"USA Containers <{signature.get('email')}>",
        "email_to": [order.get("customer", {}).get("email"), signature.get("email")],
        "subject": f"Your Container Delivery Invoice #{order_id} ({region})",
        "html": env.get_template("confirmationDateEmail.html").render(data=email_data),
    }
    logger.info(f"Sending time frame email {order_id}")
    return post_email_message(context=context)


def send_wrong_payments(settled_orders, not_settled_orders, orders_in_paid_status_declined, account):
    link = "https://weare.usacontainers.co/"
    if account.id == 2:
        link = "https://estimate.amobilebox.com"

    default_email = "tanner@mobilestoragetech.com"
    account_email = account.cms_attributes.get("account_email", default_email)
    if not account_email:
        account_email = default_email

    context = {
        "email_to": [account_email],
        "subject": "Incorrectly settled orders and pending orders.",
        "html": "Wrong settled orders <br><br>"
        + "<br>".join(
            [
                f"Order <a href=\"{link}#/invoices/{x['display_order_id']}\">{x['display_order_id']} </a>: Auth amount is different by {x['margin_of_error']}."
                for x in settled_orders.values()
                if x['margin_of_error'] != 0
            ]
        )
        + "<br>Orders not settled <br><br>"
        + "<br>".join(
            [
                f"Order <a href=\"{link}#/invoices/{x['display_order_id']}\">{x['display_order_id']}</a>: Transaction has not settled."
                for x in not_settled_orders.values()
            ]
        )
        + "<br>Orders with status paid but with declined credit cards: <br><br>"
        + "<br>".join(
            [
                f"Order <a href=\"{link}#/invoices/{x}\">{x}</a>: Transaction has not settled."
                for x in orders_in_paid_status_declined
            ]
        ),
    }

    return post_email_message(context=context)


def send_tracking_number(order: Dict[str, Any], tracking_number: str) -> bool:
    order_id = f"R{order.get('order_id')}" if order.get("is_rent_to_own", None) else order.get("display_order_id")

    context = {
        "email_from": settings.EMAIL_FROM,
        "email_to": [order.get("customer", {}).get("email")],
        "subject": f"Accessory tracking number #{order_id}",
        "html": f"Accessory tracking number {tracking_number} has been attached to order {order_id}.",
    }
    return post_email_message(context=context)


def send_tracking_number_attached(order) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("accessorySupplierAttached.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    products = []
    for line_item in order.line_items:
        if line_item.other_inventory:
            obj = {
                "product_name": line_item.other_inventory.product.name,
                "product_link": line_item.other_inventory.product.product_link,
                "vendor": line_item.other_inventory.vendor.name,
                "tracking_number": line_item.other_inventory.tracking_number,
            }
            products.append(obj)
    if len(products) == 0:
        logger.info("Sending tracking number attached mail failed, products dont have any attached inventory")
        return False

    customer_email = order.customer.email if order.customer else ""
    email_data = {
        "order_id": order.display_order_id,
        "name": order.customer.first_name if order.customer else "",
        "products": products,
    }

    order_id = order.display_order_id

    context = {
        "email_from": "USA Containers <parts@usacontainers.co>",
        "email_to": [customer_email],
        "subject": f"Great news! Your accessory order {order_id} has shipped!",
        "html": env.get_template("accessorySupplierAttached.html").render(data=email_data),
    }
    return post_email_message(context=context)


def send_accesory_delivered(order, line_item) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("accessoryDelivered.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    customer_email = order.customer.email if order.customer else ""

    order_id = order.display_order_id

    context = {
        "email_from": "USA Containers <parts@usacontainers.co>",
        "email_to": [customer_email],
        "subject": f"Your accessory order {order_id} is complete [Line Item {str(line_item)[:6]}]",
        "html": env.get_template("accessoryDelivered.html").render(data={}),
    }
    return post_email_message(context=context)


def send_signed_pod_contract_mail(email_info: dict[str, str]) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("paymentOnDeliverySignedContractEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    STAGE: str = settings.STAGE
    if STAGE.lower() == "dev":
        BASE_URL = "http://localhost:5173/#"
    elif STAGE.lower() == "prod":
        BASE_URL = "https://pricing.usacontainers.co/#"

    email_info['BASE_URL'] = BASE_URL

    context = {
        "email_to": [email_info.get("customer_email")],
        "subject": "Payment On Delivery Signed Contract",
        "html": env.get_template("paymentOnDeliverySignedContractEmail.html").render(data=email_info),
        "email_from": "USA Containers <cod@usacontainers.co>",
        "cc": ["cod@usacontainers.co"],
    }

    return post_email_message(context=context)


def send_initial_email_payment_on_delivery(email_info: dict[str, str]) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("paymentOnDeliveryInitialEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    STAGE: str = settings.STAGE
    if STAGE.lower() == "dev":
        BASE_URL = "http://localhost:5173/#"
    elif STAGE.lower() == "prod":
        BASE_URL = "https://pricing.usacontainers.co/#"

    email_info['BASE_URL'] = BASE_URL

    context = {
        "email_to": [email_info.get("customer_email")],
        "subject": "Payment On Delivery Contract Initial Email",
        "html": env.get_template("paymentOnDeliveryInitialEmail.html").render(data=email_info),
        "email_from": "USA Containers <cod@usacontainers.co>",
        "cc": ["cod@usacontainers.co"],
    }

    return post_email_message(context=context)


def send_initial_rental_contract_email(email_info: dict) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("rentalContract.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    STAGE: str = settings.STAGE
    if STAGE.lower() == "dev":
        BASE_URL = "http://localhost:5173/#"
    elif STAGE.lower() == "prod":
        BASE_URL = "https://pricing.usacontainers.co/#"

    email_info['BASE_URL'] = BASE_URL

    context = {
        "email_to": [email_info.get("customer_email")],
        "subject": f"USA Containers Rental Agreement #{ email_info['display_order_id'] }",
        "html": env.get_template("rentalContract.html").render(data=email_info),
        "email_from": "USA Containers <rentals@usacontainers.co>",
    }

    return post_email_message(context=context)


def send_customer_rental_statement(email_info: dict) -> bool:

    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("rentalStatement.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)
    logger.info(email_info)

    context = {
        "email_from": "USA Containers <rentals@usacontainers.co>",
        "email_to": [email_info.get("customer_detail", {}).email],
        "subject": f"Rental Statement #{ email_info.get('order_detail', {}).display_order_id }",
        "html": env.get_template("rentalStatement.html").render(data=email_info),
    }

    logger.info(f"Sending rental statement email, here's the info: \n{email_info}")

    return post_email_message(context=context)


def send_payment_on_delivery_contract_mail(email_info: dict[str, str]) -> bool:
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    pages = ("paymentOnDeliveryEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)

    email_data = {
        "url": email_info.get("url"),
    }
    context = {
        "email_from": "USA Containers <cod@usacontainers.co>",
        "email_to": [email_info.get("customer_email")],
        "subject": "Payment On Delivery Contract",
        "html": env.get_template("paymentOnDeliveryEmail.html").render(data=email_data),
    }

    logger.info(f"Sending payment on delivery email, here's the info: \n{email_data}")

    return post_email_message(context=context)


def send_application_submitted_email(email: str, display_order_id: str, order_id: str) -> bool:
    order_link = f"https://weare.usacontainers.co/#/invoices/{display_order_id}"
    context = {
        "email_from": "USA Containers <rentals@usacontainers.co>",
        "email_to": [email],
        "subject": f"Application submitted for order #{display_order_id}",
        "html": f"Order {display_order_id} has submitted a rental application, click the link below to view. <br> <a href=\"{order_link}\">{display_order_id}</a>",
    }

    return post_email_message(context=context)


def send_application_submitted_email_to_customer(email: str, display_order_id: str) -> bool:
    context = {
        "email_from": "USA Containers <rentals@usacontainers.co> ",
        "email_to": [email],
        "subject": f"Application submitted for order #{display_order_id}",
        "html": """&#x2713; You have successfully submitted your application. &#x2713; <br>
                Please watch out for further communication from us within 1-2 business days. <br>
                For any questions, please email rentals@usacontainers.co.""",
    }

    return post_email_message(context=context)


def send_inventory_release_notification(item: List[Dict[str, Any]]) -> bool:
    env = Environment(autoescape=select_autoescape(enabled_extensions=["html", "xml"]))
    pages = ("releaseNotificationEmail.html", "head.html")
    env.loader = get_templates_dict_loader(pages=pages)
    # put the top 3 container releases into the subject
    # we should pass down all the releases into the email
    top_3_container_releases = [x['container_release_number'] for x in item[:3]]

    context = {
        "email_from": 'USA Containers <operations@usacontainers.co>',
        "email_to": ['operations@usacontainers.co'],
        "cc": ['tanner@mobilestoragetech.com'],
        "subject": "Container Release " + ','.join(top_3_container_releases),
        "html": env.get_template("releaseNotificationEmail.html").render(data=item),
    }

    logger.info(f"Releases {[x['container_release_number'] for x in item[:3]]} are incomplete")

    return post_email_message(context=context)
