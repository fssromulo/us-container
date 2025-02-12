<template>
  <div class="flex flex-wrap justify-center w-full">
    <div class="w-full m-4">
      <label class="font-bold text-900 dark:text-0">Payment Type</label>
    </div>
    <div
      class="field"
      :class="{
        'col-12': state.paymentType == 'CC' && !props.hasTransactionDate
      }"
    >
      <Select
        class="p-component p-inputtext-fluid"
        :loading="state.loading"
        v-model="state.paymentType"
        :options="paymentTypes"
        @click="loadPaymentMethods"
        placeholder="Select a payment type"
        scrollHeight="330px"
        optionLabel="label"
        optionValue="value"
      />
    </div>
    <div class="ml-6 field" v-if="props.hasTransactionDate">
      <label for="state" class="font-medium text-900 dark:text-0"
        >Paid On</label
      >
      <DatePicker
        style="width: 210px"
        showIcon
        showButtonBar
        v-model="state.paid_at"
        dateFormat="mm/dd/y"
        id="paid_on"
        class="p-component p-inputtext-fluid"
      />
    </div>
    <div class="ml-6 field">
      <Textarea
        v-if="state.paymentType != 'CC'"
        v-model="state.notes"
        :autoResize="true"
        rows="2"
        placeholder="Payment Notes"
        label="Notes"
        cols="20"
      />
    </div>
  </div>
</template>
<script setup>
  import { reactive, computed, watch, onMounted } from "vue"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useTransactionTypeStore } from "../../../store/modules/transactionTypeStore"
  import { defaultPaymentTypesDropDown } from "@/utils/paymentTypes"
  import PaymentMethodsApi from "@/api/payment_methods"
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"

  const paymentMethodsApi = new PaymentMethodsApi()
  const customerOrderStore = useCustomerOrder()

  const transactionTypeStore = useTransactionTypeStore()
  let paymentOptions = defaultPaymentTypesDropDown()

  const customerApi = new CustomerApi()
  const toast = useToast()

  const props = defineProps({
    hasTransactionDate: {
      type: Boolean,
      default: false
    },
    orderId: { type: String, default: "" },
    rentalPeriodId: { type: String, default: "" },
    transactionTypeId: { type: String, default: "" },
    canSaveTransactionType: { type: Boolean, default: false },
    transactionTypes: { type: String, default: "" },
    selectedRentPeriodsIds: { type: Array, default: [] },
    excludePaymentTypes: { type: Array, default: [] },
    paymentType: { type: String, default: "Cash" }
  })

  const state = reactive({
    paymentType: props.paymentType,
    loading: false,
    notes: "",
    hasAch: false,
    account_number: "",
    routing_number: "",
    bank_name: "",
    paymentTypes: null,
    can_use_credit_card: false,
    paid_at: new Date()
  })
  //selectedRentPeriodsIds

  const emit = defineEmits(["transactionTypeSaved", "transactionTypeChanged"])
  const paymentTypes = computed(() => {
    if (state.paymentTypes == null) {
      return []
    }
    const filteredTypes = state.paymentTypes.filter(
      (pmtType) => !props.excludePaymentTypes.includes(pmtType.label)
    )
    // state.paymentType = filteredTypes[0].label;
    return filteredTypes
  })
  const saveTransactionType = async () => {
    state.loading = true
    let tType = {
      payment_type: state.paymentType,
      order_id: props.orderId === "" ? null : props.orderId,
      rent_period_id: props.rentalPeriodId === "" ? null : props.rentalPeriodId,
      notes: state.notes
    }
    const { data, error } = await customerApi.addTransactionType(tType)
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Payment means saved successful",
        group: "br",
        life: 2000
      })
    }
    emit("transactionTypeSaved", {})
    state.loading = false
    state.notes = ""
  }

  const saveTransactionTypes = async () => {
    emit("transactionTypeSaved", {})
  }

  watch(
    () => transactionTypeStore.canSaveTransactionType,
    async (newVal, oldVal) => {
      if (newVal) {
        if (
          props.selectedRentPeriodsIds.length > 0 ||
          transactionTypeStore.periodIds.length > 0
        ) {
          await saveTransactionTypes()
        } else {
          await saveTransactionType()
        }
        transactionTypeStore.canSaveTransactionType = false
      }
    }
  )
  watch(
    () => state.paymentType,
    async (newVal) => {
      emit("transactionTypeChanged", {
        paymentType: newVal,
        notes: state.notes,
        bankName: state.bank_name,
        routingNumber: state.routing_number,
        accountNumber: state.account_number,
        paid_at: state.paid_at
      })
    }
  )

  watch(
    () => state.notes,
    async (newVal) => {
      emit("transactionTypeChanged", {
        paymentType: state.paymentType,
        notes: state.notes,
        bankName: state.bank_name,
        routingNumber: state.routing_number,
        accountNumber: state.account_number,
        paid_at: state.paid_at
      })
    }
  )

  watch(
    () => state.notes,
    async (newVal) => {
      emit("transactionTypeChanged", {
        paymentType: state.paymentType,
        notes: newVal,
        bankName: state.bank_name,
        routingNumber: state.routing_number,
        accountNumber: state.account_number,
        paid_at: state.paid_at
      })
    }
  )
  watch(
    () => state.paid_at,
    async (newVal) => {
      emit("transactionTypeChanged", {
        paymentType: state.paymentType,
        notes: state.notes,
        bankName: state.bank_name,
        routingNumber: state.routing_number,
        accountNumber: state.account_number,
        paid_at: state.paid_at
      })
    }
  )
  watch(
    () => customerOrderStore?.order,
    async (newVal) => {
      state.can_use_credit_card = orderCanUseCreditCard(
        customerOrderStore?.order
      )
    }
  )
  const loadPaymentMethods = async () => {
    if (state.paymentTypes == null || state.paymentTypes.length == 0) {
      state.loading = true
      state.paymentType = props.paymentType
      const paymentMethodsData = await paymentMethodsApi.getAllPaymentMethods()
      paymentOptions = paymentMethodsData.data.value
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
      if (state.hasAch) {
        paymentOptions.push({
          value: "Echeck (ACH On File)",
          label: "Echeck (Use ACH On File)"
        })
      }
      state.paymentTypes = paymentOptions
      state.loading = false
    }
  }
  onMounted(async () => {
    const customerProfileId = customerOrderStore?.order?.customer_profile_id
    if (customerProfileId) {
      const { data, error } = await customerApi.getCustomerProfile(
        customerProfileId
      )
      for (var i = 0; i < data?.value?.profile?.paymentProfiles.length; i++) {
        if (
          data?.value?.profile?.paymentProfiles[i].payment?.bankAccount !=
          undefined
        ) {
          state.hasAch = true
          state.routing_number =
            data.value.profile.paymentProfiles[
              i
            ].payment.bankAccount.routingNumber
          state.account_number =
            data.value.profile.paymentProfiles[
              i
            ].payment.bankAccount.accountNumber
          state.bank_name =
            data.value.profile.paymentProfiles[
              i
            ].payment.bankAccount.nameOnAccount
        }
      }
    }
    state.can_use_credit_card = orderCanUseCreditCard(customerOrderStore?.order)
    await loadPaymentMethods()
  })
</script>
