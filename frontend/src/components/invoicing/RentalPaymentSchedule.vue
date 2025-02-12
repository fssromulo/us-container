<template>
  <div v-if="!props.isOnlyOneRentPeriod && false">
    <div class="flex flex-wrap justify-center field-checkbox">
      <label
        for="payDownRentPeriod"
        class="block font-medium text-900 dark:text-0"
        >{{
          state.isPayDownRentPeriods ? "Pay Lump Sum" : "Pay Rent Periods"
        }}</label
      >
    </div>
    <div class="flex flex-wrap justify-center field-checkbox">
      <ToggleSwitch
        id="payDownRentPeriod"
        v-model="state.isPayDownRentPeriods"
        type="text"
      />
    </div>
  </div>
  <div v-if="state.isPayDownRentPeriods">
    <div class="">
      <span class="text-2xl font-medium">Rent Periods</span>
    </div>
    <span
      class="text-xl font-medium"
      v-if="$ability.can('update', 'rental_payments')"
      >Select the rent periods you would like to pay down</span
    >
    <SelectButton
      class="p-12 ml-2"
      v-model="state.selectedCategory"
      :options="state.categories"
      optionLabel="name"
      placeholder="Select a category"
    />
    <div>
      <DataTable
        v-model:selection="state.selectedRows"
        size="small"
        :value="state.rentPeriods"
        dataKey="id"
        :paginator="true"
        :rows="25"
        ref="dt"
        :rowsPerPageOptions="[5, 15, 25, 50, 100]"
      >
        <Column selectionMode="multiple"></Column>
        <Column field="start_date" header="Start Date" :sortable="true">
          <template #body="slotProps">
            <p>
              {{ slotProps.data.start_date }}
              <Badge
                v-if="
                  !isDateRangePastOrCurrent(
                    slotProps.data.start_date,
                    slotProps.data.end_date
                  ) && $ability.can('update', 'rental_period_dates')
                "
                severity="warning"
                class="edit-badge"
                size="large"
                @click="update_rental_period('start_date', slotProps.data)"
              >
                <i class="pi pi-pencil" style="font-size: 0.9rem" />
              </Badge>
            </p>
          </template>
        </Column>
        <Column field="end_date" header="End Date" :sortable="true">
          <template #body="slotProps">
            <p>
              {{ slotProps.data.end_date }}
            </p>
          </template>
        </Column>

        <Column
          field="display_calculated_rent_period_balance"
          header="Rent Balance"
          :sortable="true"
        ></Column>
        <Column
          field="display_calculated_rent_period_fee_balance"
          header="Fee Balance"
          :sortable="true"
        >
        </Column>
        <Column
          field="display_calculated_rent_period_tax_balance"
          header="Tax Balance"
          :sortable="true"
        ></Column>
        <Column
          field="display_calculated_rent_period_total_balance"
          header="Total Balance"
          :sortable="true"
        ></Column>
        <Column field="status" header="Status" :sortable="true"></Column>
        <Column header="Actions">
          <template
            #body="slotProps"
            v-if="$ability.can('view', 'rental_payment_schedule')"
          >
            <Button @click="viewDetails(slotProps.data)">View Period</Button>

            <Button
              type="button"
              icon="pi pi-trash text-sm"
              @click="deleteRentPeriod(slotProps.data)"
              class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
              :loading="
                getValue(
                  state.deleteRentPeriodLoading,
                  slotProps.data.id,
                  false
                )
              "
              :disabled="
                getValue(
                  state.deleteRentPeriodLoading,
                  slotProps.data.id,
                  false
                )
              "
            ></Button>
          </template>
        </Column>
        <ColumnGroup type="footer">
          <Row>
            <Column
              footer="Totals"
              :colspan="3"
              footerStyle="text-align:right"
            />
            <Column :footer="$fc(state.total_rental_price)" />
            <Column :footer="$fc(state.total_fees)" />
            <Column :footer="$fc(state.total_tax)" />
            <Column :footer="$fc(state.total_total_balance)" />
          </Row>
        </ColumnGroup>
      </DataTable>
      <Button
        :loading="state.loading"
        label="Send Rental Statement"
        @click="sendRentalStatement()"
        class="m-1 p-button-accent p-button-lg"
        v-if="$ability.can('update', 'send_rental_statement')"
      />
      <Button
        @click="
          state.partialRentalStatementDatesDialog =
            !state.partialRentalStatementDatesDialog
        "
        label="View Rental Statement"
        :loading="state.loadingPartialRentalStatement"
        class="m-1 p-button-accent p-button-lg"
        v-if="$ability.can('view', 'rental_statement')"
      />
      <Button
        @click="initMultipleRentalPayment()"
        v-if="
          state.selectedRows.length > 0 &&
          selectedRowsContainsPaid == false &&
          $ability.can('update', 'rental_payments')
        "
        :label="goToPaymentLabel"
        class="m-1 p-button-accent p-button-lg"
      />
      <Button
        @click="waiveAllFees()"
        v-if="
          state.rentPeriods.length > 1 &&
          state.selectedRows.length > 0 &&
          $ability.can('update', 'rental_payments')
        "
        label="Waive all fees"
        class="m-1 p-button-accent p-button-lg"
      />
      <Button
        @click="addNewPeriods()"
        label="Add Rent Periods"
        class="m-1 p-button-accent p-button-lg"
      />

      <br />
      <!-- <div class="col-span-12 mb-4 field md:col-span-12" v-if="$ability.can('update', 'rental_period_price')">
        <label
          for="new_rental_period"
          class="font-medium text-900 dark:text-0"
          style="margin: 10px"
          >New rental period price</label
        >
        <InputNumber
          mode="currency"
          currency="USD"
          locale="en-US"
          style="margin: 10px"
          v-model="state.new_rental_period_price"
          id="price"
          type="text"
        />
        <Button
          @click="change_rental_period"
          label="Change rent price"
          :disabled="state.new_rental_period_price === 0"
          class="m-1 p-button-accent p-button-lg"
          :loading="state.loading"
        />
      </div> -->
      <ReportingFilterOptions
        @runReport="runReport"
        :displayCondition="false"
        :displayProductType="false"
        report_name="transactions_report"
        :clear_report_names="['transactions_report']"
        :displayPurchaseType="false"
        :displaySelectVendor="false"
        :onlyDates="true"
      />

      <DataTable
        :value="state.transactions_report"
        tableStyle="min-width: 50rem; max-width:98%;height:400px"
        :scrollable="true"
      >
        <Column
          field="created_at"
          header="Date"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="payment_type"
          header="Payment Type"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="notes"
          header="Notes"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="amount"
          header="Amount"
          style="max-width: 10%"
          sticky
        ></Column>
      </DataTable>
    </div>

    <Dialog
      v-model:visible="state.dialogVisible"
      modal
      header="Header"
      closeOnEscape
      :dismissableMask="true"
      :breakpoints="{ '1199px': '80vw', '575px': '90vw' }"
      :style="{ width: '75rem' }"
    >
      <template #header>
        <div class="inline-flex items-center justify-center gap-2">
          <span class="font-bold whitespace-nowrap"
            >Rent Period {{ state.selectedRentPeriod.start_date }} -
            {{ state.selectedRentPeriod.end_date }}</span
          >

          <Button
            label="Open Rental Invoice"
            :class="
              smAndSmaller
                ? 'p-button-primary p-button-sm text-sm ml-4'
                : 'p-button-primary text-lg ml-4'
            "
            @click="openPaymentPage(state.selectedRentPeriod.id)"
          />
          <Button
            label="Send Period Invoice"
            :loading="state.sendPeriodInvoice"
            :class="
              smAndSmaller
                ? 'p-button-primary p-button-sm text-sm ml-4'
                : 'p-button-primary text-lg ml-4'
            "
            @click="sendPeriodInvoice(state.selectedRentPeriod.id)"
          />
        </div>
      </template>
      <single-rental-period
        :order_id="props.order_id"
        :rentPeriod="state.selectedRentPeriod"
        :reset-order="resetOrder"
        :has-ach="props.hasAch"
        :resetRentPeriod="state.resetRentPeriod"
        :application-accepted="applicationAccepted"
        @onPayDown="state.dialogVisible = false"
      />
      <template #footer> </template>
    </Dialog>
    <Dialog
      v-model:visible="state.editing_rent_period"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Update Rental Due Date"
      :modal="true"
      class="p-fluid"
    >
      <UpdateRentalPeriod
        v-if="state.editing_rent_period"
        :editingData="state.rental_period_props"
        @reloadRentalPeriod="resetOrder"
      ></UpdateRentalPeriod>
    </Dialog>
    <Dialog
      v-model:visible="state.addRentPeriods"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Add Rent Period"
      :modal="true"
      class="p-fluid"
    >
      <addRentPeriods
        :editingData="state.rental_period_props"
        @reloadRentalPeriod="resetOrder"
      ></addRentPeriods>
    </Dialog>
    <Dialog
      v-model:visible="state.viewRentalStatement"
      modal
      header="Client Rental Statement"
      closeOnEscape
      :dismissableMask="true"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
      :style="{ width: '50rem' }"
    >
      <RentalStatement
        :transactionList="state.transactionList"
        :customerDetail="state.customerDetail"
        :orderDetail="state.orderDetail"
        :companyName="state.companyName"
        :orderInfo="state.orderInfo"
        :orderCustomerProfileId="customerStore.order.customer_profile_id"
        :order="customerStore.order"
        :pdf_url="state.pdf_url"
      ></RentalStatement>
    </Dialog>

    <Dialog
      v-model:visible="state.payForMultipleRows"
      modal
      header="Pay For Rent Periods"
      closeOnEscape
      :dismissableMask="true"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
      :style="{ width: '50rem' }"
    >
      <PaymentForMultipleRows
        :disableAllFields="props.disableAllFields"
        :overridePaymentAmount="props.overridePaymentAmount"
        :selectedRentPeriodsIds="props.selectedRentPeriodsIds"
        :creditCardFeeToggleEnabled="props.creditCardFeeToggleEnabled"
        :isUpdateCreditCard="props.isUpdateCreditCard"
        :rentPaymentAmount="props.rentPaymentAmount"
        :feePaymentAmount="props.feePaymentAmount"
        :rentalAfterPayReset="props.rentalAfterPayReset"
        :isInternal="props.isInternal"
        :orderId="props.order_id"
        :hasAch="props.hasAch"
        :resetOrder="resetOrder"
        :resetRentPeriod="resetRentPeriod"
      ></PaymentForMultipleRows>
    </Dialog>

    <Dialog
      v-model:visible="state.partialRentalStatementDatesDialog"
      modal
      header="Partial Rental Statement"
      closeOnEscape
      :dismissableMask="true"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
      :style="{ width: '50rem' }"
    >
      <div class="flex flex-col items-center space-y-4 p-4">
        <span class="relative w-full max-w-md">
          <DatePicker
            class="ml-4"
            inputId="range"
            dateFormat="mm/dd/yy"
            v-model="state.partialRentalStatementDates"
            selectionMode="range"
            :manualInput="false"
          />
          <label
            for="calendar"
            class="absolute -top-2.5 left-3.5 bg-white px-1 text-sm text-gray-600"
          >
            Date Range
          </label>
        </span>

        <Button
          @click="printRentalStatement((partial = true))"
          label="View Rental Statement"
          class="m-1 p-button-accent p-button-lg"
        />
      </div>
    </Dialog>
  </div>
  <div v-else>
    <add-rent-payment
      ::has-ach="props.hasAch"
      :order_id="props.order_id"
      :rent-period-ids="props.selectedRentPeriodsIds"
      :reset-function="resetOrder"
    />
  </div>
</template>

<script setup>
  import { reactive, watch, inject, computed, ref } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import CustomerApi from "@/api/customers"

  import { dfa, dfc } from "@/service/DateFormat.js"
  import CustomerService from "../../service/Customers"
  import { onMounted } from "vue"
  import { DateTime } from "luxon"
  import SingleRentalPeriod from "./SingleRentalPeriod.vue"
  import AddRentPayment from "./payment/AddRentPayment.vue"
  import RentalStatement from "./rent/RentalStatement.vue"
  import PaymentForMultipleRows from "./payment/PaymentForMultipleRows.vue"
  import UpdateRentalPeriod from "./UpdateRentalPeriod.vue"
  import addRentPeriods from "./addRentPeriods.vue"
  import ReportingFilterOptions from "../reporting/ReportingFilterOptions.vue"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useConfirm } from "primevue/useconfirm"
  import { useUsers } from "@/store/modules/users"

  const confirm = useConfirm()
  const usersStore = useUsers()

  const intervalManager = new IntervalManager()
  const reportsApi = new ReportsApi()
  const useLoadingStateStore = loadingStateStore()

  const $fc = inject("$formatCurrency")
  const $ability = inject("$ability")

  const toast = useToast()

  const customerApi = new CustomerApi()

  const customerStore = useCustomerOrder()
  const customerService = new CustomerService()

  const props = defineProps({
    resetRentPeriod: {
      type: Function,
      default: () => {}
    },
    updateSelectedRentPeriods: {
      type: Function,
      default: () => {}
    },
    isOnlyOneRentPeriod: {
      type: Boolean,
      default: false
    },
    order_id: {
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
    hasAch: {
      type: Boolean,
      default: false
    }
  })

  const openPaymentPage = (rent_period_id) => {
    if (import.meta.env.DEV) {
      let url = `${import.meta.VITE_APP_PAYMENT_URL}/#/rental_invoice/${
        customerStore.order.id
      }/${rent_period_id}`
      window.open(url, "_blank")
      return
    }

    if (import.meta.env.PROD) {
      let invoice_email_link = usersStore.cms?.links?.invoice_email_link
      let url =
        invoice_email_link + `${state.customerOrder.id}/${rent_period_id}`
      url = url.replace("payment", "rental_invoice")
      window.open(url, "_blank")
      return
    }
  }

  const getValue = (obj, key, defaultValue = null) => {
    return obj?.[key] ?? defaultValue
  }

  const runFunctionInInterval = (name, dataObj, fun) => {
    return async function () {
      const result = await reportsApi.retrieveByName(name, dataObj)
      console.log(result.data.value)
      useLoadingStateStore.setIsLoading(false)
      if (result.data.value != null) {
        if (result.data.value.result.length == 0) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "No results for report, try again.",
            group: "br",
            life: 5000
          })
        } else {
          fun(result.data.value.result)
        }
      }
      return result.data.value
    }
  }

  const deleteRentPeriod = (rentPeriodData) => {
    confirm.require({
      target: event.target,
      message: "Are you sure you want to delete this rent period?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        if (rentPeriodData.id) {
          state.deleteRentPeriodLoading[rentPeriodData.id] = true
          let updatedOrderResponse = await customerApi.getOrderById(
            customerStore.order.id
          )
          if (updatedOrderResponse.data.value.rent_periods.length <= 1) {
            toast.add({
              severity: "error",
              summary: "Error",
              detail: "At least 1 rent period must be remaining.",
              group: "br",
              life: 5000
            })
            state.deleteRentPeriodLoading = false
            return
          }
          const { data, error } = await customerApi.deleteRentPeriod(
            rentPeriodData.id
          )
          state.deleteRentPeriodLoading[rentPeriodData.id] = false
          if (error.value) {
            state.loading = false
            toast.add({
              severity: "error",
              summary: "Error",
              detail: "Error deleting rent period.",
              group: "br",
              life: 5000
            })
            return
          } else {
            toast.add({
              severity: "success",
              summary: "Success",
              detail: "Successfully delete rent period.",
              group: "br",
              life: 5000
            })
            await resetOrder(true)
          }
        }
      },
      reject: () => {}
    })
  }

  const runReport = async (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]

    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: state.selectedAccount,
      order_ids: [customerStore.order.id],
      run_by: "user"
    }

    await reportsApi.runByName("transactions_report", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("transactions_report", dataObj, function (result) {
        state.transactions_report = result
        state.transactions_report.map((el) => {
          el.created_at = dfc(el.created_at)

          if (el.notes == null) {
            el.notes = ""
          }
          if (el.response_from_gateway != null) {
            const responseFromGatewayJson = JSON.parse(el.response_from_gateway)
            el.notes +=
              "Account Type: " +
              responseFromGatewayJson?.transactionResponse?.accountType +
              " "
            el.notes +=
              "Account Number: " +
              responseFromGatewayJson?.transactionResponse?.accountNumber +
              " "
          }
          return el
        })
      }),
      function () {},
      3000,
      12000
    )
  }

  const dt = ref()

  const sorttedRentPeriod = computed(() => {
    return state.rentPeriods.sort((a, b) => {
      const start_date_luxon_a = DateTime.fromISO(a.start_date)
      const start_date_luxon_b = DateTime.fromISO(b.end_date)
      return start_date_luxon_a - start_date_luxon_b
    })
  })
  const addNewPeriods = () => {
    state.addRentPeriods = !state.addRentPeriods
  }
  const update_rental_period = (type, data) => {
    // This is where the rental_period props are set to then be sent down to the updaterentalperiod as a prop to that component
    const currentIndex = sorttedRentPeriod.value.indexOf(data)
    if (currentIndex > 0) {
      state.rental_period_props.min_date = new Date(
        sorttedRentPeriod.value[currentIndex - 1].end_date
      )
    }
    state.rental_period_props.selected_period = data
    state.rental_period_props.option = type
    state.rental_period_props.subsequent_periods =
      sorttedRentPeriod.value.slice(currentIndex + 1) || []
    switch (type) {
      case "start_date":
        if (currentIndex !== state.rentPeriods.length - 1) {
          // this isnt the first previous so lets get the next one
          state.rental_period_props.end_date = DateTime.fromISO(
            state.rentPeriods[currentIndex - 1]
              ? state.rentPeriods[currentIndex - 1].end_date
              : ""
          )
        } else {
          state.rental_period_props.end_date = ""
        }
        state.rental_period_props.start_date = ""
        break
    }
    state.editing_rent_period = true
  }
  const resetRentPeriod = () => {
    state.resetRentPeriod = !state.resetRentPeriod
  }

  const initMultipleRentalPayment = () => {
    state.payForMultipleRows = true
  }

  const waiveAllFees = async () => {
    state.loading = true
    let data_request = {
      rent_periods: state.selectedRows
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
      resetOrder(true)
    }
    state.loading = false
  }

  const closePayDialog = () => {
    state.payForMultipleRows = false
  }

  const viewDetails = (rowData) => {
    // Implement the logic to view details of a specific row
    console.log("Viewing details for:", rowData)
    state.dialogVisible = true
    state.selectedRentPeriod = rowData
  }

  const checkStatus = (period) => {
    let today = DateTime.now()
    //TODO remove. this is for testing
    // today = today.plus({ months: 2})
    let returnValue = ""
    let start_date = DateTime.fromISO(period.start_date)
    let end_date = DateTime.fromISO(period.end_date)
    let isTodayPastStartDate = today > start_date
    let isCurrentPeriod = start_date <= today && today <= end_date
    let isOverDue =
      isTodayPastStartDate && period.calculated_rent_period_total_balance !== 0
    if (period.calculated_rent_period_total_balance === 0) {
      returnValue = "Paid"
    } else if (isOverDue) {
      returnValue = "Overdue"
    } else if (isCurrentPeriod) {
      returnValue = "Current"
    } else {
      returnValue = "Upcoming"
    }
    return returnValue
  }
  const applicationAccepted = computed(() => {
    return (
      customerStore?.order?.application_response.length > 0 &&
      customerStore?.order?.application_response[0].date_accepted
    )
  })

  const goToPaymentLabel = computed(() => {
    console.log(
      typeof state.selectedRows[0]
        .display_calculated_rent_period_total_balance_default
    )
    const sum = state.selectedRows.reduce(
      (accumulator, currentValue) =>
        accumulator +
          typeof currentValue?.display_calculated_rent_period_total_balance_default ==
        "string"
          ? parseFloat(
              currentValue?.display_calculated_rent_period_total_balance_default
                ?.slice(1)
                .replace(",", "")
            ).toFixed(2)
          : currentValue?.display_calculated_rent_period_total_balance_default,
      0.0
    )
    console.log(sum)
    return "Go To Payment ( $" + sum.toFixed(2) + " )"
  })

  const transformRentPeriodFees = () => {
    state.rentPeriods.map((period) => {
      // ... existing code to add status and format values ...

      // Convert start and end dates to Luxon DateTime for sorting
      period.start_date_luxon = DateTime.fromISO(period.start_date)
      period.end_date_luxon = DateTime.fromISO(period.end_date)
    })

    // Sort by start_date from most recent to latest in the future
    state.rentPeriods.sort((a, b) => a.start_date_luxon - b.start_date_luxon)

    state.rentPeriods.map((period) => {
      // adding this to the dict so that we can have live statuses. needs to be before so we can get unformatted dates
      period.status = checkStatus(period)
      period.start_date = dfc(period.start_date)
      period.end_date = dfc(period.end_date)
      period.display_calculated_rent_period_total_balance = $fc(
        period?.calculated_rent_period_total_balance
      )

      period.display_amount_owed = $fc(period?.amount_owed)
      period.display_total = $fc(period.calculated_total_amount)

      period.display_calculated_rent_period_total_balance_default =
        period?.calculated_rent_period_total_balance
      period.display_calculated_rent_period_balance = $fc(
        period?.calculated_rent_period_balance
      )
      period.display_calculated_rent_period_tax_balance = $fc(
        period?.calculated_rent_period_tax_balance
      )
      period.display_calculated_rent_period_tax = $fc(
        period?.calculated_rent_period_tax
      )
      period.display_calculated_rent_period_fee_balance = $fc(
        period?.calculated_rent_period_fee_balance
      )
      period.amount_owed = $fc(period?.amount_owed)
      period.display_calculated_rent_period_fees = $fc(
        period?.calculated_rent_period_fees
      )
    })
  }

  const resetOrder = async (fetchOrder = false) => {
    await customerStore.orderResetLock.acquire()

    if (fetchOrder == true) {
      customerStore.fetchOrderFull = true
    } else if (customerStore.fetchOrderFull == true) {
      customerStore.fetchOrderFull = false
      fetchOrder = true
    }
    state.editing_rent_period = false
    // the reload is used when we update a rent period, but when we just load the data the first time
    // then we dont need to reload it
    if (fetchOrder) {
      let updatedOrderResponse = await customerApi.getOrderById(
        customerStore.order.id
      )
      if (updatedOrderResponse.data.value.status == "Delinquent") {
        if (
          updatedOrderResponse.data.value.status.calculated_rent_balance == 0
        ) {
          updatedOrderResponse = await customerApi.updateOrder(
            customerStore.order.id,
            { status: "Delivered" }
          )
        }
      }
      customerStore.setOrder(null)
      customerStore.setOrder(updatedOrderResponse.data)
    }
    let order = customerStore.order
    order = customerService.orderDto()
    state.rentPeriods = order.rent_periods
    transformRentPeriodFees()

    if (fetchOrder) {
      // updating the selected rent period
      state.selectedRentPeriod = state.rentPeriods.find((period) => {
        return period.id === state.selectedRentPeriod?.id
      })
    }

    state.payForMultipleRows = false
    state.isPayDownRentPeriods = true

    await customerStore.orderResetLock.release()
  }

  const change_rental_period = async () => {
    state.loading = true
    const { error, data } = await customerApi.updateRentPeriodPrice(
      customerStore.order.id,
      state.new_rental_period_price
    )

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Updated rent price",
        group: "br",
        life: 5000
      })
      resetOrder(true)
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to update rent price",
        group: "br",
        life: 5000
      })
    }
    state.loading = false
  }

  onMounted(() => {
    resetOrder(false)
    resetRentPeriodsList({ name: "All", code: "ALL" })
  })

  const state = reactive({
    addRentPeriods: false,
    rentPeriods: [],
    sendPeriodInvoice: false,
    selectedRows: [],
    dialogVisible: false,
    selectedRentPeriod: {},
    useCreditCard: true,
    isPayDownRentPeriods: true,
    loading: false,
    loadingRentalStatement: false,
    loadingPartialRentalStatement: false,
    viewRentalStatement: false,
    transactionList: [],
    customerDetail: {},
    orderDetail: {},
    companyName: "",
    orderInfo: {},
    payForMultipleRows: false,
    resetRentPeriod: false,
    new_rental_period_price: 0,
    editing_rent_period: false,
    updated_rent_period_detail: {},
    rental_period_props: {
      start_date: "",
      selected_period: {},
      option: "",
      subsequent_periods: [],
      rent_due_on_day: customerStore?.order?.rent_due_on_day,
      order_id: customerStore?.order?.id
    },
    categories: [
      { name: "All", code: "ALL" },
      { name: "Paid", code: "Paid" },
      { name: "Overdue", code: "Overdue" },
      { name: "Upcoming", code: "Upcoming" }
    ],
    selectedCategory: { name: "All", code: "ALL" },
    total_rental_price: 0,
    total_fees: 0,
    total_tax: 0,
    total_total_balance: 0,
    transactions_report: [],
    deleteRentPeriodLoading: {},
    partialRentalStatementDatesDialog: false,
    partialRentalStatementDates: []
  })
  const isDateRangePastOrCurrent = (startDate, endDate) => {
    const currentDate = new Date()
    const start = new Date(startDate)
    const end = new Date(endDate)
    if (end < currentDate) {
      return true
    }

    // Check if the range is current
    if (start <= currentDate && currentDate <= end) {
      return true
    }

    // If not in the past or current, it must be in the future
    return false
  }

  const sendPeriodInvoice = async (periodId) => {
    //sendRentalStatement
    state.sendPeriodInvoice = true
    let { data, error } = await customerApi.resendRentalPeriodInvoice(
      customerStore.order.id,
      periodId
    )
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Rental Period Invoice Sent",
        detail: "Successfully sent rental period invoice",
        group: "br",
        life: 5000
      })
      state.sendPeriodInvoice = false
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error sending rental period invoice",
        group: "br",
        life: 5000
      })
      state.sendPeriodInvoice = false
    }
  }
  const sendRentalStatement = async () => {
    //sendRentalStatement
    state.loading = true
    let { data, error } = await customerApi.sendRentalStatement(
      customerStore.order.id
    )
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Rental Statement Sent",
        detail: "Successfully sent customer's rental statement",
        group: "br",
        life: 5000
      })
      state.loading = false
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error sending customer rental statment",
        group: "br",
        life: 5000
      })
      state.loading = false
    }
  }

  const printRentalStatement = async (partial = false) => {
    //generateRentalStatement

    if (!partial) {
      state.loadingRentalStatement = true
    } else {
      state.loadingPartialRentalStatement = true
    }
    let data_request = {
      partial: partial,
      partialRentalStatementDates: state.partialRentalStatementDates
    }
    let { data, error } = await customerApi.generateRentalStatementWeb(
      customerStore.order.id,
      data_request
    )
    if (data.value) {
      state.viewRentalStatement = true
      state.transactionList = data.value.transactions_list
      state.customerDetail = data.value.customer_detail
      state.orderDetail = data.value.order_detail
      state.companyName = data.value.company_name
      state.orderInfo = data.value.order_info
      toast.add({
        severity: "success",
        summary: "Rental Statement Generated",
        detail: "Successfully generated customer's rental statement",
        group: "br",
        life: 5000
      })
      if (!partial) state.loadingRentalStatement = false
      else state.loadingPartialRentalStatement = false
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error generating customer rental statment",
        group: "br",
        life: 5000
      })
      state.loadingRentalStatement = false
      state.viewRentalStatement = true
    }
  }

  const selectedRowsContainsPaid = computed(() => {
    return state.selectedRows.some((el) => el.status === "Paid")
  })

  watch(
    () => state.selectedRows,
    (newVal, oldVal) => {
      props.updateSelectedRentPeriods(newVal)
    }
  )

  const resetRentPeriodsList = async (category) => {
    state.selectedRows = []
    await resetOrder(false)
    state.rentPeriods = state.rentPeriods.filter((el) => {
      if (category.code == "ALL") {
        return true
      }
      if (category.code == el.status) {
        return true
      } else {
        return false
      }
    })

    state.total_rental_price = state.rentPeriods.reduce(
      (accumulator, currentValue) => {
        let result = parseFloat(
          currentValue.amount_owed.replace(/[^0-9.]/g, "")
        )
        return accumulator + result
      },
      0
    )

    state.total_fees = state.rentPeriods.reduce((accumulator, currentValue) => {
      let result = currentValue.calculated_rent_period_fee_balance
      return accumulator + result
    }, 0)

    state.total_tax = state.rentPeriods.reduce((accumulator, currentValue) => {
      let result = currentValue.calculated_rent_period_tax
      return accumulator + result
    }, 0)

    state.total_total_balance = state.rentPeriods.reduce(
      (accumulator, currentValue) => {
        let result = currentValue.calculated_rent_period_total_balance
        return accumulator + result
      },
      0
    )
  }

  watch(
    () => state.selectedCategory,
    async (newVal, oldVal) => {
      resetRentPeriodsList(state.selectedCategory)
    }
  )

  watch(
    () => customerStore.order,
    (newVal, oldVal) => {
      resetOrder()
      resetRentPeriodsList(state.selectedCategory)
    }
  )
</script>

<style scoped>
  .edit-badge {
    cursor: pointer;
  }
  .edit-badge:hover {
    cursor: pointer;
  }
</style>
