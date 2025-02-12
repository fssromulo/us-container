/* eslint-disable no-console */
import { defineStore } from "pinia"

export const useTaxes = defineStore("taxes", {
  state: () => {
    return {
      taxes: []
    }
  },
  getters: {},
  actions: {
    setTaxes(taxes) {
      this.taxes = taxes
    }
  }
})
