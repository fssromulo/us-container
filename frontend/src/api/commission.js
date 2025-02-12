import { useHttp } from "@/composables/useHttp"

export default class CommissionApi {
  constructor() {}
  async getCommissions(queryParams) {
    return useHttp(`/commissions${queryParams}`, "GET")
  }

  async updateCommissionPeriod(queryParams) {
    return useHttp(`/update_commission_period${queryParams}`, "GET")
  }

  async closed_commissions_date(data) {
    return useHttp(`/closed_commissions_date`, "POST", data)
  }

  async getClosedCommissionResults(
    startDate,
    endDate,
    user_id,
    teamCommission = false,
    isManagerOnly = true
  ) {
    const queryParams = user_id
      ? `?user_id=${user_id}&start_date=${startDate}&end_date=${endDate}&team=${teamCommission}`
      : `?start_date=${startDate}&end_date=${endDate}&team=${teamCommission}&is_manager_only=${isManagerOnly}`
    return useHttp(`/closed_commission_results${queryParams}`, "GET")
  }

  async fetchRankings(queryParams) {
    return useHttp(`/rankings${queryParams}`, "GET")
  }
}
