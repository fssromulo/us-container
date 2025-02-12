<template>
  <div>
    <ul
      class="flex p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900"
    >
      <template :key="idx" v-for="(name, idx) in rentPeriodTabs">
        <li class="pr-4">
          <a
            v-ripple
            class="flex items-center px-6 py-4 transition-colors duration-150 cursor-pointer hover:bg-100 dark:hover:bg-700 rounded-border p-ripple"
            :class="{
              'border-blue-600 text-blue-600 hover:border-blue-600':
                state.activeTab === name.value,
              'text-700 dark:text-100': state.activeTab !== name.value
            }"
            @click="state.activeTab = name.value"
          >
            <span class="text-2xl font-medium">{{ name.name }}</span>
          </a>
        </li>
        <li class="flex items-center">
          <div style="width: 1px; height: 50%" class="border border-r"></div>
        </li>
      </template>
    </ul>
  </div>
  <!-- Payment Details -->
  <div
    class="grid grid-cols-1 grid-cols-12 gap-4 my-4"
    v-if="state.activeTab === 'over_view'"
    style="height: 32vh"
  >
    <div class="col-span-12">
      <strong>Period Amount</strong>
      <DataTable
        :value="[
          {
            rent_amount: state.rentPeriod.display_amount_owed,
            r_amount: state.rentPeriod.calculated_rent_period_balance,
            id: state.rentPeriod.id,
            r_fee_balance: state.rentPeriod.display_calculated_rent_period_fees,
            c_r_period_tax: state.rentPeriod.display_calculated_rent_period_tax,
            r_period_tax: state.rentPeriod.calculated_rent_period_tax,
            total: state.rentPeriod.display_total,
            status: state.rentPeriod.status
          }
        ]"
      >
        <Column field="rent_amount" header="Rent">
          <template #body="slotProps">
            <InputNumber
              id="rentAmount"
              v-model="state.rentPaymentAmountEdit"
              v-if="state.isEditingAmt && state.editingId === slotProps.data.id"
              :disabled="state.isLoading"
              mode="currency"
              currency="USD"
              locale="en-US"
              class="block w-1/2"
            />
            <span v-else>{{ slotProps.data.rent_amount }}</span>
            <Message
              v-if="state.isEditingAmt && state.editingId === slotProps.data.id"
              severity="info"
              >Note: Adjusting the rent period amount will NOT adjust the tax
              amount</Message
            >
          </template>
        </Column>
        <Column field="r_fee_balance" header="Fee"></Column>
        <Column field="c_r_period_tax" header="Tax">
          <template #body="slotProps">
            <InputNumber
              id="taxAmount"
              v-model="state.taxPaymentAmountEdited"
              v-if="state.isEditingAmt && state.editingId === slotProps.data.id"
              mode="currency"
              currency="USD"
              locale="en-US"
              :disabled="state.isLoading"
              class="block w-1/2"
            />
            <span v-else>{{ slotProps.data.c_r_period_tax }}</span>
          </template>
        </Column>
        <Column field="total" header="Total"></Column>
        <Column field="status" header="Status"></Column>
        <Column header="Edit">
          <template #body="slotProps">
            <Button
              class="p-button-raised p-button-secondary"
              icon="pi pi-save"
              @click="handleRentPeriodUpdate"
              :loading="state.isLoading"
              v-if="state.isEditingAmt && state.editingId === slotProps.data.id"
            />
            <Button
              @click="
                editMonthlyAmt(
                  slotProps.data.id,
                  slotProps.data.r_amount,
                  slotProps.data.r_period_tax
                )
              "
              class="p-button-raised p-button-secondary"
              icon="pi pi-pencil"
              :loading="state.isLoading"
              v-else
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="col-12">
      <strong class="ml-3">Transactions</strong>
      <ViewTransactionType
        :resetFunction="props.resetOrder"
        :rentPeriodId="state.rentPeriod.id"
        :orderId="order_id"
      />
    </div>
  </div>

  <div
    class="grid grid-cols-12 gap-4 my-3"
    style="height: 32vh"
    v-if="state.activeTab === 'fees'"
  >
    <div class="col-span-12 mt-4">
      <div>
        <order-alterations
          :itemsProp="state.rentPeriod.rent_period_fees"
          amountFieldName="fee_amount"
          categoryFieldName="type"
          categoryFieldName2="id"
          placeholderText="Select a fee type"
          :handleDeleteClickFunc="handleDeleteFeeClick"
          :closeConfirmationToastFunc="closeConfirmationToast"
          :freshDictAorAdd="freshFeeDict"
          addButtonText="Add Fee(s)"
          :isLoading="state.isLoading"
          :handleAddItemSaveClickFunc="handleAddFeeSaveClick"
          :showConfirmToast="showConfirmToast"
          :headingName="headersDict.rentPeriodFee"
        />
      </div>
      <div class="grid justify-center grid-cols-12 gap-2 d-flex">
        <div class="col-span-4">
          <Button
            @click="toggleEdit"
            label="Cancel"
            class="p-button-raised p-button-secondary"
          />
        </div>
        <Button
          :disabled="isRentPeriodSame"
          @click="saveRentPeriod"
          :loading="state.isLoading"
          class="col-span-4 p-button-raised"
          label="Save"
        />
        <Button
          @click="waiveAllFees"
          :loading="state.isLoading"
          class="col-span-4 p-button-raised"
          label="Waive all fees"
        />
      </div>
    </div>
  </div>

  <div
    class="col-span-12 mt-4"
    style="height: 32vh"
    v-if="state.activeTab === 'edit_dates'"
  >
    <div class="flex items-center mb-4">
      <label class="w-24">Start date</label>
      <DatePicker
        class="ml-4 p-input-large"
        v-model="state.startDate"
        style="width: 150px"
        dateFormat="m/d/yy"
        fluid
      />
    </div>

    <div class="flex items-center mb-4">
      <label class="w-24">End date</label>
      <DatePicker
        class="ml-4 p-input-large"
        v-model="state.endDate"
        style="width: 150px"
        dateFormat="m/d/yy"
        fluid
      />
    </div>

    <Button
      @click="editDates"
      :loading="state.isLoading"
      class="col-span-4 p-button-raised"
      label="Edit Dates"
    />

    <p class="w-full mt-4 text-red-600">
      Warning: Editing rental period dates that overlap with other periods could
      cause issues with double payments. Double check your dates before saving!
    </p>
  </div>

  <div
    class="col-span-12 mt-4"
    style="height: 32vh"
    v-if="
      (applicationAccepted ||
        (customerStore.order?.applications_overridden &&
          customerStore.order?.applications_overridden.find(
            (item) => item.name === 'rent'
          )?.overridden)) &&
      state.rentPeriod.status !== 'Paid' &&
      state.activeTab === 'pay_down'
    "
  >
    <div class="grid grid-cols-12 gap-4 mt-8">
      <div class="col-span-3 mt-8 ml-2 mr-6">
        <!-- Payment Amount Inputs -->
        <Select
          class="text-xl"
          v-model="state.payment"
          :options="[
            { label: 'Pay In Full', value: 'Paid' },
            { label: 'Add Payment', value: 'Partially Paid' }
          ]"
          placeholder="Select an option"
          optionLabel="label"
          optionValue="value"
        />
      </div>

      <div class="col-span-3 ml-2">
        <!-- Payment Amount Inputs -->
        <label for="rentAmount" class="text-gray-700"
          >Pay down rent balance</label
        >
        <InputNumber
          id="rentAmount"
          v-model="state.rentPaymentAmount"
          :disabled="state.payment == 'Paid'"
          :max="state.rentPeriod.calculated_rent_period_balance"
          mode="currency"
          currency="USD"
          locale="en-US"
          class="block w-full mt-1"
        />
        <small v-if="state.rentPaymentExceeds" class="text-red-500"
          >Cannot exceed the rent period balance.</small
        >
      </div>

      <div class="col-span-3 ml-6">
        <label for="feeAmount" class="text-gray-700"
          >Pay down fee balance</label
        >
        <InputNumber
          id="feeAmount"
          v-model="state.feePaymentAmount"
          :disabled="state.payment == 'Paid'"
          :max="state.rentPeriod.calculated_rent_period_fee_balance"
          mode="currency"
          currency="USD"
          locale="en-US"
          class="block w-full mt-1"
        />
        <small v-if="state.feePaymentExceeds" class="text-red-500"
          >Cannot exceed the fee balance.</small
        >
      </div>

      <div class="col-span-3 ml-6">
        <label for="taxAmount" class="text-gray-700"
          >Pay down tax balance</label
        >
        <InputNumber
          id="taxAmount"
          v-model="state.taxPaymentAmount"
          :disabled="state.payment == 'Paid'"
          :max="state.rentPeriod.calculated_rent_period_tax_balance"
          mode="currency"
          currency="USD"
          locale="en-US"
          class="block w-full mt-1"
        />
      </div>
    </div>
    <div
      class="grid grid-cols-12 gap-4"
      v-if="state.useCreditCard && state.can_use_credit_card"
    >
      <div class="col-span-12 card">
        <payment-fields
          :disable-all-fields="overridePaymentAmount == 0"
          :override-payment-amount="overridePaymentAmount"
          :selected-rent-periods-ids="[state.rentPeriod.id]"
          :is-internal="state.isInternal"
          :rent-payment-amount="state.rentPaymentAmount"
          :fee-payment-amount="state.feePaymentAmount"
          :tax-payment-amount="state.taxPaymentAmount"
          :rental-after-pay-reset="resetAll"
          :send-success-feed-back="true"
          :creditCardFeeToggleEnabled="creditCardFeeToggleEnabled"
          :applyBankFee="true"
          :bankFee="bankFee"
          @handleSuccessFeedback="handleSaveTransactionType"
          :showTransactionCreatedAt="true"
        />
      </div>
    </div>
    <div class="" v-else>
      <add-rent-payment
        :order_id="props.order_id"
        :override-payment-amount="overridePaymentAmount"
        :rent-payment-amount="state.rentPaymentAmount"
        :fee-payment-amount="state.feePaymentAmount"
        :tax-payment-amount="state.taxPaymentAmount"
        :rent-period-ids="[state.rentPeriod.id]"
        :reset-function="resetAll"
      />
    </div>
  </div>
  <!-- <div class="col-span-12 mt-4" v-else-if="(!applicationAccepted &&
        !customerStore.order?.override_application_process)">
  Must ovveride or receive application to pay down
</div> -->
  <Toast position="bottom-center" group="bc" :visible.sync="state.showToast">
    <template #message="slotProps">
      <div class="flex flex-col items-center" style="flex: 1">
        <div class="text-center">
          <i class="pi pi-exclamation-triangle" style="font-size: 3rem"></i>
          <div class="my-4 text-xl font-bold">
            {{ slotProps.message.summary }}
          </div>
        </div>
        <div class="flex gap-2">
          <Button
            severity="success"
            label="Yes"
            :loading="state.isLoading"
            @click="state.toastConfirmAction"
          ></Button>
          <Button
            severity="secondary"
            label="No"
            @click="state.toastCancelAction"
          ></Button>
        </div>
      </div>
    </template>
  </Toast>
</template>

<script setup>
  import { onMounted, reactive, computed, inject } from "vue"
  import PaymentFields from "./payment/PaymentFields.vue"
  import AddRentPayment from "./payment/AddRentPayment.vue"
  import OrderAlterations from "./OrderAlterations.vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"
  import cloneDeep from "lodash.clonedeep"
  import isEqual from "lodash.isequal"
  import { watch } from "vue"
  import { useUsers } from "@/store/modules/users"
  import Cart from "@/service/Cart.js"
  import { roundHalfUp } from "@/utils/formatCurrency.js"

  const cart = new Cart()
  const usersStore = useUsers()

  const emit = defineEmits(["onPayDown"])

  const customerStore = useCustomerOrder()
  const toast = useToast()
  const $removeUnusedProps = inject("$removeUnusedProps")
  import TransactionType from "./payment/TransactionType.vue"
  import ViewTransactionType from "./payment/ViewTransactionType.vue"
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"

  const customerApi = new CustomerApi()

  const props = defineProps({
    hasAch: {
      type: Boolean,
      default: false
    },
    resetRentPeriod: {
      type: Boolean,
      default: false
    },
    applicationAccepted: {
      type: Boolean,
      default: false
    },
    rentPeriod: {
      type: Object,
      default: () => ({})
    },
    order_id: {
      type: String,
      default: ""
    },
    resetOrder: {
      type: Function,
      default: () => {}
    }
  })

  const rentPeriodFeeHeader = "Rent Period Fees"

  const headersDict = {
    rentPeriodFee: rentPeriodFeeHeader
  }

  const rentPeriodTabs = computed(() => {
    let tabs = [
      { name: "Overview", value: "over_view" },
      { name: "Fees", value: "fees" }

      // {name: "Transactions", value: "transactions"}
    ]

    if (props.rentPeriod.calculated_rent_period_total_balance != 0) {
      tabs.push({ name: "Pay Down", value: "pay_down" })
    }

    tabs.push({ name: "Edit Dates", value: "edit_dates" })
    return tabs
  })

  const waiveAllFees = async () => {
    state.loading = true
    let data_request = {
      rent_periods: [props.rentPeriod]
    }
    const { data, error } = await customerApi.waiveAllFees(data_request)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed waving all fees.",
        group: "br",
        life: 5000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Successfully waived all fees.",
        group: "br",
        life: 5000
      })
      // state.rentPeriod.rent_period_fees=[]
      props.resetOrder(true)
    }
    emit("onPayDown")
    state.loading = false
  }

  const freshFeeDict = {
    // Set the 'fee_amount' property to 'null'
    fee_amount: 0,
    // Set the 'fee_type' property to 'null'
    fee_type: null
  }

  const toggleEdit = () => {
    state.isEditing = !state.isEditing
    for (let key in headersDict) {
      customerStore.setAddedOrderItems(headersDict[key], [])
    }
  }

  const hideConfirmToast = (group) => {
    toast.removeGroup(group)
  }

  const editDates = async () => {
    state.loading = true
    let request = {
      start_date:
        typeof state.startDate === "string"
          ? new Date(state.startDate).toISOString()
          : state.startDate.toISOString(),
      end_date:
        typeof state.endDate === "string"
          ? new Date(state.endDate).toISOString()
          : state.endDate.toISOString()
    }
    const { data, error } = await customerApi.update_rent_period_dates(
      request,
      state.rentPeriod.id
    )
    state.loading = false
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed updating rent period dates.",
        life: 3000,
        group: "br"
      })
      return
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: `Successfully updated rent period dates.`,
        life: 3000,
        group: "br"
      })
      await props.resetOrder(true)
    }
  }

  /**
   * Simply hiding the toast popup message
   */
  const closeConfirmationToast = () => {
    hideConfirmToast("bc")
  }

  /**
   * This is a reusable function where you can create a popup toast notification where you also can pass it the yes and no functions
   * Anyone can call this function and then pass their custom confirm and cancel functions
   * @param {funciton} confirmFunction this function will be attached to the yes button for the popup
   * @param {function} cancelfunction this funtion will be attached to the no button for the popup
   */
  const showConfirmToast = (confirmFunction, cancelfunction) => {
    toast.add({
      severity: "warn",
      summary: "Are you sure?",
      detail: "Proceed to confirm",
      group: "bc"
    })
    state.toastConfirmAction = confirmFunction
    state.toastCancelAction = cancelfunction
  }

  const overridePaymentAmount = computed(() => {
    let amount =
      state.rentPaymentAmount + state.feePaymentAmount + state.taxPaymentAmount

    return amount
  })

  const bankFee = computed(() => {
    let cms = usersStore?.cms

    let bankFees = cart.roundIt(
      props.rentPeriod.calculated_rent_period_total_balance *
        cms.convenience_fee_rate,
      2
    )

    return bankFees
  })

  const resetAll = async () => {
    state.activeTab = "overview"
    emit("onPayDown")
    await props.resetOrder(true)
    resetRentPeriod()
  }

  const cleanUp = async () => {
    await resetAll()
    state.isLoading = false
  }

  /**
   * This function is used to delete a certain fee. This has error and success handling
   * via toast messages. Finally it will close the confirmation toast popup, and then reload the
   * screen for the user with all the new information
   * @param {string} fee_id This is the given id of the fee that will be deleted
   */
  const handleDeleteFeeClick = (fee_id) => {
    if (state.rentPeriod.transaction_type_rent_period.length > 0) {
      toast.add({
        severity: "error",
        summary: "Cannot add fees when there are transactions.",
        detail: "Please delete transaction before adding fees.",
        life: 3000,
        group: "br"
      })
      return
    }
    state.isLoading = true
    customerApi
      .deleteRentPeriodFee(fee_id)
      .then((response) => {
        if (response.error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: response.error.value.response.data.detail,
            life: 3000,
            group: "br"
          })
          return
        }
        toast.add({
          severity: "success",
          summary: "Success",
          detail: `Successfully deleted`,
          life: 3000,
          group: "br"
        })
      })
      .finally(() => {
        cleanUp()
        closeConfirmationToast()
      })
  }

  const handleAddFeeSaveClick = () => {
    if (state.rentPeriod.transaction_type_rent_period.length > 0) {
      toast.add({
        severity: "error",
        summary: "Cannot add fees when there are transactions.",
        detail: "Please delete transaction before adding fees.",
        life: 3000,
        group: "br"
      })
      return
    }
    state.isLoading = true
    const transformFee = (item) => {
      console.log(item)
      return {
        fee_type: "LATE", // Set a default value if cost_type is null
        type_id: item.type || "string", // Set a default value if cost_type is null
        fee_amount: item.fee_amount || 0, // Set a default value if amount is null
        rent_period_id: state.rentPeriod.id
      }
    }

    // Transform each item in addedMiscCosts array
    const transformedFees =
      customerStore.addedOrderItems[rentPeriodFeeHeader].map(transformFee)

    customerApi
      .createRentPeriodFee(transformedFees)
      .then((response) => {
        if (response.error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: response.error.value.response.data.detail,
            life: 3000,
            group: "br"
          })
          return
        }

        toast.add({
          severity: "success",
          summary: "Success",
          detail: `Successfully added ${customerStore.addedOrderItems[rentPeriodFeeHeader]?.length} Fee(s)`,
          life: 3000,
          group: "br"
        })
      })
      .finally(() => {
        // cleanup and look to the orderdetail to do it
        cleanUp()
        customerStore.setAddedOrderItems(rentPeriodFeeHeader, []) // resets the to-be-added fields
      })
  }
  const editMonthlyAmt = (id, rentPeriodAmt, rentPeriodTax) => {
    if (!hasPeriodTransactions.value) {
      state.editingId = id
      state.isEditingAmt = !state.isEditingAmt
      state.rentPaymentAmountEdit = rentPeriodAmt
      state.taxPaymentAmountEdited = rentPeriodTax
    } else {
      toast.add({
        severity: "error",
        summary: "Cannot edit rent amount when there are transactions",
        detail: "Please delete transaction before changing rent period pricing",
        life: 3000,
        group: "br"
      })
    }
  }
  const handleRentPeriodUpdate = async () => {
    state.isLoading = true
    state.rentPeriod.amount_owed = state.rentPaymentAmountEdit
    state.rentPeriod.calculated_rent_period_tax = state.taxPaymentAmountEdited
    state.isEditingAmt = false
    await handleRentPeriodInfoUpdate()
    cleanUp()
  }
  const handleRentPeriodBalanceChange = () => {
    state.rentPeriod.calculated_rent_period_tax =
      state.originalRentPeriod.calculated_rent_period_tax
  }

  const handleRentPeriodCalculatedRentPeriodTax = () => {
    state.rentPeriod.calculated_rent_period_tax =
      state.originalRentPeriod.calculated_rent_period_tax
  }

  const isRentPeriodSame = computed(() => {
    let isRentPeriodSame = isEqual(state.rentPeriod, state.originalRentPeriod)
    return isRentPeriodSame
  })

  const handleRentPeriodFees = async () => {
    const rentPeriodFeeRequestData = $removeUnusedProps(
      state.rentPeriod.rent_period_fees,
      state.originalRentPeriod.rent_period_fees
    )

    // iterating over the feeRequestData to see if we have any differences btwn the amounts of the original and new

    let rentPeriodFeeAmtIddict = {} // this dict will include all of the ids for the fees with altered amounts. the value
    // will equal whether its been altered or not
    for (let i = 0; i < state.rentPeriod.rent_period_fees.length; i++) {
      let diff = rentPeriodFeeRequestData
      let newAmt = state.rentPeriod.rent_period_fees[i].fee_amount
      let originalAmt = state.originalRentPeriod.rent_period_fees[i].fee_amount
      if (Object.keys(diff).length !== 0) {
        // if the fee amounts do not line up, then we will add the id into the list so that we can check it later
        if (newAmt !== originalAmt) {
          rentPeriodFeeAmtIddict[state.rentPeriod.rent_period_fees[i].id] = {
            order_balance_change: newAmt - originalAmt
          }
        } else {
          rentPeriodFeeAmtIddict[state.rentPeriod.rent_period_fees[i].id] = {
            order_balance_change: 0
          }
        }
      }
    }

    // converting object into an array so that it can fit the reqs of the api route
    let rentPeriodFeeRequestDataArray = []
    console.log(rentPeriodFeeRequestData)
    rentPeriodFeeRequestDataArray = Object.values(rentPeriodFeeRequestData).map(
      (fee) => ({
        id: fee.id,
        fee_amount: fee.fee_amount,
        type_id: fee.type.id,
        rent_period_fee_balance_change:
          rentPeriodFeeAmtIddict[fee.id].order_balance_change,
        rent_period_id: state.rentPeriod.id
      })
    )
    console.log(rentPeriodFeeRequestDataArray)
    if (rentPeriodFeeRequestDataArray.length !== 0) {
      let response = await customerApi.updateRentPeriodFees(
        rentPeriodFeeRequestDataArray
      )
      if (response.error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: response.error.value.message,
          life: 3000,
          group: "br"
        })
        state.isLoading = false
        resetRentPeriod()
        return
      } else {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Fee(s) updated",
          group: "br",
          life: 2000
        })
      }
    }
  }

  const creditCardFeeToggleEnabled = computed(() => {
    return usersStore?.cms?.credit_card_fees.enable_toggle_credit_card_fees
  })

  const handleRentPeriodInfoUpdate = async () => {
    let updateRentPeriodInfoData = {
      rent_period_id: state.rentPeriod.id
    }

    const isRentPeriodBalanceChange = !isEqual(
      state.rentPeriod.calculated_rent_period_balance,
      state.originalRentPeriod.calculated_rent_period_balance
    )
    const isRentPeriodTaxChange = !isEqual(
      state.rentPeriod.calculated_rent_period_tax,
      state.originalRentPeriod.calculated_rent_period_tax
    )
    const isRentPeriodAmountOwedChange = !isEqual(
      state.rentPeriod.amount_owed,
      state.originalRentPeriod.amount_owed
    )

    if (isRentPeriodBalanceChange) {
      updateRentPeriodInfoData["balance_amt"] =
        state.rentPeriod.calculated_rent_period_balance
    }

    if (isRentPeriodTaxChange) {
      updateRentPeriodInfoData["tax_amt"] =
        state.rentPeriod.calculated_rent_period_tax
    }

    if (isRentPeriodAmountOwedChange) {
      updateRentPeriodInfoData["amount_owed"] = state.rentPeriod.amount_owed
    }

    if (
      isRentPeriodBalanceChange ||
      isRentPeriodTaxChange ||
      isRentPeriodAmountOwedChange
    ) {
      let response = await customerApi.updateRentPeriodInfo(
        updateRentPeriodInfoData
      )

      if (response.error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: response.error.value.message,
          life: 3000,
          group: "br"
        })
        state.isLoading = false
        resetRentPeriod()
        return
      } else {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Rent Period updated",
          group: "br",
          life: 2000
        })
      }
    }
  }

  const handleSaveTransactionType = async () => {
    state.paymentCompleted = true
    emit("onPayDown")
  }
  const hasPeriodTransactions = computed(() => {
    return state.rentPeriod.transaction_type_rent_period.length > 0
  })
  const handleTransactionTypeSaved = async () => {
    resetRentPeriod()
    state.transactionType =
      state.rentPeriod.transaction_type_rent_period[0]?.payment_type || ""
    state.transactionTypeId =
      state.rentPeriod.transaction_type_rent_period[0]?.id || ""
    state.paymentCompleted = false
  }

  const saveRentPeriod = async () => {
    state.isLoading = true
    await handleRentPeriodFees()
    await handleRentPeriodInfoUpdate()
    await cleanUp()
  }

  const resetRentPeriod = () => {
    state.rentPeriod = cloneDeep(props.rentPeriod)
    state.originalRentPeriod = cloneDeep(props.rentPeriod)
    state.rentPaymentAmount =
      state.rentPeriod.calculated_rent_period_balance || 0
    state.feePaymentAmount =
      state.rentPeriod.calculated_rent_period_fee_balance || 0
    state.taxPaymentAmount =
      state.rentPeriod.calculated_rent_period_tax_balance || 0
  }

  const state = reactive({
    togglePaydown: false,
    useCreditCard: false,
    rentPeriod: {},
    originalRentPeriod: {},
    rentPaymentAmount: 0,
    feePaymentAmount: 0,
    taxPaymentAmount: 0,
    isInternal: true,
    isEditing: false,
    isLoading: false,
    toastConfirmAction: null,
    toastCancelAction: null,
    transactionTypeId: "",
    transactionType: "",
    paymentCompleted: false,
    activeTab: rentPeriodTabs.value[0].value,
    payment: "Paid",
    editingId: "",
    isEditingAmt: false,
    rentPaymentAmountEdit: 0,
    taxPaymentAmountEdited: 0,
    can_use_credit_card: false,
    startDate: null,
    endDate: null
  })

  onMounted(async () => {
    resetRentPeriod()

    state.can_use_credit_card = orderCanUseCreditCard(customerStore.order)

    state.transactionType =
      state.rentPeriod.transaction_type_rent_period[0]?.payment_type || ""
    state.transactionTypeId =
      state.rentPeriod.transaction_type_rent_period[0]?.id || ""

    const { data, error } = await customerApi.get_tax_rate(
      customerStore.order.id
    )
    state.tax_rate = data.value

    state.startDate = state.rentPeriod.start_date
    state.endDate = state.rentPeriod.end_date
  })

  watch(
    () => customerStore.order,
    async (newVal, oldVal) => {
      state.can_use_credit_card = orderCanUseCreditCard(customerStore.order)
    }
  )

  watch(
    () => state.togglePaydown,
    (newVal, oldVal) => {
      toggleEdit()
    }
  )

  watch(
    () => state.activeTab,
    async (newVal, oldVal) => {
      if (state.activeTab == "pay_down") {
        resetRentPeriod()
      }
    }
  )

  watch(
    () => props.resetRentPeriod,
    (newVal, oldVal) => {
      resetRentPeriod()
    }
  )

  function resetRentPeriodTax() {
    const rental_tax_paid =
      (state.rentPaymentAmount || 0) * (state.tax_rate || 0)

    const max_rental_tax_paid =
      (state.rentPeriod?.calculated_rent_period_balance || 0) *
      (state.tax_rate || 0)

    const max_tax = state.rentPeriod?.calculated_rent_period_tax_balance || 0

    const max_tax_remaining_for_fees = max_tax - max_rental_tax_paid

    const max_tax_fees_paid = Math.min(
      (state.feePaymentAmount || 0) * (state.tax_rate || 0),
      max_tax_remaining_for_fees
    )

    state.taxPaymentAmount = roundHalfUp(
      rental_tax_paid + max_tax_fees_paid < 0
        ? 0
        : rental_tax_paid + max_tax_fees_paid
    )
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
