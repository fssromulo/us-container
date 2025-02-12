import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class CouponApi {
  async getAllCouponsInsecure(account_id) {
    return usePublicHttp(`/coupons?account_id=${account_id}`, "GET")
  }

  async getAllCoupons() {
    return useHttp(`/coupons`, "GET")
  }

  async getACouponWithId(couponId) {
    return useHttp(`/coupon/${couponId}`, "GET")
  }
  async getACouponWithCode(couponCode) {
    return useHttp(`/coupon/code/${couponCode}`, "GET")
  }
  async getAPublicCouponWithCode(couponCode, account_id) {
    return usePublicHttp(`/coupon/code/${account_id}/${couponCode}`, "GET")
  }

  async deleteCoupon(couponId) {
    return useHttp(`/coupon/${couponId}`, "DELETE")
  }
  async updateCoupon(couponId, data) {
    return useHttp(`/coupon/${couponId}`, "PATCH", data)
  }
  async createCoupon(data) {
    return useHttp(`/coupon`, "POST", data)
  }
  async applyCoupon(data) {
    return useHttp(`/coupon/apply`, "POST", data)
  }

  async removeCoupon(data) {
    return useHttp(`/coupon/remove`, "POST", data)
  }
  async removePublicCoupon(data) {
    return usePublicHttp(`/coupon/remove`, "POST", data)
  }

  async getACouponOrders(couponId) {
    return useHttp(`/coupon/orders/${couponId}`, "GET")
  }
  async getAnOrderCoupons(orderId) {
    return useHttp(`/coupon/codes/${orderId}`, "GET")
  }
  async unsetMultipleCouponCode(couponId, data) {
    return useHttp(`/coupon/unset-all/${couponId}`, "DELETE", data)
  }
}
