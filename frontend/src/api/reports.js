import { useHttp } from "@/composables/useHttp"

export default class ReportsApi {
  async getProductTypes() {
    return useHttp(`/product_types`, "GET")
  }

  async getVendors(account_id) {
    return useHttp(`/vendors/${account_id}`, "GET")
  }

  async runByName(name, data) {
    return useHttp(`/reports/by_name/${name}`, "POST", data)
  }
  async notes_rankings(data) {
    return useHttp(`/reports/notes_rankings`, "POST", data)
  }

  async retrieveByName(name, data) {
    return useHttp(`/reports/retrieve_by_name/${name}`, "POST", data)
  }

  async clearReports(name, account_id) {
    return useHttp(`/reports/clear_by_name/${name}/${account_id}`, "GET")
  }

  async closeCommissions(data) {
    return useHttp(`/reports/close_commissions`, "POST", data)
  }
}
