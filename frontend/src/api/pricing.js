import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class PricingApi {
  constructor() {}
  // Locations
  async getLocations() {
    return useHttp(`/locations`, "GET")
  }

  async getLocationsPublic(accountId) {
    return usePublicHttp(`/locations/${accountId}`, "GET")
  }

  async getLocationById(id) {
    return useHttp(`/location/${id}`, "GET")
  }

  async createLocation(data) {
    return useHttp(`/location`, "POST", data)
  }

  async updateLocation(id, data) {
    return useHttp(`/location/${id}`, "PATCH", data)
  }

  // Container Pricing
  async getContainerPricingPublic(accountId) {
    return usePublicHttp(`/prices/${accountId}`, "GET")
  }

  async getContainerPricing() {
    return useHttp(`/prices`, "GET")
  }

  async getContainerPriceById(id) {
    return useHttp(`/price/${id}`, "GET")
  }

  async deleteContainerPricing(id) {
    return useHttp(`/price/${id}`, "DELETE")
  }

  async setRentalPrice(data) {
    return useHttp(`/set_rental_price`, "POST", data)
  }

  async updateContainerPricing(id, data) {
    return useHttp(`/price/${id}`, "PATCH", data)
  }

  async createContainerPricing(data) {
    return useHttp(`/price`, "POST", data)
  }

  // Accessory Pricing
  async getProductPublic(accountId) {
    return usePublicHttp(`/products/${accountId}`, "GET")
  }

  async getProduct() {
    return useHttp(`/products`, "GET")
  }

  async getProductById(id) {
    return useHttp(`/product/${id}`, "GET")
  }

  async deleteProduct(id) {
    return useHttp(`/product/${id}`, "DELETE")
  }

  async updateProduct(id, data) {
    return useHttp(`/product/${id}`, "PATCH", data)
  }

  async createProduct(data) {
    return useHttp(`/product`, "POST", data)
  }

  // Product Categories
  async getProductCategoryPublic(accountId) {
    return usePublicHttp(`/product_categories/${accountId}`, "GET")
  }

  async getProductCategory() {
    return useHttp(`/product_categories`, "GET")
  }
  async updateProductCategory(id, data) {
    return useHttp(`/product_category/${id}`, "PATCH", data)
  }
  async deleteProductCategory(id) {
    return useHttp(`/product_category/${id}`, "DELETE")
  }

  async getProductCategory() {
    return useHttp(`/product_categories`, "GET")
  }
  async updateProductCategory(id, data) {
    return useHttp(`/product_category/${id}`, "PATCH", data)
  }
  async deleteProductCategory(id) {
    return useHttp(`/product_category/${id}`, "DELETE")
  }

  async createProductCategory(data) {
    return useHttp(`/product_category`, "POST", data)
  }
  async getProductCategoryById(id) {
    return useHttp(`/product_category/${id}`, "GET")
  }

  async setGlobalPOD(data) {
    return useHttp(`/set_global_pod`, "POST", data)
  }
}
