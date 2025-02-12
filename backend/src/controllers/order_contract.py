# Python imports

# Python imports
import asyncio
from typing import Dict, List

# Pip imports
from fastapi import status
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.crud.account_crud import account_crud
from src.crud.order_contract_crud import order_contract_crud
from src.database.models.account import Account
from src.database.models.order_contract import OrderContract
from src.schemas.order_contract import OrderContractIn


lock = asyncio.Lock()

statuses_levels = {
    "contract-sent-to-signer": 1,
    "signer-viewed-the-contract": 2,
    "signer-signed": 3,
    "contract-signed": 4,
}


async def save_order_contract(order_contract_dict: dict) -> str:
    return_status = ""
    # This will allow for multiple requests to come in at the same time, but they will be handled syncronously.
    async with lock:
        # getting a fresh order every time so we can capture any updates
        # order: Order = await order_crud.get_one(order.id)
        # if len(order.order_contract) > 0:
        # if there is not an order contract with this id already, then we just create one,
        try:
            existing_order_contract: OrderContract = await order_contract_crud.get_one(
                order_contract_dict.get("contract_id", "")
            )
            if statuses_levels.get(order_contract_dict['status'], 5) <= statuses_levels.get(
                existing_order_contract.status, 5
            ):
                return status.HTTP_200_OK
            item_id: str = existing_order_contract.id
            order_contract_in = OrderContractIn(**order_contract_dict)
            await order_contract_crud.update(item_id, order_contract_in)
            return_status = status.HTTP_200_OK
        except DoesNotExist:
            await order_contract_crud.create(OrderContractIn(**order_contract_dict))
            return_status = status.HTTP_201_CREATED

    return return_status


async def is_autopay_from_signed_contract(order_id: str, account_id: int) -> bool:
    """
    This function will check the recently signed contract that has autopay information and will see if the user
    has opted to do autopay
    Note: This will only be effective and grab the proper information if the user has signed the contract
    """
    # We need to grab the most recent contract from order_contract whose title == account.cms_attributes.get("contract_title_with_rent_autopay_info", "")
    # then we need to grab the is_auto_pay_yes field from the signer_field_values
    # return is_auto_pay_yes == 1
    is_auto_pay: bool
    most_recent_contract_with_autopay_info: OrderContract
    account: Account = await account_crud.get_one(account_id)
    contract_title_with_autopay_info: str = account.cms_attributes.get("contract_title_with_rent_autopay_info", "")
    contracts: List[OrderContract] = await order_contract_crud.get_contracts_by_order_id(order_id)
    contracts_with_autopay_info: List[OrderContract] = []

    for contract in contracts:
        contract_title: str = contract.meta_data["data"]["contract"]["title"]
        if contract_title.lower() == contract_title_with_autopay_info.lower():
            contracts_with_autopay_info.append(contract)

    contracts_with_autopay_info.sort(key=lambda x: x.created_at, reverse=True)
    if len(contracts_with_autopay_info) == 0:
        return False
    most_recent_contract_with_autopay_info = contracts_with_autopay_info[0]

    # TODO assuming that there is only 1 signer at this time
    signer_field_values: Dict[str, str] = most_recent_contract_with_autopay_info.meta_data["data"]["contract"][
        "signers"
    ][0]["signer_field_values"]

    is_auto_pay_yes_field: str = signer_field_values.get("is_auto_pay_yes", "0")
    if is_auto_pay_yes_field:
        is_auto_pay = is_auto_pay_yes_field == "1"
        return is_auto_pay
