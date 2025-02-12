import { useHttp } from "@/composables/useHttp"

export default class Cache {
  constructor() {}

  async clear() {
    return useHttp(`/cache`, "DELETE")
  }
}
