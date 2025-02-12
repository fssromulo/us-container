<template>
  <div class="col-12">
    <label
      for="partialPay"
      v-if="state.bulk_payment != 'bulk_payment'"
      class="font-medium text-900"
    >
      Total for all ({{ props.mergedOrders.length }}) orders:
      {{ $fc(state.total) }}
    </label>
  </div>
  <div class="col-12">
    <label
      for="partialPay"
      v-if="state.bulk_payment == 'bulk_payment'"
      class="font-medium text-900"
      >Enter Amount To Pay (Rental Balance:
      {{ $fc(state.overridePaymentAmount) }})</label
    >
  </div>

  <div class="field col-12" v-if="state.bulk_payment == 'bulk_payment'">
    <InputNumber
      :placeholder="0"
      mode="currency"
      style="width: 100%"
      currency="USD"
      id="partialPay"
      v-model="state.overridePaymentAmount"
      type="text"
    />
  </div>

  <div class="col-12">
    <div class="mb-5 col-12">
      <label class="font-medium text-900">Payment Type</label>
    </div>
    <div
      class="mt-4 field col-4"
      :class="{ 'col-12': state.paymentType == 'CC' }"
    >
      <Select
        class="text-xl"
        :loading="state.loading"
        v-model="state.paymentType"
        :options="paymentTypes"
        placeholder="Select a payment type"
        scrollHeight="330px"
        optionLabel="label"
        optionValue="value"
      />
    </div>
    <div
      class="mt-4 field col-4"
      :class="{ 'col-12': state.paymentType == 'CC' }"
    >
      <Select
        class="text-xl"
        :loading="state.loading"
        v-model="state.bulk_payment"
        :options="state.bulk_payment_options"
        placeholder="Select a payment type"
        scrollHeight="330px"
        optionLabel="label"
        optionValue="value"
      />
    </div>

    <div
      class="mt-4 field col-4"
      :class="{ 'col-12': state.paymentType == 'CC' }"
    >
      <label>Transaction creation date</label>
      <br />
      <DatePicker
        style="width: 210px"
        showIcon
        showButtonBar
        v-model="state.transaction_paid_at"
        dateFormat="mm/dd/y"
        id="paid_on"
        class="p-component p-inputtext-fluid"
      />

      <br />
    </div>

    <div class="mt-4 field col-4">
      <div
        v-for="order in props.mergedOrders"
        v-if="state.bulk_payment == 'individual_payment'"
        :key="order"
        class="flex flex-col"
      >
        <label :for="order" class="mb-1 text-sm font-medium text-gray-700">
          {{ state.merged_orders_dict[order].display_order_id }}
          <span v-if="state.merged_orders_dict[order].type != 'RENT'">{{
            state.merged_orders_dict[order].type
          }}</span>
        </label>
        <InputNumber
          :id="order"
          v-model="state.individual_amounts[order]"
          :disabled="state.merged_orders_dict[order].type != 'RENT'"
          mode="currency"
          currency="USD"
          locale="en-US"
          class="w-full"
        />
      </div>
    </div>
  </div>
  <div v-if="isCreditCardPayment">
    <payment-fields
      :disable-all-fields="false"
      :is-internal="true"
      :override-payment-amount="state.overridePaymentAmount"
      :overridePaymentMethod="payDownRentalCreditCardHandler"
      :credit-card-selected="isCreditCardPayment"
      :applyBankFee="true"
      :bankFee="bankFee"
      :multipleOrders="true"
    />
  </div>
  <div v-else>
    <Button
      :label="`Pay ${$fc(state.overridePaymentAmount)}`"
      style="max-width: 200px"
      @click="payOrder"
      :loading="state.loading"
      class="p-button-primary p-button-rounded p-button-lg"
    ></Button>
  </div>
</template>

<script setup>
  import {
    onMounted,
    reactive,
    defineProps,
    computed,
    inject,
    watch,
    defineEmits,
    ref
  } from "vue"
  import { defaultPaymentTypesDropDown } from "@/utils/paymentTypes"
  import PaymentFields from "./payment/PaymentFields.vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"
  import PaymentMethodsApi from "@/api/payment_methods"
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"

  const paymentMethodsApi = new PaymentMethodsApi()
  const toast = useToast()
  const customerOrderStore = useCustomerOrder()
  const customerStore = useCustomerOrder()
  const usersStore = useUsers()
  const customerApi = new CustomerApi()

  const emit = defineEmits(["payed"])
  const paymentTypes = ref(defaultPaymentTypesDropDown())

  onMounted(async () => {
    state.overridePaymentAmount = props.paymentAmount

    state.total = state.overridePaymentAmount

    let fullOrders = await customerApi.getOrdersByIds(props.mergedOrders)
    fullOrders.data.value.forEach((el) => {
      state.merged_orders_dict[el.id] = el
    })

    props.mergedOrders.forEach(async (el) => {
      state.individual_amounts[el] = 0
    })

    const paymentMethodsData = await paymentMethodsApi.getAllPaymentMethods()
    state.can_use_credit_card = orderCanUseCreditCard(customerStore.publicOrder)
    paymentTypes.value = paymentMethodsData.data.value
      .map((el) => {
        return {
          label: el.display_name,
          value: el.name
        }
      })
      .filter((e) => {
        if (state.can_use_credit_card == true) return true
        return e.value === "CC" ? false : true
      })
  })

  const isCreditCardPayment = computed(() => {
    return state.paymentType === "CC"
  })

  const $fc = inject("$formatCurrency")

  const props = defineProps({
    paymentAmount: {
      type: Number,
      default: 0
    },
    mergedOrders: {
      type: Array,
      default: []
    },
    resetOrder: {
      type: Function,
      default: []
    }
  })

  const state = reactive({
    rentPeriodId: "",
    transactionTypeId: "",
    paymentCompleted: false,
    paymentType: "Cash",
    overridePaymentAmount: 0,
    paymentOption: "Pay all",
    order: {},
    loading: false,
    can_use_credit_card: false,
    bulk_payment_options: [
      { label: "Bulk payment", value: "bulk_payment" },
      { label: "Individual payment", value: "individual_payment" }
    ],
    bulk_payment: "bulk_payment",
    individual_amounts: {},
    merged_orders_dict: {},
    transaction_paid_at: null,
    total: 0
  })

  const bankFee = computed(() => {
    let cms = customerOrderStore.publicCms || usersStore.cms
    let bankFees = cms.convenience_fee_rate * state.overridePaymentAmount
    return bankFees
  })

  const payDownRentalCreditCardHandler = async (paymentObj) => {
    const otherPaymentObj = {
      lump_sum_amount: state.overridePaymentAmount,
      payment_option: props.paymentOption,
      payment_type: "CC",
      mergedOrders: props.mergedOrders,
      bulk_payment: state.bulk_payment,
      individual_payments: [],
      transaction_paid_at: state.transaction_paid_at
    }

    Object.keys(state.individual_amounts).forEach((key) => {
      if (state.individual_amounts[key] != 0) {
        otherPaymentObj["individual_payments"].push({
          order_id: key,
          payment_amount: state.individual_amounts[key]
        })
      }
    })

    await customerApi
      .payOtherRentalOrdersCreditCard({
        other_payment: otherPaymentObj,
        payment_request: paymentObj
      })
      .then(async (response) => {
        console.log(response)
        if (response.error.value) {
          state.error = "Payment was Unsuccessful"
          return
        } else {
          customerStore.setOrder(null)
          customerStore.setOrder(response.data.value)
          toast.add({
            severity: "success",
            summary: "Success",
            detail: "Payment Successful",
            group: "br",
            life: 2000
          })
        }
        emit("payed")

        await props.resetOrder()
      })
  }

  const payOrder = async () => {
    state.loading = true
    let dataReq = {
      mergedOrders: props.mergedOrders,
      paymentAmount: state.overridePaymentAmount,
      paymentType: state.paymentType,
      bulk_payment: state.bulk_payment,
      individual_payments: [],
      transaction_paid_at: state.transaction_paid_at
    }

    Object.keys(state.individual_amounts).forEach((key) => {
      if (state.individual_amounts[key] != 0) {
        dataReq["individual_payments"].push({
          order_id: key,
          payment_amount: state.individual_amounts[key]
        })
      }
    })

    await customerApi
      .payOtherOrdersRentalOrder(dataReq)
      .then(async (response) => {
        if (response.error.value) {
          state.error = "Payment was Unsuccessful"
          state.loading = false

          return
        } else {
          toast.add({
            severity: "success",
            summary: "Success",
            detail: "Payment Successful",
            group: "br",
            life: 2000
          })
          state.loading = false
          await props.resetOrder()
          emit("payed")
        }
      })
  }

  watch(
    () => customerStore.publicOrder,
    (newVal) => {
      state.can_use_credit_card = orderCanUseCreditCard(
        customerStore.publicOrder
      )
    }
  )

  watch(
    () => state.individual_amounts,
    (newVal) => {
      state.overridePaymentAmount = 0
      Object.keys(state.individual_amounts).forEach((key) => {
        console.log(state.merged_orders_dict, state.individual_amounts)
        if (
          state.merged_orders_dict[key].calculated_remaining_order_balance <
          state.individual_amounts[key]
        ) {
          state.individual_amounts[key] =
            state.merged_orders_dict[key].calculated_remaining_order_balance
        } else if (state.individual_amounts[key] < 0) {
          state.individual_amounts[key] = 0
        }

        state.overridePaymentAmount += state.individual_amounts[key]
      })
    },
    { deep: true }
  )
</script>
