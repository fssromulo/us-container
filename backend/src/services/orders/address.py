
from src.crud.order_address_crud import address_crud
from src.schemas.orders import OrderAddressIn


async def save_address(address, id = None, account_id = None):
    address_dict = address.dict(exclude_unset=True)

    if id:
        saved_address = await address_crud.update(account_id, id,
            OrderAddressIn(**address_dict)
        )
    else:
        saved_address = await address_crud.create(OrderAddressIn(**address_dict))

    return saved_address