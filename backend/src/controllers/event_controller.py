# Python imports
import base64
import json
import time
from datetime import datetime, timedelta

# Pip imports
import httpx
from loguru import logger

# Internal imports
from src.crud.account_crud import account_crud
from src.database.models.orders.line_item import LineItem
from src.utils.convert_time import date_strftime
from src.utils.order_zone import fetch_region, fetch_zone
from src.utils.utility import make_json_serializable


def _map_inventory_to_woocomerce(payload):
    woocomerce_dict = {
        "id": payload['instance']['payload']['metadata'].get("id", "")
        if payload['instance']['payload']['metadata']
        else None,
        "sku": payload['instance']['payload']['container_number'],
        "name": payload['instance']['payload']['product'],
        "regular_price": str(payload['instance']['payload']['revenue']),
        "description": str(payload['instance']['payload']['description']),
        "images": []
    }

    for image in payload['instance']['payload']['image_urls']:
        woocomerce_dict['images'].append({"src": image['image_url']})

    return woocomerce_dict

mapping_functions = {
    "map_inventory_to_woocomerce": _map_inventory_to_woocomerce
}

def _map_request_data(res, data):
    if 'mapping_function' in res:
        mapping_function = mapping_functions.get(res['mapping_function'], lambda x: x)
        if res.get('metadata_key'):
            metadata = data['instance']['payload']['metadata']
            if metadata and res['metadata_key'] in metadata:
                data['instance']['payload']['metadata'] = metadata[res['metadata_key']]
        data = mapping_function(data)

    return data


def _prepare_headers(res):
    headersList = {"Content-Type": "application/json"}
    if 'api_key' in res:
        headersList['Authorization'] = f"Bearer {res['api_key']}"
    if "consumer_key" in res and "consumer_secret" in res:
        headersList["User-Agent"] = "curl/7.88.1"
    return headersList


def _prepare_params(res):
    params = {}
    if "consumer_key" in res and "consumer_secret" in res:
        params = {'consumer_key': res['consumer_key'], 'consumer_secret': res['consumer_secret']}
    return params


def _prepare_url(endpoint, data):
    id = data.get("id")
    if 'id' in data:
        del data['id']
    endpoint = endpoint.replace("<id>", str(id))
    return endpoint


async def _select_events_and_prepare(account_id, id, payload, object, operation, topic):
    account = await account_crud.get_one(account_id=account_id)
    logger.info(f"Processing event {topic}")
    external_integrations = account.external_integrations
    if external_integrations is None:
        return
    result = {}
    for res in external_integrations.get('resources', []):
        # logger.info("External integration call", external_integrations)
        # TODO remove the None condition check once all events have their appropriate topics set
        if (res['enabled'] and 'event_types' not in res) or (
            res['enabled'] and ('event_types' in res) and ('All' in res['event_types'] or topic in res['event_types'])
        ):
            logger.info('sending to', res['endpoint'])
            endpoint = res['endpoint']

            headers_list = _prepare_headers(res)

            data = {"instance": payload, "instance_id": id, "object": object, "operation": operation}
            data = _map_request_data(res, data)
            params = _prepare_params(res)
            endpoint = _prepare_url(res['endpoint'], data)

            ret = await send_event(data, res['method'], params, endpoint, headers_list,
                             res['retry_policy']['max_attempts'],
                             res['timeout'],
                             res['retry_policy']['backoff_factor'])

            if res.get('metadata_key') and res['method'] == 'POST':
                result[res['metadata_key']] = ret

    return result


async def send_event(data, method, params, endpoint, header_list, max_attempts, timeout, backoff_factor):
    async with httpx.AsyncClient() as client:
        try:
            for _ in range(max_attempts):
                response = await client.request(
                    method=method, url=endpoint, params=params,
                    json=data, headers=header_list, timeout=timeout
                )
                logger.info(response.text)
                if response.status_code == 200 or response.status_code == 201:
                    return json.loads(response.text)
                else:
                    time.sleep(backoff_factor * 2**_)
        except httpx.HTTPStatusError as e:
            logger.info("Http status error: " + str(e))
        except Exception as e:
            logger.info("Exception: " + str(e))


async def paid_at_event(existing_order, paid_at, background_tasks):
    container_product_city = None
    for li in existing_order.line_items:
        if li.product_type != "CONTAINER_ACCESSORY":
            container_product_city = li.product_city
            break
    zone = await fetch_zone(container_product_city, existing_order.account_id)
    event_payload = {
        "topic": "update:order:paid_at",
        "payload": {
            "id": existing_order.id,
            "display_order_id": existing_order.display_order_id,
            "status": existing_order.status,
            "zone": zone,
            "customer": {
                "phone": existing_order.customer.phone,
                "email": existing_order.customer.email,
                "name": existing_order.customer.full_name,
                "delivery_address": existing_order.address.full_address,
            },
            "paid_at": date_strftime(paid_at, '%a, %B {S} %Y') if paid_at is not None else "",
        },
    }
    await _select_events_and_prepare(
        existing_order.account_id,
        str(existing_order.id),
        make_json_serializable(event_payload),
        "order",
        "update",
        'update:order:paid_at',
    )


async def completed_at_event(existing_order, completed_at, background_tasks):
    """
    Send event when order is completed
    """
    container_product_city = None
    for li in existing_order.line_items:
        if li.product_type != "CONTAINER_ACCESSORY":
            container_product_city = li.product_city
            break
    zone = await fetch_zone(container_product_city, existing_order.account_id)
    event_payload = {
        "topic": "update:order:completed_at",
        "payload": {
            "id": existing_order.id,
            "display_order_id": existing_order.display_order_id,
            "status": existing_order.status,
            "zone": zone,
            "customer": {
                "phone": existing_order.customer.phone,
                "email": existing_order.customer.email,
                "name": existing_order.customer.full_name,
                "delivery_address": existing_order.address.full_address,
            },
            "completed_at": date_strftime(completed_at, '%a, %B {S} %Y'),
        },
    }
    await _select_events_and_prepare(
        existing_order.account_id,
        str(existing_order.id),
        make_json_serializable(event_payload),
        "order",
        "update",
        'update:order:completed_at',
    )


async def scheduled_date_event(existing_line_item, scheduled_date, background_tasks):
    zone = await fetch_zone(existing_line_item.product_city, existing_line_item.order.account_id)
    event_payload = {
        "topic": "update:line_item:scheduled_date",
        "payload": {
            "id": existing_line_item.id,
            "order": {
                "id": existing_line_item.order.id,
                "display_order_id": existing_line_item.order.display_order_id,
                "status": existing_line_item.order.status,
                "zone": zone,
            },
            "customer": {
                "phone": existing_line_item.order.customer.phone,
                "email": existing_line_item.order.customer.email,
                "name": existing_line_item.order.customer.full_name,
                "delivery_address": existing_line_item.order.address.full_address,
            },
            "scheduled_date": scheduled_date,
        },
    }
    await _select_events_and_prepare(
        existing_line_item.order.account_id,
        str(existing_line_item.id),
        make_json_serializable(event_payload),
        "line_item",
        "update",
        'update:line_item:scheduled_date',
    )


async def potential_date_event(existing_line_item, potential_date, background_tasks):
    zone = await fetch_zone(existing_line_item.product_city, existing_line_item.order.account_id)
    event_payload = {
        "topic": "update:line_item:potential_date",
        "payload": {
            "id": existing_line_item.id,
            "order": {
                "id": existing_line_item.order.id,
                "display_order_id": existing_line_item.order.display_order_id,
                "status": existing_line_item.order.status,
                "zone": zone,
            },
            "customer": {
                "phone": existing_line_item.order.customer.phone,
                "email": existing_line_item.order.customer.email,
                "name": existing_line_item.order.customer.full_name,
                "delivery_address": existing_line_item.order.address.full_address,
            },
            "potential_date": potential_date,
        },
    }
    await _select_events_and_prepare(
        existing_line_item.order.account_id,
        str(existing_line_item.id),
        make_json_serializable(event_payload),
        "line_item",
        "update",
        'update:line_item:potential_date',
    )


async def delivery_date_event(existing_line_item, delivery_date, background_tasks):
    zone = await fetch_zone(existing_line_item.product_city, existing_line_item.order.account_id)
    event_payload = {
        "topic": "update:line_item:delivery_date",
        "payload": {
            "id": existing_line_item.id,
            "order": {
                "id": existing_line_item.order.id,
                "display_order_id": existing_line_item.order.display_order_id,
                "status": existing_line_item.order.status,
                "zone": zone,
            },
            "customer": {
                "phone": existing_line_item.order.customer.phone,
                "email": existing_line_item.order.customer.email,
                "name": existing_line_item.order.customer.full_name,
                "delivery_address": existing_line_item.order.address.full_address,
            },
            "delivery_date": delivery_date,
        },
    }
    await _select_events_and_prepare(
        existing_line_item.order.account_id,
        str(existing_line_item.id),
        make_json_serializable(event_payload),
        "line_item",
        "update",
        'update:line_item:delivery_date',
    )


async def set_date_event(existing_line_item, delivery_date, background_tasks):
    zone = await fetch_zone(existing_line_item.product_city, existing_line_item.order.account_id)
    event_payload = {
        "topic": "update:line_item:delivery_date",
        "payload": {
            "id": existing_line_item.id,
            "order": {
                "id": existing_line_item.order.id,
                "display_order_id": existing_line_item.order.display_order_id,
                "status": existing_line_item.order.status,
                "zone": zone,
            },
            "customer": {
                "phone": existing_line_item.order.customer.phone,
                "email": existing_line_item.order.customer.email,
                "name": existing_line_item.order.customer.full_name,
                "delivery_address": existing_line_item.order.address.full_address,
            },
            "delivery_date": delivery_date,
        },
    }
    await _select_events_and_prepare(
        existing_line_item.order.account_id,
        str(existing_line_item.id),
        make_json_serializable(event_payload),
        "line_item",
        "update",
        'update:line_item:delivery_date',
    )


async def timeframe_event(line_item, order, start_dt, end_dt, background_tasks):
    zone = await fetch_zone(line_item.product_city, order.account_id)
    event_payload = {
        "topic": "update:line_item:time_frame",
        "payload": {
            "id": line_item.id,
            "order": {"id": order.id, "display_order_id": order.display_order_id, "status": order.status, "zone": zone},
            "customer": {
                "phone": order.customer.phone,
                "email": order.customer.email,
                "name": order.customer.full_name,
                "delivery_address": order.address.full_address,
            },
            "start_date": date_strftime(start_dt, '%a, %B {S} %Y'),
            "end_date": date_strftime(end_dt, '%a, %B {S} %Y'),
        },
    }
    await _select_events_and_prepare(
        order.account_id,
        str(line_item.id),
        make_json_serializable(event_payload),
        "line_item",
        "update",
        'update:line_item:time_frame',
    )


async def confirmation_event(line_item, order, set_date, background_tasks):
    if (order.type == "PURCHASE_ACCESSORY"):
        return
    zone = await fetch_zone(line_item.product_city, order.account_id)
    event_payload = {
        "topic": "update:line_item:set_date",
        "payload": {
            "id": line_item.id,
            "order": {"id": order.id, "display_order_id": order.display_order_id, "status": order.status, "zone": zone},
            "customer": {
                "phone": order.customer.phone,
                "email": order.customer.email,
                "name": order.customer.full_name,
                "delivery_address": order.address.full_address,
            },
            "set_date": set_date,
        },
    }
    await _select_events_and_prepare(
        order.account_id,
        str(line_item.id),
        make_json_serializable(event_payload),
        "line_item",
        "update",
        'update:line_item:set_date',
    )


async def pod_signed_event(order, customer_info, signed_at, background_tasks):
    if (order.type == "PURCHASE_ACCESSORY"):
        return
    container_product_city = None
    for li in order.line_items:
        if li.product_type != "CONTAINER_ACCESSORY":
            container_product_city = li.product_city
            break
    zone = await fetch_zone(container_product_city, order.account_id)
    event_payload = {
        "topic": "update:order:signed_at",
        "payload": {
            "id": order.id,
            "display_order_id": order.display_order_id,
            "status": order.status,
            "zone": zone,
            "customer": {
                "phone": customer_info.get("phone", ""),
                "email": customer_info.get("email", ""),
                "name": customer_info.get("full_name", ""),
                "delivery_address": order.address.full_address,
            },
            "signed_at": date_strftime(signed_at, '%a, %B {S} %Y'),
        },
    }
    await _select_events_and_prepare(
        order.account_id,
        str(order.id),
        make_json_serializable(event_payload),
        "order",
        "update",
        'update:order:signed_at',
    )


async def invoice_created_event(order, customer_info, created_at, background_tasks):
    container_product_city = None
    due_date = order.created_at + timedelta(days=5)
    for li in order.line_items:
        if li.product_type != "CONTAINER_ACCESSORY":
            container_product_city = li.product_city
            break
    as_is = False
    if len([x for x in order.line_items if 'as_is' in x.attributes]) > 0:
        as_is = True
    zone = await fetch_zone(container_product_city, order.account_id)
    event_payload = {
        "topic": "create:order:created_at",
        "payload": {
            "id": order.id,
            "display_order_id": order.display_order_id,
            "status": order.status,
            "attributes": order.attributes,
            "zone": zone,
            "customer": {
                "phone": customer_info.get("phone", ""),
                "email": customer_info.get("email", ""),
                "name": customer_info.get("full_name", ""),
                "delivery_address": order.address.full_address,
            },
            "created_date": date_strftime(created_at, '%a, %B {S} %Y'),
            "due_date": date_strftime(due_date, '%a, %B {S} %Y'),
            "as_is": as_is,
            "message_type": order.message_type,
        },
    }
    await _select_events_and_prepare(
        order.account_id,
        str(order.id),
        make_json_serializable(event_payload),
        "order",
        "create",
        'create:order:created_at',
    )


async def accessory_invoice_created_event(order, customer_info, created_at, background_tasks):
    container_product_city = None
    due_date = order.created_at + timedelta(days=5)
    event_payload = {
        "topic": "create:order:accessory_created_at",
        "payload": {
            "id": order.id,
            "display_order_id": order.display_order_id,
            "status": order.status,
            "attributes": order.attributes,
            "customer": {
                "phone": customer_info.get("phone", ""),
                "email": customer_info.get("email", ""),
                "name": customer_info.get("full_name", ""),
                "delivery_address": order.address.full_address,
            },
            "created_date": date_strftime(created_at, '%a, %B {S} %Y'),
            "due_date": date_strftime(due_date, '%a, %B {S} %Y'),
        },
    }
    await _select_events_and_prepare(
        order.account_id,
        str(order.id),
        make_json_serializable(event_payload),
        "order",
        "create",
        'create:order:accessory_created_at',
    )


async def inventory_attached_event(account_id, order_number, city, inventory, background_tasks):
    zone = await fetch_zone(city, account_id)
    event_payload = {
        "topic": "update:inventory:attach",
        "payload": {
            "display_order_id": order_number,
            "zone": zone,
            "release_number": inventory.container_release_number,
            "container_number": inventory.container_number,
        },
    }
    await _select_events_and_prepare(
        account_id,
        str(order_number),
        make_json_serializable(event_payload),
        "inventory",
        "update",
        'update:inventory:attach',
    )


async def inventory_detached_event(account_id, order_number, city, inventory, background_tasks):
    zone = await fetch_zone(city, account_id)
    event_payload = {
        "topic": "update:inventory:detach",
        "payload": {
            "display_order_id": order_number,
            "zone": zone,
            "release_number": inventory.container_release_number,
            "container_number": inventory.container_number,
        },
    }
    await _select_events_and_prepare(
        account_id,
        str(order_number),
        make_json_serializable(event_payload),
        "inventory",
        "update",
        'update:inventory:detach',
    )


async def pickup_event(customer_order, selected_line_item, pickup_region, city, background_tasks):
    zone = await fetch_zone(city, customer_order.account_id)
    depot = selected_line_item.inventory.depot
    event_payload = {
        "topic": "update:line_item:pickup",
        "payload": {
            "pickup_details": {
                "order_id": customer_order.display_order_id,
                "container_size": selected_line_item.title.replace(" Used", " Used WWT/CW ").strip(),
                "release_number": selected_line_item.inventory.container_release_number,
                "depot_name": depot.name,
                "depot_phone": depot.primary_phone,
                "depot_address": depot.full_address,
                "pickup_region": pickup_region,
            },
            "customer": {
                "phone": customer_order.customer.phone,
                "email": customer_order.customer.email,
                "name": customer_order.customer.full_name,
            },
            "order": {
                "id": customer_order.id,
                "display_order_id": customer_order.display_order_id,
                "status": customer_order.status,
                "zone": zone,
            },
            "id": selected_line_item.id,
        },
    }
    await _select_events_and_prepare(
        customer_order.account_id,
        str(customer_order.display_order_id),
        make_json_serializable(event_payload),
        "line_item",
        "update",
        'update:line_item:pickup',
    )


async def as_is_event(customer_order):
    due_date = customer_order.created_at + timedelta(days=5)
    event_payload = {
        "topic": 'create:order:created_at_as_is',
        "payload": {
            "phone": customer_order.customer.phone,
            "email": customer_order.customer.email,
            "name": customer_order.customer.full_name,
            "id": customer_order.id,
            "display_order_id": customer_order.display_order_id,
            "created_date": date_strftime(customer_order.created_at, '%a, %B {S} %Y'),
            "due_date": date_strftime(due_date, '%a, %B {S} %Y'),
        },
    }
    await _select_events_and_prepare(
        customer_order.account_id,
        str(customer_order.display_order_id),
        make_json_serializable(event_payload),
        "order",
        "create",
        'create:order:created_at_as_is',
    )


async def inventory_created(account_id, inventory):
    event_payload = {
        "topic": "create:inventory:create",
        "payload": {
            "container_number": inventory.container_number,
            "container_release_number": inventory.container_release_number,
            "depot": inventory.depot.name,
            "vendor": inventory.vendor.name,
            "product": inventory.product.title if inventory.product else None,
            "created_at": date_strftime(inventory.created_at, '%a, %B {S} %Y'),
            "total_cost": inventory.total_cost,
            "status": inventory.status,
            "purchase_type": inventory.purchase_type,
            "invoice_number": inventory.invoice_number,
            "pickup_at": date_strftime(inventory.pickup_at, '%a, %B {S} %Y') if inventory.pickup_at else "",
            "payment_type": inventory.payment_type,
            "paid_at":  date_strftime(inventory.paid_at, '%a, %B {S} %Y') if inventory.paid_at else "",
            "image_urls": inventory.image_urls,
            "metadata": inventory.metadata,
            "description": inventory.description,
            "revenue": inventory.revenue
        }
    }
    return await _select_events_and_prepare(
        account_id,
        str(inventory.container_number),
        make_json_serializable(event_payload),
        "inventory",
        "create",
        'create:inventory:create',
    )


async def rental_period_invoice_event(order, customer_info, created_at, period_id, background_tasks):
    container_product_city = None
    due_date = order.created_at + timedelta(days=5)
    for li in order.line_items:
        if li.product_type != "CONTAINER_ACCESSORY":
            container_product_city = li.product_city
            break
    as_is = False
    if len([x for x in order.line_items if 'as_is' in x.attributes]) > 0:
        as_is = True
    zone = await fetch_zone(container_product_city, order.account_id)
    event_payload = {
        "topic": "create:rent_period:created_at",
        "payload": {
            "id": order.id,
            "display_order_id": order.display_order_id,
            "rental_period_id": period_id,
            "status": order.status,
            "attributes": order.attributes,
            "zone": zone,
            "customer": {
                "phone": customer_info.get("phone", ""),
                "email": customer_info.get("email", ""),
                "name": customer_info.get("full_name", ""),
                "delivery_address": order.address.full_address,
            },
            "created_date": date_strftime(created_at, '%a, %B {S} %Y'),
            "due_date": date_strftime(due_date, '%a, %B {S} %Y'),
            "as_is": as_is,
        },
    }

    await _select_events_and_prepare(
        order.account_id,
        str(order.id),
        make_json_serializable(event_payload),
        "order",
        "create",
        'create:rent_period:created_at',
    )


async def inventory_updated(account_id, inventory):
    event_payload = {
        "topic": "update:inventory:update",
        "payload": {
            "container_number": inventory.container_number,
            "container_release_number": inventory.container_release_number,
            "depot": inventory.depot.name,
            "vendor": inventory.vendor.name,
            "product": inventory.product.title if inventory.product else None,
            "created_at": date_strftime(inventory.created_at, '%a, %B {S} %Y'),
            "total_cost": inventory.total_cost,
            "status": inventory.status,
            "purchase_type": inventory.purchase_type,
            "invoice_number": inventory.invoice_number,
            "pickup_at": date_strftime(inventory.pickup_at, '%a, %B {S} %Y') if inventory.pickup_at else "",
            "payment_type": inventory.payment_type,
            "paid_at":  date_strftime(inventory.paid_at, '%a, %B {S} %Y') if inventory.paid_at else "",
            "image_urls": inventory.image_urls,
            "metadata": inventory.metadata,
            "description": inventory.description,
            "revenue": inventory.revenue

        }
    }
    await _select_events_and_prepare(
        account_id,
        str(inventory.container_number),
        make_json_serializable(event_payload),
        "inventory",
        "update",
        'update:inventory:update',
    )


async def inventory_deleted(account_id, inventory):
    event_payload = {
        "topic": "delete:inventory:delete",
        "payload": {
            "container_number": inventory.container_number,
            "container_release_number": inventory.container_release_number,
            "depot": inventory.depot.name,
            "vendor": inventory.vendor.name,
            "product": inventory.product.title if inventory.product else None,
            "created_at": date_strftime(inventory.created_at, '%a, %B {S} %Y'),
            "total_cost": inventory.total_cost,
            "status": inventory.status,
            "purchase_type": inventory.purchase_type,
            "invoice_number": inventory.invoice_number,
            "pickup_at": date_strftime(inventory.pickup_at, '%a, %B {S} %Y') if inventory.pickup_at else "",
            "payment_type": inventory.payment_type,
            "paid_at":  date_strftime(inventory.paid_at, '%a, %B {S} %Y') if inventory.paid_at else "",
            "image_urls": inventory.image_urls,
            "metadata": inventory.metadata,
            "description": inventory.description,
            "revenue": inventory.revenue

        }
    }

    await _select_events_and_prepare(
        account_id,
        str(inventory.container_number),
        make_json_serializable(event_payload),
        "inventory",
        "delete",
        'delete:inventory:delete',
    )

async def order_paid_agent_notification(order_number, is_pod, account_id,agent, existing_order, recipients, background_tasks):
    product_city = None
    for line_item in existing_order.line_items:
        if line_item.product_city:
            product_city = line_item.product_city

    zone = await fetch_zone(product_city, account_id)
    event_payload = {
        "topic": "update:user:paid_at",
        "payload": {
            "display_order_id": order_number,
            "zone": zone,
            "recipients": ", ".join(recipients),
            "depot_city": product_city,
            "is_pod":'Yes' if is_pod else 'No',
            "agent": agent,
            "customer": {
                "phone": existing_order.customer.phone,
                "email": existing_order.customer.email,
                "name": existing_order.customer.full_name,
                "first_name": existing_order.customer.first_name,
                "delivery_address": existing_order.address.full_address,
            },
        },
    }
    await _select_events_and_prepare(
        account_id,
        str(order_number),
        make_json_serializable(event_payload),
        "order",
        "update",
        'update:user:paid_at',
    )

async def order_pod_signed_agent_notification(order_number, is_pod, account_id, agent, existing_order, recipients, background_tasks):
    product_city = None
    for line_item in existing_order.line_items:
        if line_item.product_city:
            product_city = line_item.product_city
    zone = await fetch_zone(product_city, account_id)
    event_payload = {
        "topic": "update:user:signed_at",
        "payload": {
            "display_order_id": order_number,
            "zone": zone,
            "recipients": ", ".join(recipients),
            "depot_city": product_city,
            "is_pod":'Yes' if is_pod else 'No',
            "agent": agent,
            "customer": {
                "phone": existing_order.customer.phone,
                "email": existing_order.customer.email,
                "name": existing_order.customer.full_name,
                "first_name": existing_order.customer.first_name,
                "delivery_address": existing_order.address.full_address,
            },

        },
    }
    await _select_events_and_prepare(
        account_id,
        str(order_number),
        make_json_serializable(event_payload),
        "order",
        "update",
        'update:user:signed_at',
    )
