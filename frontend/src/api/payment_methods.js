import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class PaymentMethodsApi {
  async getAllPaymentMethods() {
    return useHttp(`/payment_methods`, "GET")
  }

  async update(dataReq, id) {
    return useHttp(`/payment_methods/${id}`, "PATCH", dataReq)
  }

  async create(dataReq, id) {
    return useHttp(`/payment_methods/${id}`, "POST", dataReq)
  }

  async delete(id) {
    return useHttp(`/payment_methods/${id}`, "DELETE")
  }
}
