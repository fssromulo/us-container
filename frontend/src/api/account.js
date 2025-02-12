import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class AccountApi {
  async getPublicAccount(accountId) {
    return usePublicHttp(`/account/${accountId}`, "GET")
  }

  async getAccount() {
    return useHttp("/account", "GET")
  }
  async getRoles() {
    return useHttp("/list_roles", "GET")
  }

  async updateAccount(data) {
    return useHttp(`/account`, "PATCH", data)
  }
  async updateAccountAttribute(data) {
    return useHttp(`/account/attributes`, "PATCH", data)
  }
}
