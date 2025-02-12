import { useHttp } from "@/composables/useHttp"

export default class LineItemApi {
  constructor() {}
  async updateLineItem(data) {
    return useHttp(`/line_item`, "PATCH", data)
  }

  async updateLineItemExtra(data) {
    return useHttp(`/line_item_extra`, "PATCH", data)
  }

  async deleteLineItem(id) {
    return useHttp(`/line_item/${id}`, "DELETE")
  }

  async sendPickupEmail(id) {
    return useHttp(`/line_item/pickup_email/${id}`, "GET")
  }
}
