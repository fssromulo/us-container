import { useHttp, usePublicHttp, fetchFile } from "@/composables/useHttp"

export default class CustomerApi {
  constructor() {}

  async searchCustomers(params, emulatedUserId = null, skip = 0) {
    if (emulatedUserId) {
      return useHttp(
        `/search_orders?${params}&skip=${skip}&emulated_user_id=${emulatedUserId}`,
        "GET"
      )
    } else {
      return useHttp(`/search_orders?${params}&skip=${skip}`, "GET")
    }
  }

  async refreshCache() {
    return useHttp("/orders/refreshCache", "GET")
  }

  async deleteOrder(order_id) {
    return useHttp(`/order/${order_id}`, "DELETE")
  }

  async getCustomersByStatus(
    status,
    category,
    emulatedUserId = null,
    productType = "ALL",
    skip = 0,
    pull_all = false
  ) {
    if (emulatedUserId) {
      return useHttp(
        `/orders?status=${status}&order_type=${category}&skip=${skip}&emulated_user_id=${emulatedUserId}&product_type=${productType}&pull_all=${pull_all}`,
        "GET"
      )
    } else {
      return useHttp(
        `/orders?status=${status}&order_type=${category}&skip=${skip}&product_type=${productType}&pull_all=${pull_all}`,
        "GET"
      )
    }
  }

  async downloadRentReceipt(orderId, data) {
    return useHttp(`/generate_rent_receipt_pdf/${orderId}`, "POST", data)
  }

  async emailRentalReceipt(orderId, emailToAddress, data) {
    return useHttp(
      `/email_rental_receipt/${orderId}/${emailToAddress}`,
      "POST",
      data
    )
  }

  async downloadRentalInvoice(orderId, rentPeriodId) {
    return useHttp(
      `/generate_rental_invoice_pdf?order_id=${orderId}&rent_period_id=${rentPeriodId}`,
      "GET"
    )
  }

  async downloadInvoice(orderId, usePaidPdf = false) {
    if (usePaidPdf) {
      return useHttp(`/generate_order_pdf?order_id=${orderId}`, "GET")
    } else {
      return fetchFile(`/generate_order_pdf?order_id=${orderId}`, "GET")
    }
  }

  async removeCustomerProfile(id) {
    return useHttp(`/payment/remove_customer_profile`, "DELETE", {
      order_id: id
    })
  }

  async removeCustomerPaymentProfile(id, type) {
    return useHttp(`/payment/remove_customer_payment_profile`, "DELETE", {
      order_id: id,
      type: type
    })
  }

  async createQuickRent(data) {
    return useHttp("/quick_rent", "POST", data)
  }

  async createQuickSale(data) {
    return useHttp("/quick_sale", "POST", data)
  }

  async payRentalOrder(data) {
    return useHttp(`/payment/rental`, "POST", data)
  }

  async changeCreditCard(data) {
    return useHttp(`/payment/change_credit_card`, "POST", data)
  }

  async getCustomerProfile(customer_profile_id) {
    return useHttp(`/payment/customer_profile/${customer_profile_id}`, "GET")
  }

  async updateACH(data) {
    return useHttp(`/payment/update_ach`, "POST", data)
  }

  async addACH(data) {
    return useHttp(`/payment/add_ach`, "POST", data)
  }

  async addCardOnFile(data) {
    return useHttp(`/payment/add_card_on_file`, "POST", data)
  }

  async payLumpSumRentalOrder(data) {
    return useHttp(`/payment/rental/lump_sum`, "POST", data)
  }

  async payOtherRentalOrderCreditCard(data) {
    return useHttp(`/payment/rental/other/credit_card`, "POST", data)
  }

  async payOtherRentalOrdersCreditCard(data) {
    return useHttp(`/payment/rental/other_orders/credit_card`, "POST", data)
  }

  async payOtherOrdersRentalOrder(data) {
    return useHttp(`/payment/rental/other_orders`, "POST", data)
  }

  async payOtherRentalOrder(data) {
    return useHttp(`/payment/rental/other`, "POST", data)
  }

  async waiveAllFees(data) {
    return useHttp(`/payment/rental/waive_all_fees`, "POST", data)
  }

  async resendInvoice(id) {
    return useHttp(`/resend_order/${id}`, "GET")
  }
  async resendContactInvoice(contact_id, order_id) {
    return useHttp(`/resend_order/${contact_id}/${order_id}`, "GET")
  }
  async resendRentalPeriodInvoice(id, period_id) {
    return useHttp(`/resend_order/${id}/period/${period_id}`, "GET")
  }

  async sendeRentalContract(id) {
    return usePublicHttp(`/send_rental_contract/${id}`, "GET")
  }
  async getPublicDaysToDeliver(account_id, city) {
    return usePublicHttp(
      `/get_delivery_days/${account_id}?city=${encodeURIComponent(city)}`,
      "GET"
    )
  }

  async sendPaymentOnDeliveryContract(id) {
    return useHttp(`/contracts/send_payment_on_delivery_contract/${id}`, "GET")
  }

  async sendPaymentOnDeliveryContractFromPayment(id) {
    return usePublicHttp(
      `/contracts/send_payment_on_delivery_contract_from_payment/${id}`,
      "GET"
    )
  }

  async publicSignPodContract(id, app) {
    return usePublicHttp(
      `/contracts/sign_payment_on_delivery_contract_from_payment/${id}`,
      "POST",
      app
    )
  }

  async convertToPurchase(id) {
    return useHttp(`/convert_order_to_purchase/${id}`, "GET")
  }

  async createCustomerOrder(data) {
    return useHttp(`/customer`, "POST", data)
  }

  async createCustomerOrderPublic(data, accountId, code = null) {
    const path = code
      ? `/customer/${accountId}?user_id=${code}`
      : `/customer/${accountId}`
    return usePublicHttp(path, "POST", data)
  }

  async getOrderByDisplayId(id) {
    return useHttp(`/order_by_display_id/${id}`, "GET")
  }

  async sendAgentEmailRTO(id) {
    return useHttp(`/send_agent_status_email/${id}`, "GET")
  }

  async getOrderLineItemsHistory(id) {
    return useHttp(`/order_line_items_history/${id}`, "GET")
  }

  async payByCreditCard(data) {
    return usePublicHttp("/payment", "POST", data)
  }

  async getOrderByIdPublic(id) {
    return usePublicHttp(`/order/${id}`, "GET")
  }

  async getOrdersByIds(ids) {
    return useHttp(`/orders_by_ids?ids=${ids}`, "GET")
  }

  async getLineItem(account_id, id) {
    return usePublicHttp(`/line_item/${account_id}/${id}`, "GET")
  }

  async acceptQuote(id) {
    return usePublicHttp(`/accept_quote/${id}`, "PATCH")
  }

  async getOrderById(id) {
    return useHttp(`/order/${id}`, "GET")
  }

  async updateOrder(id, data) {
    return useHttp(`/order/${id}`, "PATCH", data)
  }

  async previewPayment(id, data) {
    return useHttp(`/order/${id}/preview`, "POST", data)
  }

  async saveNote(data) {
    return useHttp(`/notes`, "POST", data)
  }

  async updateNote(id, data) {
    return useHttp(`/note/${id}`, "PATCH", data)
  }

  async updateNoteIsPublic(id, data) {
    return useHttp(`/notes_is_public/${id}`, "PATCH", data)
  }

  async gtrack(user_id, order_id) {
    const data = {
      client_id: user_id,
      events: [
        {
          name: "paid_order",
          params: {
            order_id: order_id
          }
        }
      ]
    }
    return usePublicHttp(`/google_analytics`, "POST", data)
  }

  async applyDiscount(id, data) {
    return useHttp(`/order_discount/${id}`, "PATCH", data)
  }

  async updateCustomer(id, data) {
    return useHttp(`/customer/${id}`, "PATCH", data)
  }

  async updateCustomerProfile(id, data) {
    return useHttp(`/customer_profile/${id}`, "PATCH", data)
  }

  async updateAddress(addressId, orderId, data) {
    return useHttp(
      `/order_address/${addressId}/order/${orderId}`,
      "PATCH",
      data
    )
  }

  async createCustomerApplication(data) {
    return usePublicHttp(`/customer_application`, "POST", data)
  }

  async updateCreditApplication(applicationId, data) {
    return useHttp(`/customer_application/${applicationId}`, "PATCH", data)
  }

  // The following methods are used for the CRUD of Misc cost funcitonality that is added to the OrderDetail.vue
  async createMiscCost(data) {
    return useHttp("/misc_costs", "POST", data)
  }

  async getApplicationSchemasByName(name, orderId) {
    return useHttp(`/get_application_schemas_by_name/${name}/${orderId}`, "GET")
  }

  async updateMiscCost(data) {
    return useHttp("/misc_costs", "PATCH", data)
  }

  async deleteMiscCost(id) {
    return useHttp(`/misc_costs/${id}`, "DELETE", {})
  }
  // this method specifically gets all of the cost type options that will populate a dropdown in the edit section
  async getAllCostTypes() {
    return useHttp(`/cost_type`, "GET", {})
  }
  async deleteFee(id) {
    return useHttp(`/fee/${id}`, "DELETE", {})
  }
  async createFee(data) {
    return useHttp(`/fee`, "POST", data)
  }
  async removeRushFee(orderId) {
    return useHttp(`/fee_rush/${orderId}`, "DELETE")
  }
  async updateFee(data) {
    return useHttp(`/fee`, "PATCH", data)
  }
  async deleteRentPeriodFee(id) {
    return useHttp(`/rent_period_fee/${id}`, "DELETE", {})
  }
  async deleteRentPeriod(id) {
    return useHttp(`/rent_period/${id}`, "DELETE", {})
  }
  async createRentPeriodFee(data) {
    return useHttp(`/rent_period_fee`, "POST", data)
  }
  async updateRentPeriodFees(data) {
    return useHttp(`/rent_period_fee`, "PATCH", data)
  }
  async sendRentalStatement(orderId) {
    return useHttp(`/send/rental_statement_email/${orderId}`, "GET")
  }

  async generateRentalStatementWeb(orderId, data) {
    return useHttp(
      `/generate_client_rental_statement_web/${orderId}`,
      "POST",
      data
    )
  }

  async generateRentalStatemenPdf(orderId) {
    return useHttp(`/generate_rental_statement_pdf?order_id=${orderId}`, "GET")
  }
  async updateRentPeriodInfo(data) {
    return useHttp(`/rent_period_info`, "POST", data)
  }
  async updateRentPeriodPrice(order_id, price) {
    const data = {
      order_id: order_id,
      price: price
    }
    return useHttp(`/rent_period_price`, "PUT", data)
  }
  async addRentPeriods(data) {
    return useHttp(`/generate_new_periods`, "PUT", data)
  }
  async updateRentPeriodDueDate(updated_period, subsequent_period_ids) {
    const data = {
      updated_period: updated_period,
      subsequent_period_ids: subsequent_period_ids
    }
    return useHttp(`/rent_period_due_date`, "PATCH", data)
  }

  async addTransactionType(data) {
    return useHttp("/transaction_type", "POST", data)
  }

  async getOrderByRentPeriodId(id) {
    return useHttp(`/get_order_by_rent_period_id/${id}`)
  }

  async getGroupedTransactions(id) {
    return useHttp(`/transaction_types_grouped/${id}`)
  }

  async duplicateOrder(id) {
    return useHttp(`/duplicate_order/${id}`)
  }

  async editTransactionType(transactionTypeId, data) {
    return useHttp(`/transaction_type/${transactionTypeId}`, "PATCH", data)
  }
  async customerSearch(params) {
    return useHttp(`/search_customers?${params}`, "GET")
  }
  async singleCustomerSearch(params) {
    return useHttp(`/search_single_customers?${params}`, "GET")
  }

  async singleCustomer(id) {
    return useHttp(`/single_customer/${id}`, "GET")
  }

  async customerSearchSingleCustomerId(single_customer_id) {
    return useHttp(`/single_customer_id_orders/${single_customer_id}`, "GET")
  }

  async addCustomerContact(data) {
    return useHttp(`/single_customer_contacts`, "POST", data)
  }
  async editCustomerContact(data) {
    return useHttp(`/single_customer_contacts`, "PATCH", data)
  }

  async deleteCustomerContact(customer_id, address_id) {
    return useHttp(
      `/single_customer_contacts/${customer_id}/${address_id}`,
      "DELETE"
    )
  }

  async getCustomerContact(customer_id) {
    return useHttp(`/single_customer_contacts/${customer_id}`, "GET")
  }

  async unlink_single_customer(order_id) {
    return useHttp(`/unlink_single_customer/${order_id}`, "GET")
  }

  async getChatLog(phone) {
    return useHttp(`/chat_log/${phone}`, "GET")
  }

  async mergeCustomers(data) {
    return useHttp(`/merge_customers`, "POST", data)
  }

  async updateCustomerContacts(id, data) {
    return useHttp(`/customer_contacts/${id}`, "PATCH", data)
  }

  async updateCustomerAddress(id, data) {
    return useHttp(`/customer_address/${id}`, "PATCH", data)
  }

  async retrieveTransactionTypes(data) {
    if (data.orderId) {
      return useHttp("/get_order_transaction_types/" + data.orderId, "GET")
    } else if (data.rentPeriodId) {
      return useHttp(
        "/get_period_transaction_types/" + data.rentPeriodId,
        "GET"
      )
    }
  }

  async addFeeType(data) {
    return useHttp("/fee_type", "POST", data)
  }

  async updateFeeType(id, data) {
    return useHttp("/fee_type/" + id, "PATCH", data)
  }

  async fetchFeeTypes() {
    return useHttp("/fee_type", "GET")
  }

  async getVendorTypes() {
    return useHttp("/vendor_type", "GET")
  }
  async relatedContainers(releaseNumber) {
    return useHttp(`/related_containers?release_number=${releaseNumber}`, "GET")
  }

  async getCountries() {
    return useHttp("/countries", "GET")
  }

  async addCountry(data) {
    return useHttp("/country", "POST", data)
  }

  async sendPaymentOnDeliveryContractRedirect(order_id, account_id) {
    return useHttp(
      `/contracts/send_payment_on_delivery_contract_real/${order_id}/${account_id}`,
      "GET"
    )
  }

  async removeTransaction(transaction_id) {
    return useHttp(`/transaction_type/${transaction_id}`, "DELETE")
  }
  async initStripe(data = {}) {
    return usePublicHttp(`/init_stripe_payment`, "POST", data)
  }

  async checkTransactionStatus(data) {
    return usePublicHttp(
      `/stripe_transaction_status/${data.orderToken}/${data.clientSecret}/${data.accountId}`,
      "GET"
    )
  }

  async getRentOnDueDate(data) {
    return useHttp(`/get_rent_on_due_date`, "POST", data)
  }
  async driverPaymentNotification(data) {
    return useHttp(`/notify_payment`, "POST", data)
  }

  async getFixedLocationPricesByPostalCode(postal_code) {
    return useHttp(`/fixed_location_prices/${postal_code}`)
  }

  async calculate_remaining_balance(data, order_id) {
    return useHttp(`/calculate_remaining_balance/${order_id}`, "POST", data)
  }

  async calculate_remaining_balance(data, order_id) {
    return useHttp(`/calculate_remaining_balance/${order_id}`, "POST", data)
  }

  async transactions_rent_periods(data) {
    return useHttp(`transactions_rent_periods`, "POST", data)
  }

  async generate_web_rental_order_table_data(order_id, rent_period_id) {
    return useHttp(
      `/generate_web_rental_order_table_data/${order_id}/${rent_period_id}`
    )
  }

  async get_receipt_items_report(filters) {
    return useHttp(`get_receipt_items_report`, "POST", filters)
  }

  async abrevTitle(data) {
    return useHttp(`abrev_title`, "POST", data)
  }

  async get_all_container_attributes() {
    return useHttp(`get_all_container_attributes`)
  }

  async get_tax_rate(order_id) {
    return useHttp(`/get_tax_rate/${order_id}`)
  }

  async get_exported_orders(
    status,
    order_type,
    emulated_user_id,
    displayOrderIds
  ) {
    return useHttp(
      `/exported_orders?status=${status}&order_type=${order_type}&emulated_user_id=${emulated_user_id}&displayOrderIds=${displayOrderIds}`,
      "GET"
    )
  }

  async update_rent_period_dates(request, rent_period_id) {
    return useHttp(
      `/update_rent_period_dates/${rent_period_id}`,
      "POST",
      request
    )
  }

  async is_pay_on_delivery(data) {
    return useHttp(`/is_pay_on_delivery`, "POST", data)
  }

  async printRentalStatementMultipleOrders(single_customer_id, request) {
    return useHttp(
      `/print_rental_statement_multiple_orders/${single_customer_id}`,
      "POST",
      request
    )
  }
}
