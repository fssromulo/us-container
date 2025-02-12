import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class DriverApi {
  constructor() {}

  async getDrivers(cached = true) {
    if (cached) {
      return useHttp("/drivers", "GET")
    } else {
      return useHttp("/drivers", "GET", null, { "Cache-Control": "no-cache" })
    }
  }

  async getDriverById(id) {
    return useHttp(`/driver/${id}`, "GET")
  }

  async updateDriver(id, data) {
    return useHttp(`/driver/${id}`, "PATCH", data)
  }

  async createDriver(data) {
    return useHttp(`/driver`, "POST", data)
  }

  async deleteDriver(id) {
    return useHttp(`/driver/${id}`, "DELETE")
  }
}
