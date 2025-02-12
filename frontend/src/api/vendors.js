import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class VendorsApi {
  constructor() {}

  async getVendors() {
    return useHttp("/vendor", "GET")
  }

  async getVendorById(id) {
    return useHttp(`/vendor/${id}`, "GET")
  }

  async updateVendor(id, data) {
    return useHttp(`/vendor/${id}`, "PATCH", data)
  }

  async createVendor(data) {
    return useHttp(`/vendor`, "POST", data)
  }
}
