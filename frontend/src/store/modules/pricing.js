/* eslint-disable no-console */
import { defineStore } from "pinia"

export const useContainerPrices = defineStore("pricing", {
  state: () => {
    return {
      containerPrices: [],
      filteredAccessoriesPrices: [],
      productCategories: [],
      accessoryPrices: [],
      locations: []
    }
  },
  getters: {},
  actions: {
    setContainerPrices(prices) {
      //prices.sort((a, b) => a.title.localeCompare(b.title));
      this.containerPrices = prices
    },
    setAccessoryPrices(products) {
      this.accessoryPrices = products
    },
    setProductCategories(productCategories) {
      this.productCategories = productCategories
    },
    setLocations(locations) {
      this.locations = locations
    },
    setAccessories(accessories) {
      accessories.sort((a, b) => a.title.localeCompare(b.title))
      this.accessoriesPrices = prices
    },
    setFilteredAccessories(accessories) {
      accessories.sort((a, b) => a.title.localeCompare(b.title))
      this.filteredAccessoriesPrices = accessories
    }
  }
})
