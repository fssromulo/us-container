import { useHttp } from "@/composables/useHttp"

export default class QuoteSearchesApi {
  async createQuoteSearch(data) {
    return useHttp(`/quote_searches`, "POST", data)
  }

  async getQuoteSearches(date1, date2, zone, user) {
    if (date1 === undefined && user == "ALL") {
      return useHttp("/quote_searches", "GET")
    } else {
      zone = encodeURIComponent(zone)
      return useHttp(
        `/quote_searches?date1=${date1}&date2=${date2}&timezone=${zone}&selected_user_id=${user}`,
        "GET"
      )
    }
  }
}
