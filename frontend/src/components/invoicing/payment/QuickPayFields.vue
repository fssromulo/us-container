<template>
  <div class="flex flex-wrap justify-center field-checkbox">
    <div
      class="grid grid-cols-12 gap-4 ml-2 p-fluid w-full"
      v-if="props.overridePaymentAmountEditable"
    >
      <div class="col-span-12">
        <label class="font-medium text-900 dark:text-0">Pay Down</label>
      </div>
      <div class="col-span-12 mb-4 field">
        <Select
          class="p-component p-inputtext-fluid"
          v-model="state.paymentOption"
          :options="[
            { label: 'Pay In Full', value: 'Pay all' },
            { label: 'Add Payment', value: 'Partially Paid' }
          ]"
          placeholder="Select an option"
          scrollHeight="330px"
          optionLabel="label"
          optionValue="value"
        />
      </div>
      <div class="col-span-12 flex flex-col items-center">
        <div class="col-span-3 mt-5">
          <label for="rentAmount" class="text-gray-700"
            >Pay down rent balance</label
          >
          <InputNumber
            id="rentAmount"
            v-model="state.rentPaymentAmount"
            :disabled="state.paymentOption == 'Pay all'"
            :max="rentalPeriodsComputed.calculated_rent_period_balance"
            mode="currency"
            currency="USD"
            locale="en-US"
            class="block w-full mt-1"
          />
          <small v-if="state.rentPaymentExceeds" class="text-red-500"
            >Cannot exceed the rent period balance.</small
          >
        </div>
        <div class="col-span-3 mt-5">
          <label for="feeAmount" class="text-gray-700"
            >Pay down fee balance</label
          >
          <InputNumber
            id="feeAmount"
            v-model="state.feePaymentAmount"
            :disabled="state.paymentOption == 'Pay all'"
            :max="rentalPeriodsComputed.calculated_rent_period_fee_balance"
            mode="currency"
            currency="USD"
            locale="en-US"
            class="block w-full mt-1"
          />
          <small v-if="state.feePaymentExceeds" class="text-red-500"
            >Cannot exceed the fee balance.</small
          >
        </div>
        <div class="col-span-3 mt-5">
          <label for="taxAmount" class="text-gray-700"
            >Pay down tax balance</label
          >
          <InputNumber
            id="taxAmount"
            v-model="state.taxPaymentAmount"
            :disabled="state.paymentOption == 'Pay all'"
            :max="rentalPeriodsComputed.calculated_rent_period_tax_balance"
            mode="currency"
            currency="USD"
            locale="en-US"
            class="block w-full mt-1"
          />
        </div>
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
      <div class="col-span-12">
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
        <payment-fields
          :disable-all-fields="props.disableAllFields"
          :override-payment-amount="overridePaymentAmount"
          :selected-rent-periods-ids="props.selectedRentPeriodsIds"
          :is-internal="props.isInternal"
          :rental-after-pay-reset="props.rentalAfterPayReset"
          :send-success-feed-back="true"
          @handleSuccessFeedback="resetAll"
          :applyBankFee="true"
          :bankFee="bankFee"
          :overridePaymentMethod="payDownRentalCreditCardHandler"
          :rent-payment-amount="state.rentPaymentAmount"
          :fee-payment-amount="state.feePaymentAmount"
          :tax-payment-amount="state.taxPaymentAmount"
          :credit-card-selected="isCreditCardPayment"
        />
      </div>
    </div>
    <div class="grid grid-cols-12 gap-4" v-else>
      <div class="col-span-12">
        <add-rent-payment
          :has-payment="true"
          :order_id="props.orderId"
          :override-payment-amount="overridePaymentAmount"
          :rent-period-ids="state.selectedRentPeriodsIds"
          :reset-function="resetAll"
          :has-ach="state.hasAch"
          :routing-number="state.routingNumber"
          :account-number="state.accountNumber"
          :payment-type="state.paymentType"
          :bank-name="state.bankName"
          :paymentOption="state.paymentOption"
          :rent-payment-amount="state.rentPaymentAmount"
          :parentState="state"
          :fee-payment-amount="state.feePaymentAmount"
          :tax-payment-amount="state.taxPaymentAmount"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { onMounted, reactive, defineProps, computed, inject } from "vue"
  // import VueHtmlToPaper from 'vue-html-to-paper';
  import CustomerApi from "@/api/customers"
  import TransactionType from "./TransactionType.vue"
  import PaymentFields from "./PaymentFields.vue"
  import AddRentPayment from "./AddRentPayment.vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import Cart from "@/service/Cart.js"
  import { useTransactionTypeStore } from "@/store/modules/transactionTypeStore"
  import CustomerService from "@/service/Customers"
  import { watch } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import { useToast } from "primevue/usetoast"
  import { DateTime } from "luxon"
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"
  import { reset } from "@formkit/vue"
  import { roundHalfUp } from "@/utils/formatCurrency.js"

  const transactionTypeStore = useTransactionTypeStore()
  const $fc = inject("$formatCurrency")
  const toast = useToast()

  const cart = new Cart()
  const customerOrderStore = useCustomerOrder()
  const customerStore = useCustomerOrder()
  const usersStore = useUsers()
  const customerApi = new CustomerApi()
  const customerService = new CustomerService()

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
    order: {
      type: Object,
      default: {}
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
    paymentOption: "Pay all",
    order: {},
    transaction_paid_at: null,
    togglePaydown: false,
    useCreditCard: false,
    rentPaymentAmount: 0,
    feePaymentAmount: 0,
    taxPaymentAmount: 0,
    transactionTypeId: "",
    payment: "Paid",
    can_use_credit_card: false,
    transaction_paid_at: null
  })
  const calculatedBalance = computed(() => {
    if (state.paymentOption == "Pay all") {
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
    } else if (state.paymentOption == "Total Balance") {
      if (state.order.calculated_paid_thru === "NOT APPLICABLE")
        return state.order.rent_periods[0]
          ?.calculated_rent_period_balance_with_tax
      return state.order.rent_periods
        ?.filter((period) => {
          return period.calculated_rent_period_balance > 0
        })
        .map((period) => period.calculated_rent_period_balance_with_tax)
        .reduce((acc, currentValue) => acc + currentValue, 0)
    } else {
      //calculated_rent_period_fee_balance
      return state.order.rent_periods
        ?.filter((period) => {
          return period.calculated_rent_period_fee_balance > 0
        })
        .map((period) => period.calculated_rent_period_fee_balance_with_tax)
        .reduce((acc, currentValue) => acc + currentValue, 0)
      return 1
    }
  })
  const rentalPeriodsComputed = computed(() => {
    return props.order.rent_periods
      .filter((period) => {
        if (period.calculated_rent_period_total_balance !== 0) {
          return true
        }
        return false
      })
      .map((period) => {
        return {
          calculated_rent_period_balance: period.calculated_rent_period_balance,
          calculated_rent_period_fee_balance:
            period.calculated_rent_period_fee_balance,
          calculated_rent_period_tax_balance: period.calculated_rent_period_tax
        }
      })
      .reduce(
        (acc, period) => {
          acc.calculated_rent_period_balance +=
            period.calculated_rent_period_balance
          acc.calculated_rent_period_fee_balance +=
            period.calculated_rent_period_fee_balance
          acc.calculated_rent_period_tax_balance +=
            period.calculated_rent_period_tax_balance
          return acc
        },
        {
          calculated_rent_period_balance: 0,
          calculated_rent_period_fee_balance: 0,
          calculated_rent_period_tax_balance: 0
        }
      )
  })

  const overridePaymentAmount = computed(() => {
    let amount =
      state.rentPaymentAmount + state.feePaymentAmount + state.taxPaymentAmount

    return amount
  })

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
  }
  const loadOrder = () => {
    let order = customerService.orderDto()
    state.originalOrder = cloneDeep(order)
    state.order = cloneDeep(order)
    state.order.customer_application_schema_id =
      state.order?.customer_application_schema?.id || null
  }

  onMounted(async () => {
    transactionTypeStore.setCanSaveTransactionType(false)
    state.paymentType = props.paymentType
    state.overridePaymentAmount = props.overridePaymentAmount
    loadOrder()
    const { data, error } = await customerApi.get_tax_rate(
      customerStore.order.id
    )
    state.tax_rate = data.value
    resetRentPeriod()
    state.can_use_credit_card = orderCanUseCreditCard(state.order)
  })
  const calculateRentTotal = () => {
    const { rent_periods, calculated_monthly_subtotal } = props.order

    let calculated_rent
    if (rent_periods.length >= 2) {
      calculated_rent = rent_periods[1].calculated_rent_period_tax
    } else {
      calculated_rent =
        rent_periods[0]?.calculated_rent_period_tax_without_downpayment || 0
    }

    return calculated_rent + calculated_monthly_subtotal
  }

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

  const resetRentPeriod = () => {
    let rentPeriod = rentalPeriodsComputed.value
    state.originalRentPeriod = rentPeriod
    state.rentPaymentAmount = rentPeriod.calculated_rent_period_balance || 0
    state.feePaymentAmount = rentPeriod.calculated_rent_period_fee_balance || 0
    state.taxPaymentAmount = rentPeriod.calculated_rent_period_tax_balance || 0
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

  const payDownRentalCreditCardHandler = async (paymentObj) => {
    const otherPaymentObj = {
      lump_sum_amount: overridePaymentAmount.value,
      rent_period_paid_amt: state.rentPaymentAmount,
      rent_period_fee_paid_amt: state.feePaymentAmount,
      rent_period_tax_paid_amt: state.taxPaymentAmount,
      payment_option: props.paymentOption,
      order_id: customerStore.order.id,
      payment_type: "CC",
      transaction_created_at: state.transaction_paid_at
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
                  compareWithRentPeriodMap[key]
                    .calculated_rent_period_total_balance
              );
            }
          });

          transactionTypeStore.setPeriodIds(changed_periods_ids);
          transactionTypeStore.setAmount(amount);
          */
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
  watch(
    () => calculatedBalance.value,
    (newVal) => {
      state.overridePaymentAmount = calculatedBalance.value
    },
    { immediate: true, deep: true }
  )
  watch(
    () => state.order,
    (newVal, oldVal) => {
      state.can_use_credit_card = orderCanUseCreditCard(state.order)
    }
  )

  const resetRentPeriodTax = () => {
    const rentPeriod = rentalPeriodsComputed.value
    let rental_tax_paid = state.rentPaymentAmount * state.tax_rate
    let max_rental_tax_paid =
      rentPeriod.calculated_rent_period_balance * state.tax_rate
    let max_tax = rentPeriod.calculated_rent_period_tax_balance
    let max_tax_remaining_for_fees = max_tax - max_rental_tax_paid
    let max_tax_fees_paid = Math.min(
      state.feePaymentAmount * state.tax_rate,
      max_tax_remaining_for_fees
    )
    state.taxPaymentAmount = roundHalfUp(rental_tax_paid + max_tax_fees_paid)
    if (Math.abs(state.taxPaymentAmount - max_tax) <= 0.02) {
      state.taxPaymentAmount = max_tax
    }
  }

  watch(
    () => state.rentPaymentAmount,
    (newVal, oldVal) => {
      resetRentPeriodTax()
    }
  )

  watch(
    () => state.feePaymentAmount,
    (newVal, oldVal) => {
      resetRentPeriodTax()
    }
  )
</script>
