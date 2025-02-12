import _flattenDeep from "lodash.flattendeep"
import cloneDeep from "lodash.clonedeep"
import {
  dfa,
  dfl,
  dfc,
  dfc_without_zone,
  convertDateForPost
} from "@/service/DateFormat"
import { useCustomerOrder } from "@/store/modules/customerOrder"
import { useUsers } from "../store/modules/users"
import UsersService from "./User"
import toCamelCase from "@/utils/toCamelCase"
import { defaultPaymentTypesDropDown } from "@/utils/paymentTypes"

import CustomerApi from "../api/customers"

export default class CustomerService {
  constructor() {
    this.customersStore = useCustomerOrder()
    this.userStore = useUsers()
    this.usersService = new UsersService()
    this.statuses = { Paid: "Paid", Overdue: "Overdue", Upcoming: "Upcoming" }
    this.customerApi = new CustomerApi()
    this.paymentOptions = defaultPaymentTypesDropDown()
  }

  async setOrders(orders, status) {
    if (!status) return
    const storeProperty = toCamelCase(`${status.toLowerCase()} orders`)
    const updatedOrders = [
      ...cloneDeep(this.customersStore[storeProperty]),
      ...orders
    ]
    const noDupsOrders = updatedOrders.filter(
      (v, i, a) => a.findIndex((t) => t.line_item_id === v.line_item_id) === i
    )
    noDupsOrders.sort(
      (a, b) => new Date(b.order_created_at) - new Date(a.order_created_at)
    )

    // uppercase first letter
    const setter = toCamelCase(`set ${storeProperty}`)
    this.customersStore[setter](noDupsOrders)
  }

  async resetOrders(status) {
    const storeProperty = toCamelCase(`${status.toLowerCase()} orders`)
    const setter = toCamelCase(`set ${storeProperty}`)
    this.customersStore[setter]([])
  }

  /**
   *
   * @param {Array} array
   * @param {String} orderId
   * @returns {Array}
   */
  findOrderLineItemIndexes(array, orderId) {
    let indexes = []
    if (array == null) {
      return indexes
    }
    indexes = array.reduce((acc, curr, index) => {
      if (curr.order_id === orderId) {
        acc.push(index)
      }
      return acc
    }, [])
    return indexes
  }

  /**
   *
   * @param {Array} array
   * @param {String} lineItemId
   * @returns {Number}
   */
  findOrderLineItemIndex(array, lineItemId) {
    let index
    index = array.map((o) => o.line_item_id).indexOf(lineItemId)

    return index
  }

  async swapCustomerOrderLineItem(orderId, orderLineItemData, status) {
    // this function needs to find the given lineitem that is being affected and swap that out
    const { data } = await this.customerApi.getOrderById(orderId)
    let clonedOrders = []
    let orderLineItems = this.dtoOrder([data.value])
    let index
    let updatedLineItemId = orderLineItemData.line_item_id

    // if we are in search and filter, then we will want to run this specific logic
    if (this.customersStore.searchedOrders.length > 0) {
      let customerStoreSearchedOrdersLineItems =
        this.customersStore.searchedOrders

      index = this.findOrderLineItemIndex(
        customerStoreSearchedOrdersLineItems,
        updatedLineItemId
      )
      if (index !== -1) {
        clonedOrders = cloneDeep(customerStoreSearchedOrdersLineItems)
        let updatedOrderLineItemData = orderLineItems.find(
          (o) => o.line_item_id === updatedLineItemId
        )
        clonedOrders[index] = updatedOrderLineItemData
        this.customersStore.setSearchedOrders([])
        this.customersStore.setSearchedOrders(clonedOrders)
      } else {
        console.log("There was an issue finding the lineitems to update.")
      }
    } else {
      // this will return a dto version of the order so the fields will not be the same
      // as teh order model
      const propertyName = toCamelCase(`${status} Orders`)
      const customerStoreStatusOrderLineItems =
        this.customersStore[propertyName]
      // here we need to accommodate for that and look at what the dto calls for the order
      index = this.findOrderLineItemIndex(
        customerStoreStatusOrderLineItems,
        updatedLineItemId
      )

      if (index !== -1) {
        clonedOrders = cloneDeep(customerStoreStatusOrderLineItems)
        let updatedOrderLineItemData = orderLineItems.find(
          (o) => o.line_item_id === updatedLineItemId
        )
        clonedOrders[index] = updatedOrderLineItemData
        const setter = toCamelCase(`set ${propertyName}`)
        this.customersStore[setter](clonedOrders)
      } else {
        console.log("Invalid order status:", status)
      }
    }
  }

  addDateFormatting(o, objName) {
    let returnObj = {
      order_display_delivered_at: null,
      order_display_completed_at: null,
      order_display_paid_at: null,
      order_display_signed_at: null
    }

    if (!o) {
      console.log("no object passed to addDateFormatting ", objName)
      return returnObj
    }
    Object.keys(o).forEach((k) => {
      const newKey = `${objName}_${k}`
      switch (newKey) {
        case "order_created_at":
          returnObj["display_created_at"] = dfc(o[k])
          returnObj[newKey] = o[k]
          break
        case "order_modified_at":
          returnObj["display_modified_at"] = dfc(o[k])
          returnObj[newKey] = dfa(o[k])
          break
        case "order_completed_at":
          returnObj["display_completed_at"] = o[k] ? dfc(o[k]) : null
          returnObj["order_completed_at"] = o[k]
          break
        case "order_paid_at":
          returnObj["display_paid_at"] = o[k] ? dfc(o[k]) : null
          returnObj["order_paid_at"] = o[k]
          break
        case "order_signed_at":
          returnObj["display_signed_at"] = o[k] ? dfc(o[k]) : null
          returnObj["order_signed_at"] = o[k]
          break
        case "order_delivered_at":
          returnObj["display_delivered_at"] = o[k] ? dfc(o[k]) : null
          returnObj["order_delivered_at"] = o[k]
          break
        case "line_item_potential_date":
          returnObj[newKey] = o[k] ? dfc(o[k]) : null
          break
        case "line_item_scheduled_date":
          returnObj[newKey] = o[k] ? dfc(o[k]) : null
          returnObj["line_item_org_scheduled_date"] = o[k]
          break
        case "order_user":
          // const user = this.userStore.users.find(u => u.id === o[k].id)
          returnObj["order_agent"] = o[k]?.full_name
          // returnObj['order_managing_agent'] = user?.assistant?.manager?.full_name ? user.assistant.manager.full_name : user.full_name
          break
        case "line_item_potential_driver":
          returnObj["line_item_potential_driver_id"] = o[k]?.id
          break
        case "line_item_inventory":
          returnObj["line_item_inventory_id"] = o[k]?.id
          returnObj["line_item_inventory_container_release_number"] =
            o[k]?.container_release_number
          returnObj["line_item_inventory"] = o[k]
          break
        default:
          returnObj[newKey] = o[k]
          break
      }
    })
    return returnObj
  }

  transformOrder(order) {
    let mergedOrder = {}
    const clonedOrder = cloneDeep(order)
    let line_items = cloneDeep(clonedOrder.line_items)
    delete clonedOrder.line_items
    let mappedCustomer = {}

    if (clonedOrder.customer) {
      mappedCustomer = this.addDateFormatting(clonedOrder.customer, "customer")
    }

    delete clonedOrder.customer
    const mappedOrder = this.addDateFormatting(clonedOrder, "order")

    return line_items.map((line_item) => {
      const mappedLineItem = this.addDateFormatting(line_item, "line_item")
      return Object.assign({}, mappedLineItem, mappedOrder, mappedCustomer)
    })
  }

  dtoOrder(orders_list) {
    if (!orders_list) return []

    const flattenedOrders = _flattenDeep(
      orders_list.map((c) => {
        return this.transformOrder(c)
      })
    )
    return flattenedOrders.filter(
      (v, i, a) => a.findIndex((t) => t.line_item_id === v.line_item_id) === i
    )
  }

  async swapCustomerOrder(orderId, status, old_status) {
    // this function needs to find the given lineitem that is being affected and swap that out
    const { data } = await this.customerApi.getOrderById(orderId)
    let clonedOrders = []
    let orderLineItems = this.dtoOrder([data.value])
    let indexes = []

    // if we are in search and filter, then we will want to run this specific logic
    if (this.customersStore.searchedOrders.length > 0) {
      let customerStoreSearchedOrdersLineItems =
        this.customersStore.searchedOrders

      indexes = this.findOrderLineItemIndexes(
        customerStoreSearchedOrdersLineItems,
        orderId
      )
      if (indexes.length !== 0) {
        clonedOrders = cloneDeep(customerStoreSearchedOrdersLineItems)
        indexes.forEach((i) => {
          clonedOrders[i] = orderLineItems.find(
            (o) => o.line_item_id === clonedOrders[i].line_item_id
          )
        })
        this.customersStore.setSearchedOrders([])
        this.customersStore.setSearchedOrders(clonedOrders)
      } else {
        console.log("There was an issue finding the lineitems to update.")
      }
    } else {
      // this will return a dto version of the order so the fields will not be the same
      // as teh order model
      let orderStatus = status
      const propertyName = toCamelCase(`${old_status} Orders`)
      const customerStoreStatusOrderLineItems =
        this.customersStore[propertyName]
      // here we need to accommodate for that and look at what the dto calls for the order
      //list of the given order's line items
      indexes = this.findOrderLineItemIndexes(
        customerStoreStatusOrderLineItems,
        orderId
      )

      if (indexes.length !== 0) {
        clonedOrders = cloneDeep(customerStoreStatusOrderLineItems)
        indexes.forEach((i) => {
          clonedOrders[i] = orderLineItems.find(
            (o) => o.line_item_id === clonedOrders[i].line_item_id
          )
        })
        let newPropertyName = toCamelCase(`${status} Orders`)
        const setter = toCamelCase(`set ${propertyName}`)
        this.customersStore[setter](clonedOrders)

        if (status != old_status) {
          newPropertyName = toCamelCase(`${old_status} Orders`)
          for (let i = 0; i < indexes.length; i++) {
            this.customersStore[propertyName].splice(indexes[i], 1)
          }
        }
      } else {
        console.log("Invalid order status:", orderStatus)
      }
    }
  }

  orderDto = () => {
    const order = cloneDeep(this.customersStore.order)
    delete order.customer
    return Object.assign({}, order, {
      user_id: order.user?.id,
      created_at: dfl(order.created_at),
      signed_at: dfl(order.signed_at),
      paid_at: !dfc(order.paid_at).includes("Invalid")
        ? dfc_without_zone(
            convertDateForPost(new Date(order.paid_at)).toISOString()
          )
        : "",
      delivered_at: !dfc(order.delivered_at).includes("Invalid")
        ? dfc_without_zone(
            convertDateForPost(new Date(order.delivered_at)).toISOString()
          )
        : "",
      completed_at: !dfc(order.completed_at).includes("Invalid")
        ? dfc_without_zone(
            convertDateForPost(new Date(order.completed_at)).toISOString()
          )
        : "",
      display_paid_at: dfl(order.calculated_paid_in_full_date),
      display_delivered_at: dfl(order.delivered_at),
      display_completed_at: dfl(order.completed_at),
      customer_application_schema_id:
        order?.customer_application_schema?.id || null
    })
  }

  dtoCustomer(customer) {
    if (!customer) return []
    return customer.order.map((order) => {
      return {
        ...order,
        customer: customer
      }
    })
  }

  columnOrdering(can) {
    return [
      {
        field: "line_item_id",
        display: "Line Item Id",
        sortable: true,
        style: "min-width: 140px",
        isButton: true,
        showOnStatus: [],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_note",
        display: "Notes",
        sortable: true,
        style: "min-width: 120px",
        isButton: true,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "first payment received",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed",
          "Delayed",
          "first_payment_received"
        ],
        allowed: can("read", "order_column-notes")
      },
      {
        field: "display_created_at",
        display: "Created",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        showOnStatus: [
          "Invoiced",
          "Expired",
          "Cancelled",
          "Purchase Order",
          "Search&Filter"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_calculated_paid_in_full_date",
        display: "Paid",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Delayed",
          "first payment received",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: true
      },
      {
        field: "order_signed_at",
        display: "POD Signed",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        showOnStatus: ["POD", "Search&Filter", "To Deliver"],
        exceptOrderType: ["RENT"],
        allowed: can("read", "order_column-set_date")
      },
      {
        field: "order_calculated_signed_date",
        display: "Rental Signed",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Delayed",
          "first payment received",
          "Search&Filter",
          "To Deliver",
          "SIGNED"
        ],
        allowed: true,
        exceptOrderType: ["PURCHASE", "PURCHASE_ACCESSORY", "RENT_TO_OWN"]
      },
      {
        field: "display_completed_at",
        display: "Completed",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        showOnStatus: ["Completed", "Search&Filter"],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "display_delivered_at",
        display: "Delivered",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        showOnStatus: ["Delivered", "Search&Filter"],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_scheduled_date",
        display: "Set Date",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        isDatepicker: true,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-set_date"),
        updateAbility: "order_column-set_date",
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_note",
        display: "Delivery Notes",
        sortable: true,
        style: "min-width: 200px",
        isButton: false,
        isInput: true,
        showOnStatus: ["Paid", "Delayed", "Expired", "Cancelled", "To Deliver"],
        allowed: can("read", "order_column-delivery_notes"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_potential_date",
        display: "Potential Date",
        sortable: true,
        style: "min-width: 100px",
        isDatepicker: true,
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-potential_date"),
        updateAbility: "order_column-potential_date",
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_address.full_address",
        display: "Address",
        sortable: true,
        style: "min-width: 250px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned"
        ],
        allowed: can("read", "order_column-customerAddress"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "customer_full_name",
        display: "Name",
        sortable: true,
        style: "min-width: 160px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "first_payment_received",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed",
          "Delayed"
        ],
        allowed: can("read", "order_column-customer")
      },
      {
        field: "customer_company_name",
        display: "Company Name",
        sortable: true,
        style: "min-width: 120px",
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "first payment received",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: can("read", "order_column-customer")
      },
      {
        field: "order_calculated_paid_thru",
        display: "Paid Thru",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Active",
          "On Rent",
          "first payment received",
          "Delinquent"
        ],
        allowed: can("read", "order_column-customer")
      },
      {
        field: "customer_phone",
        display: "Phone",
        sortable: true,
        style: "min-width: 160px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "first_payment_received",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: true
      },
      {
        field: "line_item_welcome_call",
        display: "Welcome call",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        dropdown: [
          { value: "YES", label: "Yes" },
          { value: "NO", label: "No" },
          { value: "IN PROGRESS", label: "In Progress" }
        ],
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-welcome_call"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_door_orientation",
        display: "Door orientation",
        sortable: true,
        style: "min-width: 220px",
        isButton: false,
        dropdown: [
          { value: "Facing Cab", label: "Facing Cab" },
          { value: "Opposite of Cab", label: "Opposite of Cab" }
        ],
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-door_orientation"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_title",
        display: "Size",
        sortable: true,
        style: "min-width: 160px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "first payment received",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: true
      },
      {
        field: "line_item_location",
        display: "Warehouse Location",
        sortable: true,
        style: "min-width: 160px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_inventory_container_number",
        display: "Container Number",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "first payment received",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver"
        ],
        allowed: can("read", "order_column-container_release")
      },
      {
        field: "line_item_inventory_container_release_number",
        display: "Container Assigned",
        sortable: true,
        style: "min-width: 100px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver"
        ],
        allowed: can("read", "order_column-container_release"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_good_to_go",
        display: "GTG",
        sortable: true,
        style: "min-width: 120px",
        dropdown: [
          { value: "YES", label: "Yes" },
          { value: "NO", label: "No" },
          { value: "IN PROGRESS", label: "In Progress" }
        ],
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-good_to_go"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_potential_driver_id",
        display: "Potential Driver",
        sortable: true,
        style: "min-width: 130px",
        dropdown: true,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-potential_driver_id"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_potential_miles",
        display: "Potential Miles",
        sortable: true,
        style: "min-width: 80px",
        isButton: false,
        isInput: true,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-potential_miles"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_potential_dollar_per_mile",
        display: "Potential dollar per mile",
        sortable: true,
        style: "min-width: 80px",
        isButton: false,
        isInput: true,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-potential_doller_per_mile"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_calculated_potential_driver_charge",
        display: "Potential driver charge",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_driver.company_name",
        display: "Release sent",
        sortable: true,
        style: "min-width: 160px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-release_sent"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_payment_type",
        display: "Payment Type",
        sortable: true,
        style: "min-width: 210px",
        dropdown: this.paymentOptions,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-payment_type"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_agent",
        display: "Agent",
        sortable: true,
        style: "min-width: 200px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned"
        ],
        allowed: can("read", "order_column-agent_email"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_calculated_total_price",
        display: "Total",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_calculated_monthly_subtotal",
        display: "Rent Subtotal",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: ["On Rent", "Signed"],
        isAmount: true,
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_calculated_rent_balance",
        display: "Rental Balance",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: ["On Rent"],
        isAmount: true,
        allowed: true
      },
      {
        field: "order_is_autopay",
        display: "Is Auto Pay",
        sortable: true,
        isBool: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: ["On Rent"],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_revenue",
        display: "Container price",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_shipping_revenue",
        display: "Shipping Price",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_calculated_order_tax",
        display: "Tax",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_address.county",
        display: "CU County",
        sortable: true,
        style: "min-width: 160px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_address.state",
        display: "State",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "customer_email",
        display: "Email",
        sortable: true,
        style: "min-width: 240px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_shipping_cost",
        display: "Shipping cost",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-shipping_cost"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "line_item_inventory_total_cost",
        display: "Product cost",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-container_cost"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_estimated_profit",
        display: "Estimated profit",
        sortable: true,
        style: "min-width: 120px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Delayed",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "To Deliver"
        ],
        allowed: can("read", "order_column-estimated_line_item_profit"),
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_address.city",
        display: "CU City",
        sortable: true,
        style: "min-width: 160px",
        isButton: false,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: true,
        exceptOrderType: ["RENT"]
      },
      {
        field: "order_address.full_address",
        display: "Delivery Address",
        sortable: true,
        style: "min-width: 120px",
        isButton: true,
        showOnStatus: [
          "Paid",
          "Partially Paid",
          "Purchase Order",
          "POD",
          "Delivered",
          "Completed",
          "Search&Filter",
          "On Rent",
          "To Deliver",
          "Estimate",
          "Quote",
          "Invoiced",
          "Expired",
          "Cancelled",
          "Approved",
          "Delinquent",
          "Returned",
          "Signed"
        ],
        allowed: can("read"),
        displayOnExportsOnly: true,
        exceptOrderType: ["RENT"]
      }
    ]
  }
}
