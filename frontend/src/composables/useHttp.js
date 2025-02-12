import axios from "axios"
import { useAxios } from "@vueuse/integrations/useAxios"

import { auth0 } from "../service/authService.js"
import { useErrorHandler } from "@/store/modules/errorHandler"

export const instance = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_URL
})

export const noAuthHTTP = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_URL
})

export const intercept = instance.interceptors.request.use(
  async (instance) => {
    try {
      let token = null
      if (auth0.isAuthenticated.value) {
        token = await auth0.getAccessTokenSilently()
      }

      if (token) {
        instance.headers["Access-Control-Max-Age"] = "3600"
        instance.headers["Authorization"] = `Bearer ${token}`
        instance.headers["ngrok-skip-browser-warning"] = "69420"
      } else {
        return instance
      }
    } catch (error) {
      console.log("error", error)
    }

    return instance
  },
  async (error) => {
    return Promise.reject(error)
  }
)

instance.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const errorHandler = useErrorHandler()
    if (
      !window.location.href.includes("payment") &&
      (error.response.status === 401 || error.response.status === 403)
    ) {
      console.log("401 error")
      if (error.response.status === 403)
        errorHandler.setError(
          true,
          error.response.data.detail,
          error.response.status
        )
      return Promise.reject(error)
    }
    return Promise.reject(error)
  }
)

export const useGenericHttp = (path, method, data = null, headers = {}) => {
  const requestConfig = {
    method: method,
    headers: headers
  }
  if (data) {
    requestConfig.data = data
  }
  console.log(requestConfig)
  console.log(data)
  return useAxios(path, requestConfig)
}

export const usePublicHttp = (path, method, data = null, headers = {}) => {
  headers = Object.assign(headers, {
    "ngrok-skip-browser-warning": "69420"
  })

  const requestConfig = {
    method: method,
    headers: headers
  }
  if (data) {
    requestConfig.data = data
  }
  return useAxios(`/public${path}`, requestConfig, noAuthHTTP)
}

export const useHttp = (path, method, data = null, headers = {}) => {
  headers = Object.assign(headers, {
    "ngrok-skip-browser-warning": "69420"
  })

  const requestConfig = {
    method: method,
    headers: headers
  }
  if (data) {
    requestConfig.data = data
  }
  return useAxios(path, requestConfig, instance)
}

export const fetchFile = (path, method, data = null, headers = {}) => {
  headers = Object.assign(headers, {
    "ngrok-skip-browser-warning": "69420"
  })

  const requestConfig = {
    method: method,
    headers: headers,
    responseType: "blob"
  }
  if (data) {
    requestConfig.data = data
  }
  return useAxios(path, requestConfig, instance)
}
