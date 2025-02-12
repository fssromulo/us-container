/* eslint-disable no-console */

import { useStorage } from "@vueuse/core"
import { defineStore } from "pinia"
import {
  originalOrderFilters,
  selectedSearchCriteriaOriginal
} from "@/utils/constants"
import { cloneDeep } from "lodash"

// useStorage("users", []),
// useStorage("currentUser", null),
export const useUsers = defineStore("users", {
  state: () => {
    return {
      users: [],
      currentUser: null,
      roles: [],
      commission_roles: [],
      darkMode: useStorage("darkMode", false),
      cms: null,
      integrations: null,
      // loggingOut: useStorage("loggingOut", false),
      isEmulating: false,
      offlineMode: false,
      selectedSearchCriteria: cloneDeep(selectedSearchCriteriaOriginal),
      orderFilters: cloneDeep(originalOrderFilters)
    }
  },
  getters: {},
  actions: {
    // setLoggingOut(loggingOut) {
    //   this.loggingOut = loggingOut;
    // },
    setIntegrations(integrations) {
      this.integrations = integrations
    },
    setCms(cms) {
      this.cms = cms
    },
    setRoles(roles) {
      this.roles = roles
    },
    setCommissionRoles(roles) {
      this.commission_roles = roles
    },
    setIsEmulating(isEmulating) {
      this.isEmulating = isEmulating
    },
    setCurrentUser(currentUser) {
      this.currentUser = currentUser
    },
    setOrderFilters(orderFilters) {
      this.orderFilters = orderFilters
    },
    setProductTypes(productTypes) {
      this.productTypes = productTypes
    },
    setSelectedSearchCriteria(selectedSearchCriteria) {
      this.selectedSearchCriteria = selectedSearchCriteria
    },
    setUsers(users) {
      this.users = users
    },
    setAssistantsAndManagers(assistantsAndManagers) {
      this.assistantsAndManagers = assistantsAndManagers
    },
    setTeamsAndLeads(teamsAndLeads) {
      this.teamsAndLeads = teamsAndLeads
    },
    setOfflineMode(offlineMode) {
      this.offlineMode = offlineMode
    }
  }
})
