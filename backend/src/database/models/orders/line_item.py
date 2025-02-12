# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from tortoise import fields, models
from tortoise.exceptions import NoValuesFetched


class LineItem(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    scheduled_date = fields.DatetimeField(null=True)
    potential_date = fields.DatetimeField(null=True)
    delivery_date = fields.DatetimeField(null=True)
    minimum_shipping_cost = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    potential_dollar_per_mile = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    potential_miles = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_cost = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    revenue = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    shipping_revenue = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    shipping_cost = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    potential_driver_charge = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    convenience_fee = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    good_to_go = fields.TextField(null=True)
    welcome_call = fields.TextField(null=True)
    pickup_email_sent = fields.BooleanField(default=False)
    missed_delivery = fields.BooleanField(default=False)
    door_orientation = fields.TextField(null=True)
    product_city = fields.TextField(null=True)
    product_state = fields.TextField(null=True)
    container_size = fields.TextField(null=True)
    condition = fields.TextField(null=True)
    rent_period = fields.IntField(null=True)
    interest_owed = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_rental_price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    monthly_owed = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    attributes = fields.JSONField(null=True)
    inventory = fields.OneToOneField("models.ContainerInventory", related_name="line_items", null=True, blank=True)
    other_inventory = fields.OneToOneField("models.OtherInventory", related_name="line_items", null=True, blank=True)
    driver = fields.ForeignKeyField("models.Driver", related_name="line_item_driver", null=True, blank=True)
    file_upload = fields.ForeignKeyField("models.FileUpload", related_name="file_upload", null=True, blank=True)
    product_type = fields.TextField(null=True)
    other_product_name = fields.TextField(null=True)
    other_product_shipping_time = fields.TextField(null=True)
    potential_driver = fields.ForeignKeyField(
        "models.Driver",
        related_name="line_item_driver_potential",
        null=True,
        blank=True,
    )
    order = fields.ForeignKeyField("models.Order", related_name="line_items", null=True)
    paid_at = fields.DatetimeField(null=True)

    def calculated_potential_driver_charge(self) -> Optional[Decimal]:
        if self.potential_dollar_per_mile is not None and self.potential_miles is not None:
            return self.potential_dollar_per_mile * self.potential_miles
        return self.potential_driver_charge

    def full_cost(self) -> Optional[Decimal]:
        if self.container_cost() is None:
            return Decimal("0")
        shipping = 0 if not self.shipping_cost else self.shipping_cost
        return self.container_cost() + shipping

    def calculated_total_revenue(self) -> Optional[Decimal]:
        total = Decimal("0")
        if self.revenue is not None:
            total += self.revenue
        if self.shipping_revenue is not None:
            total += self.shipping_revenue

        return total

    def calculated_monthly_owed(self) -> Optional[Decimal]:
        if self.rent_period is None:
            return 0
        return self.total_rental_price / self.rent_period

    def container_cost(self) -> Optional[Decimal]:
        if self.inventory and hasattr(self.inventory, "total_cost"):
            return self.inventory.total_cost
        if self.product_cost:
            return self.product_cost
        return Decimal("0")

    def estimated_profit(self) -> Optional[Decimal]:
        if self.revenue is None or self.shipping_revenue is None:
            return Decimal("0")
        return (self.revenue + self.shipping_revenue) - self.full_cost()

    def title(self) -> str:
        if self.product_type is None or self.product_type != "CONTAINER_ACCESSORY":
            high_cube = (
                "Standard" if not self.attributes else "High Cube" if self.attributes.get("high_cube") else "Standard"
            )
            double_door = "" if not self.attributes else "Double Doors" if self.attributes.get("double_door") else ""
            as_is = "AS IS" if self.attributes and self.attributes.get("as_is") else ""
            premium = "Premium" if self.attributes and  self.attributes.get("premium") else ""
            wwt = "WWT/CW" if self.attributes and self.attributes.get("wwt_cw") else ""
            open_side = "Open Side" if self.attributes and self.attributes.get("open_side") else ""
            side_doors = "Side Doors" if self.attributes and self.attributes.get("side_doors") else ""
            type = f"{high_cube} {as_is} {premium} {wwt} {open_side} {side_doors} {double_door}".strip()
            type = " ".join(filter(lambda x: True if x != '' else False, type.split(" ")))
            product_type = "" if not self.attributes else "" if not self.attributes.get("portable") else "Portable"
            return f"{self.container_size}' {self.condition} {type} {product_type}".strip()
        elif self.other_product_name:
            return self.other_product_name
        else:
            return ""

    def vendor_name(self) -> str:
        if self.inventory is None and self.other_inventory is None:
            return ""
        if self.inventory is not None:
            if (
                hasattr(self.inventory, "vendor")
                and self.inventory.vendor is not None
                and hasattr(self.inventory.vendor, "name")
            ):
                return self.inventory.vendor.name
        if self.other_inventory is not None:
            if (
                hasattr(self.other_inventory, "vendor")
                and self.other_inventory.vendor is not None
                and hasattr(self.other_inventory.vendor, "name")
            ):
                return self.other_inventory.vendor.name
        return ""

    def calculated_accessory_commission(self) -> Optional[Decimal]:
        if self.product_type is not None and self.product_type == "CONTAINER_ACCESSORY":
            return self.revenue * Decimal(10/100)
        else:
            return Decimal(0)

    def calculated_rental_name(self) -> str:
        if self.product_type is None or self.product_type != "CONTAINER_ACCESSORY":
            high_cube = (
                "Standard" if not self.attributes else "High Cube" if self.attributes.get("high_cube") else "Standard"
            )
            type = f"{high_cube}".strip()
            return f"{self.container_size}' {type}".strip()
        elif self.other_product_name:
            return self.other_product_name
        else:
            return ""

    def abrev_title(self) -> str:
        if self.product_type == "CONTAINER_ACCESSORY":
            return self.other_product_name or ""
        
        high_cube = (
            "STD" if not self.attributes else "HC" if self.attributes.get("high_cube") else "STD"
        )
        double_door = "" if not self.attributes else "DD" if self.attributes.get("double_door") else ""
        as_is = "AS IS" if self.attributes and self.attributes.get("as_is") else ""
        premium = "PRM" if self.attributes and  self.attributes.get("premium") else ""
        wwt = "WWT/CW" if self.attributes and self.attributes.get("wwt_cw") else ""
        open_side = "OS" if self.attributes and self.attributes.get("open_side") else ""
        side_doors = "SD" if self.attributes and self.attributes.get("side_doors") else ""
        container_type = f"{high_cube} {as_is} {premium} {wwt} {open_side} {side_doors} {double_door}".strip()
        container_type = " ".join(filter(lambda x: True if x != '' else False, container_type.split(" ")))
        product_type = "" if not self.attributes else "" if not self.attributes.get("portable") else "Portable"

        return f"{self.container_size}' {self.condition} {container_type} {product_type}".strip()

    def abbrev_title_w_container_number(self) -> str:
        if self.inventory and hasattr(self.inventory, "container_number"):
            return f"{self.abrev_title()} | {self.inventory.container_number}"
        return self.abrev_title()

    def location(self) -> str:
        if self.product_city and self.product_state:
            return f"{self.product_city}, {self.product_state}"
        return ""
    def container_address(self) ->str:
        try:
            return self.inventory_address[0].full_address_computed() if self.inventory_address and len(self.inventory_address) > 0 else ""
        except NoValuesFetched:
              return ""
    def calculated_description(self) -> str:
        description = self.abrev_title()
        if self.inventory and hasattr(self.inventory, "container_number"):
            description += f" | {self.inventory.container_number}"
        location = self.container_address()
        # if location and location != "":
        #     description += f" | {location}"
        return description

    def calc_abrev_title_w_container_number_w_address(self) -> str:
        abrev = self.abbrev_title_w_container_number()
        address = self.container_address()
        if address != "":
            abrev += f" | {address}"
        return abrev


    class PydanticMeta:
        exclude = [
            "created_at",
            "modified_at",
            "potential_driver.account",
            "potential_driver.deliveries",
            "driver.account",
            "order.account",
            "driver.deliveries",
            "order.customer.account",
            "order.customer.account_id",
        ]
        computed = (
            "location",
            "estimated_profit",
            "title",
            "abrev_title",
            "calculated_potential_driver_charge",
            "calculated_total_revenue",
            "calculated_rental_name",
            "vendor_name",
            "calculated_accessory_commission",
            "abbrev_title_w_container_number",
            "calculated_description",
            "container_address",
            "calc_abrev_title_w_container_number_w_address",
            # "delivery_days",
            # "location_region",
            # "calculated_total_rto_price"
        )

    class Meta:
        table = "line_item"

    def __str__(self):
        return f"{self.id}"
