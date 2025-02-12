# Python imports
import os
import textwrap

# Pip imports
from loguru import logger


def generate_files():
    # Function to create a snake_case version of a class name
    def snake_case(name):
        result = [name[0].lower()]
        for char in name[1:]:
            if char.isupper():
                result.extend(["_", char.lower()])
            else:
                result.append(char)
        return "".join(result)

    # Retrieve the model class name from the user
    model_class_name = input("Enter the name of your model class: ")

    # Define the output directory

    # Generate the file content for the schema
    schema_template = textwrap.dedent(
        f"""
    # Pip imports
    from pydantic import Extra
    from tortoise.contrib.pydantic import pydantic_model_creator

    # Internal imports
    from src.database.models import {model_class_name}


    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True

    {model_class_name}In = pydantic_model_creator(
        {model_class_name},
        name="{model_class_name}In",
        exclude=("id", "created_at", "modified_at"),
        exclude_readonly=True,
        config_class=Config,
    )

    {model_class_name}Out = pydantic_model_creator(
        {model_class_name},
        name="{model_class_name}Out",
        exclude_readonly=True
    )
    """
    )

    # Generate the file content for the controller
    controller_template = textwrap.dedent(
        f"""
    # Python imports
    #import logging
    #import os
    #import random

    # Pip imports
    #from fastapi import HTTPException, status
    #from tortoise import Model
    #from tortoise.exceptions import DoesNotExist

    # Internal imports
    from src.schemas.{snake_case(model_class_name)} import {model_class_name}Out, {model_class_name}In
    from src.crud.{snake_case(model_class_name)}_crud import {snake_case(model_class_name)}_crud
    from src.auth.auth import Auth0User

    async def create_{snake_case(model_class_name)}({snake_case(model_class_name)}: {model_class_name}In, user: Auth0User) -> {model_class_name}Out:
        saved_{snake_case(model_class_name)} = await {snake_case(model_class_name)}_crud.create({snake_case(model_class_name)})
        return saved_{snake_case(model_class_name)}
    """
    )

    # Generate the file content for the CRUD operations
    crud_template = textwrap.dedent(
        f"""
    # ...

    from src.schemas.{snake_case(model_class_name)} import (
        {model_class_name}In,
        {model_class_name}Out,
    )

    from src.crud.tortise_crud_mapper import TortoiseCRUD
    from src.database.models import {model_class_name}

    {snake_case(model_class_name)}_crud = TortoiseCRUD(
        schema={model_class_name}Out,
        create_schema={model_class_name}In,
        update_schema={model_class_name}In,
        db_model={model_class_name},
    )
    """
    )

    # Generate the file content for the API route
    api_template = textwrap.dedent(
        f"""
    # Pip imports
    from fastapi import APIRouter, Depends, status

    # Internal imports
    from src.auth.auth import Auth0User
    from src.controllers import {snake_case(model_class_name)}
    from src.dependencies import auth
    from src.schemas.{snake_case(model_class_name)} import {model_class_name}Out, {model_class_name}In

    router = APIRouter(
        tags=["{snake_case(model_class_name)}"],
        dependencies=[Depends(auth.implicit_scheme)],
        responses={{status.HTTP_404_NOT_FOUND: {{"description": "Not found"}}}},
    )

    @router.post("/{snake_case(model_class_name)}", response_model={model_class_name}Out)
    async def create_{snake_case(model_class_name)}({snake_case(model_class_name)}: {model_class_name}In, user: Auth0User = Depends(auth.get_user)):
        return await {snake_case(model_class_name)}.create_{snake_case(model_class_name)}({snake_case(model_class_name)}, user)
    """
    )

    # Output the generated templates to files
    with open(os.path.join(os.getcwd(), f"src/schemas/{snake_case(model_class_name)}.py"), "w") as f:
        f.write(schema_template)

    with open(os.path.join(os.getcwd(), f"src/controllers/{snake_case(model_class_name)}.py"), "w") as f:
        f.write(controller_template)

    with open(os.path.join(os.getcwd(), f"src/crud/{snake_case(model_class_name)}_crud.py"), "w") as f:
        f.write(crud_template)

    with open(os.path.join(os.getcwd(), f"src/api/{snake_case(model_class_name)}.py"), "w") as f:
        f.write(api_template)
    logger.info(f"Templates for {model_class_name} generated successfully!")


if __name__ == "__main__":
    generate_files()
