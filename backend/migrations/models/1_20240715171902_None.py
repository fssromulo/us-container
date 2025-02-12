from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "inventory_new" (
    "id" VARCHAR(255) NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "total_cost" DECIMAL(10,2),
    "status" TEXT,
    "purchase_type" VARCHAR(50),
    "invoice_number" TEXT,
    "invoiced_at" TIMESTAMPTZ,
    "pickup_at" TIMESTAMPTZ,
    "payment_type" TEXT,
    "paid_at" TIMESTAMPTZ
);
COMMENT ON COLUMN "inventory_new"."purchase_type" IS 'RENT: RENT\nRENT_TO_OWN: RENT_TO_OWN\nPURCHASE: PURCHASE\nALL: ALL';
CREATE TABLE IF NOT EXISTS "inventory_category_new" (
    "id" VARCHAR(255) NOT NULL  PRIMARY KEY,
    "name" TEXT
);
CREATE TABLE IF NOT EXISTS "account" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "cms_attributes" JSONB,
    "auth0_management_token_modified_at" TIMESTAMPTZ,
    "auth0_management_token" TEXT,
    "integrations" JSONB
);
CREATE TABLE IF NOT EXISTS "order_customer" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_name" TEXT,
    "last_name" TEXT,
    "street_address" TEXT,
    "email" VARCHAR(255) NOT NULL,
    "phone" TEXT,
    "zip" TEXT,
    "state" TEXT,
    "city" TEXT,
    "county" TEXT,
    "company_name" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "customer" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "first_name" TEXT,
    "last_name" TEXT,
    "company_name" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "depot" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT,
    "street_address" TEXT,
    "zip" TEXT,
    "primary_email" VARCHAR(255),
    "secondary_email" TEXT,
    "primary_phone" TEXT,
    "secondary_phone" TEXT,
    "city" TEXT,
    "state" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "coupon_code" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "amount" DECIMAL(10,2) NOT NULL,
    "minimum_discount_threshold" DECIMAL(10,2) NOT NULL,
    "name" TEXT NOT NULL,
    "code" VARCHAR(20) NOT NULL UNIQUE,
    "start_date" TIMESTAMPTZ NOT NULL,
    "end_date" TIMESTAMPTZ NOT NULL,
    "city" JSONB,
    "size" JSONB,
    "is_permanent" BOOL,
    "type" TEXT,
    "role" JSONB,
    "rules" JSONB,
    "is_stackable" BOOL NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "location_price_new" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "city" TEXT,
    "state" TEXT,
    "province" TEXT,
    "zip" TEXT,
    "region" VARCHAR(20),
    "cost_per_mile" DECIMAL(10,2),
    "minimum_shipping_cost" DECIMAL(10,2),
    "pickup_region" VARCHAR(20),
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "location_price_new"."region" IS 'A: A\nB: B\nC: C\nD: D';
COMMENT ON COLUMN "location_price_new"."pickup_region" IS 'EAST: EAST\nWEST: WEST';
CREATE TABLE IF NOT EXISTS "location_price" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "city" TEXT,
    "state" TEXT,
    "zip" TEXT,
    "region" VARCHAR(20),
    "cost_per_mile" DECIMAL(10,2),
    "minimum_shipping_cost" DECIMAL(10,2),
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "location_price"."region" IS 'A: A\nB: B\nC: C\nD: D';
CREATE TABLE IF NOT EXISTS "product_category" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "container_product_new" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT,
    "description" TEXT,
    "price" DECIMAL(10,2),
    "monthly_price" DECIMAL(10,2),
    "cost_per_mile" DECIMAL(10,2),
    "minimum_shipping_cost" DECIMAL(10,2),
    "container_size" TEXT,
    "height" INT,
    "width" INT,
    "length" INT,
    "condition" TEXT,
    "product_type" TEXT,
    "location_id" UUID REFERENCES "location_price_new" ("id") ON DELETE CASCADE,
    "product_category_id" UUID REFERENCES "product_category" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_container_p_locatio_e61a27" ON "container_product_new" ("location_id");
CREATE INDEX IF NOT EXISTS "idx_container_p_product_31667a" ON "container_product_new" ("product_category_id");
CREATE TABLE IF NOT EXISTS "product_new" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT,
    "description" TEXT,
    "price" DECIMAL(10,2),
    "monthly_price" DECIMAL(10,2),
    "cost_per_mile" DECIMAL(10,2),
    "minimum_shipping_cost" DECIMAL(10,2),
    "location_id" UUID REFERENCES "location_price_new" ("id") ON DELETE CASCADE,
    "product_category_id" UUID REFERENCES "product_category" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_product_new_locatio_7503a6" ON "product_new" ("location_id");
CREATE INDEX IF NOT EXISTS "idx_product_new_product_65d7af" ON "product_new" ("product_category_id");
CREATE TABLE IF NOT EXISTS "other_product_new" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT,
    "description" TEXT,
    "price" DECIMAL(10,2),
    "monthly_price" DECIMAL(10,2),
    "cost_per_mile" DECIMAL(10,2),
    "minimum_shipping_cost" DECIMAL(10,2),
    "shipping_time" TEXT,
    "product_link" TEXT,
    "in_stock" BOOL NOT NULL  DEFAULT True,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "location_id" UUID REFERENCES "location_price_new" ("id") ON DELETE CASCADE,
    "product_category_id" UUID REFERENCES "product_category" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_other_produ_locatio_bf4213" ON "other_product_new" ("location_id");
CREATE INDEX IF NOT EXISTS "idx_other_produ_product_f2f24c" ON "other_product_new" ("product_category_id");
CREATE TABLE IF NOT EXISTS "address" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "street_address" TEXT,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "zip" TEXT,
    "state" TEXT,
    "city" TEXT,
    "county" TEXT,
    "type" VARCHAR(8),
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION
);
COMMENT ON COLUMN "address"."type" IS 'PERSONAL: PERSONAL\nBUSINESS: BUSINESS\nDELIVERY: DELIVERY\nSECONDARY: SECONDAY';
CREATE TABLE IF NOT EXISTS "customer_contact" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "email" TEXT,
    "phone" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "customer_id" UUID NOT NULL REFERENCES "customer" ("id") ON DELETE CASCADE,
    "customer_address_id" UUID NOT NULL REFERENCES "address" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_customer_co_custome_1d894f" ON "customer_contact" ("customer_id");
CREATE TABLE IF NOT EXISTS "audit" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "user_id" UUID,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "entity_name" TEXT NOT NULL,
    "object_id" VARCHAR(50),
    "request_data" JSONB,
    "operation_type" TEXT NOT NULL,
    "request_url" TEXT NOT NULL,
    "group_id" UUID NOT NULL
);
CREATE TABLE IF NOT EXISTS "auth_management_token" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "token" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "cms" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "attributes" JSONB,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "container_price" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "container_size" TEXT,
    "product_type" VARCHAR(50),
    "sale_price" DECIMAL(10,2),
    "daily_rental_price" DECIMAL(10,2),
    "monthly_rental_price" DECIMAL(10,2),
    "attributes" JSONB,
    "condition" TEXT,
    "description" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "location_id" UUID REFERENCES "location_price" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_container_p_locatio_cc4f68" ON "container_price" ("location_id");
COMMENT ON COLUMN "container_price"."product_type" IS 'SHIPPING_CONTAINER: SHIPPING_CONTAINER\nPORTABLE_CONTAINER: PORTABLE_CONTAINER';
CREATE TABLE IF NOT EXISTS "cost_type" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "customer_application_schema" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "full_schema_name" VARCHAR(50),
    "name" VARCHAR(30),
    "content" JSONB NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_customer_ap_account_d14a44" ON "customer_application_schema" ("account_id");
CREATE TABLE IF NOT EXISTS "driver" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "company_name" TEXT,
    "city" TEXT,
    "state" TEXT,
    "province" TEXT,
    "cost_per_mile" DECIMAL(10,2),
    "cost_per_100_miles" DECIMAL(10,2),
    "phone_number" TEXT,
    "email" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "event_history" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "action" TEXT NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "fee_type" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT NOT NULL,
    "is_taxable" BOOL NOT NULL  DEFAULT False,
    "is_archived" BOOL NOT NULL  DEFAULT False,
    "is_editable" BOOL NOT NULL  DEFAULT True,
    "adjusts_profit" BOOL NOT NULL  DEFAULT True,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_fee_type_account_dc27d0" ON "fee_type" ("account_id");
CREATE TABLE IF NOT EXISTS "location_distances" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "destination_zip" TEXT NOT NULL,
    "destination_city" TEXT NOT NULL,
    "origin_zip" TEXT NOT NULL,
    "distance" DECIMAL(10,2) NOT NULL
);
CREATE TABLE IF NOT EXISTS "order_address" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "street_address" TEXT,
    "zip" TEXT,
    "state" TEXT,
    "city" TEXT,
    "county" TEXT
);
CREATE TABLE IF NOT EXISTS "order_id_counter" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "order_id" INT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "tax" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "rate" DECIMAL(10,6) NOT NULL,
    "state" TEXT NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tax_account_c03e94" ON "tax" ("account_id");
CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "first_name" VARCHAR(50),
    "last_name" VARCHAR(50),
    "display_name" VARCHAR(50),
    "is_active" BOOL NOT NULL  DEFAULT True,
    "phone" VARCHAR(50),
    "role_id" TEXT,
    "preferences" JSONB,
    "rental_preferences" JSONB,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_users_account_e306ac" ON "users" ("account_id");
CREATE TABLE IF NOT EXISTS "order" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "display_order_id" VARCHAR(50) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "paid_at" TIMESTAMPTZ,
    "completed_at" TIMESTAMPTZ,
    "delivered_at" TIMESTAMPTZ,
    "signed_at" TIMESTAMPTZ,
    "payment_type" VARCHAR(23),
    "remaining_balance" DECIMAL(10,2),
    "sub_total_price" DECIMAL(10,2),
    "total_price" DECIMAL(10,2),
    "gateway_cost" DECIMAL(10,2),
    "profit" DECIMAL(10,2),
    "pay_on_delivery_contract_sent_count" INT,
    "type" VARCHAR(11),
    "status" VARCHAR(50),
    "attributes" JSONB,
    "coming_from" TEXT,
    "is_discount_applied" BOOL NOT NULL  DEFAULT False,
    "allow_external_payments" BOOL NOT NULL  DEFAULT True,
    "credit_card_fee" BOOL NOT NULL  DEFAULT True,
    "rent_due_on_day" INT,
    "purchase_order_number" TEXT,
    "purchased_order_job_id" TEXT,
    "customer_profile_id" TEXT,
    "override_application_process" BOOL NOT NULL  DEFAULT False,
    "charge_gateway_cost" BOOL NOT NULL  DEFAULT True,
    "is_autopay" BOOL NOT NULL  DEFAULT False,
    "is_late_fee_applied" BOOL NOT NULL  DEFAULT True,
    "leadconnect_sent" BOOL NOT NULL  DEFAULT False,
    "first_payment_strategy" TEXT NOT NULL,
    "primary_payment_method" TEXT NOT NULL,
    "pod_sign_page_url" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "billing_address_id" UUID REFERENCES "order_address" ("id") ON DELETE CASCADE,
    "customer_id" UUID REFERENCES "order_customer" ("id") ON DELETE CASCADE,
    "customer_application_schema_id" UUID REFERENCES "customer_application_schema" ("id") ON DELETE CASCADE,
    "single_customer_id" UUID REFERENCES "customer" ("id") ON DELETE CASCADE,
    "user_id" UUID REFERENCES "users" ("id") ON DELETE CASCADE,
    "address_id" UUID  UNIQUE REFERENCES "order_address" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_order_display_5c9342" ON "order" ("display_order_id");
CREATE INDEX IF NOT EXISTS "idx_order_status_a1c7e6" ON "order" ("status");
CREATE INDEX IF NOT EXISTS "idx_order_account_e98d5a" ON "order" ("account_id");
CREATE INDEX IF NOT EXISTS "idx_order_billing_685a5f" ON "order" ("billing_address_id");
CREATE INDEX IF NOT EXISTS "idx_order_custome_dd5667" ON "order" ("customer_application_schema_id");
CREATE INDEX IF NOT EXISTS "idx_order_single__39c953" ON "order" ("single_customer_id");
CREATE INDEX IF NOT EXISTS "idx_order_user_id_ce7302" ON "order" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_order_address_85e2bb" ON "order" ("address_id");
COMMENT ON COLUMN "order"."payment_type" IS 'CC: CC\nECheck: Echeck\nCheck: Check\nFinanced: Financed\nWire: Wire\nRTO: RTO\nLeased: Leased\nLease: Lease\nZelle: Zelle\nCash: Cash\nECheck_ACH: Echeck (ACH On File)\nECheck_Record: Echeck (Record Payment)';
COMMENT ON COLUMN "order"."type" IS 'RENT: RENT\nRENT_TO_OWN: RENT_TO_OWN\nPURCHASE: PURCHASE\nALL: ALL';
CREATE TABLE IF NOT EXISTS "order_balance" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "remaining_balance" DECIMAL(10,2) NOT NULL,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_order_balan_order_i_5e269f" ON "order_balance" ("order_id");
CREATE TABLE IF NOT EXISTS "order_tax" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "tax_amount" DECIMAL(10,2) NOT NULL,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_order_tax_order_i_44eab6" ON "order_tax" ("order_id");
CREATE TABLE IF NOT EXISTS "rent_period" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "start_date" TIMESTAMPTZ,
    "end_date" TIMESTAMPTZ,
    "amount_owed" DECIMAL(10,2) NOT NULL,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_rent_period_order_i_d7dd2b" ON "rent_period" ("order_id");
CREATE TABLE IF NOT EXISTS "coupon_code_order" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "coupon_id" UUID NOT NULL REFERENCES "coupon_code" ("id") ON DELETE CASCADE,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "assistant" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "manager_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "assistant_id" UUID NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_assistant_manager_4ad9eb" ON "assistant" ("manager_id");
CREATE INDEX IF NOT EXISTS "idx_assistant_assista_573298" ON "assistant" ("assistant_id");
CREATE TABLE IF NOT EXISTS "commission" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "flat_commission" DECIMAL(10,2),
    "commission_percentage" DECIMAL(10,2),
    "commission_effective_date" TIMESTAMPTZ NOT NULL,
    "rental_commission_rate" DECIMAL(10,2),
    "rental_effective_rate" DECIMAL(10,2),
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "customer_application_response" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "response_content" JSONB NOT NULL,
    "date_accepted" TIMESTAMPTZ,
    "date_rejected" TIMESTAMPTZ,
    "order_id" UUID NOT NULL UNIQUE REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "fee" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fee_amount" DECIMAL(10,2) NOT NULL,
    "fee_type" VARCHAR(50),
    "due_at" TIMESTAMPTZ,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE,
    "type_id" UUID REFERENCES "fee_type" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_fee_order_i_8a6702" ON "fee" ("order_id");
CREATE INDEX IF NOT EXISTS "idx_fee_type_id_4f6103" ON "fee" ("type_id");
COMMENT ON COLUMN "fee"."fee_type" IS 'LATE: LATE\nCREDIT_CARD: CREDIT_CARD\nRUSH: RUSH\nFIRST_PAYMENT: FIRST_PAYMENT';
CREATE TABLE IF NOT EXISTS "file_upload" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "filename" TEXT NOT NULL,
    "content_type" TEXT NOT NULL,
    "folder_type" TEXT NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_file_upload_account_3aa6cc" ON "file_upload" ("account_id");
CREATE INDEX IF NOT EXISTS "idx_file_upload_order_i_4a2aa6" ON "file_upload" ("order_id");
CREATE TABLE IF NOT EXISTS "misc_cost" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "amount" DECIMAL(10,2) NOT NULL,
    "cost_type_id" UUID NOT NULL REFERENCES "cost_type" ("id") ON DELETE CASCADE,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_misc_cost_cost_ty_830073" ON "misc_cost" ("cost_type_id");
CREATE INDEX IF NOT EXISTS "idx_misc_cost_order_i_df1496" ON "misc_cost" ("order_id");
CREATE TABLE IF NOT EXISTS "order_commission" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "display_order_id" VARCHAR(50) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_team_commission" BOOL NOT NULL  DEFAULT False,
    "paid_at" TIMESTAMPTZ,
    "completed_at" TIMESTAMPTZ,
    "delivered_at" TIMESTAMPTZ,
    "sub_total_price" DECIMAL(10,4),
    "total_price" DECIMAL(10,4),
    "profit" DECIMAL(10,4),
    "is_team_lead" BOOL,
    "can_see_profit" BOOL NOT NULL  DEFAULT True,
    "total_commission" DECIMAL(10,4),
    "manager_commission_owed" DECIMAL(10,4),
    "agent_commission_owed" DECIMAL(10,4),
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "agent_id" UUID REFERENCES "users" ("id") ON DELETE CASCADE,
    "managing_agent_id" UUID REFERENCES "users" ("id") ON DELETE CASCADE,
    "team_lead_id" UUID REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_order_commi_account_49657a" ON "order_commission" ("account_id");
CREATE INDEX IF NOT EXISTS "idx_order_commi_agent_i_828724" ON "order_commission" ("agent_id");
CREATE INDEX IF NOT EXISTS "idx_order_commi_managin_340550" ON "order_commission" ("managing_agent_id");
CREATE INDEX IF NOT EXISTS "idx_order_commi_team_le_8c264d" ON "order_commission" ("team_lead_id");
CREATE TABLE IF NOT EXISTS "order_contract" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "status" TEXT NOT NULL,
    "contract_id" TEXT NOT NULL,
    "meta_data" JSONB,
    "contract_pdf_link" TEXT,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_order_contr_order_i_28f333" ON "order_contract" ("order_id");
CREATE TABLE IF NOT EXISTS "order_credit_card" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "card_type" VARCHAR(6),
    "merchant_name" VARCHAR(15),
    "response_from_gateway" JSONB,
    "order_id" UUID NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "order_credit_card"."card_type" IS 'CREDIT: CREDIT\nDEBIT: DEBIT';
COMMENT ON COLUMN "order_credit_card"."merchant_name" IS 'AMEX: AMEX\nVISA: VISA\nMASTERCARD: MASTERCARD\nDISCOVER: DISCOVER\nDINERS: DINERS\nJCB: JCB\nUNIONPAY: UNIONPAY\nMAESTRO: MAESTRO\nAMERICAN_EXPRESS: AMERICANEXPRESS';
CREATE TABLE IF NOT EXISTS "quote_searches" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "postal_code" TEXT NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_quote_searc_account_6e1e6e" ON "quote_searches" ("account_id");
CREATE INDEX IF NOT EXISTS "idx_quote_searc_user_id_924b6f" ON "quote_searches" ("user_id");
CREATE TABLE IF NOT EXISTS "rent_period_balance" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "remaining_balance" DECIMAL(10,2) NOT NULL,
    "rent_period_id" UUID NOT NULL REFERENCES "rent_period" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_rent_period_rent_pe_308a9a" ON "rent_period_balance" ("rent_period_id");
CREATE TABLE IF NOT EXISTS "rent_period_fee_balance" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "remaining_balance" DECIMAL(10,2) NOT NULL,
    "rent_period_id" UUID NOT NULL REFERENCES "rent_period" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_rent_period_rent_pe_3b8b5e" ON "rent_period_fee_balance" ("rent_period_id");
CREATE TABLE IF NOT EXISTS "rent_period_fee" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fee_amount" DECIMAL(10,2) NOT NULL,
    "fee_type" VARCHAR(50),
    "due_at" TIMESTAMPTZ,
    "description" TEXT,
    "rent_period_id" UUID NOT NULL REFERENCES "rent_period" ("id") ON DELETE CASCADE,
    "type_id" UUID REFERENCES "fee_type" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_rent_period_rent_pe_396e38" ON "rent_period_fee" ("rent_period_id");
CREATE INDEX IF NOT EXISTS "idx_rent_period_type_id_bae01b" ON "rent_period_fee" ("type_id");
COMMENT ON COLUMN "rent_period_fee"."fee_type" IS 'LATE: LATE\nCREDIT_CARD: CREDIT_CARD\nRUSH: RUSH\nFIRST_PAYMENT: FIRST_PAYMENT';
CREATE TABLE IF NOT EXISTS "rent_period_tax" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "tax_amount" DECIMAL(10,2) NOT NULL,
    "rent_period_id" UUID NOT NULL REFERENCES "rent_period" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_rent_period_rent_pe_a14df3" ON "rent_period_tax" ("rent_period_id");
CREATE TABLE IF NOT EXISTS "rent_period_total_balance" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "remaining_balance" DECIMAL(10,2) NOT NULL,
    "rent_period_id" UUID NOT NULL REFERENCES "rent_period" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_rent_period_rent_pe_437f1a" ON "rent_period_total_balance" ("rent_period_id");
CREATE TABLE IF NOT EXISTS "team_member" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "team_lead_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "team_member_id" UUID NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_team_member_team_le_5257b2" ON "team_member" ("team_lead_id");
CREATE INDEX IF NOT EXISTS "idx_team_member_team_me_97000d" ON "team_member" ("team_member_id");
CREATE TABLE IF NOT EXISTS "transaction_type" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "payment_type" VARCHAR(40) NOT NULL,
    "notes" TEXT,
    "amount" DOUBLE PRECISION,
    "group_id" UUID,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "order_id" UUID REFERENCES "order" ("id") ON DELETE CASCADE,
    "rent_period_id" UUID REFERENCES "rent_period" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_transaction_account_08a4c5" ON "transaction_type" ("account_id");
CREATE INDEX IF NOT EXISTS "idx_transaction_order_i_345208" ON "transaction_type" ("order_id");
CREATE INDEX IF NOT EXISTS "idx_transaction_rent_pe_004616" ON "transaction_type" ("rent_period_id");
CREATE TABLE IF NOT EXISTS "reports" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT NOT NULL,
    "query" TEXT NOT NULL,
    "run_by" TEXT NOT NULL,
    "run_at" TIMESTAMPTZ NOT NULL,
    "result" JSONB,
    "query_hash" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_reports_account_aff772" ON "reports" ("account_id");
CREATE TABLE IF NOT EXISTS "test_table2" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "id2" UUID
);
CREATE TABLE IF NOT EXISTS "container_attribute" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "container_product_attribute" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "container_attribute_id" UUID REFERENCES "container_attribute" ("id") ON DELETE CASCADE,
    "container_product_new_id" UUID REFERENCES "container_product_new" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_container_p_contain_3f4213" ON "container_product_attribute" ("container_attribute_id");
CREATE INDEX IF NOT EXISTS "idx_container_p_contain_2fe823" ON "container_product_attribute" ("container_product_new_id");
CREATE TABLE IF NOT EXISTS "vendor_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_vendor_type_account_b1784e" ON "vendor_type" ("account_id");
CREATE TABLE IF NOT EXISTS "vendor" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT,
    "address" TEXT,
    "city" TEXT,
    "state" TEXT,
    "zip" TEXT,
    "primary_phone" TEXT,
    "primary_email" VARCHAR(255),
    "secondary_phone" TEXT,
    "secondary_email" TEXT,
    "country" TEXT,
    "country_code_primary" TEXT,
    "country_code_secondary" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "type_id" INT REFERENCES "vendor_type" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_vendor_account_ff42e2" ON "vendor" ("account_id");
CREATE INDEX IF NOT EXISTS "idx_vendor_type_id_d5ddf4" ON "vendor" ("type_id");
CREATE TABLE IF NOT EXISTS "container_inventory_new" (
    "id" VARCHAR(255) NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "total_cost" DECIMAL(10,2),
    "status" TEXT,
    "purchase_type" VARCHAR(50),
    "invoice_number" TEXT,
    "invoiced_at" TIMESTAMPTZ,
    "pickup_at" TIMESTAMPTZ,
    "payment_type" TEXT,
    "paid_at" TIMESTAMPTZ,
    "container_number" TEXT,
    "container_release_number" TEXT,
    "container_color" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "depot_id" UUID REFERENCES "depot" ("id") ON DELETE CASCADE,
    "product_id" UUID REFERENCES "container_product_new" ("id") ON DELETE CASCADE,
    "vendor_id" UUID REFERENCES "vendor" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "container_inventory_new"."purchase_type" IS 'RENT: RENT\nRENT_TO_OWN: RENT_TO_OWN\nPURCHASE: PURCHASE\nALL: ALL';
CREATE TABLE IF NOT EXISTS "inventory" (
    "id" VARCHAR(255) NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "total_cost" DECIMAL(10,2),
    "price" DECIMAL(10,2),
    "monthly_price" DECIMAL(10,2),
    "condition" TEXT,
    "container_number" TEXT,
    "container_release_number" TEXT,
    "status" VARCHAR(9),
    "container_size" TEXT,
    "type" JSONB,
    "purchase_type" VARCHAR(50),
    "invoice_number" TEXT,
    "invoiced_at" TIMESTAMPTZ,
    "pickup_at" TIMESTAMPTZ,
    "payment_type" TEXT,
    "paid_at" TIMESTAMPTZ,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "depot_id" UUID REFERENCES "depot" ("id") ON DELETE CASCADE,
    "location_price_id" UUID REFERENCES "location_price" ("id") ON DELETE CASCADE,
    "vendor_id" UUID REFERENCES "vendor" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "inventory"."status" IS 'ATTACHED: Attached\nAVAILABLE: Available\nIN_LINE: In Line\nDELIVERED: Delivered\nUNKNOWN: UNKNOWN\nReady: Ready';
COMMENT ON COLUMN "inventory"."purchase_type" IS 'RENT: RENT\nRENT_TO_OWN: RENT_TO_OWN\nPURCHASE: PURCHASE\nALL: ALL';
CREATE TABLE IF NOT EXISTS "other_inventory_new" (
    "id" VARCHAR(255) NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "total_cost" DECIMAL(10,2),
    "status" TEXT,
    "purchase_type" VARCHAR(50),
    "invoice_number" TEXT,
    "invoiced_at" TIMESTAMPTZ,
    "pickup_at" TIMESTAMPTZ,
    "payment_type" TEXT,
    "paid_at" TIMESTAMPTZ,
    "tracking_number" TEXT,
    "quantity" INT,
    "delivered" TEXT,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "product_id" UUID REFERENCES "other_product_new" ("id") ON DELETE CASCADE,
    "vendor_id" UUID REFERENCES "vendor" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_other_inven_account_0f105c" ON "other_inventory_new" ("account_id");
COMMENT ON COLUMN "other_inventory_new"."purchase_type" IS 'RENT: RENT\nRENT_TO_OWN: RENT_TO_OWN\nPURCHASE: PURCHASE\nALL: ALL';
CREATE TABLE IF NOT EXISTS "line_item" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "scheduled_date" TIMESTAMPTZ,
    "potential_date" TIMESTAMPTZ,
    "delivery_date" TIMESTAMPTZ,
    "minimum_shipping_cost" DECIMAL(10,2),
    "potential_dollar_per_mile" DECIMAL(10,2),
    "potential_miles" DECIMAL(10,2),
    "product_cost" DECIMAL(10,2),
    "revenue" DECIMAL(10,2),
    "shipping_revenue" DECIMAL(10,2),
    "shipping_cost" DECIMAL(10,2),
    "tax" DECIMAL(10,2),
    "potential_driver_charge" DECIMAL(10,2),
    "convenience_fee" DECIMAL(10,2),
    "good_to_go" TEXT,
    "welcome_call" TEXT,
    "pickup_email_sent" BOOL NOT NULL  DEFAULT False,
    "missed_delivery" BOOL NOT NULL  DEFAULT False,
    "door_orientation" TEXT,
    "product_city" TEXT,
    "product_state" TEXT,
    "container_size" TEXT,
    "condition" TEXT,
    "rent_period" INT,
    "interest_owed" DECIMAL(10,2),
    "total_rental_price" DECIMAL(10,2),
    "monthly_owed" DECIMAL(10,2),
    "attributes" JSONB,
    "product_type" TEXT,
    "other_product_name" TEXT,
    "other_product_shipping_time" TEXT,
    "driver_id" UUID REFERENCES "driver" ("id") ON DELETE CASCADE,
    "order_id" UUID REFERENCES "order" ("id") ON DELETE CASCADE,
    "potential_driver_id" UUID REFERENCES "driver" ("id") ON DELETE CASCADE,
    "inventory_id" VARCHAR(255)  UNIQUE REFERENCES "container_inventory_new" ("id") ON DELETE CASCADE,
    "other_inventory_id" VARCHAR(255)  UNIQUE REFERENCES "other_inventory_new" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "delivery" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE,
    "driver_id" UUID NOT NULL REFERENCES "driver" ("id") ON DELETE CASCADE,
    "line_item_id" UUID NOT NULL REFERENCES "line_item" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "inventory_address" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "address_id" UUID REFERENCES "address" ("id") ON DELETE CASCADE,
    "inventory_id" VARCHAR(255) REFERENCES "inventory" ("id") ON DELETE CASCADE,
    "line_item_id" UUID REFERENCES "line_item" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_inventory_a_address_82c8bb" ON "inventory_address" ("address_id");
CREATE INDEX IF NOT EXISTS "idx_inventory_a_invento_0c7803" ON "inventory_address" ("inventory_id");
CREATE INDEX IF NOT EXISTS "idx_inventory_a_line_it_a592de" ON "inventory_address" ("line_item_id");
CREATE TABLE IF NOT EXISTS "rental_history" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "rent_started_at" TIMESTAMPTZ,
    "rent_ended_at" TIMESTAMPTZ,
    "inventory_id" VARCHAR(255) REFERENCES "container_inventory_new" ("id") ON DELETE CASCADE,
    "line_item_id" UUID NOT NULL REFERENCES "line_item" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_rental_hist_invento_8c4436" ON "rental_history" ("inventory_id");
CREATE INDEX IF NOT EXISTS "idx_rental_hist_line_it_b328e6" ON "rental_history" ("line_item_id");
CREATE TABLE IF NOT EXISTS "notes" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "title" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_public" BOOL,
    "author_id" UUID REFERENCES "users" ("id") ON DELETE CASCADE,
    "customer_id" UUID REFERENCES "order_customer" ("id") ON DELETE CASCADE,
    "depot_id" UUID REFERENCES "depot" ("id") ON DELETE CASCADE,
    "driver_id" UUID REFERENCES "driver" ("id") ON DELETE CASCADE,
    "inventory_id" VARCHAR(255) REFERENCES "container_inventory_new" ("id") ON DELETE CASCADE,
    "line_item_id" UUID REFERENCES "line_item" ("id") ON DELETE CASCADE,
    "order_id" UUID REFERENCES "order" ("id") ON DELETE CASCADE,
    "rental_history_id" UUID REFERENCES "rental_history" ("id") ON DELETE CASCADE,
    "vendor_id" UUID REFERENCES "vendor" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_notes_custome_283edb" ON "notes" ("customer_id");
CREATE INDEX IF NOT EXISTS "idx_notes_depot_i_3bf943" ON "notes" ("depot_id");
CREATE INDEX IF NOT EXISTS "idx_notes_driver__1dc0af" ON "notes" ("driver_id");
CREATE INDEX IF NOT EXISTS "idx_notes_invento_7c6732" ON "notes" ("inventory_id");
CREATE INDEX IF NOT EXISTS "idx_notes_line_it_7bac11" ON "notes" ("line_item_id");
CREATE INDEX IF NOT EXISTS "idx_notes_order_i_d22368" ON "notes" ("order_id");
CREATE INDEX IF NOT EXISTS "idx_notes_rental__ef2f84" ON "notes" ("rental_history_id");
CREATE INDEX IF NOT EXISTS "idx_notes_vendor__7291ff" ON "notes" ("vendor_id");
CREATE TABLE IF NOT EXISTS "country" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "country_name" TEXT,
    "code" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
