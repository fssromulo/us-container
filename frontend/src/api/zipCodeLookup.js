import { useHttp } from "@/composables/useHttp"

export default class ZipCodeLookup {
  constructor() {}

  async deleteZipCode(zip_code) {
    return useHttp(`/location_distance/${zip_code}`, "DELETE")
  }
}
