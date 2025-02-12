
import time

from fastapi import HTTPException

from src.crud.assistant_crud import assistant_crud
from src.crud.partial_order_crud import partial_order_crud
from src.utils.order_update_in_cache import swap_cache
from loguru import logger

async def prepare_order_cache_swap(old_order, new_order, user_id, account_id):    
    start_time = time.perf_counter()

    user_ids = [user_id]
    try:
        assistant = await assistant_crud.get_by_assistant_id(user_id)
    except HTTPException as e:
        if e.status_code == 404:
            assistant = None
        else:
            raise e
    if assistant:
        user_ids.append(assistant.manager.id)

    if user_id != old_order.user.id:
        user_ids.append(old_order.user.id)
    if user_id != new_order.user.id:
        user_ids.append(new_order.user.id)

    old_statuses = [old_order.status]
    new_statuses = [new_order.status]

    if old_order.status.upper() == 'TO_DELIVER':
        old_statuses += ['Paid', 'Pod', 'First_Payment_Received']

    if new_order.status != old_order.status and new_order.status.upper() == 'TO_DELIVER':
        new_statuses += ['Paid', 'Pod', 'First_Payment_Received']

    if old_order.status in ['Paid', 'Pod', 'First_Payment_Received']:
        old_statuses += ['To_Deliver']

    if new_order.status != old_order.status and new_order.status in ['Paid', 'Pod', 'first_payment_received']:
        new_statuses += ['To_Deliver']

    if old_order.type == 'RENT' and old_order.status.upper() == 'ON_RENT':
        old_statuses += ['Delinquent', 'Delivered']

    if new_order.type == 'RENT' and new_order.status != old_order.status and new_order.status.upper() == 'ON_RENT':
        new_statuses += ['Delinquent', 'Delivered']

    if old_order.type == 'RENT' and old_order.status in ['Delinquent', 'Delivered']:
        old_statuses += ['On_Rent']

    if new_order.type == 'RENT' and new_order.status != old_order.status and new_order.status in ['Delinquent', 'Delivered']:
        new_statuses += ['On_Rent']
    
    order_line_items_loaded = await partial_order_crud.get_one_line_items(old_order.id, account_id=account_id)
    if old_order.status != new_order.status:
        try:
            swap_cache(new_statuses=new_statuses,
                        old_statuses=old_statuses, 
                        swap_statuses=[], 
                        new_line_items=order_line_items_loaded,
                        order_type=old_order.type,
                        user_ids=user_ids,
                        account_id=account_id)
            
            swap_cache(new_statuses=new_statuses,
                        old_statuses=old_statuses, 
                        swap_statuses=[], 
                        new_line_items=order_line_items_loaded,
                        order_type="ALL",
                        user_ids=user_ids,
                        account_id=account_id)
        except Exception as e:
            logger.error(str(e))
    else:
        swap_statuses = [new_order.status]
        if new_order.status.upper() == 'TO_DELIVER':
            swap_statuses += ['Paid', 'Pod', 'First_Payment_Received']

        if new_order.status in ['Paid', 'Pod', 'First_Payment_Received']:
            swap_statuses += ['To_Deliver']

        if new_order.type == 'RENT' and new_order.status.upper() == 'ON_RENT':
            swap_statuses += ['Delinquent', 'Delivered']

        if new_order.type == 'RENT' and new_order.status in ['Delinquent', 'Delivered']:
            swap_statuses += ['On_Rent']

        try:
            swap_cache(new_statuses=[],
                        old_statuses=[], 
                        swap_statuses=swap_statuses, 
                        new_line_items=order_line_items_loaded,
                        order_type=old_order.type,
                        user_ids=user_ids,
                        account_id=account_id)
            
            swap_cache(new_statuses=[],
                        old_statuses=[], 
                        swap_statuses=swap_statuses, 
                        new_line_items=order_line_items_loaded,
                        order_type="ALL",
                        user_ids=user_ids,
                        account_id=account_id)
        except Exception as e:
            logger.error(str(e))
    
    # try:
    #     clear_cache(statuses, old_order.type, user_ids, Auth0User.app_metadata['account_id'])
    # except Exception as e:
    #     logger.info(str(e))

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    logger.info(f'Redis Update Order - Execution time: {execution_time:.4f} seconds')