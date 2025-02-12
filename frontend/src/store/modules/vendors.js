/* eslint-disable no-console */

import { defineStore } from "pinia"

export const useVendors = defineStore("vendors", {
  state: () => {
    return {
      vendors: []
    }
  },
  getters: {},
  actions: {
    setVendors(vendors) {
      this.vendors = vendors
    }
  }
})
