import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class LogisticsZonesApi {
  async getAllLogisticsZones() {
    return useHttp(`/logistics_zones`, "GET")
  }

  async update(dataReq, id) {
    return useHttp(`/logistics_zones/${id}`, "PATCH", dataReq)
  }

  async create(dataReq, id) {
    return useHttp(`/logistics_zones/${id}`, "POST", dataReq)
  }

  async delete(id) {
    return useHttp(`/logistics_zones/${id}`, "DELETE")
  }
}
