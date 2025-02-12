import { useHttp } from "@/composables/useHttp"

export default class ContractApi {
  constructor() {}

  async sendAuthorizationForm(id, form_with_upload) {
    return useHttp(
      `/contracts/send_authorization_form?order_id=${id}&with_photo=${form_with_upload}`,
      "GET"
    )
  }

  async sendMainContract(id) {
    return useHttp(`/contracts/send_main_contract?order_id=${id}`, "GET")
  }
}
