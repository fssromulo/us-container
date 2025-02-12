<template>
  <div class="container">
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"
          >Enter Coupon Code</label
        >
        <InputText
          class="w-full"
          v-model="state.code"
          placeholder="Coupon Code"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-6 field col-sm-6 col-md-3">
        <Button
          class="p-button-rounded p-button-successsave"
          label="Apply Coupon"
          :loading="loading"
          :disabled="!isValidateForm || loading"
          @click="validateCoupon"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, ref, computed, inject, defineEmits } from "vue"

  import { useToast } from "primevue/usetoast"
  import CouponApi from "@/api/coupon"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const $isPublic = inject("$isPublic")

  const emit = defineEmits(["couponApplied"])

  const $route = inject("$route")
  const customerApi = new CustomerApi()
  const customerOrderStore = useCustomerOrder()

  const toast = useToast()
  const isValidateForm = computed(() => {
    if (state.code.length < 2) return false
    return true
  })

  const hasCoupon = computed(() => {
    return customerOrderStore.publicOrder.coupon_code_order.length > 0
  })
  const couponIsUsed = (couponCode) => {
    return customerOrderStore.publicOrder.coupon_code_order.some(
      (coupon) => coupon.coupon.code == couponCode
    )
  }

  const couponApi = new CouponApi()

  const validateCoupon = async () => {
    const dataToSave = { ...state }
    if (!couponIsUsed(dataToSave.code)) {
      loading.value = true
      // first validate coupon
      let { data, error } = await couponApi.getAPublicCouponWithCode(
        dataToSave.code,
        customerOrderStore.publicOrder.account_id
      )
      if (
        data.value &&
        (!data.value.is_expired || data.value.isPermanent) &&
        (data.value.type == "external" || data.value.type == "both")
      ) {
        let can_apply_coupon = false
        customerOrderStore.publicOrder.line_items.forEach((item) => {
          if (
            (Object.keys(data.value.size).length === 0 ||
              data.value.size.hasOwnProperty(item.title)) &&
            (Object.keys(data.value.city).length == 0 ||
              data.value.city.hasOwnProperty(item.product_city))
          ) {
            can_apply_coupon = true
          }
        })

        if (can_apply_coupon) {
          await applyCoupon(data.value.id)
          state.code = ""
        } else {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Cannot apply coupon.",
            group: "br",
            life: 5000
          })
          loading.value = false
        }
      } else {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Coupon code is not valid",
          group: "br",
          life: 5000
        })
        loading.value = false
      }

      if (data.value.is_expired) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Coupon code is expired",
          group: "br",
          life: 5000
        })
        loading.value = false
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Coupon code is not valid",
          group: "br",
          life: 5000
        })
        loading.value = false
      }
    } else {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "You have already used the coupon code",
        group: "br",
        life: 5000
      })
    }
  }
  const applyCoupon = async (couponId) => {
    let { data, error } = await couponApi.applyCoupon({
      coupon_id: couponId,
      order_id: $route.currentRoute.value.params.orderId
    })
    await syncOrderData()
    if (data.value) {
      emit("couponApplied")
      toast.add({
        severity: "success",
        summary: "Coupon applied",
        detail: "Successfully applied coupon",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail:
          "Make sure the code is valid and you havent applied a coupon on this order",
        group: "br",
        life: 5000
      })
    }
    loading.value = false
  }
  const syncOrderData = async () => {
    const { data } = await customerApi.getOrderByIdPublic(
      $route.currentRoute.value.params.orderId
    )
    customerOrderStore.setPublicOrder(data.value)
  }

  const state = reactive({
    code: ""
  })
  const loading = ref(false)
</script>
<style></style>
