from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "inventory" DROP CONSTRAINT "fk_inventor_account_8aac08c6";
        ALTER TABLE "inventory" DROP CONSTRAINT "fk_inventor_vendor_edfd4e03";
        ALTER TABLE "inventory" DROP CONSTRAINT "fk_inventor_depot_30df2f2f";
        ALTER TABLE "inventory" DROP CONSTRAINT "fk_inventor_location_067c1d32";
        CREATE TABLE IF NOT EXISTS "container_inventory" (
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
    "product_id" UUID REFERENCES "container_product" ("id") ON DELETE CASCADE,
    "vendor_id" UUID REFERENCES "vendor" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "container_inventory"."purchase_type" IS 'RENT: RENT\nRENT_TO_OWN: RENT_TO_OWN\nPURCHASE: PURCHASE\nALL: ALL';;
        ALTER TABLE "inventory" DROP COLUMN "location_price_id";
        ALTER TABLE "inventory" DROP COLUMN "container_number";
        ALTER TABLE "inventory" DROP COLUMN "condition";
        ALTER TABLE "inventory" DROP COLUMN "depot_id";
        ALTER TABLE "inventory" DROP COLUMN "account_id";
        ALTER TABLE "inventory" DROP COLUMN "container_release_number";
        ALTER TABLE "inventory" DROP COLUMN "type";
        ALTER TABLE "inventory" DROP COLUMN "vendor_id";
        ALTER TABLE "inventory" DROP COLUMN "monthly_price";
        ALTER TABLE "inventory" DROP COLUMN "price";
        ALTER TABLE "inventory" DROP COLUMN "container_size";
        ALTER TABLE "inventory" ALTER COLUMN "status" TYPE TEXT USING "status"::TEXT;
        ALTER TABLE "inventory" ALTER COLUMN "status" TYPE TEXT USING "status"::TEXT;
        ALTER TABLE "inventory" ALTER COLUMN "status" TYPE TEXT USING "status"::TEXT;
        ALTER TABLE "inventory" ALTER COLUMN "status" TYPE TEXT USING "status"::TEXT;
        CREATE TABLE IF NOT EXISTS "inventory_category" (
    "id" VARCHAR(255) NOT NULL  PRIMARY KEY,
    "name" TEXT
);;
        CREATE TABLE IF NOT EXISTS "other_inventory" (
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
    "product_id" UUID REFERENCES "other_product" ("id") ON DELETE CASCADE,
    "vendor_id" UUID REFERENCES "vendor" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_other_inven_account_003ad2" ON "other_inventory" ("account_id");
COMMENT ON COLUMN "other_inventory"."purchase_type" IS 'RENT: RENT\nRENT_TO_OWN: RENT_TO_OWN\nPURCHASE: PURCHASE\nALL: ALL';;
        CREATE TABLE IF NOT EXISTS "container_product" (
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
CREATE INDEX IF NOT EXISTS "idx_container_p_locatio_9f2fc7" ON "container_product" ("location_id");
CREATE INDEX IF NOT EXISTS "idx_container_p_product_cee0ef" ON "container_product" ("product_category_id");;
        CREATE TABLE IF NOT EXISTS "product" (
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
CREATE INDEX IF NOT EXISTS "idx_product_locatio_b67b51" ON "product" ("location_id");
CREATE INDEX IF NOT EXISTS "idx_product_product_bb3bcc" ON "product" ("product_category_id");;
        CREATE TABLE IF NOT EXISTS "other_product" (
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
CREATE INDEX IF NOT EXISTS "idx_other_produ_locatio_79428b" ON "other_product" ("location_id");
CREATE INDEX IF NOT EXISTS "idx_other_produ_product_60db38" ON "other_product" ("product_category_id");;
        DROP TABLE IF EXISTS "product_new";
        DROP TABLE IF EXISTS "inventory_new";
        DROP TABLE IF EXISTS "other_product_new";
        DROP TABLE IF EXISTS "inventory_address";
        DROP TABLE IF EXISTS "other_inventory_new";
        DROP TABLE IF EXISTS "container_product_new";
        DROP TABLE IF EXISTS "inventory_category_new";
        DROP TABLE IF EXISTS "container_inventory_new";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "inventory" ADD "location_price_id" UUID;
        ALTER TABLE "inventory" ADD "container_number" TEXT;
        ALTER TABLE "inventory" ADD "condition" TEXT;
        ALTER TABLE "inventory" ADD "depot_id" UUID;
        ALTER TABLE "inventory" ADD "account_id" INT NOT NULL;
        ALTER TABLE "inventory" ADD "container_release_number" TEXT;
        ALTER TABLE "inventory" ADD "type" JSONB;
        ALTER TABLE "inventory" ADD "vendor_id" UUID;
        ALTER TABLE "inventory" ADD "monthly_price" DECIMAL(10,2);
        ALTER TABLE "inventory" ADD "price" DECIMAL(10,2);
        ALTER TABLE "inventory" ADD "container_size" TEXT;
        ALTER TABLE "inventory" ALTER COLUMN "status" TYPE VARCHAR(9) USING "status"::VARCHAR(9);
        ALTER TABLE "inventory" ALTER COLUMN "status" TYPE VARCHAR(9) USING "status"::VARCHAR(9);
        ALTER TABLE "inventory" ALTER COLUMN "status" TYPE VARCHAR(9) USING "status"::VARCHAR(9);
        ALTER TABLE "inventory" ALTER COLUMN "status" TYPE VARCHAR(9) USING "status"::VARCHAR(9);
        DROP TABLE IF EXISTS "container_inventory";
        DROP TABLE IF EXISTS "inventory_category";
        DROP TABLE IF EXISTS "other_inventory";
        DROP TABLE IF EXISTS "container_product";
        DROP TABLE IF EXISTS "product";
        DROP TABLE IF EXISTS "other_product";
        ALTER TABLE "inventory" ADD CONSTRAINT "fk_inventor_location_067c1d32" FOREIGN KEY ("location_price_id") REFERENCES "location_price" ("id") ON DELETE CASCADE;
        ALTER TABLE "inventory" ADD CONSTRAINT "fk_inventor_depot_30df2f2f" FOREIGN KEY ("depot_id") REFERENCES "depot" ("id") ON DELETE CASCADE;
        ALTER TABLE "inventory" ADD CONSTRAINT "fk_inventor_vendor_edfd4e03" FOREIGN KEY ("vendor_id") REFERENCES "vendor" ("id") ON DELETE CASCADE;
        ALTER TABLE "inventory" ADD CONSTRAINT "fk_inventor_account_8aac08c6" FOREIGN KEY ("account_id") REFERENCES "account" ("id") ON DELETE CASCADE;"""
