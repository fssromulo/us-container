# Python imports
import json
import os
from typing import List

# Pip imports
import requests
from tortoise import Model, Tortoise

# Internal imports
from src.auth.auth import Auth0User
from src.crud.reports_crud import reports_crud
from src.lambdas.process_reports import clean_run_by, compute_hash, async_handler
from src.schemas.reports import FilterObject
from src.crud.vendor_crud import vendor_crud
from src.crud.order_commission_crud import order_commission_crud, OrderCommissionIn

STAGE = os.environ.get("STAGE", "dev")


async def get_reports(user: Auth0User) -> List[Model]:
    return await reports_crud.get_all(user.app_metadata['account_id'])


async def get_report(id: str, user: Auth0User) -> Model:
    return await reports_crud.get_one(user.app_metadata['account_id'], id)


async def get_reports_by_name(name: str, user: Auth0User) -> Model:
    return await reports_crud.get_by_name(user.app_metadata['account_id'], name)


async def run_reports_by_name_without_lambda(name: str, filter: FilterObject, user: Auth0User) -> dict:
    obj = {
        "query": str(name),
        "run_by": str(filter.run_by),
        "begin_date": str(filter.begin_date),
        "end_date": str(filter.end_date),
        "conditions": str(filter.conditions),
        "productTypes": str(filter.productTypes),
        "account_id": str(user.app_metadata["account_id"]),
        "states": str(filter.states),
        "statuses": str(filter.statuses),
        "role_id": str(filter.role_id),
        "purchase_type": str(filter.purchase_type),
        "vendors": str(filter.vendors),
        "order_ids": str(filter.order_ids),
        "manager": str(filter.manager),
        "can_read_all": str(filter.can_read_all),
        "user_id": str(filter.user_id),
        "purchase_types": str(filter.purchase_types),
    }

    obj = {"Records": [{"body": json.dumps(obj)}]}

    await async_handler(obj, None)
    return


def run_reports_by_name(name: str, filter: FilterObject, user: Auth0User) -> dict:
    url = (
        "https://msjhei7pj6.execute-api.us-west-2.amazonaws.com/dev/"
        if STAGE == "dev"
        else "https://h55aecwzjh.execute-api.us-west-2.amazonaws.com/prod/"
    )

    run_by = clean_run_by(filter.run_by)

    params = f"report?query={name}&run_by={run_by}&begin_date={filter.begin_date}&end_date={filter.end_date}&account_id={user.app_metadata['account_id']}&conditions={filter.conditions}&productTypes={filter.productTypes}&statuses={filter.statuses}&states={filter.states}&role_id={filter.role_id}&purchase_type={filter.purchase_type}&vendors={filter.vendors}&order_ids={filter.order_ids}&manager={filter.manager}&can_read_all={filter.can_read_all}&user_id={filter.user_id}&purchase_types={filter.purchase_types}"

    req_url = url + params
    headers = {"x-api-key": f"7d9dc87a-2244-4eae-8b7c-8b913ed0a6f5-{STAGE}"}
    response = requests.get(req_url, headers=headers, timeout=30)
    return response.json()


async def clear_by_name(name, account_id):
    await reports_crud.delete_by_name(name, account_id)


async def save_commissions(data, account_id):
    order_commissions = []
    for item in data.result:
        manager_commission = item['manager_commission'] if item['manager_commission'] else 0
        agent_commission = item['agent_commission'] if item['agent_commission'] else 0

        order_commissions.append(
            OrderCommissionIn(
                is_team_commission=False,
                paid_at=item['paid_at'],
                completed_at=item['completed_at'],
                delivered_at=item['delivered_at'],
                sub_total_price=item['subtotal_amount'],
                total_price=item['total_price'],
                profit=item['profit'],
                is_team_lead=None,
                managing_agent_id=item['manager_id'],
                agent_id=item['agent_id'],
                can_see_profit=True,
                account_id=account_id,
                manager_commission_owed=item['manager_commission'],
                agent_commission_owed=item['agent_commission'],
                display_order_id=item['display_order_id'],
                total_commission=manager_commission + agent_commission,
            )
        )

    await order_commission_crud.bulk_create(order_commissions, len(order_commissions))


async def retrieve_by_name(name: str, filter: FilterObject) -> Model:
    obj = {
        "query": str(name),
        "run_by": str(filter.run_by),
        "begin_date": str(filter.begin_date),
        "end_date": str(filter.end_date),
        "conditions": str(filter.conditions),
        "productTypes": str(filter.productTypes),
        "account_id": str(filter.account_id),
        "statuses": str(filter.statuses),
        "states": str(filter.states),
        "role_id": str(filter.role_id),
        "purchase_type": str(filter.purchase_type),
    }

    hash = compute_hash(json.loads(json.dumps(obj)))
    result = await reports_crud.get_by_hash(filter.account_id, name, hash)

    if len(result) == 0:
        return None
    else:
        return result[0]


async def get_vendors(account_id):
    vendors = await vendor_crud.get_all(account_id=account_id)
    return [x.name for x in vendors]


async def get_product_types():
    return [
        {'Result': '10 Used High Cube Double Door'},
        {'Result': '10 Used High Cube'},
        {'Result': '10 Used Double Door'},
        {'Result': '10 Used Standard'},
        {'Result': '10 One-Trip High Cube Double Door'},
        {'Result': '10 One-Trip High Cube'},
        {'Result': '10 One-Trip Double Door'},
        {'Result': '10 One-Trip Standard'},
        {'Result': '20 Used High Cube Double Door'},
        {'Result': '20 Used High Cube'},
        {'Result': '20 Used Double Door'},
        {'Result': '20 Used Standard'},
        {'Result': '20 One-Trip High Cube Double Door'},
        {'Result': '20 One-Trip High Cube'},
        {'Result': '20 One-Trip Double Door'},
        {'Result': '20 One-Trip Standard'},
        {'Result': '40 Used High Cube Double Door'},
        {'Result': '40 Used High Cube'},
        {'Result': '40 Used Double Door'},
        {'Result': '40 Used Standard'},
        {'Result': '40 One-Trip High Cube Double Door'},
        {'Result': '40 One-Trip High Cube'},
        {'Result': '40 One-Trip Double Door'},
        {'Result': '40 One-Trip Standard'},
    ]
