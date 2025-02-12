/* eslint-disable no-console */
import { defineStore } from "pinia"

export const useCoupons = defineStore("coupons", {
  state: () => {
    return {
      coupons: [],
      selectedCoupon: {}
    }
  },
  getters: {},
  actions: {
    setCoupons(coupons) {
      this.coupons = coupons
    },
    setSelectedCoupon(coupon) {
      this.selectedCoupon = coupon
    }
  }
})
