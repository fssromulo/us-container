/* eslint-disable no-console */
import { defineStore } from "pinia"
import { useStorage } from "@vueuse/core"

export const useDownpaymentStrategyStore = defineStore(
  "downpaymentStrategyStore",
  {
    state: () => {
      return {
        downpaymentStrategy: ""
      }
    },
    getters: {},
    actions: {
      setDownpaymentStrategy(val) {
        this.downpaymentStrategy = val
      }
    }
  }
)
