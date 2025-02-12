import { usePublicHttp, useGenericHttp } from "@/composables/useHttp"
import GoogleMapsApi from "@/api/googleMaps"

const MILE_TO_METER = 1609.344
const KM_TO_METER = 1000

const googleMapsApi = new GoogleMapsApi()

export const lookupZip = async (
  originZip,
  destinationLocations,
  account_country
) => {
  const { data } = await usePublicHttp(`/location_distance/${originZip}`, "GET")
  if (data.value.length) {
    console.log("zip found in db")
    const responseZips = data.value.map((d) => d.destination_zip)
    const missingZips = destinationLocations
      .map((l) => l.zip)
      .filter((d) => !responseZips.includes(d))
    if (missingZips.length) {
      const missingLocations = destinationLocations.filter((l) =>
        missingZips.includes(l.zip)
      )
      console.log("missingZips", missingLocations)
      console.log("missing some zips from db")
      let newLocationDistances = await googleDistanceMatrixService(
        originZip,
        missingLocations,
        account_country
      )
      console.log("newLocationDistances", newLocationDistances)
      return [...data.value, ...newLocationDistances]
    }
    return data.value
  } else {
    console.log("zip not found in db")
    const distanceDestinations = await googleDistanceMatrixService(
      originZip,
      destinationLocations,
      account_country
    )
    return distanceDestinations
  }
}

const chunkArray = (array, size) => {
  const chunked_arr = []
  let index = 0
  while (index < array.length) {
    chunked_arr.push(array.slice(index, size + index))
    index += size
  }
  return chunked_arr
}

export const googleDistanceMatrixService = async (
  originZip,
  locations,
  account_country
) => {
  const destinationZips = locations.map((l) => l.zip)

  const { data } = await googleMapsApi.geoNamesSearchTomTom(
    originZip,
    account_country
  )
  const geoNameSearchResponse = data.value.results.filter(
    (r) => r.matchConfidence.score >= 1
  )[0]

  const googleDestinationPromises = await Promise.all(
    chunkArray(destinationZips, 25).map(async (chunk) => {
      const r = await searchByLatLongCityState(
        geoNameSearchResponse || {},
        chunk
      )
      return r
    })
  )
  const r = googleDestinationPromises.reduce((acc, curr) => {
    return {
      ...acc,
      rows: [...acc.rows, ...curr.rows],
      origin_addresses: [...acc.origin_addresses, ...curr.origin_addresses]
    }
  })

  let distanceDestinations = []

  // if (r.hasOwnProperty("status") && r.rows[0].elements.length === 0) {
  //   console.log("no results found");
  //   r = await searchByLatLongCityState(originZip, destinationZips);
  // }

  if (r.origin_addresses[0] === "") {
    console.log("no origin address found")
  } else {
    const customerBasicAddressDetails = r.origin_addresses[0]
    console.log("customerBasicAddressDetails", customerBasicAddressDetails)
    r.rows[0].elements.forEach((e, i) => {
      if (e) {
        if (e.status === "ZERO_RESULTS") {
          console.log("no results found")
          return
        }
        distanceDestinations.push({
          destination_zip: locations[i].zip,
          destination_city: locations[i].city,
          origin_zip: originZip,
          distance:
            account_country == "Canada"
              ? String(Number(e.distance?.value) / KM_TO_METER)
              : String(Number(e.distance?.value) / MILE_TO_METER)
        })
      }
    })
  }

  const addDistancesToDBPromises = distanceDestinations.map(async (d) => {
    const { data } = await googleMapsApi.addZipCodeToDB(d)
    return data.value
  })
  const newItems = await Promise.all(addDistancesToDBPromises)
  return newItems
  // return await lookupZip(originZip, locations);
}

export const searchByLatLongCityState = async (
  geoNameSearchResponse,
  destinationZips
) => {
  // let latLng = `${geoNameSearchResponse.lat},${geoNameSearchResponse.lng}`;
  let basicAddr = `${geoNameSearchResponse?.address?.freeformAddress}+${geoNameSearchResponse?.address?.countrySubdivisionName}+${geoNameSearchResponse?.address?.postalCode}`
  console.log(basicAddr)
  let r = await googleMapsApi.callGoogleService([basicAddr], destinationZips)

  if (
    r.rows[0].elements.length === 0 ||
    r.rows[0].elements.some((e) => e.status === "ZERO_RESULTS")
  ) {
    console.log("trying city/state")
    let cityState = `${geoNameSearchResponse?.address?.postalName}+${geoNameSearchResponse?.address?.countrySubdivisionName}`
    r = await googleMapsApi.callGoogleService([cityState], destinationZips)
  }

  if (
    r.rows[0].elements.length === 0 ||
    r.rows[0].elements.some((e) => e.status === "ZERO_RESULTS")
  ) {
    console.log("trying lat/lng")
    let latLng = `${geoNameSearchResponse?.position?.lat},${geoNameSearchResponse?.position?.lon}`
    r = await googleMapsApi.callGoogleService([latLng], destinationZips)
  }

  return r
}

//   async getDistances(zip) {
//     return usePublicHttp(`/location_distances/${zip}`, "GET");
//   }
