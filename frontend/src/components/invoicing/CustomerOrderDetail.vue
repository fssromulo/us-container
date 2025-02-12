<template>
  <div>
    <ul
      class="flex p-2 m-0 overflow-x-scroll list-none select-none surface-card"
      style="max-width: 95vw"
    >
      <template :key="idx" v-for="(name, idx) in filteredComponentList">
        <li class="pr-3">
          <a
            v-ripple
            class="flex px-4 py-3 transition-colors cursor-pointer align-items-center hover:surface-100 border-round transition-duration-150 p-ripple"
            :class="{
              'border-blue-600 text-blue-600 hover:border-blue-600':
                state.active === idx,
              'text-700': state.active !== idx
            }"
            @click="state.active = idx"
          >
            <span class="text-2xl font-medium">{{ name }}</span>
          </a>
        </li>
        <li class="mt-5 align-items-center">
          <div
            style="width: 1px; height: 50%"
            class="border-right-1 surface-border"
          ></div>
        </li>
      </template>
    </ul>
  </div>

  <div
    v-if="
      state.active ===
      filteredComponentList.indexOf(
        customerOrderStore.order.type != 'RENT'
          ? `Order Detail`
          : `Customer Detail`
      )
    "
    style="height: 75vh"
  >
    <div class="flex flex-col gap-4 md:flex-row">
      <div
        :class="{
          'md:w-1/2':
            smAndSmaller ||
            !$ability.can('view', 'rental_payments') ||
            customerStore.order.type !== 'RENT',
          card: true,
          'md:w-1/2':
            !smAndSmaller &&
            customerStore.order?.type === 'RENT' &&
            $ability.can('view', 'rental_payments')
        }"
        class="w-full"
      >
        <customer-detail
          :swap-customer-order="props.swapCustomerOrder"
          @hideOrderDetails=""
        />
      </div>
      <div
        v-if="
          customerStore.order?.type === 'RENT' &&
          $ability.can('view', 'rental_payments')
        "
        class="card md:w-1/2"
      >
        <quick-pay @update-customer-order="reloadRentalPeriod" />
      </div>
    </div>
    <hr />
    <div class="flex flex-col items-center m-5" v-if="hasRushFees">
      <Tag
        severity="success"
        value="Rush"
        rounded
        size="large"
        style="font-size: 1.5rem; background: green; padding: 0.5rem"
      ></Tag>
    </div>
    <div class="flex flex-col gap-4 md:flex-row">
      <div class="md:w-1/2 card">
        <order-detail
          v-if="customerStore.order?.type !== 'RENT'"
          :swap-customer-order="props.swapCustomerOrder"
          :has-ach="state.isUpdateAch"
          :hasCreditCard="state.isUpdateCreditCard"
          :routing-number="state.routing_number"
          :account-number="state.account_number"
          :bank-name="state.bank_name"
          @update-rent-periods="reloadRentalPeriod"
        />
        <rent-detail
          v-else
          :swap-customer-order="props.swapCustomerOrder"
          :has-ach="state.isUpdateAch"
          :hasCreditCard="state.isUpdateCreditCard"
          :routing-number="state.routing_number"
          :account-number="state.account_number"
          :bank-name="state.bank_name"
          @update-rent-periods="reloadRentalPeriod"
        />
      </div>

      <div class="md:w-1/2 card">
        <line-item :swapCustomerOrder="props.swapCustomerOrder" />
      </div>
    </div>
  </div>

  <div
    v-if="state.active === filteredComponentList.indexOf('Customer Chat Log')"
  >
    <CustomerChatLog :customer_phone="customerStore.order.customer.phone" />
  </div>

  <div
    v-if="
      state.active === filteredComponentList.indexOf('Rental Detail') &&
      usersStore?.cms?.uses_other_orders
    "
    style="height: 75vh"
  >
    <div class="grid">
      <div class="col-4">
        <div class="card">
          <customer-detail :swap-customer-order="props.swapCustomerOrder" />
        </div>
      </div>
      <div class="col-8">
        <div class="card">
          <div class="grid">
            <div class="col-6">
              <span class="ml-2 text-2xl">
                Current Balance: {{ $fc(mergedOrdersCurrentBalance) }}</span
              >
            </div>
            <div class="col-6">
              <Button
                v-if="$ability.can('update', 'rental_payments')"
                :disabled="mergedOrdersCurrentBalance <= 0"
                @click="initMultipleOrdersPayment()"
                class="ml-2 p-button-accent p-button-lg"
                >Go to payment
              </Button>
              <Button
                @click="
                  state.dialogPrintRentalStatement =
                    !state.dialogPrintRentalStatement
                "
                class="ml-2 p-button-accent p-button-lg"
                >Print rental statement
              </Button>
            </div>
          </div>
          <DataTable :value="state.mergedOrders">
            <Column
              :frozen="true"
              field="display_order_id"
              header="Rent Id"
              style="width: 75px"
              :sortable="true"
            >
              <template #body="slotProps">
                <Button
                  class="p-button-rounded p-button-primary"
                  @click="openDialog(slotProps.data.display_order_id)"
                  >{{ slotProps.data?.display_order_id }}
                </Button>
              </template>
            </Column>
            <Column
              field="calculated_abreviated_line_items_title"
              header="Size"
            ></Column>
            <Column
              field="calculated_rent_balance"
              header="Rental Balance"
            ></Column>
            <Column field="calculated_paid_thru" header="Paid Thru"></Column>
            <Column
              :frozen="true"
              field="address.full_address"
              header="Address"
              style="width: 250px"
              :sortable="true"
            >
              <template #body="slotProps">
                <p>
                  {{ slotProps?.data?.address?.full_address }}
                </p>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
    </div>
    <div class="card">
      <span class="ml-2 text-2xl">Rental Transaction History</span>
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
        <Column field="id" header="Receipt" style="max-width: 10%" sticky>
          <template #body="slotProps">
            <Button
              class="p-button-rounded p-button-primary"
              @click="receiptClick()"
            >
              Receipt
            </Button>
          </template>
        </Column>
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
        <Column field="amount" header="Amount" style="max-width: 10%" sticky>
          <template #body="slotProps">
            {{ $fc(slotProps.data.amount) }}
          </template>
        </Column>
      </DataTable>
    </div>
  </div>

  <div
    v-if="
      state.active === filteredComponentList.indexOf('Update Payment Method')
    "
    style="height: 75vh"
  >
    <div class="card">
      <div class="flex flex-col items-center gap-4 my-8 mt-8 mb-2">
        <ToggleSwitch v-model="state.ach" v-if="state.can_use_credit_card" />
        <span
          class="ml-2 font-medium text-900 dark:text-0"
          v-if="state.can_use_credit_card"
          >{{ state.ach ? "ACH" : "Card" }}</span
        >
        <span class="ml-2 font-medium text-900 dark:text-0" v-else>{{
          "ACH"
        }}</span>
      </div>

      <AchFields
        v-if="state.ach_payment_profile_present && state.ach"
        :isUpdateAch="true"
        :refreshFunction="refresh_customer_profile"
      >
      </AchFields>
      <AchFields
        v-if="!state.ach_payment_profile_present && state.ach"
        :refreshFunction="refresh_customer_profile"
      >
      </AchFields>
      <PaymentFields
        v-if="
          !state.ach &&
          state.credit_card_payment_profile_present &&
          state.can_use_credit_card
        "
        :disableAllFields="false"
        :isUpdateCreditCard="true"
        :is-internal="true"
        :refreshFunction="refresh_customer_profile"
      />
      <PaymentFields
        v-if="
          !state.ach &&
          !state.credit_card_payment_profile_present &&
          state.can_use_credit_card
        "
        :disableAllFields="false"
        :is-add-card-on-file="true"
        :is-internal="true"
        :refreshFunction="refresh_customer_profile"
      />
    </div>
  </div>

  <div
    v-if="state.active === filteredComponentList.indexOf('Add Payment Method')"
    style="height: 75vh"
  >
    <div class="card">
      <div class="flex flex-col items-center">
        <div class="">
          <ToggleSwitch v-model="state.ach" v-if="state.can_use_credit_card" />
          <span
            class="ml-2 font-medium text-900 dark:text-0"
            v-if="state.can_use_credit_card"
            >{{ state.ach ? "ACH" : "Card" }}</span
          >
          <span class="ml-2 font-medium text-900 dark:text-0" v-else>{{
            "ACH"
          }}</span>
        </div>
      </div>

      <AchFields
        v-if="state.ach_payment_profile_present && state.ach"
        :isUpdateAch="true"
        :refreshFunction="refresh_customer_profile"
      >
      </AchFields>
      <AchFields
        v-if="!state.ach_payment_profile_present && state.ach"
        :refreshFunction="refresh_customer_profile"
      >
      </AchFields>
      <PaymentFields
        v-if="
          !state.ach &&
          state.credit_card_payment_profile_present &&
          state.can_use_credit_card
        "
        :disableAllFields="false"
        :isUpdateCreditCard="true"
        :is-internal="true"
        :refreshFunction="refresh_customer_profile"
      />
      <PaymentFields
        v-if="
          !state.ach &&
          !state.credit_card_payment_profile_present &&
          state.can_use_credit_card
        "
        :disableAllFields="false"
        :is-add-card-on-file="true"
        :is-internal="true"
        :refreshFunction="refresh_customer_profile"
      />
    </div>
  </div>

  <div
    v-if="state.active === filteredComponentList.indexOf('Notes')"
    style="height: 75vh"
  >
    <div class="card">
      <NoteDetail :order="customerStore.order" :showTitle="false" />
    </div>
  </div>
  <div
    v-if="showApplication"
    class="grid grid-cols-12 gap-4 shadow-xl"
    style="height: 75vh"
  >
    <div v-if="!application && isPaid" class="col-span-12 card">
      <p class="mt-4 text-2xl text-center">
        This order was created, sold, and delivered without an application
      </p>
    </div>
    <div v-if="!application && !isPaid" class="col-span-12 card">
      <p class="mt-4 text-2xl text-center"> No application submitted </p>
    </div>
    <div class="col-span-12 mb-2 card">
      <div
        class="flex flex-col items-center mb-4"
        v-if="
          customerStore.order?.application_response.length > 0 ||
          state.mappedPhotos.length > 0
        "
      >
        <ul
          class="flex p-2 m-0 overflow-x-scroll list-none select-none surface-card"
          style="max-width: 95vw"
        >
          <template
            :key="idx"
            v-for="(
              response, idx
            ) in customerStore.order?.application_response?.filter((e) =>
              $isObjectPopulated(e.response_content)
            )"
          >
            <li class="pr-3">
              <a
                v-ripple
                class="flex px-4 py-3 transition-colors cursor-pointer align-items-center hover:surface-100 border-round transition-duration-150 p-ripple"
                :class="{
                  'border-blue-600 text-blue-600 hover:border-blue-600':
                    state.application_response === idx,
                  'text-700': state.application_response !== idx
                }"
                @click="state.application_response = idx"
              >
                <span class="text-2xl font-medium">{{
                  response.customer_application_schema.full_schema_name
                }}</span>
              </a>
            </li>
            <li class="mt-5 align-items-center">
              <div
                style="width: 1px; height: 50%"
                class="border-right-1 surface-border"
              ></div>
            </li>
          </template>
          <template
            v-if="
              state.mappedPhotos.length > 0 &&
              $ability.can('view', 'rental_application_photos')
            "
          >
            <li class="pr-3">
              <a
                v-ripple
                class="flex px-4 py-3 transition-colors cursor-pointer align-items-center hover:surface-100 border-round transition-duration-150 p-ripple"
                :class="{
                  'border-blue-600 text-blue-600 hover:border-blue-600':
                    state.application_response === -1,
                  'text-700': state.application_response !== -1
                }"
                @click="state.application_response = -1"
              >
                <span class="text-2xl font-medium">Manual Application</span>
              </a>
            </li>
            <li class="mt-5 align-items-center">
              <div
                style="width: 1px; height: 50%"
                class="border-right-1 surface-border"
              ></div>
            </li>
          </template>
        </ul>
      </div>
      <view-application
        :response="selectedApplication"
        v-if="
          customerStore.order?.application_response.length > 0 &&
          state.application_response !== -1
        "
      />
      <div class="col-span-12 pb-8 mt-2">
        <Carousel
          v-if="
            state.application_response == -1 &&
            state.mappedPhotos.length &&
            $ability.can('view', 'rental_application_photos')
          "
          :value="state.mappedPhotos"
          :numVisible="1"
          :numScroll="1"
          :responsiveOptions="responsiveOptions"
        >
          <template #item="slotProps">
            <div class="px-1 py-2 text-center">
              <div class="mb-4">
                <Image
                  :src="slotProps.data.presigned_url"
                  alt="Image"
                  class="shadow"
                  width="150"
                  preview
                />
              </div>
            </div>
          </template>
        </Carousel>
      </div>
    </div>
    <div class="col-span-12 pb-8 mt-2">
      <application-status
        class="mt-2"
        :resetFunction="resetOrder"
        :response="selectedApplication"
        :allResponses="allApplications"
        :manualApplication="true"
      />
    </div>

    <div class="col-span-12 pb-8 mt-2">
      <application-status
        class="mt-2"
        :resetFunction="resetOrder"
        :response="selectedApplication"
        :allResponses="allApplications"
        :manualApplication="false"
      />
    </div>
  </div>
  <div
    v-if="
      state.active === filteredComponentList.indexOf('Charge Card') &&
      state.can_use_credit_card
    "
    class="shadow-xl card"
    style="height: 75vh"
  >
    <payment-fields
      :disable-all-fields="paymentDetailsDisabled"
      :is-internal="state.isInternal"
      :applyBankFee="true"
      :bankFee="bankFee"
      :creditCardFeeToggleEnabled="creditCardFeeToggleEnabled"
    />
  </div>
  <div v-show="showHistorySchedule" class="mt-4 shadow" style="height: 75vh">
    <div class="grid grid-cols-12 gap-4">
      <div v-show="isRent || isRentToOwn" class="col-span-12 card">
        <rental-payment-schedule
          :update-selected-rent-periods="updateSelectedRentPeriods"
          :is-only-one-rent-period="isOnlyOneRentPeriod"
          :order_id="customerStore.order?.id"
          :key="state.forceReloadKey"
          :disable-all-fields="state.selectedRentPeriodRows.length == 0"
          :override-payment-amount="overridePaymentAmount"
          :selected-rent-periods-ids="selectedRentPeriodsIds"
          :is-internal="state.isInternal"
          :has-ach="state.isUpdateAch"
          :rental-after-pay-reset="reloadRentalPeriod"
        />
      </div>
    </div>
    <div style="" class="grid grid-cols-1 gap-4 md:grid-cols-2 card">
      <view-transaction-type
        :resetFunction="resetOrder"
        :orderId="customerStore.order?.id"
      />
    </div>
  </div>
  <Dialog
    v-model:visible="state.multipleOrdersPaymentDialog"
    closeOnEscape
    :modal="true"
  >
    <div class="col-12">
      <PayBulkOtherOrders
        :resetOrder="resetOrder"
        :paymentAmount="mergedOrdersCurrentBalance"
        :mergedOrders="
          state.mergedOrders.map((el) => {
            return el.id
          })
        "
        @payed="state.multipleOrdersPaymentDialog = false"
      />
    </div>
  </Dialog>

  <Dialog
    v-model:visible="state.openReceiptDialog"
    closeOnEscape
    :modal="false"
    :breakpoints="orderDialogBreakpoints"
    :dismissableMask="true"
    keepInViewPort
  >
    <Receipt :transaction_id="state.receipt_transaction_id" />
  </Dialog>

  <Dialog
    v-model:visible="state.dialogPrintRentalStatement"
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
          v-model="state.rentalStatementDates"
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
        @click="printRentalStatement()"
        :disabled="state.loadingPrintRentalStatement"
        :loading="state.loadingPrintRentalStatement"
        label="View Rental Statement"
        class="m-1 p-button-accent p-button-lg"
      />
    </div>
  </Dialog>
</template>

<script setup>
  import CustomerDetail from "./CustomerDetail.vue"
  import OrderDetail from "./OrderDetail.vue"
  import RentDetail from "./RentDetail.vue"
  import LineItem from "./LineItem.vue"
  import QuickPay from "./QuickPay.vue"
  import LineItemDetail from "./LineItemDetail.vue"
  import { dfa, dfc } from "@/service/DateFormat.js"
  import Receipt from "@/pages/Receipt.vue"
  import PaymentFields from "./payment/PaymentFields.vue"

  import ViewApplication from "../applications/ViewApplication.vue"
  import ApplicationStatus from "../applications/ApplicationStatus.vue"
  import PaymentHistory from "./PaymentHistory.vue"
  import ViewTransactionType from "./payment/ViewTransactionType.vue"
  import RentalPaymentSchedule from "./RentalPaymentSchedule.vue"
  import { useUsers } from "@/store/modules/users"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { computed, inject, onMounted, watch } from "vue"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import { reactive, ref } from "vue"
  import AccountService from "@/service/Account.js"
  import NoteDetail from "../notes/NoteDetail.vue"
  import CustomerApi from "@/api/customers"
  import Cart from "@/service/Cart.js"
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"
  import AchFields from "./payment/AchFields.vue"
  import PayBulkOtherOrders from "./PayBulkOtherOrders.vue"
  import CustomerChatLog from "./CustomerChatLog.vue"
  import ReportingFilterOptions from "../reporting/ReportingFilterOptions.vue"
  import { useRouter } from "vue-router"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import UploadApi from "@/api/upload.js" // Import the UploadApi class
  import { useToast } from "primevue/usetoast"
  const toast = useToast()

  const intervalManager = new IntervalManager()
  const reportsApi = new ReportsApi()
  const useLoadingStateStore = loadingStateStore()
  const router = useRouter()
  const cart = new Cart()
  const customerApi = new CustomerApi()
  const customerOrderStore = useCustomerOrder()
  const $ability = inject("$ability")
  const $fc = inject("$formatCurrency")
  const uploadApi = new UploadApi()

  const $isObjectPopulated = inject("$isObjectPopulated")

  const props = defineProps({
    swapCustomerOrder: {
      type: Function,
      required: false,
      default: () => {}
    },
    openDialog: {
      type: Function,
      default: () => {}
    }
  })

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

  const selectedApplication = computed(() => {
    return (
      customerStore.order?.application_response.filter((e) =>
        $isObjectPopulated(e.response_content)
      )[state.application_response] || {}
    )
  })
  const allApplications = computed(() => {
    return customerStore.order?.application_response
  })
  const hasRushFees = computed(() => {
    return (
      customerStore.order.fees.filter((e) => {
        return e.fee_type == "RUSH"
      }).length > 0
    )
  })
  const runReport = async (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]

    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: state.selectedAccount,
      order_ids: state.mergedOrders.map((el) => el.id),
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

  const openDialog = (display_order_id) => {
    props.openDialog(display_order_id)
  }

  const receiptClick = () => {
    state.receipt_transaction_id = slotProps.data.id
    state.openReceiptDialog = true
  }

  const accountService = new AccountService()

  const customerStore = useCustomerOrder()
  const paymentFieldsDisabled = false

  const extend = computed(() => {
    const lineItems = cloneDeep(customerStore.order).line_items
    for (var i = 0; i < lineItems.length; i++) {
      if (lineItems[i].inventory !== null) {
        return true
      }
    }
    return false
  })

  const initMultipleOrdersPayment = () => {
    state.multipleOrdersPaymentDialog = true
  }

  const usersStore = useUsers()

  const orderDialogBreakpoints = computed(() => {
    return {
      "2000px": application.value ? "130vw" : "80vw",
      "1400px": application.value ? "130vw" : "80vw",
      "1200px": application.value ? "96vw" : "75vw",
      "992px": "95vw",
      "600px": "100vw",
      "480px": "100vw",
      "320px": "100vw"
    }
  })

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")

  const isRent = computed(() => {
    return customerStore.order?.type === "RENT"
  })

  const isRentToOwn = computed(() => {
    return customerStore.order?.type === "RENT_TO_OWN"
  })

  const isPurchase = computed(() => {
    return (
      (customerStore.order?.type === "PURCHASE") |
      (customerStore.order?.type === "PURCHASE_ACCESSORY")
    )
  })

  const isPaid = computed(() => {
    return (
      customerStore.order?.status === "Paid" ||
      customerStore.order?.status === "Partially Paid" ||
      customerStore.order?.status === "Delivered" ||
      customerStore.order?.status === "Completed"
    )
  })

  const mergedOrdersCurrentBalance = computed(() => {
    let sum = 0
    state.mergedOrders.forEach((el) => {
      sum += el.calculated_rent_balance
    })
    return sum
  })

  const applicationAccepted = computed(() => {
    return selectedApplication.value.date_accepted
  })

  const isOnlyOneRentPeriod = computed(() => {
    if (isRent) {
      let isOnlyOneRentPeriod = customerStore?.order?.rent_periods?.length === 1
      return isOnlyOneRentPeriod
    } else {
      return false
    }
  })

  const showApplication = computed(() => {
    const allowRentApplications = usersStore?.cms?.applications?.rent
    const allowRentToOwnApplications =
      usersStore?.cms?.applications?.rent_to_own
    const allowPurchaseApplications = usersStore?.cms?.applications?.purchase

    const onPage =
      state.active ===
        filteredComponentList.value.indexOf("Purchase Application") ||
      state.active === filteredComponentList.value.indexOf("Applications") ||
      state.active ===
        filteredComponentList.value.indexOf("Rent to own Application")
    if (isRent.value) {
      return allowRentApplications && onPage
    }
    if (isRentToOwn.value) {
      return allowRentToOwnApplications && onPage
    }
    if (isPurchase.value) {
      return allowPurchaseApplications && onPage
    }
  })

  const paymentDetailsDisabled = computed(() => {
    if (customerStore.order?.override_application_process) return false

    return (
      customerStore.order?.order_contract?.findIndex((contract) => {
        return contract?.status?.toLowerCase() === "contract-signed"
      }) === -1
    )
  })

  const creditCardFeeToggleEnabled = computed(() => {
    return usersStore.cms?.credit_card_fees.enable_toggle_credit_card_fees
  })

  const showHistorySchedule = computed(() => {
    return (
      applicationAccepted &&
      (state.active ===
        filteredComponentList.value.indexOf("Rental Schedule & History") ||
        state.active ===
          filteredComponentList.value.indexOf(
            "Rental to own Schedule & History"
          ) ||
        state.active === filteredComponentList.value.indexOf("Payment History"))
    )
  })

  const application = computed(() => {
    return (
      $isObjectPopulated(selectedApplication.value.response_content) ||
      $isObjectPopulated(customerStore.order?.file_upload) ||
      null
    )
  })

  const filteredComponentList = computed(() => {
    const orderDetailTitle =
      customerOrderStore.order?.type != "RENT"
        ? `Order Detail`
        : `Customer Detail`

    let componentsList = []
    if (isRent.value) {
      if (customerOrderStore.order?.customer_profile_id !== null) {
        componentsList = [
          orderDetailTitle,
          "Rental Detail",
          "Other Order",
          "Notes",
          "Applications",
          "Update Payment Method",
          "Rental Schedule & History"
        ].filter((e) => {
          if (e === "Applications")
            return $ability.can("read", "rental_application")
          if (e === "Update Payment Method")
            return $ability.can("update", "payment_method")
          if (e === "Rental Schedule & History")
            return $ability.can("view", "rental_schedule")
          return true
        })
      } else {
        componentsList = [
          orderDetailTitle,
          "Rental Detail",
          "Other Order",
          "Notes",
          "Applications",
          "Add Payment Method",
          "Rental Schedule & History"
        ]
      }
    }
    if (isRentToOwn.value) {
      if (customerOrderStore.order.customer_profile_id !== null) {
        componentsList = [
          orderDetailTitle,
          "Rental Detail",
          "Other Order",
          "Notes",
          "Rent to own Application",
          "Update Payment Method",
          "Rent to own Schedule & History"
        ]
      } else {
        componentsList = [
          orderDetailTitle,
          "Rental Detail",
          "Other Order",
          "Notes",
          "Rent to own Application",
          "Add Payment Method",
          "Rent to own Schedule & History"
        ]
      }
    }
    if (isPurchase.value) {
      if (
        applicationAccepted.value ||
        customerStore.order?.override_application_process
      ) {
        componentsList = [
          orderDetailTitle,
          "Rental Detail",
          "Other Order",
          "Notes",
          "Purchase Application",
          "Charge Card",
          "Payment History",
          "Customer Chat Log"
        ]
      } else {
        componentsList = [
          orderDetailTitle,
          "Rental Detail",
          "Notes",
          "Purchase Application",
          "Payment History",
          "Customer Chat Log"
        ]
      }
    }

    return componentsList.filter((component) => {
      if (component == "Customer Chat Log") {
        return $ability.can("view", "customer_chat")
      }
      if (component == "Other Order") {
        return state.other_orders.length > 1
      }
      if (component === "Rental Detail") {
        return (
          usersStore?.cms?.uses_other_orders && state.mergedOrders.length >= 1
        )
      }
      if (component === "Applications") {
        return usersStore?.cms?.applications?.rent
      }
      if (
        component === "Rent to own Application" ||
        component === "Rent to own Schedule & History"
      ) {
        return usersStore?.cms?.applications?.rent_to_own
      }
      if (component === "Purchase Application") {
        return usersStore?.cms?.applications?.purchase
      }

      if (component === "Charge Card") {
        return usersStore?.cms?.internal_payment_enabled && isUnpaidStatus.value
      }
      return true
    })
  })

  const printRentalStatement = async () => {
    let request = {
      dates: state.rentalStatementDates
    }
    state.loadingPrintRentalStatement = true
    const { data, error } =
      await customerApi.printRentalStatementMultipleOrders(
        customerStore.order.single_customer.id,
        request
      )
    state.loadingPrintRentalStatement = false

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error generating rental statement.",
        group: "br",
        life: 5000
      })
    } else {
      window.open(data.value["pdf_url"], "_blank")
    }
  }

  const isUnpaidStatus = computed(() => {
    return (
      customerStore.order?.status?.toLowerCase() === "invoiced" ||
      customerStore.order?.status?.toLowerCase() === "partially paid" ||
      customerStore.order?.status?.toLowerCase() === "delayed" ||
      customerStore.order?.status?.toLowerCase() === "estimate" ||
      customerStore.order?.status?.toLowerCase() === "purchase order" ||
      customerStore.order?.status?.toLowerCase() === "quote"
    )
  })

  const updateSelectedRentPeriods = (newVal) => {
    state.selectedRentPeriodRows = newVal
  }

  const overridePaymentAmount = computed(() => {
    let amount = 0
    if (state.selectedRentPeriodRows.length > 0) {
      state.selectedRentPeriodRows.map((period) => {
        amount += period.calculated_rent_period_total_balance
      })
    }
    return amount
  })

  const bankFee = computed(() => {
    let cms = customerOrderStore.publicCms || usersStore.cms
    let bankFees = cart.roundIt(
      customerStore.order.calculated_remaining_order_balance *
        cms.convenience_fee_rate,
      2
    )

    if (customerStore.order.type === "RENT") {
      const rent_periods = customerStore.order.rent_periods.filter((item) =>
        selectedRentPeriodsIds.value.includes(item.id)
      )
      bankFees = cart.roundIt(
        rent_periods.reduce(
          (accumulator, crt) =>
            accumulator + crt["calculated_rent_period_total_balance"],
          0
        ) * cms.convenience_fee_rate,
        2
      )
    }

    return bankFees
  })

  const selectedRentPeriodsIds = computed(() => {
    let rentPeriodsIds = []
    state.selectedRentPeriodRows.forEach((period) => {
      rentPeriodsIds.push(period.id)
    })
    return rentPeriodsIds
  })

  const reloadRentalPeriod = (updatedOrder, isOrderAlreadyUpdated = false) => {
    if (!isOrderAlreadyUpdated) {
      customerStore.setOrder(null)
      customerStore.setOrder(updatedOrder)
    }
    state.selectedRentPeriodRows = []
    state.forceReloadKey += 1
  }
  const responsiveOptions = ref([
    {
      breakpoint: "1199px",
      numVisible: 1,
      numScroll: 1
    },
    {
      breakpoint: "991px",
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: "767px",
      numVisible: 1,
      numScroll: 1
    }
  ])

  const resetOrder = async () => {
    const { data, isLoading, error } = await customerApi.getOrderByDisplayId(
      customerStore.order.display_order_id
    )
    customerStore.setOrder(null)
    customerStore.setOrder(data.value)
    console.log("order updated in Pinia")
    if (usersStore?.cms?.uses_other_orders) {
      if (customerStore.order.single_customer !== null) {
        const { data, error } =
          await customerApi.customerSearchSingleCustomerId(
            customerStore.order.single_customer.id
          )
        state.mergedOrders = []
        state.other_orders = []
        if (data?.value) {
          data.value.forEach((order) => {
            if (!order.is_archived) {
              state.mergedOrders.push(order)
            }
          })
        }
      }
    }
    await setPhotos()
  }

  const state = reactive({
    active: 0,
    isResetting: false,
    selectedRentPeriodRows: [],
    isInternal: true,
    forceReloadKey: 0,
    mergedOrders: [],
    ach: false,
    isUpdateAch: false,
    can_use_credit_card: false,
    isUpdateCreditCard: false,
    account_number: "",
    routing_number: "",
    bank_name: "",
    ach_payment_profile_present: false,
    credit_card_payment_profile_present: false,
    multipleOrdersPaymentDialog: false,
    transactions_report: [],
    openReceiptDialog: false,
    application_response: 0,
    mappedPhotos: [],
    other_orders: [],
    dialogPrintRentalStatement: false,
    rentalStatementDates: [],
    loadingPrintRentalStatement: false
  })

  const setPhotos = async () => {
    if (customerStore.order?.file_upload && !state.mappedPhotos.length) {
      const uploads = Array.isArray(customerStore.order?.file_upload)
        ? customerStore.order?.file_upload
        : [customerStore.order?.file_upload]

      const promises = uploads.map((u) => {
        return uploadApi.getPresignedGetUrl(
          u.filename,
          u.folder_type,
          customerStore.order.account_id,
          customerStore.order.id,
          null
        )
      })
      Promise.all(promises).then((values) => {
        state.mappedPhotos = values.map((v, i) => {
          return {
            ...uploads[i],
            presigned_url: v.data.value
          }
        })
        if (
          customerStore.order?.application_response.length == 0 &&
          state.mappedPhotos.length > 0
        ) {
          state.application_response = -1
        }
      })
    }
  }

  if (!state.mappedPhotos.length && customerStore.order?.file_upload) {
    setPhotos()
  }

  const refresh_customer_profile = async () => {
    const customerProfileId = customerOrderStore.order.customer_profile_id
    if (customerProfileId) {
      const { data, error } = await customerApi.getCustomerProfile(
        customerProfileId
      )

      state.ach_payment_profile_present = false
      state.credit_card_payment_profile_present = false

      for (var i = 0; i < data.value.profile.paymentProfiles.length; i++) {
        if (
          data?.value?.profile?.paymentProfiles[i]?.payment?.bankAccount !=
          undefined
        ) {
          state.isUpdateAch = true
          state.ach_payment_profile_present = true
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

        if (
          data?.value?.profile?.paymentProfiles[i]?.payment?.creditCard !=
          undefined
        ) {
          state.credit_card_payment_profile_present = true
        }
      }
    }
  }

  onMounted(async () => {
    try {
      resetOrder()

      let state_active = state.active
      if (usersStore?.cms.order_detail_active_tab) {
        state_active = usersStore?.cms.order_detail_active_tab
      }

      if (state_active === 1 && state.mergedOrders.length < 2) {
        state_active = 0
      }
      state.active = state_active

      await refresh_customer_profile()
      state.can_use_credit_card = orderCanUseCreditCard(
        customerOrderStore.order
      )
    } catch (err) {
      console.error("Error during onMounted execution:", err)
    }
  })

  watch(
    () => customerStore.order,
    async (newVal, oldVal) => {
      const customerProfileId = customerOrderStore?.order?.customer_profile_id
      if (customerProfileId) {
        const { data, error } = await customerApi.getCustomerProfile(
          customerProfileId
        )
        for (var i = 0; i < data.value.profile.paymentProfiles.length; i++) {
          if (
            data?.value?.profile?.paymentProfiles[i]?.payment?.bankAccount !=
            undefined
          ) {
            state.isUpdateAch = true
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

          if (
            data?.value?.profile?.paymentProfiles[i]?.payment?.creditCard !=
            undefined
          ) {
            state.isUpdateCreditCard = true
          }
        }
      }
      await setPhotos()
      state.can_use_credit_card = orderCanUseCreditCard(
        customerOrderStore.order
      )
    }
  )
</script>
