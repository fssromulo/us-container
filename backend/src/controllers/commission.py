# Python imports
import uuid
from decimal import Decimal
from typing import Dict, List

# Pip imports
from fastapi import HTTPException, status
from loguru import logger
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

# Internal imports
from src.auth.auth import Auth0User
from src.config import settings
from src.crud.commission_crud import commission_crud
from src.crud.order_commission_crud import order_commission_crud
from src.crud.order_crud import order_crud
from src.crud.user_crud import user_crud
from src.database.models.comission import Commission
from src.database.models.order_comission import OrderCommision
from src.database.models.user import User
from src.schemas.commission import CommissionIn, CommissionOut
from src.schemas.order_commission import OrderCommissionIn, OrderCommissionOut
from src.schemas.users import UserOutSchema
from src.utils.users import ROLES_DICT, get_ids_from_user, get_user_ids
from src.crud.partial_order_crud import partial_order_crud

STAGE: str = settings.STAGE


async def create_commission(commission: CommissionIn, user: Auth0User) -> Model:
    saved_commission = await commission_crud.create(commission)
    return saved_commission


async def search_pickup_and_delivered(user, searched_user_ids, start_date, end_date):
    orders_list = []
    orders = await partial_order_crud.search_orders(
        user.app_metadata["account_id"],
        user_ids=searched_user_ids,
        start_date=start_date,
        end_date=end_date,
        delivered_at=True,
    )
    orders_list.extend([order for order in orders])

    pickup_orders = await partial_order_crud.search_orders(
        user.app_metadata["account_id"],
        user_ids=searched_user_ids,
        status="Completed",
        pickup=True,
        start_date=start_date,
        end_date=end_date,
        completed_at=True,
    )
    orders_list.extend([order for order in pickup_orders])

    # remove duplicates from order list
    orders_list = list({order.id: order for order in orders_list}.values())
    return orders_list


async def generate_commissions(
    user: Auth0User,
    user_id: str = None,
    emulated_user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    team: bool = False,
    user_commissions: list = [],
    order_commission: bool = False,
):
    """
    Generates commission data for a user or a team within a specified date range.

    This function computes the commissions based on the orders picked up and delivered
    in the given time frame. It can operate in various modes, such as team mode, individual mode,
    and emulated user mode, adjusting its behavior based on the permissions of the user making the request.
    It supports filtering by user, team, and date range, and can also compute order-based commissions.

    Parameters:
    - user (Auth0User): The user object, containing permissions and metadata.
    - user_id (str, optional): The ID of the user for whom to generate commissions. If not specified, uses the ID from the `user` object.
    - emulated_user_id (str, optional): The ID of the user to emulate, if the requester has the appropriate permissions.
    - start_date (str, optional): The start date for the period to calculate commissions, in a string format.
    - end_date (str, optional): The end date for the period to calculate commissions, in a string format.
    - team (bool, optional): Whether to calculate commissions for the team. Defaults to False.
    - order_commission (bool, optional): Whether to calculate commissions based on orders. Defaults to False.

    Returns:
    List[Commission]: A list of Commission objects calculated for the specified parameters.

    Raises:
    HTTPException: If no orders match the query or if an error occurs during the operation.

    This function uses several helper methods (`get_user_ids`, `user_crud.get_one`, `search_pickup_and_delivered`,
    `order_crud.search_orders`, `get_ids_from_user`, `commission_crud.get_all`, and `orderToCommission`) to perform its tasks.
    These methods are assumed to be asynchronous and interact with the database or external services.
    """

    # Attempt to execute the main logic of the function, capturing exceptions for error handling
    try:
        # Extract the account ID from the user's app metadata
        account_id = user.app_metadata["account_id"]
        searched_user_ids = None
        # Check if the user has permission to read all orders
        can_read_all = [p for p in user.permissions if p == "read:all_orders"]
        user_ids = None

        # If the user cannot read all orders or specific users are being searched, fetch the user IDs
        if not can_read_all or searched_user_ids:
            user_ids = await get_user_ids(
                account_id,
                user_id if user_id else user.id.replace("auth0|", ""),
                includeManager=True,
                includeTeam=True,
                includeTeamDeep=team,
            )

            searched_user_ids = user_ids

        # If an emulated user ID is provided and the user has the necessary permissions, emulate that user
        if emulated_user_id and len([p for p in user.permissions if p == "emulate:users"]):
            user = await user_crud.get_one(account_id, emulated_user_id)
            searched_user_ids = await get_user_ids(user)

        # Ensure all user IDs in the searched list are strings, or set to None if not applicable
        searched_user_ids = [str(user_id) for user_id in searched_user_ids] if searched_user_ids else None
        # Determine the length of the searched user IDs list for later use
        searched_user_ids_length = len(searched_user_ids) if searched_user_ids else 0

        # Retrieve a list of orders based on the specified parameters
        orders_list = await search_pickup_and_delivered(user, searched_user_ids, start_date, end_date)
        team_list: List[str] = None

        # Retrieve all users in the account for later processing
        all_users: List[UserOutSchema] = await user_crud.get_all(
            account_id
        )  # moving this out here so it can be accessible for the rest of the function

        # If the team mode is enabled, perform additional logic for team orders
        if team:
            qualifying_orders = await order_crud.filter_rankings(
                user.app_metadata["account_id"],
                user_ids=searched_user_ids,
                status="Paid,Delivered,Completed,Partially Paid",
                paid_at=True,
                start_date=start_date,
                end_date=end_date,
            )

            # If a specific user ID is provided, fetch that user, otherwise work with team leads
            if user_id:
                user = await user_crud.get_one(account_id, user_id)
                if not len(user.team_lead):
                    raise HTTPException(status_code=status.HTTP_200_OK, detail="No orders for query")
            else:
                team_leads = [u for u in all_users if len(u.team_lead)]
                # Ensure team leads are unique by their ID
                team_leads = list({team_lead.id: team_lead for team_lead in team_leads}.values())

            # Process each team lead, determining their team's eligibility based on total revenue
            for team_lead in team_leads:
                list_of_team_lead_agents = await get_ids_from_user(account_id, team_lead, includeManager=True)
                list_of_team_lead_agents.append(team_lead.id)

                list_of_team_lead_agents = [str(user_id) for user_id in list_of_team_lead_agents]
                # Check if the team lead is the only agent in their team
                if len(list_of_team_lead_agents) == 1:
                    if str(team_lead.id) == list_of_team_lead_agents[0]:
                        logger.info("team lead is only agent in team", team_lead.id)

                # sum of total revenue accross orders for this period must be 20k or greater
                # Calculate the total revenue from orders for this team lead and their agents
                total_revenue = sum(
                    [
                        order.calculated_total_price
                        for order in qualifying_orders
                        if str(order.user.id) in list_of_team_lead_agents
                    ]
                )
                # If the total revenue is less than the threshold, update the orders list to exclude these orders
                if total_revenue < 20000:
                    team_list = await get_ids_from_user(
                        account_id,
                        team_lead,
                        includeTeam=True,
                        includeTeamDeep=True,
                        includeManager=True,
                        all_users=all_users,
                    )
                    team_list = [str(user_id) for user_id in team_list]
                    orders_list = [order for order in orders_list if str(order.user.id) not in team_list]

        # Retrieve all commission history for the account
        all_commission_history: List[CommissionOut] = await commission_crud.get_all(account_id)
        # building a dictionary of all the commission history for a given account so that we can do quick filtering and lookup for information to improve speed and performance
        all_commission_hist_dict: Dict[str, CommissionOut] = {}
        for item in all_commission_history:
            # item_user_id = item.user.id
            # check if item is a dict or a Commission object, and get the user ID accordingly
            item_user_id = item.user.id if isinstance(item, CommissionOut) else item.get("user").get("id")

            # Check if the user_id is already in the dictionary
            if item_user_id in all_commission_hist_dict:
                # If it's already there, append the item to the list
                all_commission_hist_dict[item_user_id].append(item)
            else:
                # If it's not in the dictionary, create a new list and add the item
                all_commission_hist_dict[item_user_id] = [item]

        all_users_dict: dict = {}

        # building a dictionary of users from the all_users so that we can do quick look ups for information in ordertocommission
        for item in all_users:
            all_users_dict[item.id] = item

        # find the current user in the all user dict
        # Determine the current user from the user ID or the authenticated user
        current_user: User = None
        if user_id:
            current_user = all_users_dict[uuid.UUID(user_id)]
        else:
            current_user_id = user.id.replace("auth0|", "")
            current_user = all_users_dict[uuid.UUID(current_user_id)]

        # Set the override rate based on whether team mode is active
        overrideRate = Decimal(0.05) if team else None  # this satisfies the code in Commission.js on line 248
        # Calculate commission for each order in the list
        orderCommission = [
            await orderToCommission(
                order,
                current_user,
                searched_user_ids_length,
                overrideRate,
                order_commission,
                all_users_dict=all_users_dict,
                all_commission_hist_dict=all_commission_hist_dict,
                user_commissions=user_commissions,
            )
            for order in orders_list
        ]

        # if not can_read_inventory:
        #     return [remove_driver_inventory(o) for o in orders_list]
        # Return the list of calculated commissions
        return orderCommission
    except DoesNotExist:
        # Handle case where no orders match the query by raising an HTTP exception
        raise HTTPException(status_code=status.HTTP_200_OK, detail="No orders for query")


async def update_commission_period(
    auth_user: Auth0User,
    start_date: str = None,
    end_date: str = None,
    team: bool = False,
    open: bool = False,
    is_Manager_Only: bool = True,
):
    if open:
        await order_commission_crud.delete_period(
            auth_user.app_metadata["account_id"], start_date=start_date, end_date=end_date, is_team=team
        )
        return
    else:
        await order_commission_crud.delete_period(
            auth_user.app_metadata["account_id"], start_date=start_date, end_date=end_date, is_team=team
        )
    # fetch commissions for all users
    user_commissions = await commission_crud.get_all(auth_user.app_metadata["account_id"])
    logger.info("USER COMMISSION LENGTH", len(user_commissions))

    commission_result: dict = await generate_commissions(
        user=auth_user,
        user_id=None,
        emulated_user_id=None,
        start_date=start_date,
        end_date=end_date,
        team=team,
        order_commission=False,
        user_commissions=user_commissions,
    )

    # commenting this out, because in the new ordertocommission, alot of this logic already exists
    # users = await user_crud.get_all(auth_user.app_metadata["account_id"])
    commission_list = []
    for order in commission_result:
        user = order[
            "user"
        ]  # this user will always be the manager if there is an assistant or just the manager as an agent

        team_lead_id = None
        manager_id = None
        agent_id = user.id  # but if there is not an assistant, then we keep the default being the manager
        if user.team_member:
            team_lead_id = user.team_member.team_lead.id
        if order["assistant_obj"]:
            manager_id = user.id
            agent_id = order[
                "assistant_obj"
            ].id  # if there is an assistant, then they become the agent, and teh manager assumes the managerial role
            manager = user
            if manager.team_member:
                team_lead_id = manager.team_member.team_lead.id

        commission_list.append(
            OrderCommissionIn(
                display_order_id=order["display_order_id"],
                is_team_commission=team,
                paid_at=order["paid_at"],
                completed_at=order["completed_at"],
                delivered_at=order["delivered_at"],
                sub_total_price=order["sub_total_price"],
                total_price=order["total_price"],
                profit=order["calculated_profit"],
                is_team_lead=len(user.team_lead) > 0,
                team_lead_id=team_lead_id,
                managing_agent_id=manager_id,
                agent_id=agent_id,
                account_id=order["account_id"],
                total_commission=order["commission_owed"],
                manager_commission_owed=order["manager_commission_owed"],
                agent_commission_owed=order["agent_commission_owed"],
            )
        )
    await OrderCommision.bulk_create([OrderCommision(**c.dict()) for c in commission_list])
    return await close_commission_result(
        auth_user=auth_user,
        user_id=None,
        emulated_user_id=None,
        start_date=start_date,
        end_date=end_date,
        team=team,
        is_manager_only=is_Manager_Only,
        user_commissions=user_commissions,
    )


def calculate_commissions(flats, searched_user_ids_length, is_Manager_Only: bool, isTeam=None):
    result = []

    for curr in flats:
        if (isTeam and not curr['team_lead']) or (not isTeam and not curr['user']):
            continue
        if (
            "sales_agent" == ROLES_DICT.get(STAGE, {}).get(str(curr['user'].role_id), {})
            or not curr.get('can_see_profit', True)
            and searched_user_ids_length == 1
        ):
            curr.pop('profit', None)
            curr.pop('calculated_profit', None)
            curr.pop('commission_owed', None)

        user = curr['user']
        team_lead = curr.get('team_lead')
        agent = curr.get('agent')
        key = 'team_lead' if isTeam else 'user'
        id_ = team_lead.id if isTeam else user.id

        sub_total_price = curr.get('sub_total_price', 0)
        commission_owed = curr.get('commission_owed', 0)

        assistant = curr.get('assistant')
        assistant_obj = curr.get("assistant_obj")
        assistant_id_ = assistant_obj.id if assistant_obj else None
        manager_commission_owed: Decimal = curr.get("manager_commission_owed")
        agent_commission_owed: Decimal = curr.get("agent_commission_owed")

        agentCommission = next((item for item in result if item[key].id == id_), None)
        assistantCommission = next((item for item in result if item[key].id == assistant_id_), None)
        if (
            assistant_id_ and not is_Manager_Only
        ):  # if there is an assistant and we are looking at everyone, then we want to calculate the agent's commission too
            if not assistantCommission:
                assistantCommission = {
                    key: assistant_obj,
                    'agent': assistant,
                    'commission_owed': 0,
                }
                result.append(assistantCommission)
            if agent_commission_owed:
                assistantCommission["commission_owed"] += agent_commission_owed

        if not agentCommission:
            if is_Manager_Only:
                agentCommission = {
                    key: team_lead if isTeam else user,
                    'agent': team_lead.full_name if isTeam else agent,
                    'sub_total_price': 0,
                    'commission_owed': 0,
                }
                result.append(agentCommission)
            else:
                agentCommission = {
                    key: team_lead if isTeam else user,
                    'agent': team_lead.full_name if isTeam else agent,
                    'commission_owed': 0,
                }
                result.append(agentCommission)

        if is_Manager_Only:
            agentCommission['sub_total_price'] += sub_total_price
            agentCommission['commission_owed'] += commission_owed
        else:
            agentCommission["commission_owed"] += manager_commission_owed or 0

    return result


def map_commission_rates_user_id(user_commission_rate_obj):
    if isinstance(user_commission_rate_obj, CommissionOut):
        return user_commission_rate_obj.user.id
    return user_commission_rate_obj.get("user").get("id")


def get_commission_by_order_paid_date(commission_history: Commission, order_paid_date):
    try:
        return commission_history.commission_effective_date <= order_paid_date
    except Exception as e:
        logger.error(f"Error in get_commission_by_order_paid_date: {e}")
        return False


# user_ids = await get_ids_from_user(auth_user.app_metadata["account_id"], user, includeManager=True)
async def orderToCommission(
    order,
    current_user: User,
    searched_user_ids_length,
    overrideRate=None,
    is_closed=True,
    all_users_dict: dict = None,
    all_commission_hist_dict: dict = None,
    actual_orders: list = [],
    user_commissions: list = [],
):
    """
    Calculate commission for an order based on given parameters.

    Params:
        order: The order information, typically a dictionary.
        overrideRate (float, optional): An optional override commission rate.
        order_commission (bool, optional): A flag to indicate if the incomming orders are from the order_commission table, indicating
        if they are closed/frozen orders
        all_users_dict(dict, optional): This is an optional dictionary for users that will provide
        quick lookups for user information

    """

    # Determine the profit from an order, defaulting to calculated profit if not explicitly set.
    order_profit = order.calculated_profit if hasattr(order, "calculated_profit") else order.profit

    actual_order = order
    # order can be of type Order or OrderCommissionOut
    if isinstance(order, OrderCommissionOut):
        # actual_order = await order_crud.get_one_by_display_id(1, order.display_order_id)
        actual_order = [x for x in actual_orders if x.display_order_id == order.display_order_id][0]

    # Initialize variables for managing different components of the commission.
    total_commission_owed: Decimal = 0.0
    manager_commission_owed: Decimal = 0.0
    agent_commission_owed: Decimal = 0.0
    rate: Decimal = 0.0
    calculated_total_price: Decimal = 0.0
    account_id: int = order.account_id
    is_percentage: bool = True
    manager_flat_rate: Decimal = 0.0
    commission_obj: Commission = None

    # Handling for orders that are closed/frozen, where commission data is readily available.
    # This one pulls from order_commission so all the data is already there for them
    if is_closed:
        # Determine the primary user associated with the order, either a managing agent or an agent.
        order_user = order.managing_agent if order.managing_agent else order.agent
        assistant = order.agent if order.managing_agent else None
        filtered_user = [o for o in user_commissions if map_commission_rates_user_id(o) == order_user.id]

        # Calculate the commission rate, allowing for an override if provided.

        fetched_rate = 0 if len(filtered_user) == 0 else filtered_user[0].commission_percentage / 100
        rate = overrideRate or fetched_rate

        # Directly use commission data available from the order.
        total_commission_owed = order.total_commission
        manager_commission_owed = order.manager_commission_owed
        agent_commission_owed = order.agent_commission_owed
        calculated_total_price = order.total_price
    else:
        # For open orders, perform additional logic to calculate commissions.
        if current_user.role_id == ROLES_DICT.get(STAGE, {}).get("sales_agent"):
            # If the current user is a sales agent and not the order's user, exit the function.
            if order.user.id != current_user.id:
                return

        # Re-fetch the user from the all_users_dict to ensure all relations are included bc the order.user does not have all the deep relations that are needed.
        user = all_users_dict.get(order.user.id)

        # Determine the user responsible for the order, taking into account assistants and managers.
        order_user = all_users_dict.get(user.assistant.manager.id) if user.assistant else user
        assistant = order.user if order.user.full_name != order_user.full_name else None
        # Calculate or override the commission rate
        filtered_user = [o for o in user_commissions if map_commission_rates_user_id(o) == order_user.id]

        fetched_rate_percentage = 0 if len(filtered_user) == 0 else filtered_user[0].commission_percentage / 100
        fetched_rate_flat = None if len(filtered_user) == 0 else filtered_user[0].flat_commission

        manager_flat_rate = (
            Decimal("0") if len(filtered_user) == 0 else filtered_user[0].rental_total_flat_commission_rate
        )
        rate = overrideRate or fetched_rate_percentage
        calculated_total_price = order.calculated_total_price

        # Calculate total commission owed based on the order profit and rate.
        total_commission_owed = round((order_profit * rate), 4)

        if fetched_rate_flat and not assistant:
            total_commission_owed = fetched_rate_flat

    if actual_order.type == 'RENT':
        total_commission_owed = 0

    # Process commissions for assistant roles, considering their commission history.
    # If this is an agent sale, then we will see if they have any commission history, if they do not then it will just be 0 for now
    if assistant:
        # if there is an assistant, then we will look in their commission history and grab all the records
        # where the order paid date is greater than or equal to the commission_effective_date, then with
        # those, we will order those by the commission_effective_date ascending so that the most recent one
        # will be used to determine the type of commission. this will always prevent us grabbing a future
        # commission that should not have affected that paid order bc we will grab the earliest of the commissions
        # where the paid order's date is greater than or equal to.
        # ex: The commission is paid when the order is Mark delivered The percentage is decided the
        #   time the order is paid for So I have a 20% commission set from Aug 1-31 I have 5 orders
        #   paid in Aug. All 5 of those Deliver/Complete sept 5th Sept 1. My commission goes to 30%
        #   I'm paid 20% on these 5 though.

        if not is_closed:
            # Sanitize user manager data for privacy before returning.
            # It won't let me do del on that UserOut obj and other parts of the system use user.manager atributes
            # We want to remove thse from the return object so that the agents cannot see any of this data
            remove_user_manager = order_user.dict()
            remove_user_manager["manager"] = []
            remove_user_manager["team_lead"] = []
            # remove_user_manager["team_member"]["team_member"]["manager"]=[]
            order_user = UserOutSchema(**remove_user_manager)

        commission_obj: Commission = None
        if all_commission_hist_dict:
            # Retrieve the assistant's commission history, if available.
            assistant_commission_history: List[Commission] = all_commission_hist_dict.get(assistant.id)

            # Filter and sort the commission history based on the order's paid date.
            if assistant_commission_history:  # only do this logic, if they have a history in the table

                if actual_order.type == 'RENT':
                    assistant_commission_history = list(
                        filter(
                            lambda x: get_commission_by_order_paid_date(x, actual_order.delivered_at),
                            assistant_commission_history,
                        )
                    )
                else:
                    assistant_commission_history = list(
                        filter(
                            lambda x: get_commission_by_order_paid_date(x, order.paid_at), assistant_commission_history
                        )
                    )
                if assistant_commission_history:
                    assistant_commission_history = sorted(
                        assistant_commission_history, key=lambda x: x.created_at, reverse=True
                    )
                    # Use the most recent commission rate from the sorted history.
                    commission_obj = assistant_commission_history.pop(0)

        # this is making sure they have records in the commission obj
        # Calculate the commission owed to the assistant, based on commission type.
        if commission_obj:
            if actual_order.type == 'RENT':
                if (
                    commission_obj.rental_total_flat_commission_rate != 0
                    and commission_obj.commission_percentage is not None
                ):
                    is_percentage = False
                    if not is_closed:
                        if (
                            actual_order.rent_periods
                            and len(actual_order.rent_periods) >= 1
                            and actual_order.rent_periods[0].calculated_rent_period_total_balance == 0
                            and actual_order.delivered_at is not None
                        ):

                            agent_commission_owed = round(
                                (commission_obj.rental_total_flat_commission_rate * len(actual_order.line_items)), 4
                            )
                            total_commission_owed = manager_flat_rate * len(actual_order.line_items)

            else:
                if commission_obj.commission_percentage != 0 and commission_obj.commission_percentage is not None:
                    if not is_closed:
                        agent_commission_owed = round(
                            order_profit * (commission_obj.commission_percentage / 100), 4
                        )  # changed to be agent commission percentage of the ORDER_PROFIT and not just the agent cut
                else:
                    is_percentage = False
                    if not is_closed:
                        agent_commission_owed = round((commission_obj.flat_commission * len(order.line_items)), 4)
        else:
            is_percentage = False

    if commission_obj is None and actual_order.type == 'RENT':
        logger.info("SUPPOSEDLY UNREACHABLE")
        commission_obj = None
        manager_commission_history: List[Commission] = all_commission_hist_dict.get(actual_order.user.id)
        if manager_commission_history:
            manager_commission_history = list(
                filter(
                    lambda x: get_commission_by_order_paid_date(x, actual_order.delivered_at),
                    manager_commission_history,
                )
            )
            manager_commission_history = sorted(manager_commission_history, key=lambda x: x.created_at, reverse=True)
            # Use the most recent commission rate from the sorted history.
            commission_obj = manager_commission_history.pop(0)

        if commission_obj:
            if (
                actual_order.rent_periods
                and len(actual_order.rent_periods) >= 1
                and actual_order.rent_periods[0].calculated_rent_period_total_balance == 0
                and actual_order.delivered_at is not None
            ):
                manager_commission_owed = round(
                    (commission_obj.rental_total_flat_commission_rate * len(actual_order.line_items)), 4
                )
                total_commission_owed = manager_commission_owed
    else:

        # Calculate the manager's commission by subtracting the agent's commission from the total.
        manager_commission_owed = round(
            (
                total_commission_owed - Decimal(agent_commission_owed or 0)
                if agent_commission_owed
                else total_commission_owed
            ),
            4,
        )

    return_obj: dict = {
        'id': order.id,
        'team_lead': getattr(order, "team_lead", None),
        'user': order_user,
        'agent': order_user.full_name if order_user else None,
        'assistant': assistant.full_name if assistant else "N/A",
        'display_order_id': order.display_order_id,
        'delivered_at': order.delivered_at,
        'completed_at': order.completed_at,
        'paid_at': order.paid_at,
        'sub_total_price': round(order.calculated_sub_total_price, 4)
        if hasattr(order, "calculated_sub_total_price")
        else order.sub_total_price,
        'calculated_profit': round(order_profit, 4),
        'commission_owed': round(total_commission_owed, 4)
        if total_commission_owed
        else round(
            order_profit * rate, 4
        ),  # if there is not a total_commission in the order_commissino table, that means it is an old record, so we will just return what we have been which is order_profit * rate
        "manager_commission_owed": round(manager_commission_owed, 4)
        if manager_commission_owed
        else None,  # if there is not a manager_commission in the ordre_commission table, then that means it is an old record so we will just return null. Same for the agent_commission
        "agent_commission_owed": round(agent_commission_owed, 4)
        if agent_commission_owed
        else None,  # this will return the amount if they were an agent, and a 0 if they were not
        "total_price": round(
            calculated_total_price, 4
        ),  # adding this field to accommodate for the update commission period function
        "account_id": account_id,  # adding this field to accommodate for the update commission period function
        "assistant_obj": assistant if assistant else None,
    }
    # if it is not a percentage, then we do not want to display the order profit to the agent
    # and we will only take it away if the current user looking at them is a sales agent
    if (
        current_user.role_id == ROLES_DICT.get(STAGE, {}).get("sales_agent")
        and assistant
        and searched_user_ids_length <= 1
    ):
        del return_obj["manager_commission_owed"]
        del return_obj["commission_owed"]
        if is_closed:
            logger.info(is_percentage)
            if not order.can_see_profit or not is_percentage:
                del return_obj["calculated_profit"]
        else:
            if not is_percentage:
                del return_obj["calculated_profit"]
    return return_obj


async def closed_commissions_date(dates, user):
    commissions = await order_commission_crud.get_period(
        account_id=user.app_metadata["account_id"],
        start_date=dates['start_date'],
        end_date=dates['end_date'],
        user_ids=None,
        is_team=False,
        user_id=user.id.replace("auth0|", ""),
    )

    closed_date = commissions[0].created_at if len(commissions) > 0 else None
    return closed_date


async def close_commission_result(
    auth_user: Auth0User,
    user_id: str = None,
    emulated_user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    team: bool = False,
    is_manager_only: bool = True,
    period_name: str = None,
    user_commissions: list = [],
):
    account_id = auth_user.app_metadata["account_id"]
    searched_user_ids = None
    can_read_all = [p for p in auth_user.permissions if p == "read:all_orders"]
    user_ids = None
    if not can_read_all or user_id:
        user_ids = await get_user_ids(
            account_id,
            user_id if user_id else auth_user.id.replace("auth0|", ""),
            includeManager=True,
            includeTeam=False,
            includeTeamDeep=False,
        )
        searched_user_ids = user_ids

    if emulated_user_id and len([p for p in auth_user.permissions if p == "emulate:users"]):
        user_ids = await get_user_ids(
            account_id,
            emulated_user_id,
            includeManager=True,
            includeTeam=team,
            includeTeamDeep=False,
        )
        searched_user_ids = user_ids

    searched_user_ids = [str(user_id) for user_id in searched_user_ids] if searched_user_ids else None
    searched_user_ids_length = len(searched_user_ids) if searched_user_ids else 0
    commissions = await order_commission_crud.get_period(
        account_id=auth_user.app_metadata["account_id"],
        start_date=start_date,
        end_date=end_date,
        user_ids=searched_user_ids,
        is_team=team,
        user_id=user_id,
    )

    all_users: List[User] = await user_crud.get_all(account_id)

    all_users_dict: dict = {}
    # building a dictionary of users from the all_users so that we can do quick look ups for information in ordertocommission
    for item in all_users:
        all_users_dict[item.id] = item

    # find the current user in the all user dict
    current_user: User = None
    if user_id:
        current_user = all_users_dict[uuid.UUID(user_id)]
    else:
        current_user_id = auth_user.id.replace("auth0|", "")
        current_user = all_users_dict[uuid.UUID(current_user_id)]
    closed_date = commissions[0].created_at if len(commissions) > 0 else None
    overrideRate = Decimal(0.05) if team else None
    all_commission_history: List[CommissionOut] = await commission_crud.get_all(account_id)
    # building a dictionary of all the commission history for a given account so that I can do quick filtering and lookup for information to improve speed and performance
    all_commission_hist_dict: Dict[str, CommissionOut] = {}
    for item in all_commission_history:
        item_user_id = item.user.id if isinstance(item, CommissionOut) else item.get("user").get("id")

        # Check if the user_id is already in the dictionary
        if item_user_id in all_commission_hist_dict:
            # If it's already there, append the item to the list
            all_commission_hist_dict[item_user_id].append(item)
        else:
            # If it's not in the dictionary, create a new list and add the item
            all_commission_hist_dict[item_user_id] = [item]

    all_users_dict: dict = {}
    # building a dictionary of users from the all_users so that we can do quick look ups for information in ordertocommission
    for item in all_users:
        all_users_dict[item.id] = item

    actual_orders = await order_crud.get_by_display_order_ids(1, [x.display_order_id for x in commissions])

    orderCommission = [
        await orderToCommission(
            order,
            current_user,
            searched_user_ids_length,
            overrideRate,
            True,
            all_users_dict,
            all_commission_hist_dict,
            actual_orders,
            user_commissions,
        )
        for order in commissions
    ]
    if searched_user_ids:
        return {'commissions': orderCommission, 'closed_date': closed_date}
    return {
        'commissions': calculate_commissions(orderCommission, searched_user_ids_length, is_manager_only, team),
        'closed_date': closed_date,
    }
