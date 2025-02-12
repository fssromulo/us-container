/* eslint-disable no-console */
import { defineStore } from "pinia"

export const useDepots = defineStore("depots", {
  state: () => {
    return {
      depots: []
    }
  },
  getters: {},
  actions: {
    setDepots(depots) {
      this.depots = depots
    }
  }
})
