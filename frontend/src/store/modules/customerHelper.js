/* eslint-disable no-console */

import { useStorage } from "@vueuse/core"
import { defineStore } from "pinia"

// useStorage("users", []),
// useStorage("currentUser", null),
export const useCustomerHelper = defineStore("customer_helper", {
  state: () => {
    return {
      first_name: "",
      last_name: "",
      company_name: "",
      customer_phone: "",
      customer_email: "",
      street_address: "",
      city: "",
      state: "",
      zip: "",
      county: "",
      version: 0,
      disable: false
    }
  },
  getters: {},
  actions: {
    setDisabled(disabled) {
      this.disable = disabled
    },
    setIncreaseVersion() {
      this.version += 1
    }
  }
})
