/* eslint-disable no-console */
import { defineStore } from "pinia"

export const useErrorHandler = defineStore("errorHandler", {
  state: () => {
    return {
      hasError: false,
      errorMessage: "",
      statusCode: 0
    }
  },
  getters: {},
  actions: {
    setError(hasError, errorMessage, statusCode) {
      console.log(hasError, errorMessage, statusCode)
      this.hasError = hasError
      this.errorMessage = errorMessage
      this.statusCode = statusCode
    }
  }
})
