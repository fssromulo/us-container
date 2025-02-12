import { useHttp } from "@/composables/useHttp"

export default class PowerBIApi {
  constructor() {}

  async getToken() {
    return useHttp("/bi_token", "GET")
  }
}
