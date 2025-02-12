<template>
  <section class="flex w-full flex-col">
    <div class="flex justify-between items-center">
      <p class="mt-0 mb-0 text-xl font-semibold text-900 dark:text-0">
        <span class=""> Quick Pay</span>
      </p>
    </div>
    <div class="grid grid-cols-12 gap-4 mt-8">
      <div class="col-span-4">
        <p class="mt-4 mb-0 text-xl font-semibold text-900 dark:text-0">
          <span class=""> Current Balance :{{ $fc(calculatedBalance) }}</span>
        </p>
      </div>
      <div class="col-span-8">
        <Button
          v-if="$ability.can('update', 'rental_payments')"
          :disabled="calculatedBalance <= 0"
          @click="initMultipleRentalPayment()"
          :label="goToPaymentLabel"
          class="ml-2 p-button-accent p-button-lg"
        />
      </div>
    </div>

    <Dialog
      v-model:visible="state.payForMultipleRows"
      modal
      header="Quick Pay"
      closeOnEscape
      :dismissableMask="true"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
      :style="{ width: '50rem' }"
    >
      <QuickPayFields
        :disableAllFields="false"
        :paymentOption="state.paymentOption"
        :overridePaymentAmount="calculatedBalance"
        :selectedRentPeriodsIds="generatedRentalPeriods"
        :paymentType="state.paymentType"
        :creditCardFeeToggleEnabled="true"
        :overridePaymentAmountEditable="true"
        :isUpdateCreditCard="false"
        :rentPaymentAmount="calculatedBalance"
        :feePaymentAmount="0"
        :rentalAfterPayReset="reloadRentalPeriod"
        :isInternal="true"
        :orderId="state.order.id"
        :hasAch="state.hasAch"
        :resetOrder="resetOrder"
        :resetRentPeriod="resetRentPeriod"
        :order="state.order"
      ></QuickPayFields>
    </Dialog>
  </section>
</template>

<script setup>
  import { reactive, onMounted, inject, computed } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import CustomerService from "@/service/Customers"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import StateService from "../../service/StateService"
  import QuickPayFields from "./payment/QuickPayFields.vue"

  import { watch } from "vue"
  const stateService = new StateService()

  const $fc = inject("$formatCurrency")

  const $ability = inject("$ability")
  const customerStore = useCustomerOrder()

  const emit = defineEmits(["updateCustomerOrder"])

  const customerService = new CustomerService()
  const customerApi = new CustomerApi()
  const goToPaymentLabel = computed(() => {
    return "Go To Payment"
  })

  const state = reactive({
    customer: {},
    originalCustomer: {},
    address: {},
    originalAddress: {},
    statesList: [],
    isLoading: false,
    isEditing: false,
    searchType: "name",
    selectedCustomer: {},
    retrievedCustomers: [],
    customerProfile: {},
    order: {},
    payForMultipleRows: false,
    paymentType: "CC",
    hasAch: false,
    paymentOption: "Pay all"
  })

  const initMultipleRentalPayment = () => {
    state.payForMultipleRows = true
  }

  const calculatedBalance = computed(() => {
    if (state.paymentOption == "Pay all") {
      // return state.order.calculated_rent_balance
      if (state.order.calculated_paid_thru === "NOT APPLICABLE")
        return state.order.rent_periods[0]?.calculated_rent_period_total_balance
      return state.order.rent_periods
        ?.filter((period) => {
          return (
            period.calculated_rent_period_total_balance > 0 &&
            period.start_date < Date.now()
          )
        })
        .map((period) => period.calculated_rent_period_total_balance)
        .reduce((acc, currentValue) => acc + currentValue, 0)
    } else {
      //calculated_rent_period_fee_balance
      return state.order.rent_periods
        ?.filter((period) => {
          return period.calculated_rent_period_fee_balance > 0
        })
        .map((period) => period.calculated_rent_period_fee_balance)
        .reduce((acc, currentValue) => acc + currentValue, 0)
      return 1
    }
  })

  const generatedRentalPeriods = computed(() => {
    if (state.order.calculated_paid_thru === "NOT APPLICABLE")
      return [state.order.rent_periods[0].id]
    return state.order.rent_periods
      .filter((period) => {
        return period.calculated_rent_period_total_balance > 0
      })
      .map((period) => period.id)
  })

  const resetCustomer = async () => {
    state.address = cloneDeep(customerStore.order?.address)
    state.originalAddress = cloneDeep(customerStore.order?.address)

    state.customer = cloneDeep(customerStore.order?.customer)
    state.originalCustomer = cloneDeep(customerStore.order?.customer)

    state.customerProfile = cloneDeep(customerStore.order?.single_customer)
    state.originalCustomerProfile = cloneDeep(
      customerStore.order?.single_customer
    )

    state.isLoading = false
    state.isEditing = false
  }

  const resetOrder = async (fetchOrder = false) => {
    await customerStore.orderResetLock.acquire()
    state.editing_rent_period = false
    // the reload is used when we update a rent period, but when we just load the data the first time
    // then we dont need to reload it

    let updatedOrderResponse = await customerApi.getOrderById(
      customerStore.order.id
    )
    if (updatedOrderResponse.data.value.status == "Delinquent") {
      if (updatedOrderResponse.data.value.status.calculated_rent_balance == 0) {
        updatedOrderResponse = await customerApi.updateOrder(
          customerStore.order.id,
          { status: "Delivered" }
        )
      }
    }
    customerStore.setOrder(updatedOrderResponse.data.value)
    let order = customerStore.order
    order = customerService.orderDto()
    state.rentPeriods = order.rent_periods
    state.originalOrder = cloneDeep(order)
    state.order = cloneDeep(order)
    state.order.customer_application_schema_id =
      state.order?.customer_application_schema?.id || null

    if (fetchOrder) {
      // updating the selected rent period
      state.selectedRentPeriod = state.rentPeriods.find((period) => {
        return period.id === state.selectedRentPeriod?.id
      })
    }

    state.payForMultipleRows = false
    state.isPayDownRentPeriods = true

    await customerStore.orderResetLock.release()
    // emit("updateCustomerOrder");
  }
  const loadOrder = () => {
    let order = customerService.orderDto()
    state.originalOrder = cloneDeep(order)
    state.order = cloneDeep(order)
    state.order.customer_application_schema_id =
      state.order?.customer_application_schema?.id || null
  }

  const reloadRentalPeriod = (updatedOrder, isOrderAlreadyUpdated = false) => {}

  watch(
    () => customerStore.order,
    (newVal) => {
      if (newVal !== null && newVal !== undefined) loadOrder()
    },
    { immediate: true, deep: true }
  )

  onMounted(async () => {
    state.statesList = stateService.getStates()
    loadOrder()
  })

  watch(
    () => customerStore.order,
    () => {
      resetCustomer()
    },
    { deep: true, immediate: true }
  )
</script>
