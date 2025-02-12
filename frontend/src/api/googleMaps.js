import { usePublicHttp, useGenericHttp } from "@/composables/useHttp"

export default class GoogleMapsApi {
  constructor() {}

  async callGoogleService(origins, destinations) {
    let googleMaps = {
      origins: origins,
      destinations: destinations
    }
    try {
      const { data } = await usePublicHttp(`/google_maps`, "POST", googleMaps)
      return data.value
    } catch (error) {
      console.log(error)
    }
  }

  async geoNamesSearchTomTom(zip, account_country) {
    if (account_country == "Canada") {
      let encodedQuery = encodeURIComponent(`Canada, ${zip}`)
      return usePublicHttp(`/tomtom/${encodedQuery}`, "GET")
    } else {
      let encodedQuery = encodeURIComponent(`USA, ${zip}`)
      return usePublicHttp(`/tomtom/${encodedQuery}`, "GET")
    }
  }

  async addZipCodeToDB(postData) {
    return usePublicHttp(`/location_distance`, "POST", postData)
  }
}
