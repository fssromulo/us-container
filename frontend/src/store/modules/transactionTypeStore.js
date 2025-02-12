/* eslint-disable no-console */
import { defineStore } from "pinia"

export const useTransactionTypeStore = defineStore("transactionTypeStore", {
  state: () => {
    return {
      periodIds: [],
      amount: [],
      canSaveTransasctionType: false
    }
  },
  getters: {},
  actions: {
    setPeriodIds(periodIds) {
      this.periodIds = periodIds
    },
    setAmount(amount) {
      this.amount = amount
    },
    setCanSaveTransactionType(boolean_val) {
      this.canSaveTransasctionType = boolean_val
    }
  }
})
