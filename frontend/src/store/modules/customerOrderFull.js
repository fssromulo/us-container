/* eslint-disable no-console */
import { defineStore } from "pinia"
import { dfs } from "@/service/DateFormat"

function mergeArrays(array1, array2) {
  const mergedArray = []

  const seenOrderIds = new Set()

  const addUniqueObject = (obj) => {
    const orderId = obj.order_id
    if (!seenOrderIds.has(orderId)) {
      mergedArray.push(obj)
      seenOrderIds.add(orderId)
    }
  }

  array1.forEach(addUniqueObject)

  array2.forEach(addUniqueObject)

  return mergedArray
}

export const useCustomerOrderFull = defineStore("useCustomerOrderFull", {
  state: () => {
    return {
      orders: [],
      displayOrderIds: {}
    }
  },
  getters: {},
  actions: {
    getDisplayedOrders() {
      const that = this

      return this.orders.filter((o) => {
        return that.displayOrderIds[o.order_display_order_id] === true
      })
    },
    getDisplayedOrdersIds() {
      const that = this

      return Object.keys(this.displayOrderIds).filter(
        (key) => that.displayOrderIds[key] === true
      )
    },
    setOrders(data) {
      this.orders = data
    },
    mergeOrders(data) {
      const newList = data

      const that = this
      const mergedList = mergeArrays(newList, this.orders)
      this.orders = mergedList
    },
    setDisplayOrderIds(ids) {
      this.displayOrderIds = {}
      const that = this
      ids.forEach(function (id) {
        that.displayOrderIds[id] = true
      })
    }
  }
})
