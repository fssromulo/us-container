<template>
  <div class="container">
    <DataTable
      v-model:selection="state.selectedOrders"
      :value="
        linkedOrders.map((order) => {
          return {
            id: order.id,
            display_order_id: order.display_order_id,
            created_at: new Date(order.start_date).toLocaleDateString('en-US'),
            full_name: order.customer.full_name,
            phone: order.customer.phone
          }
        })
      "
      dataKey="id"
      tableStyle="min-width: 50rem"
    >
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      <Column field="display_order_id" header="Order Id"></Column>
      <Column field="created_at" header="Created"></Column>
      <Column field="full_name" header="Name"></Column>
      <Column field="phone" header="Phone"></Column>
    </DataTable>
    <div class="row mt-8">
      <div class="field mb-6 col-sm-6 col-md-3 mt-8">
        <p>
          You can delete this Order after the last order's is discount is
          removed
        </p>
      </div>
      <div class="field mb-6 col-sm-6 col-md-3 mt-8">
        <Button
          class="p-button-rounded p-button-successsave"
          :label="deleteText"
          :loading="state.loading"
          :disabled="state.loading || state.selectedOrders.length == 0"
          @click="removeOrders"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
  import { reactive, computed, defineEmits } from "vue"

  import { useToast } from "primevue/usetoast"
  import { useCoupons } from "@/store/modules/coupons"
  import CouponApi from "@/api/coupon"

  const toast = useToast()
  const couponStore = useCoupons()
  const couponApi = new CouponApi()
  const emit = defineEmits(["couponRemoved", "reloadOrders", "completeDelete"])
  const { linkedOrders, couponId } = defineProps({
    linkedOrders: {
      type: Array,
      default: () => []
    },
    couponId: {
      type: String
    }
  })

  const deleteText = computed(() => {
    return state.selectedOrders == null || state.selectedOrders.length == 0
      ? "Select orders to start"
      : "Remove coupon from orders"
  })
  const removeOrders = async () => {
    await couponApi.unsetMultipleCouponCode(couponId, {
      ids: state.selectedOrders.map((coupon) => coupon.id)
    })
    emit("couponRemoved")
    if (state.selectedOrders.length == linkedOrders.length) {
      // directly delete
      emit("directlyDeleteCoupon", couponId)
    } else {
      emit("reloadOrders")
    }
  }
  const state = reactive({
    loading: false,
    selectedOrders: []
  })
</script>
