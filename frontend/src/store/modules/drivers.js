/* eslint-disable no-console */
import { useStorage } from "@vueuse/core"
import { defineStore } from "pinia"
import DriversService from "@/service/Drivers"

const driversService = new DriversService()

export const useDrivers = defineStore("drivers", {
  state: () => {
    return {
      drivers: []
    }
  },
  getters: {},
  actions: {
    setDrivers(drivers) {
      this.drivers = drivers.map((driver) => driversService.dtoDriver(driver))
    }
  }
})
