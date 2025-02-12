import { useHttp } from "@/composables/useHttp"

export default class DepotApi {
  constructor() {}

  async getDepots() {
    return useHttp("/depots", "GET")
  }

  async getDepotById(id) {
    return useHttp(`/depot/${id}`, "GET")
  }

  async updateDepot(id, data) {
    return useHttp(`/depot/${id}`, "PATCH", data)
  }

  async createDepot(data) {
    return useHttp(`/depot`, "POST", data)
  }
}
