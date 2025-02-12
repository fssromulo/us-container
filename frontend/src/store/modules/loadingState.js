/* eslint-disable no-console */
import { defineStore } from "pinia"

export const loadingStateStore = defineStore("loadingStateStore", {
  state: () => {
    return {
      isLoading: false
    }
  },
  getters: {},
  actions: {
    setIsLoading(isLoading) {
      this.isLoading = isLoading
    }
  }
})
