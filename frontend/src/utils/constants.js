import cloneDeep from "lodash.clonedeep"
export const rentalStatusOptions = [
  "Invoiced",
  "Active",
  "Approved",
  "Delivered",
  "Delinquent",
  "Returned",
  "Expired",
  "Cancelled"
]
export const salesStatusOptions = [
  { label: "Invoiced", value: "Invoiced" },
  { label: "Paid", value: "Paid" },
  { label: "Partially Paid", value: "Partially Paid" },
  { label: "Delayed", value: "Delayed" },
  { label: "Delivered", value: "Delivered" },
  { label: "Purchase Order", value: "Purchase Order" },
  { label: "Driver Paid", value: "Completed" },
  { label: "Expired", value: "Expired" },
  { label: "Cancelled", value: "Cancelled" }
]
export const rentToOwnStatusOptions = [
  "Invoiced",
  "Approved",
  "Delivered",
  "Delinquent",
  "Returned",
  "Expired",
  "Cancelled",
  "Unknown"
]

export const searchFilters = [
  {
    title: "Order ID",
    options: [
      { label: "Search Order Id", value: "display_order_id" },
      { label: "Search Container #", value: "container_number" },
      { label: "Search Release #", value: "container_release_number" },
      { label: "Search by Customer Name", value: "customer_name" },
      { label: "Search by Customer Email", value: "customer_email" },
      { label: "Search by Customer Phone", value: "customer_phone" },
      { label: "Search by Tracking Number", value: "tracking_number" },
      { label: "Search by Company Name", value: "customer_company_name" }
    ]
  }
]

export const filterValues = [
  {
    title: "Status",
    isMultiSelect: true,
    key: "statuses",
    options: [
      { label: "Invoiced", value: "Invoiced" },
      { label: "Paid", value: "Paid" },
      { label: "To Deliver", value: "To Deliver" },
      { label: "Delivered", value: "Delivered" },
      { label: "Partially Paid", value: "Partially Paid" },
      { label: "Pay On Delivery", value: "Pod" },
      { label: "Delayed", value: "Delayed" },
      { label: "Purchase Order", value: "Purchase Order" },
      { label: "Driver Paid", value: "Completed" },
      { label: "Expired", value: "Expired" },
      { label: "Cancelled", value: "Cancelled" }
    ]
  },
  {
    title: "Region",
    isMultiSelect: true,
    key: "regions",
    options: [
      { label: "A", value: "A" },
      { label: "B", value: "B" },
      { label: "C", value: "C" },
      { label: "D", value: "D" }
    ]
  },
  {
    title: "Pickup Region",
    isMultiSelect: true,
    key: "pickup_regions",
    options: [
      { label: "EAST", value: "EAST" },
      { label: "WEST", value: "WEST" }
    ]
  },
  {
    title: "Users",
    isMultiSelect: true,
    key: "users"
  },
  {
    title: "Order Type",
    isMultiSelect: true,
    key: "order_types",
    options: [
      // { label: "Rental", value: "RENT" },
      { label: "Rent to Own", value: "RENT_TO_OWN" },
      { label: "Sales", value: "PURCHASE" },
      { label: "Accessory Sales", value: "PURCHASE_ACCESSORY" },
      { label: "Rent", value: "RENT" }
    ]
  },
  {
    title: "Container Size",
    isMultiSelect: true,
    key: "container_sizes",
    options: [
      { label: "10 ft", value: "10" },
      { label: "20 ft", value: "20" },
      { label: "40 ft", value: "40" },
      { label: "45 ft", value: "45" }
    ]
  },
  {
    title: "Container Type",
    isMultiSelect: true,
    key: "container_types",
    options: [
      { label: "High Cube", value: "high_cube" },
      { label: "Double Door", value: "double_door" },
      { label: "Standard", value: "standard" }
    ]
  },
  {
    title: "City",
    isMultiSelect: true,
    key: "location"
  },
  {
    title: "GTG",
    key: "good_to_go",
    isMultiSelect: true,
    options: [
      { label: "YES", value: "YES" },
      { label: "NO", value: "NO" },
      { label: "IN PROGRESS", value: "IN PROGRESS" }
    ]
  },
  {
    title: "Welcome Call",
    key: "welcome_call",
    isMultiSelect: true,
    options: [
      { label: "YES", value: "YES" },
      { label: "NO", value: "NO" },
      { label: "IN PROGRESS", value: "IN PROGRESS" }
    ]
  },

  {
    title: "Is Rush",
    isMultiSelect: false,
    options: [
      { label: "Yes", value: "is_rush" },
      { label: "No", value: "not_rush" }
    ]
  },
  {
    title: "Has Driver",
    isMultiSelect: false,
    options: [
      { label: "Release sent", value: "driver_id" },
      { label: "Release not sent", value: "not_driver_id" }
    ]
  },
  {
    title: "Is Pickup",
    isMultiSelect: false,
    options: [
      { label: "Is Pickup", value: "pickup" },
      { label: "Is Delivery", value: "not_pickup" }
    ]
  },
  {
    title: "Set Date",
    isMultiSelect: false,
    options: [
      { label: "Set Date", value: "scheduled_date" },
      { label: "No Set Date", value: "not_schedule_date" }
    ]
  },
  {
    title: "Potential Date",
    isMultiSelect: false,
    options: [
      { label: "Potential Date", value: "potential_date" },
      { label: "No Potential Date", value: "not_potential_date" }
    ]
  },
  {
    title: "Potential Driver",
    isMultiSelect: false,
    options: [
      { label: "Potential Driver", value: "potential_driver" },
      { label: "No Potential Driver", value: "not_potential_driver" }
    ]
  },
  {
    title: "Container Attached",
    isMultiSelect: false,
    options: [
      { label: "Container Attached", value: "container_id" },
      { label: "Container Not Attached", value: "not_container_id" }
    ]
  },
  {
    title: "Condition",
    isMultiSelect: false,
    key: "container_condition",
    options: [
      { label: "One-Trip", value: "one_trip" },
      { label: "Used", value: "used" }
    ]
  },
  {
    title: "Date Type",
    isMultiSelect: true,
    isRequired: true,
    key: "date_types",
    options: [
      { label: "Date Created", value: "created_at" },
      { label: "Date Paid", value: "paid_at" },
      { label: "Date Delivered", value: "delivered_at" },
      { label: "Date Completed", value: "completed_at" },
      { label: "Date Signed", value: "signed_at" }
    ]
  }
]

export const originalOrderFilters = {
  statuses: [],
  searched_user_ids: [],
  order_types: [],
  container_sizes: [],
  container_types: [],
  one_trip: null,
  used: null,
  container_condition: null,
  location: [],
  regions: [],
  pickup_regions: [],
  scheduled_date: null,
  not_schedule_date: null,
  potential_date: null,
  not_potential_date: null,
  potential_driver: null,
  not_potential_driver: null,
  dateRange: null,
  driver_id: null,
  not_driver_id: null,
  is_rush: null,
  not_rush: null,
  good_to_go: null,
  welcome_call: null,
  created_at: null,
  signed_at: null,
  paid_at: null,
  delivered_at: null,
  completed_at: null,
  container_id: null,
  not_container_id: null,
  pickup: null,
  not_pickup: null,
  tracking_number: null,
  customer_company_name: null
}

export const selectedSearchCriteriaOriginal = {
  display_order_id: true,
  customer_name: null,
  customer_email: null,
  customer_phone: null,
  container_number: null,
  container_release_number: null,
  tracking_number: null,
  customer_company_name: null
}

export const defaultLineItem = {
  container: null,
  quantity: null,
  revenue: null,
  shipping_revenue: null,
  tax: null,
  total: null,
  door_orientation: "Facing cab",
  product_type: null,
  product_id: null
}

export const emptyCustomerOrder = {
  first_name: "",
  last_name: "",
  email: "",
  company_name: "",
  phone: "",
  street_address: "",
  city: "",
  state: "",
  zip: "",
  line_items: [cloneDeep(defaultLineItem)]
}
