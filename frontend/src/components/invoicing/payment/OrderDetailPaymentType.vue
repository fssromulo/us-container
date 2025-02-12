<template>
  <div class="grid grid-cols-12 gap-4 ml-2 p-fluid">
    <div class="col-span-6 mb-4 field">
      <label class="font-medium text-900 dark:text-0" for="selectAnOption">
        Select An Option </label
      ><br />
      <Select
        id="selectAnOption"
        class="p-component p-inputtext-fluid"
        :loading="state.loading"
        v-model="state.payment"
        :options="[
          { label: 'Pay In Full', value: 'Paid' },
          { label: 'Add Payment', value: 'Partially Paid' }
        ]"
        placeholder="Select an option"
        scrollHeight="330px"
        optionLabel="label"
        optionValue="value"
      />
    </div>
    <div class="col-span-6 mb-4 field">
      <label class="font-medium text-900 dark:text-0" for="paidAmt">
        Amount </label
      ><br />
      <InputNumber
        mode="currency"
        currency="USD"
        v-model="state.amount"
        id="tax"
        type="text"
        class="p-component p-inputtext-fluid"
        :disabled="isFullPayment || state.override_distribution"
        :class="{ 'p-invalid': state.invalid_total_amount }"
      />
    </div>

    <div class="col-span-8" v-if="$ability.can('override', 'order_balances')">
    </div>

    <div class="col-span-4" v-if="$ability.can('override', 'order_balances')">
      <label class="font-medium text-900 dark:text-0" for="subtotalAmt">
        Subtotal amount applied </label
      ><br />
      <InputNumber
        mode="currency"
        currency="USD"
        v-model="state.subtotal_to_pay"
        id="tax"
        type="text"
        style="height: 10px"
        :class="{ 'p-invalid': state.invalid_subtotal_to_pay }"
        class="p-component p-inputtext-fluid"
        :disabled="!state.override_distribution"
      />
    </div>

    <div class="col-span-8" v-if="$ability.can('override', 'order_balances')">
    </div>
    <div class="col-span-4" v-if="$ability.can('override', 'order_balances')">
      <label class="font-medium text-900 dark:text-0" for="tax">
        Tax amount applied</label
      ><br />
      <InputNumber
        mode="currency"
        currency="USD"
        v-model="state.tax_to_pay"
        id="tax"
        type="text"
        :class="{ 'p-invalid': state.invalid_tax_to_pay }"
        class="p-component p-inputtext-fluid"
        :disabled="!state.override_distribution"
      />
    </div>

    <div class="col-span-8" v-if="$ability.can('override', 'order_balances')">
    </div>
    <div class="col-span-4" v-if="$ability.can('override', 'order_balances')">
      <label class="font-medium text-900 dark:text-0" for="feeAmtApplied">
        Fees amount applied</label
      ><br />
      <InputNumber
        mode="currency"
        currency="USD"
        v-model="state.fee_to_pay"
        id="tax"
        type="text"
        class="p-component p-inputtext-fluid"
        :class="{ 'p-invalid': state.invalid_fee_to_pay }"
        :disabled="!state.override_distribution"
      />
    </div>

    <div class="col-span-12" v-if="$ability.can('override', 'order_balances')">
      <label class="font-medium text-900 dark:text-0" for="overrideDis">
        Override distribution</label
      ><br />
      <ToggleSwitch
        id="overrideDis"
        v-model="state.override_distribution"
        type="text"
      />
    </div>

    <div class="col-span-6 mb-4 field">
      <label for="pmtType" class="font-medium text-900 dark:text-0"
        >Payment Type</label
      ><br />
      <Select
        id="pmtType"
        class="p-component p-inputtext-fluid"
        :loading="state.loading"
        v-model="state.paymentType"
        :options="state.paymentTypes"
        placeholder="Select a payment type"
        scrollHeight="330px"
        optionLabel="label"
        optionValue="value"
      />
    </div>
    <div class="col-span-6 mb-4 field">
      <label class="font-medium text-900 dark:text-0" for="pmtNotes"
        >Payment Notes</label
      ><br />
      <Textarea
        v-model="state.notes"
        :autoResize="true"
        rows="2"
        placeholder="Payment Notes"
        label="Notes"
        cols="20"
        class="p-component p-inputtext-fluid"
      />
    </div>
    <div class="col-span-6 mb-12 field">
      <label for="txnDate" class="font-medium text-900 dark:text-0">Date</label
      ><br />
      <DatePicker
        id="txnDate"
        style="width: 200px"
        v-model="state.date"
        class="p-component p-inputtext-fluid"
      />
    </div>
    <div class="col-span-6"></div>
    <div class="col-span-6">
      <Button
        severity="success"
        label="Save Payment"
        :loading="state.loading"
        @click="saveTransactionType"
      ></Button>
    </div>
  </div>
</template>

<script setup>
  import {
    reactive,
    computed,
    onMounted,
    defineEmits,
    watch,
    inject
  } from "vue"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useTransactionTypeStore } from "../../../store/modules/transactionTypeStore"
  import { defaultPaymentTypesDropDown } from "@/utils/paymentTypes"
  import { useUsers } from "@/store/modules/users"
  import PaymentMethodsApi from "@/api/payment_methods"
  import { convertDateForPostRealDate } from "../../../service/DateFormat"

  const paymentMethodsApi = new PaymentMethodsApi()
  const userStore = useUsers()
  let paymentOptions = null // = defaultPaymentTypesDropDown();

  const customerOrderStore = useCustomerOrder()

  const transactionTypeStore = useTransactionTypeStore()

  const customerApi = new CustomerApi()
  const toast = useToast()

  const $ability = inject("$ability")

  const props = defineProps({
    orderDetail: {}
  })

  const state = reactive({
    paymentType: "Check",
    loading: false,
    notes: "",
    hasAch: false,
    account_number: "",
    routing_number: "",
    bank_name: "",
    payment: "Paid",
    payment_strategy: "",
    amount: props.orderDetail.calculated_remaining_order_balance,
    paymentTypes: null,
    tax_to_pay: 0,
    subtotal_to_pay: 0,
    fee_to_pay: 0,
    override_distribution: false,
    invalid_tax_to_pay: false,
    invalid_subtotal_to_pay: false,
    invalid_fee_to_pay: false,
    invalid_total_amount: false,
    date: new Date()
  })

  const isFullPayment = computed(() => {
    state.amount = props.orderDetail.calculated_remaining_order_balance
    return state.payment === "Paid"
  })
  const emit = defineEmits(["paymentAdded"])

  const saveTransactionType = async () => {
    if (
      state.invalid_fee_to_pay ||
      state.invalid_subtotal_to_pay ||
      state.invalid_tax_to_pay ||
      state.invalid_total_amount
    ) {
      toast.add({
        severity: "error",
        summary: `Invalid amounts.`,
        detail: "Invalid amounts.",
        life: 3000,
        group: "br"
      })
      return
    }
    state.loading = true
    let tType = {
      payment_type: state.paymentType,
      order_id: props.orderDetail.id,
      rent_period_id: null,
      amount: state.amount,
      notes: state.notes,
      user_id: userStore.currentUser.id,
      transaction_effective_date: convertDateForPostRealDate(
        state.date
      ).toISOString()
    }
    const { data, error } = await customerApi.addTransactionType(tType)
    if (data.value) {
      // toast.add({
      //   severity: "success",
      //   summary: "Success",
      //   detail: "Payment means saved successful",
      //   group: "br",
      //   life: 2000,
      // });
    }
    // emit("transactionTypeSaved", {});

    const newBalance =
      customerOrderStore.order.calculated_remaining_order_balance - state.amount

    const requestData = {
      payment_type: state.paymentType,
      status: state.payment,
      remaining_balance: newBalance,
      amount_paid: state.amount,
      payment_strategy: state.payment_strategy,
      payment_option: state.payment,
      transaction_type_id: data.value.id,

      override_distribution: state.override_distribution,
      fees_to_be_paid: state.fee_to_pay,
      tax_to_be_paid: state.tax_to_pay,
      subtotal_to_be_paid: state.subtotal_to_pay
    }

    const response = await customerApi.updateOrder(
      customerOrderStore.order.id,
      requestData
    )
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Order updated",
      group: "br",
      life: 2000
    })
    customerOrderStore.setOrder(null)
    customerOrderStore.setOrder(response.data)
    emit("paymentAdded", {})
    state.loading = false
  }

  onMounted(async () => {
    state.amount = props.orderDetail.calculated_remaining_order_balance

    const data = await customerApi.previewPayment(props.orderDetail.id, {
      payment_amount: state.amount
    })

    state.subtotal_to_pay = data.data.value.subtotal_to_be_paid
    state.tax_to_pay = data.data.value.tax_to_be_paid
    state.fee_to_pay = data.data.value.fees_to_be_paid

    const paymentMethodsData = await paymentMethodsApi.getAllPaymentMethods()
    paymentOptions = paymentMethodsData.data.value.map((el) => {
      return {
        label: el.display_name,
        value: el.name
      }
    })
    state.paymentTypes = paymentOptions.filter((option) => {
      return option.value != "CC" && option.value != "Credit Card"
        ? true
        : false
    })
  })

  watch(
    () => state.amount,
    async (newVal, oldVal) => {
      if (
        state.amount - props.orderDetail.calculated_remaining_order_balance >
        0.01
      ) {
        state.invalid_total_amount = true
      } else {
        state.invalid_total_amount = false
      }
      if (!state.override_distribution) {
        const data = await customerApi.previewPayment(props.orderDetail.id, {
          payment_amount: state.amount
        })

        state.subtotal_to_pay = data.data.value.subtotal_to_be_paid
        state.tax_to_pay = data.data.value.tax_to_be_paid
        state.fee_to_pay = data.data.value.fees_to_be_paid
      }
    }
  )

  watch(
    () => state.subtotal_to_pay,
    async (newVal, oldVal) => {
      if ($ability.can("override", "order_balances")) {
        if (
          state.subtotal_to_pay -
            props.orderDetail.calculated_order_subtotal_balance >
          0.01
        ) {
          state.invalid_subtotal_to_pay = true
        } else {
          state.invalid_subtotal_to_pay = false
        }
      }
      if (state.override_distribution) {
        state.amount =
          state.subtotal_to_pay + state.tax_to_pay + state.fee_to_pay
      }
    }
  )

  watch(
    () => state.tax_to_pay,
    async (newVal, oldVal) => {
      if ($ability.can("override", "order_balances")) {
        if (
          state.tax_to_pay - props.orderDetail.calculated_order_tax_balance >
          0.01
        ) {
          state.invalid_tax_to_pay = true
        } else {
          state.invalid_tax_to_pay = false
        }
      }
      if (state.override_distribution) {
        state.amount =
          state.subtotal_to_pay + state.tax_to_pay + state.fee_to_pay
      }
    }
  )

  watch(
    () => state.fee_to_pay,
    async (newVal, oldVal) => {
      if ($ability.can("override", "order_balances")) {
        if (
          state.fee_to_pay - props.orderDetail.calculated_order_fees_balance >
          0.01
        ) {
          state.invalid_fee_to_pay = true
        } else {
          state.invalid_fee_to_pay = false
        }
      }
      if (state.override_distribution) {
        state.amount =
          state.subtotal_to_pay + state.tax_to_pay + state.fee_to_pay
      }
    }
  )
</script>
