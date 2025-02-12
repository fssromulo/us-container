<template>
  <div class="items-center ml-4">
    <div v-if="state.loading" class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <table
      v-if="!state.loading"
      v-for="(item, index) in state.internal_coupons"
      :key="index"
    >
      <tbody>
        <tr>
          <td>
            <ToggleButton
              v-model="state.internal_coupons_applied[index]"
              :onLabel="item.name + ' Discount'"
              :offLabel="item.name + ' Discount'"
              @click="handleChange(item, index)"
              :loading="state.loading"
              :disabled="!state.can_be_applied[index]"
            />
            <br />
            <p
              v-if="
                state.lastActiveToggle !== null &&
                state.lastActiveToggle === index
              "
            >
              Coupon Applied!
            </p>
            <p v-if="state.can_be_applied[index] == false">
              Coupon can't be applied, it's
              {{
                state.internal_coupons[index].is_stackable
                  ? "stackable"
                  : "not-stackable"
              }}!
            </p>
          </td>
        </tr>
      </tbody>
    </table>
    <div
      v-if="Object.keys(state.internal_coupons).length === 0 && !state.loading"
    >
      <p>No coupons available for this order with your permissions</p>
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, inject } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import CouponApi from "@/api/coupon"
  import { useToast } from "primevue/usetoast"
  import CustomerApi from "@/api/customers"

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
    loading: false,
    lastActiveToggle: null,
    can_be_applied: []
  })

  const emit = defineEmits(["updatedAttributes"])

  const props = defineProps({})

  const handleChange = async (el, index) => {
    state.loading = true
    if (!state.internal_coupons_applied[index]) {
      let { data, error } = await couponApi.removeCoupon({
        coupon_id: el.id,
        order_id: customerOrderStore.order.id
      })
      if (error.value) {
        state.loading = false
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Failed!",
          life: 3000,
          group: "br"
        })
        return
      }

      handle_stackable()
    } else {
      let { data, error } = await couponApi.applyCoupon({
        coupon_id: el.id,
        order_id: customerOrderStore.order.id
      })
      if (error.value) {
        state.loading = false
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Failed!",
          life: 3000,
          group: "br"
        })
        state.internal_coupons_applied[index] = false
        return
      } else {
        state.lastActiveToggle = index
        setTimeout(() => {
          state.lastActiveToggle = null
        }, 3000)

        handle_stackable()
      }
    }

    const order_coupons_response = await couponApi.getAnOrderCoupons(
      customerOrderStore.order.id
    )
    state.internal_coupons_applied = []
    state.internal_coupons.forEach((item) => {
      const result = order_coupons_response.data.value.find(
        (obj) => obj["id"] === item.id
      )
      if (result) {
        state.internal_coupons_applied.push(true)
      } else {
        state.internal_coupons_applied.push(false)
      }
    })
    const response = await customerApi.getOrderById(customerOrderStore.order.id)
    customerOrderStore.setOrder(response.data.value)
    state.loading = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Coupon Applied!",
      life: 3000,
      group: "br"
    })
  }

  const handle_stackable = () => {
    let some_coupons_applied = false
    for (var i = 0; i < state.internal_coupons.length; i++) {
      if (state.internal_coupons_applied[i] == true) {
        some_coupons_applied = true
        if (state.internal_coupons[i].is_stackable) {
          for (var j = 0; j < state.internal_coupons.length; j++) {
            if (i != j && state.internal_coupons[j].is_stackable == false) {
              state.can_be_applied[j] = false
            } else {
              state.can_be_applied[j] = true
            }
          }
        } else {
          for (var j = 0; j < state.internal_coupons.length; j++) {
            if (i != j) {
              state.can_be_applied[j] = false
            } else {
              state.can_be_applied[j] = true
            }
          }
        }
      }
    }

    if (!some_coupons_applied) {
      for (var j = 0; j < state.internal_coupons.length; j++) {
        state.can_be_applied[j] = true
      }
    }
  }

  const hasCouponRules = (coupon) => {
    return coupon.rules !== null && coupon.rules !== undefined
  }

  const passRulesCheck = (coupon) => {
    if (hasCouponRules(coupon)) {
      if (
        customerOrderStore.order.line_item_length >=
        coupon.rules.line_item_minimum
      ) {
        return true
      } else {
        return false
      }
    }
    return true
  }

  const passedPrepaidCouponCheck = (coupon) => {
    if (coupon?.attributes?.is_pre_paid === true) {
      if (customerOrderStore.order.is_pickup) return false
      return true
    }
    return true
  }
  onMounted(async () => {
    state.loading = true
    const response = await couponApi.getAllCoupons()

    state.internal_coupons = response.data.value.filter(
      (e) =>
        (e.type == "internal" || e.type == "both") &&
        (e.is_permanent == true ||
          (new Date() > new Date(e.start_date) &&
            new Date() < new Date(e.end_date))) &&
        e.role?.hasOwnProperty(usersStore.currentUser.role_name) &&
        passRulesCheck(e) &&
        passedPrepaidCouponCheck(e)
    )

    const order_coupons_response = await couponApi.getAnOrderCoupons(
      customerOrderStore.order.id
    )
    state.internal_coupons = state.internal_coupons.filter((el) => {
      if (el.category == null) {
        return true
      } else if (el.category == "containers_only") {
        return customerOrderStore.order.line_items.some(
          (item) => item.product_type === "CONTAINER"
        )
      } else if (el.category == "accessories_only") {
        return customerOrderStore.order.line_items.some(
          (item) => item.product_type === "CONTAINER_ACCESSORY"
        )
      } else if (el.category == "both") {
        return true
      }

      return false
    })

    state.internal_coupons.forEach((item) => {
      const result = order_coupons_response.data.value.find(
        (obj) => obj["id"] === item.id
      )
      if (result) {
        state.internal_coupons_applied.push(true)
      } else {
        state.internal_coupons_applied.push(false)
      }
      state.can_be_applied.push(true)
    })

    handle_stackable()
    state.loading = false
  })
</script>
