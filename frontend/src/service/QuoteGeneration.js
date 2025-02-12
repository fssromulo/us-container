import parseAddress from "parse-address"
import { searchByLatLongCityState } from "./GoogleMaps"
import GoogleMapsApi from "@/api/googleMaps"
import CustomerApi from "@/api/customers"
import QuoteSearchesApi from "@/api/search_quotes"
import _groupBy from "lodash.groupby"
import TaxService from "@/service/Tax"
import TaxApi from "@/api/tax"
import PricingService from "@/service/Pricing"
import PricingApi from "@/api/pricing"

import { cloneDeep } from "lodash"

import { useContainerPrices } from "../store/modules/pricing"
import { useTaxes } from "../store/modules/taxes"
import { useUsers } from "../store/modules/users"
import { useCustomerOrder } from "../store/modules/customerOrder"
import { lookupZip } from "./GoogleMaps"
import { roundHalfUp } from "@/utils/formatCurrency.js"

export default class QuoteGenerationService {
  customerOrderStore = useCustomerOrder()
  pricingStore = useContainerPrices()
  taxStore = useTaxes()
  usersStore = useUsers()
  customerApi = new CustomerApi()
  quoteSearchesApi = new QuoteSearchesApi()
  taxService = new TaxService()
  taxApi = new TaxApi()
  pricingService = new PricingService()
  pricingApi = new PricingApi()
  googleMapsApi = new GoogleMapsApi()

  compute_priority = (title) => {
    const orderedTitles = {
      "20' Used Standard AS IS": 1,
      "40' Used Standard AS IS": 2,
      "40' Used High Cube AS IS": 3,
      "20' Used Standard WWT/CW": 4,
      "40' Used Standard WWT/CW": 5,
      "40' Used High Cube WWT/CW": 6,
      "20' Used Standard Premium": 7,
      "40' Used Standard Premium": 8,
      "40' Used High Cube Premium": 9,
      "20' One-Trip Standard": 10,
      "20' One-Trip High Cube": 11,
      "40' One-Trip Standard": 12,
      "40' One-Trip High Cube": 13,
      "20' One-Trip Standard Double Door": 14,
      "20' One-Trip High Cube Double Door": 15,
      "40' One-Trip Standard Double Door": 16,
      "40' One-Trip High Cube Double Door": 17,
      "20' One-Trip Standard Open Side": 18,
      "20' One-Trip High Cube Open Side": 19,
      "40' One-Trip Standard Open Side": 20,
      "40' One-Trip High Cube Open Side": 21,
      "40' One-Trip Standard Side Door": 22,
      "40' One-Trip High Cube Side Door": 23
    }

    if (orderedTitles[title] === undefined) {
      return 999
    } else {
      return orderedTitles[title]
    }
  }

  async getCustomerAddress(zip, account_country, toast) {
    const { data } = await this.googleMapsApi.geoNamesSearchTomTom(
      zip,
      account_country
    )
    if (
      data.value.results.filter((r) => r.matchConfidence.score >= 1).length == 0
    ) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: `No locations found for ${zip}`,
        life: 5000,
        group: "br"
      })
      return null
    }
    let place = data.value.results.filter(
      (r) => r.matchConfidence.score >= 1
    )[0]
    let county = data.value.results.filter(
      (r) => r.matchConfidence.score >= 1
    )[0]?.address.countrySubdivisionName
    console.log("Place", place)
    // This code will be used to fix the edge case where there is an And in the middle of the city
    // The reason these break the parseLocation is bc it will hit the first if conditional which checks
    // if there is an intersection in the address and will handle... but ours doesn't but it thinks it does
    // bc of the And in the middle. zip code 95975 is what broke this
    let city = ""
    if (place?.address.postalName != null) {
      city = place.address.postalName
    } else if (place?.address.localName != null) {
      city = place.address.localName
    } else if (place?.address.municipality != null) {
      city = place.address.municipality.split(",")[0]
    }
    let regex = /\b(?:and)\b/i
    let isCityWithStandAloneAnd = regex.test(city)
    let originalCity = ""
    let placeHolderCity = "Placeholder"
    if (isCityWithStandAloneAnd) {
      if (place.address.postalName != null) {
        originalCity = place.address.postalName
      } else if (place.address.localName != null) {
        originalCity = place.address.localName
      } else {
        originalCity = place.address.municipality
      }
      if (place.address.postalName != null) {
        place.address.postalName = placeHolderCity
      } else if (place.address.localName != null) {
        place.address.localName = placeHolderCity
      } else {
        place.address.municipality = placeHolderCity
      }
    }

    if (place?.address.postalName != null) {
      city = place.address.postalName
    } else if (place?.address.localName != null) {
      city = place.address.localName
    } else if (place?.address.municipality != null) {
      city = place.address.municipality.split(",")[0]
    }

    let partialAddress = `${city}, ${place?.address.countrySubdivisionName}, ${place?.address.postalcode}`
    let address
    let mappedAddress
    if (account_country != "Canada") {
      try {
        address = parseAddress.parseLocation(
          "519 Special Drive, " + partialAddress
        )
      } catch (e) {
        const r = await searchByLatLongCityState(zip, [zip])
        const customerBasicAddressDetails = r.origin_addresses[0]
        address = parseAddress.parseLocation(
          "519 Special Drive, " + customerBasicAddressDetails
        )
      }

      mappedAddress = {
        city: originalCity === "" ? address.city : originalCity,
        state: address.state,
        zip: zip,
        county: county,
        province: ""
      }
    } else {
      mappedAddress = {
        city: city,
        state: "",
        province: place?.address.countrySubdivisionName,
        zip: zip,
        county: ""
      }
    }
    return mappedAddress
  }

  generateQuote = async (
    state,
    mergedContainerLocationPrices,
    mergedAccessoryLocationPrices,
    resetQuote,
    toast,
    v$,
    accountMap,
    userStore,
    $isPublic
  ) => {
    let account_country = this.usersStore.cms.account_country

    let fixedLocationPrices

    const zipCode =
      this.usersStore.cms.account_country === "Canada"
        ? state.quote.searchZip
            .toUpperCase()
            .replace(" ", "")
            .replace(/^(.{3})/, "$1 ")
        : state.quote.searchZip

    if (this.usersStore.cms.feature_flags.use_maps_for_quotes == false) {
      fixedLocationPrices = await this.getFixedLocationPrices(toast, zipCode)
      if (fixedLocationPrices == null) {
        state.loading = false
        return
      }
    }

    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }

    const currentUrl = window.location.host
    const accountData = accountMap[currentUrl]

    const { data, error } = await this.quoteSearchesApi.createQuoteSearch({
      postal_code: zipCode,
      account_id: this.usersStore.cms?.id,
      user_id: userStore.currentUser?.id
    })

    state.loading = true

    if (accountData["account_id"] != userStore.cms?.id) {
      const prices = await this.pricingApi.getContainerPricingPublic(
        userStore.cms?.id
      )
      this.pricingStore.setContainerPrices(
        prices?.data?.value?.map((v) =>
          this.pricingService.dtoContainerPricing(v)
        )
      )

      const locations = await this.pricingApi.getLocationsPublic(
        userStore.cms?.id
      )
      this.pricingStore.setLocations(
        locations?.data?.value?.map((v) => this.pricingService.dtoLocation(v))
      )

      const taxes = await this.taxApi.getTaxesPublic(userStore.cms?.id)
      this.taxStore.setTaxes(taxes.data.value)
    }

    let distanceZips
    if (this.usersStore.cms.feature_flags.use_maps_for_quotes === false) {
      distanceZips = [
        {
          destination_city: fixedLocationPrices[0]?.location.city,
          destination_zip: fixedLocationPrices[0]?.location.zip,
          distance: 0,
          origin_zip: fixedLocationPrices[0]?.postal_code
        }
      ]
    } else {
      distanceZips = await lookupZip(
        zipCode,
        this.pricingStore.locations,
        account_country
      )
    }
    if (distanceZips.length === 0) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: `No locations found for this ${postalZipText.value} code`,
        life: 5000,
        group: "br"
      })
      return
    }

    let customerBasicAddress = await this.getCustomerAddress(
      zipCode,
      account_country,
      toast
    )
    if (customerBasicAddress == null) {
      state.loading = false
      return
    }
    console.log("customerBasicAddress", customerBasicAddress)
    this.customerOrderStore.setAddress(customerBasicAddress)

    let filteredContainerLocationPrices = $isPublic
      ? mergedContainerLocationPrices.value.filter(
          (c) => c.title === state.quote.selectedSize.title
        )
      : mergedContainerLocationPrices.value

    let filteredAccessoryLocationPrices = mergedAccessoryLocationPrices.value

    let quotePricingListPromises = cloneDeep(
      filteredContainerLocationPrices
    ).map(async (container) => {
      let fixedLocationPrice

      const pairedContainerDistance = distanceZips.find(
        (z) => z.destination_zip === container.zip
      )
      if (!pairedContainerDistance) {
        return
      }

      let shipping_revenue
      if (this.usersStore.cms.feature_flags.use_maps_for_quotes === false) {
        const result = this.selectFixedLocationShippingPrice(
          fixedLocationPrices,
          container,
          state.quote.buyType,
          state.quote.selectedSize
        )
        shipping_revenue = result[0]
        fixedLocationPrice = result[1]
        let skip = result[2]
        if (skip) {
          return
        }
      } else {
        shipping_revenue =
          Number(container.cost_per_mile) *
          Number(pairedContainerDistance.distance)
        if (shipping_revenue < Number(container.minimum_shipping_cost)) {
          shipping_revenue = container.minimum_shipping_cost
        }
      }

      if (state.quote.isPickupOrDelivery === "Pickup") {
        shipping_revenue = 0
      }

      const stateOrProvince =
        account_country == "Canada"
          ? customerBasicAddress.province
          : customerBasicAddress.state

      let tax = await this.taxService.calculateTax(
        container,
        state.quote.isPickupOrDelivery === "Delivery",
        this.taxStore.taxes,
        state.quote.buyType,
        this.usersStore.cms?.rent_options?.down_payment_strategy,
        shipping_revenue,
        stateOrProvince
      )

      let updatedContainer = Object.assign(container, {
        distance: pairedContainerDistance.distance,
        shipping_revenue,
        tax,
        type: "PURCHASE",
        total_revenue: shipping_revenue + container.price,
        destination_state: stateOrProvince
      })

      if (state.quote.buyType === "RENT_TO_OWN") {
        updatedContainer.type = "RENT_TO_OWN"
        return this.calculateRTOPrice(updatedContainer, tax)
      }
      if (state.quote.buyType === "RENT") {
        updatedContainer.type = "RENT"
        return this.calculateRentalPrice(updatedContainer)
      }

      if (userStore.cms.feature_flags.use_maps_for_quotes == false) {
        updatedContainer.city = fixedLocationPrice.location.city
        updatedContainer.location_id = fixedLocationPrice.location.id
        updatedContainer.location_name = fixedLocationPrice.location.city
      }
      return updatedContainer
    })
    console.log(filteredAccessoryLocationPrices)
    let quoteAccesoryPricingListPromises = cloneDeep(
      filteredAccessoryLocationPrices
    ).map(async (accessory) => {
      const pairedAccessoryDistance = distanceZips.find(
        (z) => z != undefined && z.destination_zip === accessory.zip
      )
      if (!pairedAccessoryDistance) {
        return
      }

      let shipping_revenue =
        Number(accessory.cost_per_mile) *
        Number(pairedAccessoryDistance.distance)
      if (shipping_revenue < Number(accessory.minimum_shipping_cost)) {
        shipping_revenue = accessory.minimum_shipping_cost
      }

      if (state.quote.isPickupOrDelivery === "Pickup") {
        shipping_revenue = 0
      }

      let taxableRevenue
      if (
        state.quote.buyType === "RENT_TO_OWN" ||
        state.quote.buyType === "PURCHASE"
      ) {
        taxableRevenue = accessory.sale_price + shipping_revenue
      }
      const stateOrProvince =
        account_country == "Canada"
          ? customerBasicAddress.province
          : customerBasicAddress.state
      console.log(stateOrProvince)
      let tax = await this.taxService.calculateTax(
        accessory,
        true,
        this.taxStore.taxes,
        "PURCHASE",
        taxableRevenue,
        stateOrProvince
      )

      let updatedAccessory = Object.assign(accessory, {
        distance: pairedAccessoryDistance.distance,
        shipping_revenue,
        tax,
        type: "PURCHASE",
        total_revenue: shipping_revenue + accessory.sale_price,
        destination_state: stateOrProvince
      })
      return updatedAccessory
    })

    let quotePricingList = await Promise.all(quotePricingListPromises)

    let quoteAccessoryPricingList = await Promise.all(
      quoteAccesoryPricingListPromises
    )
    // sort by title then sort by total revenue
    quotePricingList.sort((a, b) => {
      // sort by title first as that is a priority if not then just sort by total revenue
      if (
        this.orderedTitles.indexOf(a.title) <
        this.orderedTitles.indexOf(b.title)
      ) {
        return -1
      } else if (
        this.orderedTitles.indexOf(a.title) >
        this.orderedTitles.indexOf(b.title)
      ) {
        return 1
      }
      return a.total_revenue - b.total_revenue
    })
    quoteAccessoryPricingList.sort((a, b) => {
      // sort by title first as that is a priority if not then just sort by total revenue
      if (
        this.orderedTitles.indexOf(a.title) <
        this.orderedTitles.indexOf(b.title)
      ) {
        return -1
      } else if (
        this.orderedTitles.indexOf(a.title) >
        this.orderedTitles.indexOf(b.title)
      ) {
        return 1
      }
      return a.total_revenue - b.total_revenue
    })

    // find the first instance of each title in this list
    let uniqueTitles = Array.from(
      new Set(quotePricingList.map((m) => m?.title))
    )
    let uniqueQuotePricingList = uniqueTitles.map((t) => {
      return quotePricingList.find((p) => p?.title === t)
    })

    const groupedQuotesUnsortedByDistance = _groupBy(
      quotePricingList,
      "distance"
    )

    delete groupedQuotesUnsortedByDistance[undefined]
    const sortedDistanceKeys = Object.keys(
      groupedQuotesUnsortedByDistance
    ).sort((a, b) => Number(a) - Number(b))

    let mappedKeys = sortedDistanceKeys.map((k) => {
      return groupedQuotesUnsortedByDistance[k]
    })

    if (state.quote.isPickupOrDelivery === "Delivery") {
      if (this.usersStore.cms.feature_flags.use_maps_for_quotes == false) {
      } else {
        mappedKeys.unshift(uniqueQuotePricingList)
      }
    }

    if ($isPublic && state.quote.isPickupOrDelivery != "Pickup") {
      mappedKeys = mappedKeys.slice(0, 1)
      state.quotesList = mappedKeys.splice(0, 12)
    } else if ($isPublic && state.quote.isPickupOrDelivery == "Pickup") {
      state.quotesList = mappedKeys.splice(0, 4)
      state.quotesList.sort((a, b) => a[0].total_revenue - b[0].total_revenue)
    } else {
      state.quotesList = mappedKeys.splice(0, 12)
    }
    if (this.usersStore.cms.feature_flags.use_maps_for_quotes == false) {
      state.quotesList = [state.quotesList[0]]
    } else {
      for (var i = 0; i < state.quotesList.length; i++) {
        // state.quotesList[i] = state.quotesList[i].sort((a, b) => this.compute_priority(a.title) - this.compute_priority(b.title))
        state.quotesList[i] = state.quotesList[i].sort((a, b) => {
          const priorityDiff =
            this.compute_priority(a.title) - this.compute_priority(b.title)
          if (priorityDiff !== 0) {
            return priorityDiff // Sort by priority
          }
          return a.price - b.price // Sort by price if priority is the same
        })
      }
    }
    let account_id = $isPublic
      ? accountMap[window.location.host].account_id
      : userStore?.cms?.id
    await this.taxApi
      .hasAvalaraTaxIntegration(account_id)
      .then(async (response) => {
        if (!response.error.value && response.data.value == true) {
          //Avalara tax computation
          let tax_cities = {}
          let limit = 3
          for (var i = 0; i < 1; i++) {
            let quotes = state.quotesList[i]
            for (var j = 0; j < quotes.length; j++) {
              const el = quotes[j]
              if (el.tax != undefined && el.tax != 0) {
                break
              }
              if (limit >= 0 && !tax_cities.hasOwnProperty(el.location_name)) {
                tax_cities[el.location_name] = {
                  state: el.state
                }

                const { data, error } = await this.taxApi.calculateTaxAvalara(
                  zipCode,
                  el.state,
                  el.location_name,
                  account_id
                )

                if (!error.value || data.value == 1) {
                  limit -= 1
                  let tax_rate = data.value
                  tax_cities[el.location_name]["tax_rate"] = tax_rate
                } else {
                  console.log(
                    "Can't calculate tax for city " + el.location_name
                  )
                }
              }
            }
          }

          for (var i = 0; i < 3; i++) {
            let quotes = state.quotesList[i]

            if (quotes) {
              quotes.forEach((el) => {
                if (
                  tax_cities.hasOwnProperty(el.location_name) &&
                  tax_cities[el.location_name].tax_rate != undefined
                ) {
                  el.tax = el.price * tax_cities[el.location_name].tax_rate
                }
              })
            }
          }
        }
      })

    state.accessoriesList = quoteAccessoryPricingList
    state.quoteIsVisible = true

    resetQuote()
  }

  calculateRTOPrice = (container, tax) => {
    // tax = 0
    let mappedRates = this.usersStore.cms.rent_to_own_rates.map((r) => {
      let subTotal = container.price + container.shipping_revenue + tax
      //const monthly_owed = (subTotal * (1 + r.rate)) / r.months;

      const monthly_owed = subTotal / r.divide_total_price_by

      return {
        rent_period: r.months,
        monthly_owed: roundHalfUp(monthly_owed),
        total_rental_price: roundHalfUp(monthly_owed * r.months),
        tax: tax
      }
    })

    return Object.assign(container, {
      rent_to_own: mappedRates
    })
  }

  roundIt = (number, decimalPlaces = null) => {
    let returnNum = 0
    decimalPlaces == null
      ? (returnNum = Math.round(number))
      : (returnNum = Math.round(number * 10 ** decimalPlaces) / 100)
    return returnNum
  }

  calculateRentalPrice = (container) => {
    return Object.assign(container, {
      monthly_owed: roundHalfUp(container.monthly_price)
    })
  }

  getFixedLocationPrices = async (toast, postalCode) => {
    const { data } = await this.customerApi.getFixedLocationPricesByPostalCode(
      postalCode
    )
    console.log(data.value)
    if (data.value === undefined || data.value.length == 0) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: `We do not service this area.`,
        life: 5000,
        group: "br"
      })
      return null
    }

    return data.value
  }

  selectFixedLocationShippingPrice = (
    fixedLocationPrices,
    container,
    selectedBuyType,
    selectedSize
  ) => {
    let fixedLocationPrice,
      shipping_revenue,
      skip = false

    if (selectedSize != undefined && selectedSize.title.includes("20")) {
      fixedLocationPrice = fixedLocationPrices.find((el) => el.size === "20")
      if (container.container_size.includes("40")) {
        skip = true
      }
    } else if (selectedSize != undefined && selectedSize.title.includes("40")) {
      fixedLocationPrice = fixedLocationPrices.find((el) => el.size === "40")
      if (container.container_size.includes("20")) {
        skip = true
      }
    } else if (container.container_size.includes("20")) {
      fixedLocationPrice = fixedLocationPrices.find((el) => el.size === "20")
    } else if (container.container_size.includes("40")) {
      fixedLocationPrice = fixedLocationPrices.find((el) => el.size === "40")
    }

    if (selectedBuyType === "RENT") {
      shipping_revenue = fixedLocationPrice.rent_shipping_price
    }
    if (selectedBuyType === "PURCHASE") {
      shipping_revenue = fixedLocationPrice.sale_shipping_price
    }

    if (selectedBuyType === "RENT_TO_OWN") {
      // do nothing
    }

    return [shipping_revenue, fixedLocationPrice, skip]
  }

  createProductTitle = (container) => {
    let type = container.type?.standard ? " Standard" : ""
    type += container.type?.high_cube ? "High Cube" : ""
    type += container.type?.double_doors ? " Double Door" : ""

    let product_type =
      container?.product_type === "SHIPPING_CONTAINER" ||
      !container?.product_type
        ? ""
        : "Portable"
    return `${container.container_size}' ${container.condition} ${type} ${product_type}`.trim()
  }

  orderedTitles = [
    "20' Used Standard AS IS",
    "40' Used Standard AS IS",
    "40' Used High Cube AS IS",
    "20' Used Standard WWT/CW",
    "40' Used Standard WWT/CW",
    "40' Used High Cube WWT/CW",
    "20' Used Standard Premium",
    "40' Used Standard Premium",
    "40' Used High Cube Premium",
    "20' One-Trip Standard",
    "20' One-Trip High Cube",
    "40' One-Trip Standard",
    "40' One-Trip High Cube",
    "20' One-Trip Standard Double Door",
    "20' One-Trip High Cube Double Door",
    "40' One-Trip Standard Double Door",
    "40' One-Trip High Cube Double Door",
    "20' One-Trip Standard Open Side",
    "20' One-Trip High Cube Open Side",
    "40' One-Trip Standard Open Side",
    "40' One-Trip High Cube Open Side",
    "40' One-Trip Standard Side Door",
    "40' One-Trip High Cube Side Door"
  ]
}
