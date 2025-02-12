/* eslint-disable no-console */
import { defineStore } from "pinia"

export const usesSwitchToOrdersHelper = defineStore("switchToOrdersHelper", {
  state: () => {
    return {
      index: 0
    }
  },
  getters: {},
  actions: {
    switchToOrders() {
      this.index += 1
    }
  }
})
