<template>
  <div class="flex flex-wrap justify-center field-checkbox">
    <div
      class="grid grid-cols-12 gap-4 ml-2 p-fluid"
      v-if="props.overridePaymentAmountEditable"
    >
      <div class="col-span-12">
        <label for="partialPay" class="font-medium text-900 dark:text-0"
          >Enter Amount To Pay (Rental Balance:
          {{ $fc(props.overridePaymentAmount) }})</label
        >
      </div>
      <div class="col-span-12 field">
        <InputNumber
          :placeholder="0"
          mode="currency"
          style="width: 60%"
          currency="USD"
          id="partialPay"
          v-model="state.overridePaymentAmount"
          type="text"
        />
      </div>
    </div>
  </div>
  <div class="col-span-12 text-center">
    <TransactionType
      :rentalPeriodId="state.rentPeriodId"
      :transactionTypeId="state.transactionTypeId"
      :excludePaymentTypes="['CC']"
      :canSaveTransactionType="state.paymentCompleted"
      :selectedRentPeriodsIds="props.selectedRentPeriodsIds"
      @transactionTypeChanged="transactionTypeChanged"
      @transactionTypeSaved="handleTransactionTypeSaved"
      :paymentType="state.paymentType"
    />
    <div
      class="grid grid-cols-12 gap-4"
      v-if="isCreditCardPayment && state.can_use_credit_card"
    >
      <div class="col-span-12 card">
        <payment-fields
          :disable-all-fields="props.disableAllFields"
          :override-payment-amount="state.overridePaymentAmount"
          :selected-rent-periods-ids="props.selectedRentPeriodsIds"
          :is-internal="props.isInternal"
          :rental-after-pay-reset="props.rentalAfterPayReset"
          :send-success-feed-back="true"
          @handleSuccessFeedback="resetAll"
          :applyBankFee="true"
          :bankFee="bankFee"
          :credit-card-selected="isCreditCardPayment"
          :showTransactionCreatedAt="true"
        />
      </div>
    </div>
    <div class="grid grid-cols-12 gap-4" v-else>
      <div class="col-span-12 card">
        <add-rent-payment
          :has-payment="true"
          :order_id="props.orderId"
          :override-payment-amount="state.overridePaymentAmount"
          :rent-period-ids="props.selectedRentPeriodsIds"
          :reset-function="resetAll"
          :has-ach="state.hasAch"
          :routing-number="state.routingNumber"
          :account-number="state.accountNumber"
          :parentState="state"
          :payment-type="state.paymentType"
          :bank-name="state.bankName"
          :notes="state.notes"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import {
    onMounted,
    reactive,
    defineProps,
    computed,
    inject,
    watch
  } from "vue"
  // import VueHtmlToPaper from 'vue-html-to-paper';
  import TransactionType from "./TransactionType.vue"
  import PaymentFields from "./PaymentFields.vue"
  import AddRentPayment from "./AddRentPayment.vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import Cart from "@/service/Cart.js"
  import { useTransactionTypeStore } from "@/store/modules/transactionTypeStore"
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"

  const transactionTypeStore = useTransactionTypeStore()
  const $fc = inject("$formatCurrency")

  const cart = new Cart()
  const customerOrderStore = useCustomerOrder()
  const usersStore = useUsers()

  const props = defineProps({
    paymentType: {
      type: String,
      default: "CC"
    },
    hasAch: {
      type: Boolean,
      default: false
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
    disableAllFields: {
      type: Boolean,
      default: true
    },
    overridePaymentAmount: {
      type: Number,
      default: 0
    },
    overridePaymentAmountEditable: {
      type: Boolean,
      default: false
    },
    selectedRentPeriodsIds: {
      type: Array,
      default: []
    },
    creditCardFeeToggleEnabled: {
      type: Boolean,
      default: false
    },
    isUpdateCreditCard: {
      type: Boolean,
      default: false
    },
    rentPaymentAmount: {
      type: Number,
      default: 0
    },
    feePaymentAmount: {
      type: Number,
      default: 0
    },
    rentalAfterPayReset: {
      type: Function,
      default: () => {}
    },
    isInternal: {
      type: Boolean,
      default: false
    },
    resetOrder: {
      type: Function,
      default: {}
    },
    orderId: {
      type: String,
      default: ""
    }
  })
  const state = reactive({
    rentPeriodId: "",
    transactionTypeId: "",
    paymentCompleted: false,
    paymentType: props.paymentType,
    hasAch: props.hasAch,
    accountNumber: "",
    routingNumber: "",
    bankName: "",
    overridePaymentAmount: 0,
    notes: "",
    can_use_credit_card: false,
    transaction_paid_at: null
  })

  watch(
    () => customerOrderStore.order,
    (newVal, oldVal) => {
      state.can_use_credit_card = orderCanUseCreditCard(
        customerOrderStore.order
      )
    }
  )

  const isCreditCardPayment = computed(() => {
    return state.paymentType === "CC"
  })
  const transactionTypeChanged = (transactionType) => {
    state.paymentType = transactionType.paymentType
    if (transactionType.paymentType === "Echeck (ACH On File)") {
      state.bankName = transactionType.bankName
      state.routingNumber = transactionType.routingNumber
      state.accountNumber = transactionType.accountNumber
      state.hasAch = true
    } else {
      state.hasAch = false
    }
    state.notes = transactionType.notes
  }

  onMounted(async () => {
    transactionTypeStore.setCanSaveTransactionType(false)
    state.paymentType = props.paymentType
    state.overridePaymentAmount = props.overridePaymentAmount
    state.can_use_credit_card = orderCanUseCreditCard(customerOrderStore.order)
  })

  const handleSaveTransactionType = async () => {
    state.paymentCompleted = true
    transactionTypeStore.canSaveTransactionType = true
  }
  const handleTransactionTypeSaved = async () => {
    transactionTypeStore.canSaveTransactionType = false
    state.paymentCompleted = false
    await props.resetOrder(true)
  }

  const resetAll = async () => {
    handleSaveTransactionType()
    // resetRentPeriod();
  }

  const bankFee = computed(() => {
    let cms = customerOrderStore.publicCms || usersStore.cms
    let bankFees = 0
    if (customerOrderStore.order.type === "RENT") {
      const rent_periods = customerOrderStore.order.rent_periods.filter(
        (item) => props.selectedRentPeriodsIds.includes(item.id)
      )
      if (props.overridePaymentAmount && state.overridePaymentAmount) {
        bankFees = cart.roundIt(
          cms.convenience_fee_rate * state.overridePaymentAmount,
          2
        )
      } else {
        bankFees = cart.roundIt(
          rent_periods.reduce(
            (accumulator, crt) =>
              accumulator + crt["calculated_rent_period_total_balance"],
            0
          ) * cms.convenience_fee_rate,
          2
        )
      }
    }
    return bankFees
  })
</script>
