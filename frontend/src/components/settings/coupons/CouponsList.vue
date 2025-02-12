<template>
  <div class="container">
    <ConfirmPopup></ConfirmPopup>

    <h3 class="text-center">Coupon List</h3>
    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <DataTable
          :value="
            couponList.map((coupon) => {
              return {
                code: coupon.code,
                id: coupon.id,
                name: coupon.name,
                minimum_discount_threshold: coupon.minimum_discount_threshold,
                amount: coupon.amount,
                start_date: new Date(coupon.start_date).toLocaleDateString(
                  'en-US'
                ),
                end_date: new Date(coupon.end_date).toLocaleDateString('en-US'),
                city: coupon.city,
                size: coupon.size,
                is_permanent: coupon.is_permanent,
                type: coupon.type,
                role: coupon.role,
                rules: coupon.rules,
                is_stackable: coupon.is_stackable,
                category: coupon.category,
                attributes: coupon.attributes,
                percentage: coupon.percentage
              }
            })
          "
          responsiveLayout="scroll"
        >
          <Column field="code" header="Code"></Column>
          <Column field="name" header="Name"></Column>
          <Column
            field="minimum_discount_threshold"
            header="Minimum Threshold"
          ></Column>
          <Column field="amount" header="Discounted Value"></Column>
          <Column field="percentage" header="Discounted Percentage"></Column>
          <Column field="start_date" header="Start Date"></Column>
          <Column field="end_date" header="End Date"></Column>
          <Column field="id" header="Edit" style="width: 160px">
            <template #body="slotProps">
              <Button
                class="p-button-rounded"
                @click="openCoupon(slotProps.data)"
                >Edit</Button
              >
            </template>
          </Column>
          <Column field="id" header="Delete" style="width: 160px">
            <template #body="slotProps">
              <Button
                class="p-button-rounded"
                :disabled="state.isDeleting"
                @click="deleteCoupon(slotProps.data)"
                >Delete</Button
              >
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <Dialog
      v-model:visible="state.couponDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Edit Coupon"
      :modal="true"
      class="p-fluid"
    >
      <EditCoupon
        @hide="state.couponDialog = false"
        @couponEdited="state.couponDialog = false"
        :couponProp="state.selectedCoupon"
      />
    </Dialog>
    <Dialog
      v-model:visible="state.deleteCouponDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Discounted Orders"
      :modal="true"
      class="p-fluid"
    >
      <DeleteCoupon
        @hide="state.deleteCouponDialog = false"
        @couponRemoved="state.deleteCouponDialog = false"
        :linkedOrders="state.loadedCouponOrders"
        :couponId="state.selectedCoupon.id"
        @reloadOrders="reloadCoupons"
        @completeDelete="directlyDeleteCoupon"
      />
    </Dialog>
  </div>
</template>
<script setup>
  import { useCoupons } from "@/store/modules/coupons"
  import EditCoupon from "./EditCoupon.vue"
  import DeleteCoupon from "./DeleteCoupon.vue"

  import { reactive, computed } from "vue"
  import { useConfirm } from "primevue/useconfirm"
  import CouponApi from "@/api/coupon"
  import { useToast } from "primevue/usetoast"

  const confirm = useConfirm()
  const couponApi = new CouponApi()
  const toast = useToast()
  const state = reactive({
    couponDialog: false,
    selectedCoupon: {},
    isDeleting: false,
    deleteCouponDialog: false,
    loadedCouponOrders: []
  })
  const couponStore = useCoupons()
  const couponList = computed(() => {
    return couponStore.coupons || []
  })

  const openCoupon = async (coupon) => {
    state.couponDialog = true
    state.selectedCoupon = coupon
    couponStore.setSelectedCoupon(coupon)
  }

  const directlyDeleteCoupon = async (couponId) => {
    let { data, error } = await couponApi.deleteCoupon(couponId)
    if (data.value) {
      await reloadCoupons()
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
  }

  const reloadCoupons = async () => {
    const res = await couponApi.getAllCoupons()
    couponStore.setCoupons(res.data.value)
  }
  const reloadOrders = async (couponId) => {
    let { data } = await couponApi.getACouponOrders(couponId)
    if (data.value) {
      state.loadedCouponOrders = data.value
    }
    return data
  }

  const deleteCoupon = async (coupon) => {
    confirm.require({
      target: event.currentTarget,
      message: "Do you want to remove this coupon code ?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        state.isDeleting = true
        state.selectedCoupon = coupon
        let data = await reloadOrders(coupon.id)

        if (data.value) {
          if (data.value.length == 0) {
            await directlyDeleteCoupon(coupon.id)
            state.deleteCouponDialog = false
          } else {
            state.deleteCouponDialog = true
          }
        }

        state.isDeleting = false
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Rejected",
          detail: "Coupon code removal rejected",
          life: 2000
        })
      }
    })
  }
</script>
