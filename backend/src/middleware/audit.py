# Python imports
import uuid
from json import JSONDecodeError

# Pip imports
from starlette.requests import Request

# Internal imports
from src.auth.auth import Auth0User
from src.crud.audit_crud import audit_crud
from src.middleware.check_auth import check_auth
from src.schemas.audit import AuditInSchema


async def save_audit_call(request: Request):
    user: Auth0User = None
    method = request.scope['method']

    if method in ["OPTIONS", "GET"]:
        return

    path = request.scope['path']

    entity_name = ""
    first_path_element = path.split('/')[1]

    exclude_set = set(
        [
            "onvif",
            "send",
            "template",
            "j_spring_security_check",
            "generate_presigned_get_url",
            "public",
            "Autodiscover",
            "quote_searches",
        ]
    )

    if 'location' in first_path_element:
        entity_name = 'location_price'
    elif "rent_period_due_date" == first_path_element:
        entity_name = "rent_period"
    elif "delete_permission_from_role" == first_path_element:
        entity_name = "permission"
    elif "rent_period_info" == first_path_element:
        entity_name = "rent_period"
    else:
        entity_name = first_path_element

    if entity_name in exclude_set:
        return
    
    content_type = request.headers.get('content-type', '')


    # Handle different content types
    if content_type.startswith('multipart/form-data'):
        # For file uploads, create a simplified request_data
        form = await request.form()
        request_data = {
            "files": [
                {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": 0  # Size will be calculated after reading
                }
                for file in form.getlist('files')
            ]
        }
    else:
        # Try to parse JSON for other content types
        try:
            request_data = await request.json()
        except JSONDecodeError:
            request_data = {}

    user = await check_auth(request)
    item_id = ""
    for key in request.path_params:
        if 'id' in key:
            item_id = request.path_params[key]

    operation_type = ""

    if method == "POST":
        operation_type = "CREATE"
    elif method == "DELETE":
        operation_type = "DELETE"
    elif method in ["PATCH", "PUT"]:
        operation_type = "UPDATE"

    # Extract request data from the request object

    if isinstance(request_data, list):
        group_id = str(uuid.uuid4())
        for item in request_data:
            item_id = item.get('id')
            await audit_crud.create(
                AuditInSchema(
                    user_id=None if not user else user.id.split('|')[1],
                    entity_name=entity_name,
                    object_id=item_id,
                    request_data=item,
                    operation_type=operation_type,
                    request_url=request.scope['path'],
                    group_id=group_id,
                )
            )
    else:
        await audit_crud.create(
            AuditInSchema(
                user_id=None if not user else user.id.split('|')[1],
                entity_name=entity_name,
                object_id=item_id,
                request_data=request_data,
                operation_type=operation_type,
                request_url=request.scope['path'],
                group_id=str(uuid.uuid4()),
            )
        )
