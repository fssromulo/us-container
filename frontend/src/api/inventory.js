import { useHttp } from "@/composables/useHttp"

export default class InventoryApi {
  constructor() {}
  async deleteInventory(id) {
    return useHttp(`/inventory/${id}`, "DELETE")
  }

  async getOrdersWithInventory(status, selectedCategoryCode, skip = 0) {
    return useHttp(
      `/get_orders_inventory/${status}/${selectedCategoryCode}`,
      "GET"
    )
  }

  async GetOrderForContainer(container_id) {
    return useHttp(
      `/get_order_for_container?container_id=${container_id}`,
      "GET"
    )
  }

  async searchInventory(searchQuery, skip = 0) {
    return useHttp(`/search_inventory?${searchQuery}`, "GET")
  }
  async getOrdersByInventoryId(inventory_id) {
    return useHttp(`/orders_by_inventory_id/${inventory_id}`, "GET")
  }

  async getInventoryByStatus(status, category, skip = 0, limit = 0) {
    return useHttp(
      `/inventory_by_status?status=${status}&order_type=${category}&skip=${skip}&limit=300`,
      "GET"
    )
  }

  async getInventoryByDepot(depot_id) {
    return useHttp(`/inventory_by_depot/${depot_id}`, "GET")
  }

  async getInventory(skip = 0) {
    return useHttp(`/inventory?skip=${skip}`, "GET")
  }

  async getInventoryById(id) {
    return useHttp(`/inventory/${id}`, "GET")
  }

  async getInventoryByIdPrefix(id) {
    return useHttp(`/inventory/prefix/${id}`, "GET")
  }

  async createInventory(data) {
    return useHttp(`/inventory`, "POST", data)
  }

  async updateOtherInventory(id, data) {
    return useHttp(`/other_inventory/${id}`, "PATCH", data)
  }
  async detachOtherInventory(id) {
    return useHttp(`/other_inventory/${id}`, "DELETE")
  }

  async createOtherInventory(data) {
    return useHttp(`/other_inventory`, "POST", data)
  }

  async createInventoryAddress(data) {
    return useHttp(`/inventory_address`, "POST", data)
  }

  async updateInventoryAddress(id, data) {
    return useHttp(`/inventory_address/${id}`, "PATCH", data)
  }

  async updateInventory(id, data) {
    return useHttp(`/inventory/${id}`, "PATCH", data)
  }
}
