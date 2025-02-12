# Python imports
import os
from typing import Any

# Pip imports
import sentry_sdk
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from loguru import logger

# Internal imports
from redis import asyncio as aioredis
from src.config import settings
from src.database.config import TORTOISE_ORM
from src.database.register import register_tortoise
from src.database.tortoise_init import init_models
from src.middleware import handle_order_out_filter
from src.middleware.audit import save_audit_call


if os.environ.get("STAGE") == "prod":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.01,
        environment=os.environ.get("STAGE"),
        profiles_sample_rate=0.01,
    )

# enable schemas to read relationship between models
# flakes8: noqa
init_models()

"""
import 'from src.routes import users, notes' must be after 'Tortoise.init_models' why?
https://stackoverflow.com/questions/65531387/tortoise-orm-for-python-no-returns-relations-of-entities-pyndantic-fastapi
"""
# Internal imports
from src.api import (  # noqa: E402
    account,
    application_schema,
    cache,
    commissions,
    container_pricing,
    contracts,
    cost_type,
    country,
    coupon_code,
    customer_applications,
    customers,
    depot,
    driver,
    fee_api,
    fee_type,
    file_upload,
    internal_payment,
    inventory,
    inventory_address,
    line_item,
    location_pricing,
    location_distances,
    logistics_zones_api,
    misc_costs,
    notes,
    notifications,
    order_contract,
    orders,
    other_product,
    payment_methods,
    quote_searches,
    rent_period_fee,
    rent_period_info,
    rental_history,
    reports_api,
    role,
    role_permissions,
    tax,
    transaction_type,
    users,
    vendors,
    webhook_example,
)
from src.routes import public  # noqa: E402


STAGE = os.environ.get("STAGE")
root_path = "/"  # if not STAGE else f"/{STAGE}"
app = FastAPI(title="containerCRM", root_path=root_path, dependencies=[Depends(save_audit_call)])  # Here is the magic
# add_timing_middleware(app, record=logger.info, prefix="")

if not os.environ.get('STAGE'):
    os.environ['STAGE'] = 'local'


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)

app.include_router(users.router)
app.include_router(notes.router)
app.include_router(account.router)
app.include_router(vendors.router)
app.include_router(role.router)
app.include_router(role_permissions.router)
app.include_router(container_pricing.router)
app.include_router(contracts.router)
app.include_router(location_pricing.router)
app.include_router(location_distances.router)
app.include_router(customers.router)
app.include_router(coupon_code.router)
app.include_router(orders.router)
app.include_router(depot.router)
app.include_router(driver.router)
app.include_router(inventory.router)
app.include_router(line_item.router)
app.include_router(tax.router)
app.include_router(public.router)
app.include_router(file_upload.router)
app.include_router(customer_applications.router)
app.include_router(rental_history.router)
app.include_router(transaction_type.router)
app.include_router(misc_costs.router)
app.include_router(notifications.router)
app.include_router(cost_type.router)
app.include_router(fee_api.router)
app.include_router(fee_type.router)
app.include_router(quote_searches.router)
app.include_router(internal_payment.router)
app.include_router(order_contract.router)
app.include_router(notifications.router)
app.include_router(rent_period_fee.router)
app.include_router(rent_period_info.router)
app.include_router(cache.router)
app.include_router(application_schema.router)
app.include_router(reports_api.router)
app.include_router(other_product.router)
app.include_router(country.router)
app.include_router(inventory_address.router)
app.include_router(logistics_zones_api.router)
app.include_router(commissions.router)
app.include_router(payment_methods.router)
app.include_router(webhook_example.router)
"""Disable Response headers Cache-Control (set to 'no-cache').
The initial reason for this is that the fastapi-cache library sets the max-age param of the header
equal to the expire parameter that is provided to the caching layer (Redis),
so the response is also cached on the browser side, which in most cases is unnecessary."""


@app.middleware(middleware_type="http")
async def dispatch(request: Request, call_next) -> StreamingResponse:
    response: StreamingResponse = await call_next(request)
    # Consuming FastAPI response and grabbing body here
    resp_body_list: list[Any] = [section async for section in response.__dict__['body_iterator']]

    resp_body: bytearray = await handle_order_out_filter.order_out_filter(resp_body=resp_body_list)

    # Some responses no not have anything in their body, so if they don't, we don't want to interact with it
    if len(resp_body) > 0:
        # Calculate the new content length
        new_content_length = len(resp_body[0])
        # Update Content-Length header
        response.headers.update({"Content-Length": str(new_content_length)})
        # Repairing FastAPI response
        response.__setattr__('body_iterator', handle_order_out_filter.async_iterator_wrapper(resp_body))

    response.headers.update({"Cache-Control": "no-cache"})
    return response


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0  # noqa: F841


@app.get("/")
def home():
    return "Hello, World!"


@app.on_event("startup")
async def startup():
    logger.info("Starting up!")
    redis_connection_string = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    logger.info(f"Redis connection string: {redis_connection_string}")
    redis = aioredis.from_url(redis_connection_string, decode_responses=False)
    logger.info(f"Redis connection: {redis}")
    logger.info(f"Redis ping: {await redis.ping()}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


# if os.environ.get("IS_LAMBDA", None):
#     # Pip imports
#     import uvicorn

#     logger.info("Running mangum")

#     handler = Mangum(app)

#     if __name__ == "__main__":
#         uvicorn.run(app, host="0.0.0.0", port=5000)
