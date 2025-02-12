import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class TaxApi {
  constructor() {}

  async getTaxes() {
    return useHttp("/taxes", "GET")
  }

  async getTaxesPublic(accountId) {
    return usePublicHttp(`/taxes/${accountId}`, "GET")
  }

  async calculateTaxAvalara(
    customer_zip,
    container_state,
    container_city,
    accountId
  ) {
    let avalaraItem = {
      customer_zip: customer_zip,
      container_state: container_state,
      container_city: container_city
    }
    return usePublicHttp(`/taxes/avalara/${accountId}`, "POST", avalaraItem)
  }

  async hasAvalaraTaxIntegration(accountId) {
    return usePublicHttp(`/taxes/has_avalara_integration/${accountId}`, "GET")
  }
}
