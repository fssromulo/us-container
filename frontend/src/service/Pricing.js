import { dfl } from "@/service/DateFormat"

export default class PricingService {
  convertAttributesToDisplay(attributes) {
    if (!attributes) {
      return []
    }
    const value = Object.keys(attributes)
      .map((key) => {
        if (key !== "dimensions" && attributes[key]) {
          return key
        }
      })
      .filter((a) => a !== undefined)
    return value
  }

  convertDisplayAttributesToAttributes(originalAttributes, displayAttributes) {
    let attributes = Object.assign({}, originalAttributes)
    displayAttributes.forEach((attr) => {
      attributes[attr] = true
    })
    // set other booleans to false
    Object.keys(attributes).forEach((key) => {
      if (key !== "dimensions" && !displayAttributes.includes(key)) {
        attributes[key] = false
      }
    })
    return attributes
  }

  dtoProductPricing(price) {
    return Object.assign(price, {
      created_at: dfl(price.created_at),
      location_name: price.location?.city,
      location_id: price.location?.id,
      is_best_seller: "No",
      in_stock: price.in_stock,
      display_in_stock: price.in_stock ? "Yes" : "No",
      link: price.product_link || "",
      link: price.product_link || "",
      title: price.name || "",
      product_type: "CONTAINER_ACCESSORY",
      id: price.id,
      shipping: price.shipping_time || "",
      price: price.price || 0
    })
  }
  dtoContainerPricing(price) {
    const displayAttributes = this.convertAttributesToDisplay(price.attributes)
    return Object.assign(price, {
      created_at: dfl(price.created_at),
      location_name: price.location?.city,
      location_id: price.location?.id,
      displayAttributes: displayAttributes,
      attributes: price.attributes
    })
  }

  dtoLocation(location) {
    return Object.assign(location, {
      created_at: dfl(location.created_at)
    })
  }

  locationColumnOrdering = [
    {
      field: "city",
      display: "City",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "state",
      display: "State",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "province",
      display: "Province",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "zip",
      display: "Zip",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "created_at",
      display: "Created at",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "cost_per_mile",
      display: "Price per mile",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "minimum_shipping_cost",
      display: "Minimum shipping cost",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "region",
      display: "Region",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "pickup_region",
      display: "Pickup Region",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "average_delivery_days",
      display: "Delivery Days",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "is_pay_on_delivery",
      display: "Has POD Enabled?",
      sortable: true,
      style: "width: 160px"
    }
  ]

  columnOrdering = [
    {
      field: "location_name",
      display: "Location",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "title",
      display: "Container",
      sortable: true,
      style: "width: 220px"
    },
    {
      field: "price",
      display: "Price",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "monthly_price",
      display: "Monthly price",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "product_type",
      display: "Type",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "created_at",
      display: "Created at",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "description",
      display: "Description",
      sortable: true,
      style: "width: 160px"
    }
  ]
  columnAccessoryOrdering = [
    {
      field: "title",
      display: "Title",
      sortable: true,
      style: "width: 220px"
    },

    {
      field: "price",
      display: "Price",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "created_at",
      display: "Created at",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "link",
      display: "Product Link",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "display_in_stock",
      display: "In Stock",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "is_best_seller",
      display: "Best Seller",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "shipping",
      display: "Shipping Time",
      sortable: true,
      style: "width: 160px"
    }
  ]
}
