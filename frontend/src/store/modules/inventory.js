/* eslint-disable no-console */

import { defineStore } from "pinia"
import cloneDeep from "lodash.clonedeep"

export const useInventory = defineStore("inventory", {
  state: () => {
    return {
      deliveredInventory: [],
      attachedInventory: [],
      availableInventory: [],
      allInventory: [],
      delinquentInventory: [],
      readyInventory: [],
      unknownInventory: []
    }
  },
  getters: {},
  actions: {
    setDeliveredInventory(inventory) {
      this.deliveredInventory = inventory
    },
    setDelinquentInventory(inventory) {
      this.delinquentInventory = inventory
    },
    setReadyInventory(inventory) {
      this.readyInventory = inventory
    },

    setUnknownInventory(inventory) {
      this.unknownInventory = inventory
    },

    setAttachedInventory(inventory) {
      this.attachedInventory = inventory
    },
    setAvailableInventory(inventory) {
      this.availableInventory = inventory
    },
    setPastDueInventory(inventory) {
      this.pastDueInventory = inventory
    },
    setAllInventory(inventory) {
      this.allInventory = inventory
    },
    removeFromInventory(inventory) {
      this.allInventory = cloneDeep(
        this.allInventory.filter((i) => i.id !== inventory.id)
      )
      this.availableInventory = cloneDeep(
        this.availableInventory.filter((i) => i.id !== inventory.id)
      )
      this.attachedInventory = cloneDeep(
        this.attachedInventory.filter((i) => i.id !== inventory.id)
      )
      this.deliveredInventory = cloneDeep(
        this.deliveredInventory.filter((i) => i.id !== inventory.id)
      )
      this.readyInventory = cloneDeep(
        this.readyInventory.filter((i) => i.id !== inventory.id)
      )
      this.unknownInventory = cloneDeep(
        this.unknownInventory.filter((i) => i.id !== inventory.id)
      )
    }
  }
})
