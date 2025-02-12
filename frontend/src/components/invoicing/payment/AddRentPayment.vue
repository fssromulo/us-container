<template>
  <div class="">
    <div v-if="!isOverridePaymentPresent">
      <div class="grid justify-center grid-cols-12 gap-4 mt-8 mb-2">
        <label for="addPaymentAmt" class="font-medium text-900 dark:text-0"
          >Add Payment</label
        >
      </div>
      <div class="grid justify-center grid-cols-12 gap-4">
        <InputNumber
          mode="currency"
          currency="USD"
          v-model="state.addPaymentAmt"
          id="addPaymentAmt"
          type="text"
          class="col-span-3"
        />
      </div>
    </div>
    <div class="col-span-12 text-center">
      <TransactionType
        v-if="!props.hasPayment"
        :rentalPeriodId="props.rentPeriodId"
        :excludePaymentTypes="['CC']"
        :transactionTypeId="state.transactionTypeId"
        :canSaveTransactionType="state.paymentCompleted"
        @transactionTypeSaved="handleTransactionTypeSaved"
        @transactionTypeChanged="transactionTypeChanged"
      />
      <br />
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

    <PaymentFields
      v-if="state.displayCreditCardFields && state.can_use_credit_card"
      :overridePaymentAmount="paymentAmount"
      :disable-all-fields="false"
      :is-internal="true"
      :send-success-feed-back="true"
      :overridePaymentMethod="payDownRentalCreditCardHandler"
      :applyBankFee="applyBankFeeComputed"
      :bankFee="bankFee"
    />
    <Message v-if="state.error !== ''" severity="error">{{
      state.error
    }}</Message>

    <div
      class="flex flex-wrap justify-center mt-4 field-checkbox"
      v-if="!state.displayCreditCardFields"
    >
      <Button
        :label="`Pay ${$fc(paymentAmount)} ${addAchText}`"
        :disabled="state.loading"
        :loading="state.loading"
        style="max-width: 250px"
        @click="payDownRental"
        class="p-button-primary p-button-rounded p-button-lg"
      ></Button>
    </div>
  </div>
</template>

<script setup>
  import {
    reactive,
    computed,
    inject,
    watch,
    defineProps,
    onMounted
  } from "vue"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import Cart from "@/service/Cart.js"
  import TransactionType from "./TransactionType.vue"
  import { useTransactionTypeStore } from "../../../store/modules/transactionTypeStore"
  import { DateTime } from "luxon"
  import PaymentFields from "./PaymentFields.vue"
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"

  const cart = new Cart()
  const customerApi = new CustomerApi()
  const $fc = inject("$formatCurrency")
  const toast = useToast()
  const customerStore = useCustomerOrder()
  const usersStore = useUsers()

  const transactionTypeStore = useTransactionTypeStore()

  onMounted(() => {
    let isOverridePaymentPresent = props.overridePaymentAmount > 0
    state.payButtonDisabled = !isOverridePaymentPresent
    state.credit_card_fee = customerStore.order.credit_card_fee
    state.error = ""
  })

  const props = defineProps({
    hasAch: {
      type: Boolean,
      default: false
    },
    paymentOption: {
      type: String,
      default: "Pay all"
    },
    accountNumber: {
      type: String,
      default: ""
    },
    routingNumber: {
      type: String,
      default: ""
    },
    bankName: {
      type: String,
      default: ""
    },
    paymentType: {
      type: String,
      default: ""
    },
    order_id: {
      type: String,
      default: ""
    },
    hasPayment: {
      type: Boolean,
      default: false
    },
    overridePaymentAmount: {
      type: Number,
      default: 0
    },
    rentPaymentAmount: {
      type: Number,
      default: 0
    },
    feePaymentAmount: {
      type: Number,
      default: 0
    },
    taxPaymentAmount: {
      type: Number,
      default: 0
    },
    rentPeriodIds: {
      type: Array,
      default: []
    },
    resetFunction: {
      type: Function,
      default: () => {}
    },
    notes: {
      type: String,
      default: ""
    },
    parentState: {
      type: Object,
      default: {}
    }
  })

  const addAchText = computed(() => {
    if (props.hasAch && useAch.value) {
      return " with ACH On File"
    }
    return ""
  })

  const applyBankFeeComputed = computed(() => {
    return customerStore.order.credit_card_fee
  })

  const transactionTypeChanged = async (transactionType) => {
    if (transactionType.paymentType == "CC") {
      state.displayCreditCardFields = true
    } else {
      state.displayCreditCardFields = false
    }
    if (transactionType.paymentType == "Echeck (ACH On File)") {
      state.bankName = transactionType.bankName
      state.routingNumber = transactionType.routingNumber
      state.accountNumber = transactionType.accountNumber
      state.hasAch = true
    } else {
      state.hasAch = false
    }
    state.payment_type = transactionType.paymentType
    state.notes = transactionType.notes
  }

  const isOverridePaymentPresent = computed(() => {
    return props.overridePaymentAmount > 0
  })

  const payDownRentalCreditCardHandler = async (paymentObj) => {
    const otherPaymentObj = {
      lump_sum_amount: paymentAmount.value,
      payment_option: props.paymentOption,
      order_id: props.order_id,
      rent_period_ids: props.rentPeriodIds,
      payment_type: "CC"
    }

    if (props.taxPaymentAmount != null) {
      otherPaymentObj["rent_period_tax_paid_amt"] = props.taxPaymentAmount
    }
    if (props.feePaymentAmount != null) {
      otherPaymentObj["rent_period_fee_paid_amt"] = props.feePaymentAmount
    }

    if (props.rentPaymentAmount != null) {
      otherPaymentObj["rent_period_paid_amt"] = props.rentPaymentAmount
    }

    await customerApi
      .payOtherRentalOrderCreditCard({
        other_payment: otherPaymentObj,
        payment_request: paymentObj
      })
      .then((response) => {
        if (response.error.value) {
          state.error = "Payment was Unsuccessful"
          return
        } else {
          const initialRentPeriodMap = {}
          customerStore.order.rent_periods.forEach(
            (element) => (initialRentPeriodMap[element.id] = element)
          )
          const compareWithRentPeriodMap = {}
          response.data.value.rent_periods.forEach(
            (element) => (compareWithRentPeriodMap[element.id] = element)
          )

          const changed_periods_ids = []
          const amount = []
          Object.keys(initialRentPeriodMap).forEach((key) => {
            if (
              initialRentPeriodMap[key].id ==
                compareWithRentPeriodMap[key].id &&
              initialRentPeriodMap[key].calculated_rent_period_total_balance !=
                compareWithRentPeriodMap[key]
                  .calculated_rent_period_total_balance
            ) {
              changed_periods_ids.push(initialRentPeriodMap[key].id)
              amount.push(
                initialRentPeriodMap[key].calculated_rent_period_total_balance -
                  compareWithRentPeriodMap[key]
                    .calculated_rent_period_total_balance
              )
            }
          })

          transactionTypeStore.setPeriodIds(changed_periods_ids)
          transactionTypeStore.setAmount(amount)

          customerStore.setOrder(null)
          customerStore.setOrder(response.data.value)
          state.paymentCompleted = true
          transactionTypeStore.canSaveTransactionType = true

          toast.add({
            severity: "success",
            summary: "Success",
            detail: "Payment Successful",
            group: "br",
            life: 2000
          })
        }
      })
  }
  const useAch = computed(() => {
    return (
      props.paymentType == "Echeck (ACH On File)" ||
      state.payment_type == "Echeck (ACH On File)"
    )
  })
  const hasAch = computed(() => {
    return props.hasAch || state.hasAch
  })

  const payDownRental = async () => {
    state.error = ""
    state.loading = true
    let otherPaymentObj = {}
    let today = DateTime.now()
    console.log("payDownRental")

    if (isOverridePaymentPresent.value) {
      console.log("isOverridePaymentPresent")

      // This means that we are in a single rent period and are paying down indidvidual balances
      otherPaymentObj = {
        order_id: props.order_id,
        payment_option: props.paymentOption,
        rent_period_paid_amt: props.rentPaymentAmount,
        rent_period_fee_paid_amt: props.feePaymentAmount,
        rent_period_tax_paid_amt: props.taxPaymentAmount,
        rent_period_ids: props.rentPeriodIds,
        lump_sum_amount: props.overridePaymentAmount,
        rent_due_on_day: today.day,
        has_ach: hasAch.value,
        use_ach_on_file: useAch.value ? true : false,
        payment_type: state.payment_type,
        notes: props.notes == "" ? state.notes : props.notes,
        transaction_created_at: state.transaction_paid_at
      }
    } else {
      console.log("LUMP SUM AMOUNT")
      otherPaymentObj = {
        lump_sum_amount: paymentAmount.value,
        payment_option: props.paymentOption,
        order_id: props.order_id,
        has_ach: hasAch.value,
        use_ach_on_file: useAch.value ? true : false,
        payment_type: state.payment_type,
        notes: props.notes == "" ? state.notes : props.notes,
        transaction_created_at: state.transaction_paid_at
      }
    }

    await customerApi
      .payOtherRentalOrder(otherPaymentObj)
      .then(async (response) => {
        if (response.error.value) {
          state.error = "There was an error with the payment"
          return
        } else {
          /*
      const initialRentPeriodMap = {};
      customerStore.order.rent_periods.forEach(
        (element) => (initialRentPeriodMap[element.id] = element)
      );
      const compareWithRentPeriodMap = {};
      response.data.value.rent_periods.forEach(
        (element) => (compareWithRentPeriodMap[element.id] = element)
      );

      const changed_periods_ids = [];
      const amount = [];
      Object.keys(initialRentPeriodMap).forEach((key) => {
        if (
          initialRentPeriodMap[key].id == compareWithRentPeriodMap[key].id &&
          initialRentPeriodMap[key].calculated_rent_period_total_balance !=
            compareWithRentPeriodMap[key].calculated_rent_period_total_balance
        ) {
          changed_periods_ids.push(initialRentPeriodMap[key].id);
          amount.push(
            initialRentPeriodMap[key].calculated_rent_period_total_balance -
              compareWithRentPeriodMap[key].calculated_rent_period_total_balance
          );
        }
      });
      transactionTypeStore.setPeriodIds(changed_periods_ids);
      transactionTypeStore.setAmount(amount);
      */
          customerStore.setOrder(null)
          customerStore.setOrder(response.data.value)

          state.paymentCompleted = true
          //transactionTypeStore.canSaveTransactionType = true
          await props.resetFunction(true)
          toast.add({
            severity: "success",
            summary: "Success",
            detail: "Payment Successful",
            group: "br",
            life: 2000
          })
        }
      })
    state.loading = false
  }

  const paymentAmount = computed(() => {
    let overridePaymentAmount = props.overridePaymentAmount
    let fieldAmount = state.addPaymentAmt
    let amount = overridePaymentAmount > 0 ? overridePaymentAmount : fieldAmount
    return amount
  })

  const state = reactive({
    addPaymentAmt: 0,
    error: "",
    loading: false,
    payButtonDisabled: props.overridePaymentAmount <= 0,
    credit_card_fee: false,
    transactionTypeId: "",
    paymentCompleted: false,
    displayCreditCardFields: false,
    hasAch: false,
    accountNumber: "",
    routingNumber: "",
    bankName: "",
    payment_type: "Cash",
    notes: "",
    can_use_credit_card: false,
    transaction_paid_at: null
  })
  const handleTransactionTypeSaved = async () => {
    state.paymentCompleted = false
    await props.resetFunction(true)
  }

  const creditCardFeeToggleEnabled = computed(() => {
    return usersStore.cms?.credit_card_fees.enable_toggle_credit_card_fees
  })

  const bankFee = computed(() => {
    let overridePaymentAmount = props.overridePaymentAmount
    let fieldAmount = state.addPaymentAmt
    let amount = overridePaymentAmount > 0 ? overridePaymentAmount : fieldAmount

    let cms = customerStore.publicCms || usersStore.cms
    let bankFees = 0
    if (customerStore.order.type === "RENT") {
      bankFees = cart.roundIt(amount * cms.convenience_fee_rate, 2)
    }
    return bankFees
  })
  onMounted(() => {
    console.log("onMounted", props.paymentType)
    state.payment_type = props.paymentType
    state.notes = props.notes
    let isOverridePaymentPresent = props.overridePaymentAmount > 0
    state.payButtonDisabled = !isOverridePaymentPresent
    state.credit_card_fee = customerStore.order.credit_card_fee
    state.can_use_credit_card = orderCanUseCreditCard(customerStore.order)
  })
  watch(
    () => customerStore.order,
    (newVal) => {
      state.can_use_credit_card = orderCanUseCreditCard(customerStore.order)
    }
  )

  watch(
    () => props.overridePaymentAmount,
    (newVal, oldVal) => {
      if (newVal > 0) {
        state.payButtonDisabled = false
      }
    }
  )

  watch(
    () => state.addPaymentAmt,
    (newVal, oldVal) => {
      if (newVal > 0) {
        state.payButtonDisabled = false
      } else {
        state.payButtonDisabled = true
      }
    }
  )

  watch(
    () => props.parentState.paymentType,
    (newVal, oldVal) => {
      state.payment_type = newVal
    }
  )
</script>
