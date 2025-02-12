/* eslint-disable no-console */
import { defineStore } from "pinia"

export const useInvoiceHelper = defineStore("InvoiceHelper", {
  state: () => {
    return {
      cart: [],
      hideOrderDetails: false
    }
  },
  getters: {},
  actions: {
    setCart(cart) {
      this.cart = cart
    }
  }
})
