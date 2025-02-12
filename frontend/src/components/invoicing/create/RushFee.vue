<template>
  <div class="ml-4 items-center">
    <InputNumber
      mode="currency"
      currency="USD"
      v-model="state.fee_amount"
      disabled
      style="width: 210px"
      id="tax"
      type="text"
      class="flex-1"
    />
    <Button
      type="button"
      label="Add rush fee"
      class="m-1 p-button-success"
      @click="handleAddItemSaveClickFunc"
      :loading="state.isLoading"
      style="width: 200px"
    ></Button>
    <div style="margin-top: 50px" v-html="props.rush_message"></div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, inject, computed } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import CouponApi from "@/api/coupon"
  import { useToast } from "primevue/usetoast"
  import CustomerApi from "@/api/customers"
  import OrderAlterations from "../OrderAlterations.vue"

  const customerApi = new CustomerApi()

  const toast = useToast()

  const couponApi = new CouponApi()

  const usersStore = useUsers()
  const customerOrderStore = useCustomerOrder()

  const $isObjectPopulated = inject("$isObjectPopulated")
  const $ability = inject("$ability")

  const state = reactive({
    internal_coupons: [],
    internal_coupons_applied: [],
    isLoading: false,
    lastActiveToggle: null,
    fee_amount: 150
  })

  const props = defineProps({
    order_id: {
      type: String,
      default: ""
    },
    rush_fee: {
      type: Number,
      default: 150
    },
    rush_message: {
      type: String,
      default: ""
    },
    resetFunc: {
      type: Function,
      default: () => {}
    }
  })

  const emit = defineEmits(["updatedAttributes"])

  onMounted(async () => {
    state.fee_amount = props.rush_fee
  })

  const rushFeeMultiplier = computed(() => {
    let numberOf20Ft = customerOrderStore.order.line_items.filter(
      (e) => e.container_size === "20"
    ).length
    let otherFtContainers =
      customerOrderStore.order.line_items.length - numberOf20Ft
    if (numberOf20Ft > 0) {
      numberOf20Ft = Math.ceil(numberOf20Ft / 2)
    }
    return otherFtContainers + numberOf20Ft
  })

  const handleAddItemSaveClickFunc = async () => {
    state.isLoading = true

    const feeTypes = await customerApi.fetchFeeTypes()

    let foundItem = feeTypes.data.value.find((item) => item.name === "RUSH")

    const feeType = [
      {
        fee_type: "RUSH",
        type_id: foundItem.id,
        fee_amount: (state.fee_amount || 0) * rushFeeMultiplier.value,
        order_id: props.order_id,
        due_at: null
      }
    ]

    customerApi
      .createFee(feeType)
      .then(async (response) => {
        if (response.error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: response.error.value.response.data.detail,
            life: 3000,
            group: "br"
          })
          state.isLoading = false
          return
        }

        toast.add({
          severity: "success",
          summary: "Success",
          detail: `Successfully added Rush Fee`,
          life: 3000,
          group: "br"
        })
        await props.resetFunc()
      })
      .finally(() => {
        state.isLoading = false
        close()
      })
  }
</script>
