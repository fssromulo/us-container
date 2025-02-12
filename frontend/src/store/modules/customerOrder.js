/* eslint-disable no-console */
import { defineStore } from "pinia"
import { useUsers } from "./users"
import Lock from "../../service/Lock.js"

const lock = new Lock()

const resetOrderLock = new Lock()

export const useCustomerOrder = defineStore("customerOrder", {
  state: () => {
    const usersStore = useUsers()

    return {
      customer: {},
      lineItems: [],
      filteredAccessories: [],
      order: {},
      publicOrder: null,
      publicCms: null,
      forceRefresh: false,
      cart: {
        cartTypes: [
          {
            property: "accessories",
            title: "",
            name: "Accessory",
            header: "Accessories",
            note: "*Accessories shipped separately",
            fieldsMap: {
              Accessory: "title",
              Price: "sale_price",
              Qty: "quantity"
            }
          },
          {
            property: "containers",
            title: "",
            name: "Container",
            header: "Containers",
            note: ""
          }
        ],
        accessories: [],
        containers: []
      },
      createOrderStatus: "NOT_STARTED",
      selectedCategory: {
        name: "All",
        code: "ALL"
      },
      camelCasedOrderStatus: "invoicedOrders",
      currentOrderStatus: "",
      address: {},
      billing_address: {},
      applyDiscount: false,
      searchedOrders: [],
      invoicedOrders: [],
      signedOrders: [],
      paidOrders: [],
      podOrders: [],
      delayedOrders: [],
      purchaseOrderOrders: [],
      partiallyPaidOrders: [],
      toDeliverOrders: [],
      allActiveOrders: [],
      deliveredOrders: [],
      onRentOrders: [],
      completedOrders: [],
      fulfilledOrders: [],
      expiredOrders: [],
      cancelledOrders: [],
      returnedOrders: [],
      approvedOrders: [],
      awaitingDeliveryOrders: [],
      currentDelinquentOrders: [],
      firstPaymentReceivedOrders: [],
      currentOrders: [],
      delinquentOrders: [],
      estimateOrders: [],
      quoteOrders: [],
      addedOrderItems: {},
      accessoryList: [],
      lock: lock,
      orderResetLock: resetOrderLock,
      fetchOrderFull: false,
      feeTypes: []
    }
  },
  getters: {},
  actions: {
    setForceRefresh(forceRefresh) {
      this.forceRefresh = forceRefresh
    },
    setFilteredAccessories(accessories) {
      this.filteredAccessories = [...accessories]
    },
    setFeeTypes(feeTypes) {
      this.feeTypes = feeTypes
    },
    setPublicCms(cms) {
      this.publicCms = cms
    },
    setSelectedCategory(category) {
      this.selectedCategory = category
    },
    setPublicOrder(order) {
      // UNCOMMENT FOR ACCESSORIES
      // let currentNumberAccessory = Math.floor(Math.random() * (3 - 1 + 1)) + 1;
      // order.accessory_items = [... this.accessoryList.slice(0, currentNumberAccessory)];
      this.publicOrder = order
    },
    setCurrentOrders(orders) {
      this.currentOrders = orders
    },
    setSignedOrders(orders) {
      this.signedOrders = orders
    },
    setFulfilledOrders(orders) {
      this.fulfilledOrders = orders
    },
    setCamelCasedOrderStatus(status) {
      this.camelCasedOrderStatus = status
    },
    setCurrentOrderStatus(status) {
      this.currentOrderStatus = status
    },
    setCreateOrderStatus(status) {
      this.createOrderStatus = status
    },
    resetCreateOrderStatus() {
      this.createOrderStatus = "NOT_STARTED"
    },
    setOrder(order) {
      // UNCOMMENT FOR ACCESSORIES
      // let currentNumberAccessory = Math.floor(Math.random() * (3 - 1 + 1)) + 1;
      // order.accessory_items = [... this.accessoryList.slice(0, currentNumberAccessory)];
      this.order = order
    },
    setApplyDiscount(applyDiscount) {
      this.applyDiscount = applyDiscount
    },
    addToConatainerCart(item) {
      this.cart.containers.push(item)
    },
    addToAccessoriesCart(item) {
      this.cart.accessories.push(item)
    },
    removeFromContainerCart(item) {
      this.cart.containers = this.cart.containers.filter(
        (item_cart) => item_cart.containerId !== item.containerId
      )
    },
    removeFromAccessoriesCart(item) {
      this.cart.accessories = this.cart.accessories.filter(
        (item_cart) => item_cart.id !== item.id
      )
    },
    emptyContainerCart() {
      this.cart.containers = []
      this.cart.accessories = []
    },
    emptyAccessoriesCart() {
      this.cart.accessories = []
    },
    emptyCart() {
      this.cart.accessories = []
      this.cart.containers = []
    },

    setCustomer(customer) {
      this.customer = customer
    },
    setAddress(address) {
      this.address = address
    },
    setBillingAddress(billing_address) {
      this.billing_address = billing_address
    },
    setLineItems(lineItems) {
      this.lineItems = lineItems
    },
    setAccessories(accessories) {
      this.accessories = accessories
    },
    setInvoicedOrders(invoicedOrders) {
      this.invoicedOrders = invoicedOrders
    },
    setPaidOrders(paidOrders) {
      this.paidOrders = paidOrders
    },
    setPodOrders(podOrders) {
      this.podOrders = podOrders
    },
    setDelayedOrders(delayedOrders) {
      this.delayedOrders = delayedOrders
    },
    setFirstPaymentReceivedOrders(orders) {
      this.firstPaymentReceivedOrders = orders
    },
    setPartiallyPaidOrders(partiallyPaidOrders) {
      this.partiallyPaidOrders = partiallyPaidOrders
    },
    setAllActiveOrders(allActiveOrders) {
      this.allActiveOrders = allActiveOrders
    },
    setToDeliverOrders(toDeliverOrders) {
      this.toDeliverOrders = toDeliverOrders
    },
    setOnRentOrders(onRentOrders) {
      this.onRentOrders = onRentOrders
    },
    setPurchaseOrderOrders(purchaseOrderOrders) {
      this.purchaseOrderOrders = purchaseOrderOrders
    },
    setDeliveredOrders(deliveredOrders) {
      this.deliveredOrders = deliveredOrders
    },
    setEstimateOrders(estimateOrders) {
      this.estimateOrders = estimateOrders
    },
    setQuoteOrders(quoteOrders) {
      this.quoteOrders = quoteOrders
    },
    setCompletedOrders(completedOrders) {
      this.completedOrders = completedOrders
    },
    setExpiredOrders(expiredOrders) {
      this.expiredOrders = expiredOrders
    },
    setCancelledOrders(ordersCancelled) {
      this.cancelledOrders = ordersCancelled
    },
    setApprovedOrders(approvedOrders) {
      this.approvedOrders = approvedOrders
    },
    setAwaitingDeliveryOrders(awaitingDeliveryOrders) {
      this.awaitingDeliveryOrders = awaitingDeliveryOrders
    },
    setCurrentOrders(currentOrders) {
      this.currentOrders = currentOrders
    },
    setReturnedOrders(currentOrders) {
      this.returnedOrders = currentOrders
    },
    setCurrentDelinquentOrders(orders) {
      this.currentDelinquentOrders = orders
    },
    setDelinquentOrders(delinquentOrders) {
      this.delinquentOrders = delinquentOrders
    },
    setSearchedOrders(orders) {
      this.searchedOrders = orders
    },
    addToOrderItemList(key, addedOrderItem) {
      this.addedOrderItems[key].push(addedOrderItem)
    },
    setAddedOrderItems(key, addedOrderItems) {
      this.addedOrderItems[key] = addedOrderItems
    }
  }
})
