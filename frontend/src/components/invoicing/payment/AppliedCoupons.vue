<template>
  <section class="flex w-full flex-col" v-if="props.appliedCoupons.length > 0">
    <ConfirmPopup></ConfirmPopup>
    <div class="mt-2 mb-2">
      <div class="mt-2 col-span-12 md:col-span-3">
        <div
          v-if="
            props.appliedCoupons.some(
              (obj) =>
                obj.coupon.type === 'external' || obj.coupon.type === 'both'
            )
          "
          class="mb-4 text-xl font-medium text-500 dark:text-300"
          >Applied Coupon(s)</div
        >
      </div>
      <div class="grid grid-cols-12 gap-4 justify-center">
        <div
          class="col-span-12"
          v-for="(currentCouponOrder, index) in props.appliedCoupons"
          :key="index"
        >
          <Button
            v-if="currentCouponOrder.coupon.type !== 'internal'"
            class="mt-2 mr-1 p-button-rounded"
            :disabled="state.isDeleting || orderIsPaid"
            :loading="state.isDeleting"
            @click="removeCoupon(currentCouponOrder)"
          >
            {{ currentCouponOrder.coupon.name }} @
            {{
              currentCouponOrder.coupon.percentage
                ? currentCouponOrder.coupon.percentage + "%"
                : $fc(currentCouponOrder.coupon.amount)
            }},
            <span v-if="!currentCouponOrder.coupon.is_permanent"
              >Coupon will expire on
              {{
                new Date(currentCouponOrder.coupon.end_date).toLocaleDateString(
                  "en-US"
                )
              }}</span
            >
            <span v-else> It's permanent. </span>
            <i class="ml-2 pi pi-times"></i
          ></Button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
  import { computed, inject, reactive } from "vue"
  import { useConfirm } from "primevue/useconfirm"
  import { useToast } from "primevue/usetoast"
  import CouponApi from "@/api/coupon"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const $isPublic = inject("$isPublic")

  const toast = useToast()
  const couponApi = new CouponApi()
  const $route = inject("$route")
  const customerApi = new CustomerApi()
  const customerOrderStore = useCustomerOrder()

  const $fc = inject("$formatCurrency")
  const confirm = useConfirm()

  const orderIsPaid = computed(() => {
    return customerOrderStore.publicOrder.status === "Paid" ? true : false
  })
  const removeCoupon = (dataToSave) => {
    confirm.require({
      target: event.currentTarget,
      message: "Do you want to remove this coupon ?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        state.isDeleting = true
        let { data, error } = await couponApi.removePublicCoupon({
          coupon_id: dataToSave.coupon.id,
          order_id: customerOrderStore.publicOrder.id
        })
        if (data.value) {
          await syncOrderData()
          toast.add({
            severity: "success",
            summary: "Coupon removed",
            detail: "Successfully removed coupon",
            group: "br",
            life: 5000
          })
        }

        if (error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Error removing coupon code",
            group: "br",
            life: 2000
          })
        }
        state.isDeleting = false
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Rejected",
          detail: "Coupon removal rejected",
          life: 2000
        })
      }
    })
  }
  const syncOrderData = async () => {
    const { data } = await customerApi.getOrderByIdPublic(
      $route.currentRoute.value.params.orderId
    )
    customerOrderStore.setPublicOrder(data.value)
  }
  const props = defineProps({
    appliedCoupons: {
      type: Object,
      default: () => ({})
    },
    verticalTable: {
      type: Boolean,
      default: false
    }
  })
  const state = reactive({
    isDeleting: false
  })
</script>
