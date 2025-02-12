import { useHttp } from "@/composables/useHttp"
import { dfs } from "@/service/DateFormat"
import PricingService from "./Pricing"
import QuoteGenerationService from "./QuoteGeneration"
import { useInventory } from "@/store/modules/inventory"
import CustomerApi from "@/api/customers"
import cloneDeep from "lodash.clonedeep"
import InvetoryApi from "@/api/inventory"

export default class InventorysService {
  constructor() {
    this.pricingService = new PricingService()
    this.quoteGenerationService = new QuoteGenerationService()
    this.customerApi = new CustomerApi()
    this.inventoryStore = useInventory()
    this.inventoryApi = new InvetoryApi()
  }

  dtoInventory(inventory, orderInfo = null) {
    return Object.assign({}, inventory, {
      display_invoiced_at: dfs(inventory.invoiced_at),
      display_created_at: dfs(inventory.created_at),
      display_modified_at: dfs(inventory.modified_at),
      vendor_name: inventory?.vendor?.name,
      depot_name: inventory?.depot?.name,
      vendor_id: inventory?.vendor?.id,
      depot_id: inventory?.depot?.id,
      display_order_id: orderInfo?.display_order_id,
      potential_date: orderInfo?.potential_date
        ? dfs(orderInfo?.potential_date)
        : null,
      scheduled_date: orderInfo?.scheduled_date
        ? dfs(orderInfo?.scheduled_date)
        : null,
      status: inventory?.status ? inventory?.status : orderInfo?.status,
      displayTypes: this.pricingService.convertAttributesToDisplay(
        inventory.type
      ),
      title:
        inventory?.abrev_title ||
        this.quoteGenerationService.createProductTitle(inventory)
    })
  }

  orderToInventory(order) {
    return order.line_items
      .map((li) => {
        if (!li.inventory) return null
        let orderInfo = {
          display_order_id: order.display_order_id,
          potential_date: li.potential_date,
          scheduled_date: li.scheduled_date,
          status: order.status === "Delivered" ? order.status : "Attached"
        }

        return this.dtoInventory(li.inventory, orderInfo)
      })
      .filter((i) => i !== null)
  }

  inventoryListToDtos(inventoryList) {
    return inventoryList.map((c) => {
      return this.dtoInventory(c)
    })
  }
  removeOtherInventory(searchBy, searchTerm, orders) {
    if (searchBy == "ORDER_ID") return orders
    if (searchTerm == "All") return orders
    if (searchBy == "CONTAINER_RELEASE")
      return orders.map((order) => {
        let line_items = order.line_items
        order.line_items = [
          ...line_items.filter((li) => {
            if (!li.inventory) return false
            return li.inventory?.container_release_number?.includes(searchTerm)
          })
        ]
        return order
      })
    if (searchBy == "CONTAINER_NUMBER")
      return orders.map((order) => {
        let line_items = order.line_items
        order.line_items = [
          ...line_items.filter((li) => {
            if (!li.inventory) return false
            return li.inventory?.container_number?.includes(searchTerm)
          })
        ]
        return order
      })
    return orders
  }

  async swapInventory(inventoryId, status, action) {
    // this function needs to find the given lineitem that is being affected and swap that out
    const { data, isLoading, error } = await this.inventoryApi.getInventoryById(
      inventoryId
    )
    let inventoryItem = this.dtoInventory(data.value)
    let inventoryStoreList = []
    let index = -1
    switch (status) {
      case "Delivered":
        inventoryStoreList = cloneDeep(this.inventoryStore.deliveredInventory)
        index = inventoryStoreList.findIndex((i) => inventoryItem.id === i.id)
        if (index != -1) {
          inventoryStoreList[index] = inventoryItem
          this.inventoryStore.setDeliveredInventory([])
          this.inventoryStore.setDeliveredInventory(inventoryStoreList)
        } else {
          // This is a create
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.allInventory)
          ]
          this.inventoryStore.setAllInventory([])
          this.inventoryStore.setAllInventory(inventoryStoreList)
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.deliveredInventory)
          ]
          this.inventoryStore.setDeliveredInventory([])
          this.inventoryStore.setDeliveredInventory(inventoryStoreList)
        }
        break
      case "Attached":
        inventoryStoreList = cloneDeep(this.inventoryStore.attachedInventory)
        index = inventoryStoreList.findIndex((i) => inventoryItem.id === i.id)
        if (index != -1) {
          inventoryStoreList[index] = inventoryItem
          this.inventoryStore.setAttachedInventory([])
          this.inventoryStore.setAttachedInventory(inventoryStoreList)
        } else {
          // This is a create
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.allInventory)
          ]
          this.inventoryStore.setAllInventory([])
          this.inventoryStore.setAllInventory(inventoryStoreList)
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.attachedInventory)
          ]
          this.inventoryStore.setAttachedInventory([])
          this.inventoryStore.setAttachedInventory(inventoryStoreList)
        }
        break
      case "Available":
        inventoryStoreList = cloneDeep(this.inventoryStore.availableInventory)
        index = inventoryStoreList.findIndex((i) => inventoryItem.id === i.id)
        if (index != -1) {
          inventoryStoreList[index] = inventoryItem
          this.inventoryStore.setAvailableInventory([])
          this.inventoryStore.setAvailableInventory(inventoryStoreList)
        } else {
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.allInventory)
          ]
          this.inventoryStore.setAllInventory([])
          this.inventoryStore.setAllInventory(inventoryStoreList)
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.availableInventory)
          ]
          this.inventoryStore.setAvailableInventory([])
          this.inventoryStore.setAvailableInventory(inventoryStoreList)
        }
        break
      case "All":
        inventoryStoreList = cloneDeep(this.inventoryStore.allInventory)
        index = inventoryStoreList.findIndex((i) => inventoryItem.id === i.id)
        if (index != -1) {
          inventoryStoreList[index] = inventoryItem
          this.inventoryStore.setAllInventory([])
          this.inventoryStore.setAllInventory(inventoryStoreList)
        } else {
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.allInventory)
          ]
          this.inventoryStore.setAllInventory([])
          this.inventoryStore.setAllInventory(inventoryStoreList)
        }
        break
      case "Delinquent":
        inventoryStoreList = cloneDeep(this.inventoryStore.delinquentInventory)
        index = inventoryStoreList.findIndex((i) => inventoryItem.id === i.id)
        if (index != -1) {
          inventoryStoreList[index] = inventoryItem
          this.inventoryStore.setDelinquentInventory([])
          this.inventoryStore.setDelinquentInventory(inventoryStoreList)
        } else {
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.allInventory)
          ]
          this.inventoryStore.setAllInventory([])
          this.inventoryStore.setAllInventory(inventoryStoreList)
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.delinquentInventory)
          ]
          this.inventoryStore.setDelinquentInventory([])
          this.inventoryStore.setDelinquentInventory(inventoryStoreList)
        }
        break
      case "Ready":
        inventoryStoreList = cloneDeep(this.inventoryStore.readyInventory)
        index = inventoryStoreList.findIndex((i) => inventoryItem.id === i.id)
        if (index != -1) {
          inventoryStoreList[index] = inventoryItem
          this.inventoryStore.setReadyInventory([])
          this.inventoryStore.setReadyInventory(inventoryStoreList)
        } else {
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.allInventory)
          ]
          this.inventoryStore.setAllInventory([])
          this.inventoryStore.setAllInventory(inventoryStoreList)
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.readyInventory)
          ]
          this.inventoryStore.setReadyInventory([])
          this.inventoryStore.setReadyInventory(inventoryStoreList)
        }
        break
      case "UNKNOWN":
        inventoryStoreList = cloneDeep(this.inventoryStore.unknownInventory)
        index = inventoryStoreList.findIndex((i) => inventoryItem.id === i.id)
        if (index != -1) {
          inventoryStoreList[index] = inventoryItem
          this.inventoryStore.setUnknownInventory([])
          this.inventoryStore.setUnknownInventory(inventoryStoreList)
        } else {
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.allInventory)
          ]
          this.inventoryStore.setAllInventory([])
          this.inventoryStore.setAllInventory(inventoryStoreList)
          inventoryStoreList = [
            inventoryItem,
            ...cloneDeep(this.inventoryStore.unknownInventory)
          ]
          this.inventoryStore.setUnknownInventory([])
          this.inventoryStore.setUnknownInventory(inventoryStoreList)
        }
        break
    }
  }

  sizes = [
    {
      label: "10 ft",
      value: "10"
    },
    {
      label: "20 ft",
      value: "20"
    },
    {
      label: "40 ft",
      value: "40"
    },
    {
      label: "45 ft",
      value: "45"
    }
  ]

  conditions = [
    {
      label: "One-Trip",
      value: "One-Trip"
    },
    {
      label: "Used",
      value: "Used"
    }
  ]

  accessoryConditions = [
    {
      label: "New",
      value: "New"
    },
    {
      label: "Used",
      value: "Used"
    }
  ]

  types = [
    {
      label: "Standard",
      value: "standard"
    },
    {
      label: "High Cube",
      value: "high_cube"
    },
    {
      label: "Double Door",
      value: "double_door"
    },
    {
      label: "WWT/CW",
      value: "wwt_cw"
    },
    {
      label: "Premium",
      value: "premium"
    },
    {
      label: "AS IS",
      value: "as_is"
    },
    {
      label: "Open Side",
      value: "open_side"
    },
    {
      label: "Side Doors",
      value: "side_doors"
    }
    // { label: "Open Top", value: "open_top" },
    // { label: "Refrigerated", value: "refrigerated" },
    // { label: "Insulated", value: "insulated" },
    // { label: "Flat rack", value: "flat_rack" },
    // { label: "Dry van", value: "dry_van" },
    // { label: "Hazmat", value: "hazmat" },
    // { label: "Lift gate", value: "lift_gate" },
    // { label: "Heated", value: "heated" },
    // { label: "Side door", value: "side_door" },
    // { label: "Tarp", value: "tarp" },
    // { label: "Pallet jack", value: "pallet_jack" },
    // { label: "Stackable", value: "stackable" },
    // { label: "Over weight", value: "overweight" },
    // { label: "Over length", value: "overlength" },
    // { label: "Over height", value: "overheight" },
    // { label: "Over width", value: "overwidth" },
    // { label: "Over cube", value: "overcube" },
  ]

  purchase_types = [
    {
      label: "All",
      value: "ALL"
    },
    {
      label: "Purchase",
      value: "PURCHASE"
    },
    {
      label: "Accessory Purchase",
      value: "PURCHASE_ACCESSORY"
    },
    {
      label: "Rent",
      value: "RENT"
    },
    {
      label: "Rent to own",
      value: "RENT_TO_OWN"
    }
  ]

  payment_types = [
    { label: "Credit card", value: "CC" },
    { label: "Wire", value: "Wire" },
    { label: "Check", value: "Check" },
    { label: "Cash", value: "Cash" }
  ]

  defaultContainerType = {
    standard: true,
    high_cube: false,
    dimensions: "20 x 8 x 8",
    double_door: false
  }

  columnOrdering = [
    {
      field: "display_created_at",
      display: "Created on",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "display_invoiced_at",
      display: "Invoiced date",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "container_number",
      display: "Container number",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "invoice_number",
      display: "Invoice number",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "container_release_number",
      display: "Container Release",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "depot.city",
      display: "Location",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "vendor_name",
      display: "Vendor",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "depot_name",
      display: "Depot",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "product.title",
      display: "Title",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    {
      field: "total_cost",
      display: "Total cost",
      sortable: true,
      style: "width: 160px",
      status: ["All", "AttachingContainer"]
    },
    // {
    //   field: "display_order_id",
    //   display: "Order ID",
    //   sortable: true,
    //   style: "width: 100px",
    //   status: ["All"],
    // },
    {
      field: "scheduled_date",
      display: "Set Date",
      sortable: true,
      style: "width: 100px",
      status: ["All"]
    },
    {
      field: "potential_date",
      display: "Potential Date",
      sortable: true,
      style: "width: 100px",
      status: ["All"]
    },
    {
      field: "product.condition",
      display: "Condition",
      sortable: true,
      style: "width: 160px",
      status: ["All"]
    },

    {
      field: "status",
      display: "Status",
      sortable: true,
      style: "width: 160px",
      status: ["All"]
    },
    {
      field: "product.container_size",
      display: "Container size",
      sortable: true,
      style: "width: 160px",
      status: ["All"]
    },
    {
      field: "purchase_type",
      display: "Purchase type",
      sortable: true,
      style: "width: 160px",
      status: ["All"]
    }
  ]
}
