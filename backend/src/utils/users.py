# Python imports
from typing import Dict

# Internal imports
from src.crud.user_crud import user_crud


async def get_ids_from_user(
    account_id, user, includeTeam=False, includeManager=False, includeTeamDeep=False, all_users=None
):
    user_ids = []
    agents = [str(u.assistant.id) for u in user.manager] if includeManager else []
    team = [str(u.team_member.id) for u in user.team_lead] if includeTeam else []
    if includeTeamDeep:
        users_team = (
            [u for u in all_users if str(u.id) in team] if all_users else await user_crud.get_by_ids(account_id, team)
        )
        for team_member in users_team:
            team_member_agents = [str(u.assistant.id) for u in team_member.manager] if includeManager else []
            user_ids.extend(team_member_agents)

    user_ids.extend(agents)
    user_ids.extend(team)
    user_ids.append(id)
    user_ids = list(set(user_ids))
    return user_ids


async def get_user_ids(account_id, id, includeTeam=False, includeManager=False, includeTeamDeep=False):
    user_ids = []
    if not id:
        return user_ids

    existing_user = await user_crud.get_one(account_id, id)
    agents = [str(u.assistant.id) for u in existing_user.manager] if includeManager else []
    team = [str(u.team_member.id) for u in existing_user.team_lead] if includeTeam else []
    if includeTeamDeep:
        for u in team:
            team_member = await user_crud.get_one(account_id, u)
            team_member_agents = [str(u.assistant.id) for u in team_member.manager] if includeManager else []
            user_ids.extend(team_member_agents)

    user_ids.extend(agents)
    user_ids.extend(team)
    user_ids.append(id)
    user_ids = list(set(user_ids))
    return user_ids


ROLES_DICT: Dict[str, Dict[str, str]] = {
    "prod": {
        "sales_agent": "rol_bW7wiNnEtfakpJmy",
        "sales_manager": "rol_GEbHfDVHU8D7J5c0",
        "internal_sales": "rol_OOwBC28NhG4Y9V9r",
        "superadmin": "rol_D2s4oMPSdUkaL2rH",
        "sales_director": "rol_dpWbWJ6j09RsT7NY",
        "rol_bW7wiNnEtfakpJmy": "sales_agent",
        "rol_GEbHfDVHU8D7J5c0": "sales_manager",
        "rol_OOwBC28NhG4Y9V9r": "internal_sales",
        "rol_D2s4oMPSdUkaL2rH": "superadmin",
        "rol_dpWbWJ6j09RsT7NY": "sales_director",
    },
    "dev": {
        "sales_agent": "rol_bdrdf9reLqNjVX7C",
        "sales_manager": "rol_Y3Fqrny6KcXFTHnU",
        "internal_sales": "rol_VX5fKnKtv2pXOjNI",
        "sales_director": "rol_Wj564GREw93NvTyl",
        "superadmin": "rol_CAIy8AceKjETS7Hn",
        "rol_bdrdf9reLqNjVX7C": "sales_agent",
        "rol_Y3Fqrny6KcXFTHnU": "sales_manager",
        "rol_VX5fKnKtv2pXOjNI": "internal_sales",
        "rol_Wj564GREw93NvTyl": "sales_director",
        "rol_CAIy8AceKjETS7Hn": "superadmin",
    },
}
