import { useHttp } from "@/composables/useHttp"

export default class NotificationsApi {
  async sendPaidEmail(order_id) {
    return useHttp(`/send/paid_email/${order_id}`, "POST")
  }

  async sendTimeFrameEmail(line_item, order_id, data) {
    return useHttp(
      `/send/time_frame_email/${line_item}/${order_id}`,
      "POST",
      data
    )
  }

  async sendPotentialDeliveryEmail(line_item, order_id, data) {
    return useHttp(
      `/send/potential_delivery_email/${line_item}/${order_id}`,
      "POST",
      data
    )
  }

  async sendConfirmationDeliveryEmail(line_item, order_id, data) {
    return useHttp(
      `/send/confirmation_date_email/${line_item}/${order_id}`,
      "POST",
      data
    )
  }

  async sendEmailTrackingNumbers(order_id) {
    return useHttp(`/send/tracking_numbers_email/${order_id}`, "POST")
  }
}
