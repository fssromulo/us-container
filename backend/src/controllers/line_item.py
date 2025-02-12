# Python imports
import random
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List
import time

# Pip imports
from fastapi import BackgroundTasks, HTTPException, status
from loguru import logger
from tortoise.transactions import atomic
from twilio.rest import Client

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import inventory as inventory_controller
from src.controllers import subtotal_balance as subtotal_balance_controller
from src.controllers import tax_balance as tax_balance_controller
from src.controllers.event_controller import inventory_attached_event, inventory_detached_event, pickup_event
from src.controllers.notifications_controller import fetch_region_signature
from src.controllers.rent_period_info import update_rent_period_price
from src.controllers.rental_history import create_rental_history, update_rental_history
from src.crud.account_crud import account_crud
from src.crud.line_item_crud import line_item_crud
from src.crud.location_price_crud import location_price_crud
from src.crud.order_crud import OrderCRUD
from src.crud.order_tax_crud import order_tax_crud
from src.crud.rent_period_crud import rent_period_crud
from src.crud.tax_crud import tax_crud
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.crud.total_order_balance_crud import total_order_balance_crud
from src.database.models.note import Note
from src.database.models.orders.line_item import LineItem
from src.database.models.orders.order import Order
from src.schemas.line_items import LineItemIn, LineItemInUpdate, LineItemOut, UpdateLineItem
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote
from src.schemas.order_tax import OrderTaxIn
from src.schemas.orders import OrderInUpdate
from src.schemas.rental_history import RentalHistoryIn, RentalHistoryUpdate
from src.schemas.token import Status
from src.schemas.total_order_balance import TotalOrderBalanceIn
from src.services.notifications import email_service, email_service_mailersend
from src.utils.convert_time import convert_time_date, date_strftime
from src.crud.other_product_crud import other_product_crud
from src.schemas.acccessory_line_items import CreateAccessoryLineItem, AccessoryLineItemOut
from src.crud.assistant_crud import assistant_crud
from src.utils.order_update_in_cache import clear_cache, swap_cache
from src.crud.partial_order_crud import partial_order_crud
from loguru import logger
note_crud = TortoiseCRUD(schema=NoteOutSchema, create_schema=NoteInSchema, update_schema=UpdateNote, db_model=Note)
order_crud = OrderCRUD()


def random_number() -> int:
    return random.randint(1, 999999)


async def save_line_item(line_item: UpdateLineItem, user: Auth0User, line_item_id: str = None) -> LineItemOut:
    note = line_item.notes
    del line_item.notes
    line_item_dict = line_item.dict(exclude_unset=True)

    if line_item_id:
        saved_line_item = await line_item_crud.update(
            user.app_metadata.get("account_id"),
            line_item_id,
            LineItemInUpdate(**line_item_dict),
        )
    else:
        if line_item_dict["product_type"] == "CONTAINER_ACCESSORY":
            other_product = await other_product_crud.get_one(user.app_metadata.get("account_id"), line_item_dict["product_id"])
            line_item_dict['other_product_name'] = other_product.name
            line_item_dict['other_product_shipping_time'] = other_product.shipping_time
            line_item_dict['product_cost'] = other_product.price
            line_item_dict.pop("product_id")
            line_item_dict.pop("door_orientation")
            saved_line_item = await line_item_crud.saveWithAccessory(LineItemIn(**line_item_dict),
                                                   CreateAccessoryLineItem(
                                                                      id=str(uuid.uuid4()),
                                                                      product_type=line_item_dict["product_type"],
                                                                      other_product_name=line_item_dict["other_product_name"],
                                                                      other_product_shipping_time=line_item_dict["other_product_shipping_time"],
                                                                      filename=other_product.file_upload[0].filename if other_product.file_upload is not None and len(other_product.file_upload) > 0 else None,
                                                                      content_type=other_product.file_upload[0].content_type if other_product.file_upload is not None and len(other_product.file_upload) > 0 else None,
                                                                      folder_type=other_product.file_upload[0].folder_type if other_product.file_upload is not None and len(other_product.file_upload) > 0 else None,
                                                                      other_product_id = other_product.id
                                                                      ))
        else :
            saved_line_item = await line_item_crud.create(LineItemIn(**line_item_dict))

    if note:
        await note_crud.create(
            NoteInSchema(
                title=note.title,
                content=note.content,
                author_id=user.app_metadata.get("id"),
                line_item_id=saved_line_item.id,
            )
        )
    return saved_line_item


async def bulk_save_line_items(line_items: List[UpdateLineItem], fields_to_update: List[str], user: Auth0User) -> int:
    note_list: List[NoteInSchema] = []

    for li in line_items:
        note: Note = li.notes
        del li.notes
        if note:
            note_list.append(
                NoteInSchema(
                    title=note.title,
                    content=note.content,
                    author_id=user.app_metadata.get("id"),
                    line_item_id=li.id,
                )
            )
    if "notes" in fields_to_update:
        fields_to_update.remove("notes")
    if "returned_at" in fields_to_update:
        fields_to_update.remove("returned_at")

    num_updated: int = await LineItem.bulk_update(
        [LineItem(**li.dict(exclude_unset=True)) for li in line_items],
        list(li.dict(exclude_unset=True).keys()),
        len(line_items),
    )

    if len(note_list) > 0:
        await note_crud.bulk_create([NoteInSchema(**note.dict()) for note in note_list], len(line_items))
    return num_updated


async def get_line_item(line_item_id: str, user: Auth0User):
    return await line_item_crud.get_one(user.app_metadata.get("account_id"), line_item_id)


@atomic()
async def delete_line_item(line_item_id: str, user: Auth0User):
    existing_line_item: LineItem = await line_item_crud.get_one(user.app_metadata.get("account_id"), line_item_id)
    # deleting the line item first so that then the recalculation when we grab the order will take effect
    await line_item_crud.delete_one(account_id=user.app_metadata.get("account_id"), item_id=line_item_id)

    existing_order: Order = await order_crud.get_one(existing_line_item.order.id)

    # This was never getting hit with the old code, so now we want to check no
    # matter what for the diffs in from the line item deletion. This is
    # because the calculated remaining balance will always be greater
    # than 0 and now it will always be affected no matter what when there
    # is a deletion of a line item
    diff_in_revenue: Decimal = existing_line_item.revenue if existing_line_item.revenue else 0
    diff_in_shipping_rev: Decimal = existing_line_item.shipping_revenue if existing_line_item.shipping_revenue else 0

    tax_states = [li.inventory.container_inventory_address.state for li in existing_order.line_items if li.inventory and li.inventory.container_inventory_address]
    if not tax_states:
        tax_states = [existing_order.customer.state]

    tax_rate = await tax_crud.get_tax_rate(user.app_metadata.get("account_id"), tax_states[0])
    new_tax: Decimal = round((existing_order.calculated_sub_total_price * tax_rate), 2)

    old_tax: Decimal = existing_order.calculated_order_tax
    tax_diff_amt: Decimal = new_tax - old_tax
    new_tax_obj: OrderTaxIn = OrderTaxIn(tax_amount=new_tax, order_id=existing_order.id)

    await order_tax_crud.create(new_tax_obj)

    # this will be a negative number always in this function bc we are deleting a line item.

    new_balance = (
        existing_order.calculated_remaining_order_balance - diff_in_shipping_rev - diff_in_revenue + tax_diff_amt
    )
    create_order_balance: TotalOrderBalanceIn = TotalOrderBalanceIn(
        remaining_balance=new_balance, order_id=existing_order.id
    )

    await tax_balance_controller.handle_tax_balance_paydown(existing_order, tax_diff_amt, True, None, None)

    await subtotal_balance_controller.handle_subtotal_balance_paydown(
        existing_order, diff_in_shipping_rev + diff_in_revenue, False, None, None
    )

    await total_order_balance_crud.create(create_order_balance)

    user_id = user.id.replace("auth0|", "")
    try:
        assistant = await assistant_crud.get_by_assistant_id(user_id)
    except HTTPException as e:
        if e.status_code == 404:
            assistant = None
        else:
            raise e

    user_ids = [user_id]
    if assistant:
        user_ids.append(assistant.manager.id)

    if existing_order.user.id != user_id:
        user_ids.append(existing_order.user.id)

    statuses = [existing_order.status]
    if existing_order.status in ['Paid', 'first_payment_received', 'Pod']:
        statuses += ['To_Deliver']

    if existing_order.type == 'RENT' and existing_order.status in ['Delinquent', 'Delivered']:
        statuses += ['On_Rent']

    order_line_items_loaded = await partial_order_crud.get_one_line_items(existing_order.id, user.app_metadata['account_id'])

    try:
        swap_cache(new_statuses=[],
                        old_statuses=[], 
                        swap_statuses=statuses, 
                        new_line_items=order_line_items_loaded,
                        order_type=existing_order.type,
                        user_ids=user_ids,
                        account_id=user.app_metadata['account_id'])
            
        swap_cache(new_statuses=[],
                        old_statuses=[], 
                        swap_statuses=statuses, 
                        new_line_items=order_line_items_loaded,
                        order_type="ALL",
                        user_ids=user_ids,
                        account_id=user.app_metadata['account_id'])
    except Exception as e:
        logger.error(str(e))

    return Status(message="Line item deleted")


@atomic()
async def update_line_item(
    line_items: List[UpdateLineItem],
    user: Auth0User,
    inventoryIdsToMakeAvailable: List[str] = [],
    move_out_date: datetime = None,
    move_out_type: str = "Single",
    is_move_out: bool = None,
    background_tasks: BackgroundTasks = None,
) -> List[LineItemOut]:
    line_item_ids: List[str] = [line_item.id for line_item in line_items]
    multiple_li: bool = len(line_item_ids) > 1
    existing_line_items: List[LineItem] = await line_item_crud.get_by_ids(line_item_ids)
    saved_line_items: List[LineItemOut] = []  # list of the adjusted lineitems after being saved
    modified_line_items: List[UpdateLineItem] = []  # list of the adjusted lineitems before being saved
    existing_line_items_dict: Dict[str, LineItem] = {}
    line_item_dict: Dict[str, LineItem] = {}
    existing_order: Order = await order_crud.get_one(existing_line_items[0].order.id)
    difference_in_price: Decimal = 0
    changed_tracking_number_delivery_date = False
    changed_line_item = None

    tax_states = [li.inventory.container_inventory_address.state for li in existing_order.line_items if li.inventory and li.inventory.container_inventory_address]
    if not tax_states:
        tax_states = [existing_order.customer.state]
    tax_state = tax_states[0]

    tax_rate = await tax_crud.get_tax_rate(user.app_metadata.get("account_id"), tax_state)

    for li in existing_line_items:
        existing_line_items_dict[li.id] = li

    for li in line_items:
        line_item_dict[li.id] = li

    for line_item_id, value in existing_line_items_dict.items():
        existing_line_item: LineItem = value
        line_item: LineItem = line_item_dict[str(line_item_id)]
        # need to add these fields for the bulk update bc they are not nullabe in the model
        line_item.missed_delivery = existing_line_item.missed_delivery
        line_item.pickup_email_sent = existing_line_item.pickup_email_sent

        if existing_line_item.scheduled_date != line_item.scheduled_date and line_item.scheduled_date:
            line_item.good_to_go = "NO"

        if (
            existing_line_item.welcome_call
            and line_item.welcome_call
            and existing_line_item.welcome_call.upper() in ["NO", "IN PROGRESS"]
            and line_item.welcome_call.upper() == "YES"
        ):
            account = await account_crud.get_one(user.app_metadata['account_id'])
            account_sid = account.integrations.get("twilio", {}).get("account_sid", "")
            auth_token = account.integrations.get("twilio", {}).get("auth_token", "")
            from_phone = account.integrations.get("twilio", {}).get("from_phone", "")

            if auth_token != '' and account_sid != '':
                region_signature = await fetch_region_signature(existing_line_item.product_city, account.id)
                client = Client(account_sid, auth_token)
                message_to_customer = account.cms_attributes.get("sms_welcome_message", "")
                message_to_customer = message_to_customer.replace("{order_id}", existing_order.display_order_id)
                message_to_customer = message_to_customer.replace(
                    "{email}", region_signature['email'].replace(".co", ".net")
                )

                try:
                    message = client.messages.create(
                        body=message_to_customer, from_=from_phone, to=existing_order.customer.phone
                    )
                    logger.info(f"Message sent successfully. SID: {message.sid}")
                except Exception as e:
                    logger.info(f"An error occurred: {str(e)}")

        if line_item.revenue is not None or line_item.shipping_revenue is not None:
            # added this var so that I don't use the difference in price var which will keep adding up over each iteration
            individual_li_diff_in_price = 0
            can_decrease = [p for p in user.permissions if p == "read:decrease_container_revenue"]

            if (
                (existing_line_item.revenue > line_item.revenue if line_item.revenue else False)
                or (
                    existing_line_item.shipping_revenue > line_item.shipping_revenue
                    if line_item.shipping_revenue
                    else False
                )
            ) and not can_decrease:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to decrease the container revenue",
                )

            if line_item.revenue is not None:
                difference_in_price += line_item.revenue - existing_line_item.revenue
                individual_li_diff_in_price += line_item.revenue - existing_line_item.revenue
            else:
                line_item.revenue = existing_line_item.revenue

            if line_item.shipping_revenue is not None:
                difference_in_price += line_item.shipping_revenue - existing_line_item.shipping_revenue
                individual_li_diff_in_price += line_item.shipping_revenue - existing_line_item.shipping_revenue
            else:
                line_item.shipping_revenue = existing_line_item.shipping_revenue

            if abs(individual_li_diff_in_price) > 0:
                await order_crud.update(
                    user.app_metadata.get("account_id"),
                    existing_order.id,
                    OrderInUpdate(
                        **{
                            "pod_sign_page_url": None,
                            "account_id": user.app_metadata.get("account_id"),
                        }
                    ),
                )

        if line_item.shipping_cost == existing_line_item.shipping_cost:
            if (
                line_item.potential_miles != existing_line_item.potential_miles
                or line_item.potential_dollar_per_mile != existing_line_item.potential_dollar_per_mile
            ):
                if not line_item.potential_miles:
                    line_item.potential_miles = existing_line_item.potential_miles or 0
                if not line_item.potential_dollar_per_mile:
                    line_item.potential_dollar_per_mile = existing_line_item.potential_dollar_per_mile or 0

                line_item.shipping_cost = line_item.potential_miles * line_item.potential_dollar_per_mile

        if line_item.potential_date is None and multiple_li:
            line_item.potential_date = existing_line_item.potential_date
        if line_item.delivery_date is None and multiple_li:
            line_item.delivery_date = existing_line_item.delivery_date

        if line_item.scheduled_date is None and multiple_li:
            line_item.scheduled_date = existing_line_item.scheduled_date
        if line_item.scheduled_date:
            line_item.scheduled_date = convert_time_date(line_item.scheduled_date.date())
        if line_item.potential_date:
            line_item.potential_date = convert_time_date(line_item.potential_date.date())
        if line_item.delivery_date:
            line_item.delivery_date = convert_time_date(line_item.delivery_date.date())
            changed_tracking_number_delivery_date = True
            changed_line_item = line_item
            # email_service.send_accesory_delivered(existing_order, line_item)
        # check and send scheduled date event
        # if line_item.scheduled_date is not None and line_item.scheduled_date != existing_line_item.scheduled_date:
        #     await scheduled_date_event(existing_line_item, formatted_scheduled_date, background_tasks)
        # check and send potential date
        # if line_item.potential_date is not None and line_item.potential_date != existing_line_item.potential_date:
        #     await potential_date_event(existing_line_item, formatted_potential_date, background_tasks)
        # check and send delivery date
        # if line_item.delivery_date is not None and line_item.delivery_date != existing_line_item.delivery_date:
        #     await delivery_date_event(existing_line_item, formatted_delivery_date, background_tasks)

        modified_line_items.append(line_item)

    update_line_item_obj = UpdateLineItem()
    current_li_field_names: List[str] = update_line_item_obj.get_all_field_names(li)
    # update_line_item_found.driver_id
    await bulk_save_line_items(modified_line_items, current_li_field_names, user)

    if existing_order.type == "RENT":
        has_existing_line_items = False
        for modified_li in modified_line_items:

            existing_line_item = existing_line_items_dict[uuid.UUID(modified_li.id)]
            rent_periods = await rent_period_crud.get_all_by_order_id(existing_order.id)
            if not modified_li.inventory_id and existing_line_item.inventory and existing_line_item.rental_history:
                rental_history_dict = {"rent_ended_at": datetime.now()}
                if move_out_date is not None:
                    rental_history_dict = {"rent_ended_at": move_out_date}
                    # This is a move out so delete all future rent periods
                    if move_out_type != 'All':
                        await rent_period_crud.remove_all_from(
                            existing_order.id, move_out_date, existing_line_item.monthly_owed, move_out_type
                        )
                await update_rental_history(
                    existing_line_item.rental_history[0].id, RentalHistoryUpdate(**rental_history_dict)
                )
            elif not modified_li.inventory_id and existing_line_item.inventory and len(rent_periods) != 0:
                if is_move_out:
                    rental_history_dict = RentalHistoryIn(
                        **{
                            "rent_started_at": rent_periods[0].start_date,
                            "rent_ended_at": datetime.now() if move_out_date is None else move_out_date,
                            "line_item_id": existing_line_item.id,
                            "inventory_id": existing_line_item.inventory.id,
                        }
                    )
                    await create_rental_history(rental_history_dict, user)
                    if move_out_date is not None and move_out_type != 'All':
                        await rent_period_crud.remove_all_from(
                            existing_order.id, move_out_date, existing_line_item.monthly_owed, move_out_type
                        )
                else:
                    has_existing_line_items = True
            else:
                has_existing_line_items = True

            if hasattr(modified_li, 'monthly_owed') and modified_li.monthly_owed is not None:
                logger.info(f"Updating rent period price for order {existing_order.id} to {modified_li.monthly_owed}")
                monthly_owed_diff = Decimal(modified_li.monthly_owed) - Decimal(existing_line_item.monthly_owed)
                new_total_monthly_owed = Decimal(existing_order.calculated_monthly_owed_total_wo_fees_or_tax) + Decimal(monthly_owed_diff)
                await update_rent_period_price(existing_order.id, new_total_monthly_owed)

            # Check if it's dettach
            if line_items[0].inventory_id is None:

                # Don't delete if only one period(downpayment) exists
                if len(rent_periods) == 1:
                    continue
                for rent in rent_periods:
                    if hasattr(rent, 'order') and rent.calculated_rent_period_total_balance > 0:
                        await rent_period_crud.delete_one(str(rent.id))

        # CHECK IF ALL LINE ITEMS ARE DETACHED AND SET ORDER STATUS TO RETURNED
        if not has_existing_line_items:

            await order_crud.update(
                user.app_metadata.get("account_id"),
                existing_order.id,
                OrderInUpdate(
                    **{
                        "status": "Returned",
                        "user_id": existing_order.user.id,
                        "account_id": user.app_metadata.get("account_id"),
                    }
                ),
            )
        if move_out_date is not None:
            if move_out_type == 'All':
                await rent_period_crud.remove_all_from(existing_order.id, move_out_date, 0, move_out_type)
            await rent_period_crud.delete_moved_out(existing_order.id, move_out_date)

    saved_line_items: List[LineItem] = await line_item_crud.get_by_ids(line_item_ids)
    for li in saved_line_items:
        update_line_item_found = next((item for item in modified_line_items if str(item.id) == str(li.id)), None)
        if update_line_item_found.driver_id:
            found_location = await location_price_crud.get_by_city(li.product_city, user.app_metadata.get("account_id"))
            account = await account_crud.get_one(user.app_metadata.get("account_id"))
            if account.name.startswith("USA Containers"):
                email_service.send_driver_email(account, existing_order, li, found_location.region)
            else:
                email_service_mailersend.send_driver_email(existing_order, li, found_location.region, account)

    if difference_in_price != 0:
        subtotal_balance_diff = difference_in_price
        if existing_order.calculated_order_tax != 0:
            new_tax_diff: Decimal = round((difference_in_price * tax_rate), 2)
            current_tax: Decimal = existing_order.calculated_order_tax

            new_tax: Decimal = current_tax + new_tax_diff
            create_order_tax: OrderTaxIn = OrderTaxIn(tax_amount=new_tax, order_id=existing_order.id)
            await order_tax_crud.create(create_order_tax)

            difference_in_price += new_tax_diff

            await tax_balance_controller.handle_tax_balance_paydown(existing_order, new_tax_diff, True, None, None)

        create_order_balance: TotalOrderBalanceIn = TotalOrderBalanceIn(
            remaining_balance=existing_order.calculated_remaining_order_balance + difference_in_price,
            order_id=existing_order.id,
        )

        await total_order_balance_crud.create(create_order_balance)

        await subtotal_balance_controller.handle_subtotal_balance_paydown(
            existing_order, subtotal_balance_diff, True, None, None
        )

    for i in range(len(saved_line_items)):
        if not saved_line_items[i].inventory:
            continue

        inventory_id = saved_line_items[i].inventory.id

        if line_items[0].inventory_id and not await inventory_controller.check_if_inventory_matches(
            user.app_metadata.get("account_id"), saved_line_items[i].inventory.id, saved_line_items[i]
        ):
            raise HTTPException(400, "Ensure your containers match!.")

        account = await account_crud.get_one(user.app_metadata.get("account_id"))
        await inventory_controller.update_container_inventory_dict(account.id, inventory_id, {"status": "Attached"})

        # send event to event controller

        await inventory_attached_event(
            user.app_metadata['account_id'],
            existing_order.display_order_id,
            saved_line_items[i].product_city,
            saved_line_items[i].inventory,
            background_tasks,
        )
        signature = await fetch_region_signature(saved_line_items[0].product_city, account.id)
        account = await account_crud.get_one(user.app_metadata.get("account_id"))

        if line_items[i].inventory_id and signature is not None and account.name.startswith("USA Containers"):
            background_tasks.add_task(
                email_service_mailersend.send_container_update_email_to_customer,
                existing_order.display_order_id,
                True,
                signature['email'],
                account,
            )

    for inventory_id in inventoryIdsToMakeAvailable:
        if not inventory_id:
            raise HTTPException(400, "Inventory ids to make available not populated.")
        inventory = await inventory_controller.get_container_inventory(inventory_id, user)
        account = await account_crud.get_one(user.app_metadata.get("account_id"))
        await inventory_controller.update_container_inventory_dict(account.id, inventory_id, {"status": "Available"})
        signature = await fetch_region_signature(saved_line_items[0].product_city, account.id)
        account = await account_crud.get_one(user.app_metadata.get("account_id"))
        # send event to event controller
        await inventory_detached_event(
            user.app_metadata['account_id'],
            existing_order.display_order_id,
            saved_line_items[i].product_city,
            inventory,
            background_tasks,
        )

        if signature is not None and account.name.startswith("USA Containers"):
            background_tasks.add_task(
                email_service_mailersend.send_container_update_email_to_customer,
                existing_order.display_order_id,
                False,
                signature['email'],
                account,
            )

    if changed_tracking_number_delivery_date and await check_if_all_items_are_delivered(existing_order.id):
        logger.info("Sending delivered email")
        email_service.send_accesory_delivered(existing_order, changed_line_item)

    start_time = time.perf_counter() 

    user_id = user.id.replace("auth0|", "")
    try:
        assistant = await assistant_crud.get_by_assistant_id(user_id)
    except HTTPException as e:
        if e.status_code == 404:
            assistant = None
        else:
            raise e

    user_ids = [user_id]
    if assistant:
        user_ids.append(assistant.manager.id)

    if existing_order.user.id != user_id:
        user_ids.append(existing_order.user.id)

    statuses = [existing_order.status]
    if existing_order.status in ['Paid', 'first_payment_received', 'Pod']:
        statuses += ['To_Deliver']

    if existing_order.type == 'RENT' and existing_order.status in ['Delinquent', 'Delivered']:
        statuses += ['On_Rent']

    order_line_items_loaded = await partial_order_crud.get_one_line_items(existing_order.id, user.app_metadata['account_id'])

    try:
        swap_cache(new_statuses=[],
                        old_statuses=[], 
                        swap_statuses=statuses, 
                        new_line_items=order_line_items_loaded,
                        order_type=existing_order.type,
                        user_ids=user_ids,
                        account_id=user.app_metadata['account_id'])
            
        swap_cache(new_statuses=[],
                        old_statuses=[], 
                        swap_statuses=statuses, 
                        new_line_items=order_line_items_loaded,
                        order_type="ALL",
                        user_ids=user_ids,
                        account_id=user.app_metadata['account_id'])
    except Exception as e:
        logger.error(str(e))
    # try:
    #     clear_cache(statuses, existing_order.type, user_ids, user.app_metadata['account_id'])
    # except Exception as e:
    #     logger.info(str(e))
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    logger.info(f'Redis Update Line Item - Execution time: {execution_time:.4f} seconds')


    return saved_line_items


async def send_pickup_email(line_item_id: str, user: Auth0User, background_tasks) -> Status:
    existing_line_item = await line_item_crud.get_one(user.app_metadata.get("account_id"), line_item_id)
    existing_order = await order_crud.get_one(existing_line_item.order.id)
    if existing_line_item.inventory.id and existing_order.is_pickup:
        found_location = await location_price_crud.get_by_city(
            existing_line_item.product_city, user.app_metadata.get("account_id")
        )
        account = await account_crud.get_one(user.app_metadata.get("account_id"))
        if account.name.startswith("USA Containers"):
            await pickup_event(
                existing_order,
                existing_line_item,
                found_location.pickup_region,
                existing_line_item.product_city,
                background_tasks,
            )
            # await email_service.send_customer_pickup_email(
            #     existing_order, existing_line_item, found_location.region, found_location.pickup_region
            # )
        else:
            await email_service_mailersend.send_customer_pickup_email(
                existing_order, existing_line_item, found_location.region
            )

            await note_crud.create(
                NoteInSchema(
                    title="Pick up instructions",
                    content=f"Pick up instructions have been emailed to the customer (line item {str(existing_line_item.id)[:5]})",
                    author_id=user.app_metadata.get("id"),
                    line_item_id=existing_line_item.id,
                    order_id=existing_line_item.order.id,
                )
            )

    await line_item_crud.db_model.filter(id=line_item_id).update(pickup_email_sent=True)

    return Status(message="Success sending pickup email")


async def get_line_item_by_inventory_id(inventory_id: str, user: Auth0User) -> list[LineItemOut]:
    try:
        line_item = (
            await line_item_crud.db_model.filter(inventory_id=inventory_id)
            .prefetch_related("order")
            .filter(order__account_id=user.app_metadata.get("account_id"))
        )
        return line_item
    except Exception as e:
        raise e


async def check_if_all_items_are_delivered(order_id):
    existing_order: Order = await order_crud.get_one(order_id)
    all_items_delivered = True
    now = datetime.now()
    for li in existing_order.line_items:
        if li.product_type == "CONTAINER_ACCESSORY":
            if li.delivery_date is None:
                all_items_delivered = False
                break
            elif li.delivery_date.replace(tzinfo=None) > now.replace(tzinfo=None):
                all_items_delivered = False
                break
        # else :
        #     if li.scheduled_date is None:
        #         all_items_delivered = False
        #         break
        #     elif li.scheduled_date.replace(tzinfo=None) > now.replace(tzinfo=None):
        #         all_items_delivered = False
        #         break
    return all_items_delivered
