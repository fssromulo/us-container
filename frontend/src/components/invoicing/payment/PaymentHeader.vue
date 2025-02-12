<template>
  <div class="mt-4">
    <div v-html="props.displayMessage"></div>
  </div>
  <div class="grid grid-cols-12 gap-4 grid-nogutter">
    <div class="col-span-1 md:col-start-3">
      <div class="">
        <img
          :src="props.cms?.logo_settings?.logo_path"
          alt="Image"
          height="100"
        />
      </div>
    </div>
    <div :class="cms?.invoice_message ? 'col-span-6' : 'col-span-5'">
      <Message
        v-if="cms?.invoice_message"
        severity="info"
        :closable="false"
        class="p-1"
      >
        {{ cms?.invoice_message }}
      </Message>
    </div>
    <div :class="cms?.invoice_message ? 'col-span-1' : 'col-span-3'">
      <div class="p-4 mt-2">
        <div
          class="mb-4 text-2xl font-medium text-900 dark:text-0"
          v-if="isRental"
        >
          {{ displayRentalTitle }} #{{ props.orderDetails.display_order_id }}-{{
            selectedRentPeriodNumber
          }}
        </div>
        <div class="mb-4 text-2xl font-medium text-900 dark:text-0" v-else>
          {{ displayQuoteOrInvoice }} #{{ props.orderDetails.display_order_id }}
        </div>
        <Button
          @click="
            selectedRentPeriod?.id !== '' &&
            selectedRentPeriod?.id !== undefined
              ? printRentalPage()
              : printPage()
          "
          class="p-button-sm p-button-rounded"
          :loading="state.isLoading"
          >Print</Button
        >
      </div>
    </div>
  </div>
  <div class="grid grid-cols-12 gap-4 grid-nogutter">
    <div class="col-span-12 p-2"></div>
    <!-- <div class="col-span-12 md:col-span-2 p"></div> -->
    <div class="col-span-12 mt-2 md:col-span-3 md:col-start-3">
      <div class="mb-4 text-xl font-medium text-500 dark:text-300">
        {{ cms.account_name }}
      </div>
      <div
        v-if="props?.cms?.show_office_contact_details_header"
        class="mb-4 text-lg text-500 dark:text-300"
        >Office Contact Details:</div
      >
      <div class="mb-4 text-lg text-500 dark:text-300">
        {{ props.cms.company_mailing_address }}
      </div>
      <div class="mb-4 text-lg text-500 dark:text-300">
        <a :href="`tel:+1${$fp(props.cms.quote_contact_phone)}`">{{
          $fp(props.cms.quote_contact_phone)
        }}</a>
      </div>
      <div class="mb-4 text-lg text-500 dark:text-300">
        {{ props.cms.quote_contact_email }}
      </div>
      <br />
      <div v-if="props.orderDetails?.user?.phone" class="text-lg font-bold">
        Sales Rep Details:
      </div>
      <div
        v-if="props.orderDetails?.user?.display_name"
        class="mt-4 text-lg font-bold"
      >
        {{ props.orderDetails.user.display_name }}
      </div>
      <div
        v-if="props.orderDetails?.user?.phone"
        class="mt-4 text-lg font-bold"
      >
        <a :href="`tel:+1${$fp(props.orderDetails.user.phone)}`">{{
          $fp(props.orderDetails.user.phone)
        }}</a>
      </div>
    </div>
    <div v-if="isRental" class="col-span-12 mt-2 md:col-span-3">
      <div
        class="mb-4 text-xl font-medium text-500 dark:text-300"
        v-if="
          selectedRentPeriod &&
          selectedRentPeriod.calculated_rent_period_total_balance === 0
        "
        ><strong>Paid on {{ dfm(lastPaymentDate) }}</strong></div
      >
      <div
        v-if="selectedRentPeriod"
        class="mb-4 text-xl font-medium text-500 dark:text-300"
        >ORDER DATES</div
      >
      <div v-if="selectedRentPeriod" class="mb-4 text-lg text-900 dark:text-0">
        {{ displayQuoteOrInvoice }}d for:
        {{ selectedRentPeriod?.calculated_rent_period_display_dates }}
      </div>
    </div>
    <div v-if="!isRental" class="col-span-12 mt-2 md:col-span-3">
      <div class="mb-4 text-xl font-medium text-500 dark:text-300"
        >ORDER DATES</div
      >
      <div class="mb-4 text-lg text-900 dark:text-0">
        {{ displayQuoteOrInvoice }}d on:
        {{ dfm(props.orderDetails.created_at) }}
      </div>
      <div class="text-lg text-900 dark:text-0"
        >Valid through: {{ expirationDate }}</div
      >
    </div>
    <div class="col-span-12 mt-2 md:col-span-3">
      <div class="mb-4 text-xl font-medium text-500 dark:text-300">BILLING</div>
      <div class="mb-4 text-lg text-900 dark:text-0">
        {{ customer?.first_name }}
        {{ customer?.last_name }}
      </div>
      <div class="mb-4 text-lg text-900 dark:text-0">
        {{ customer?.company_name }}
      </div>
      <div
        class="mb-4 text-lg text-900 dark:text-0"
        v-if="!props.cms.hide_billing_addr_on_invoice"
      >
        {{
          props.orderDetails?.billing_address?.full_address ||
          props.orderDetails?.address?.full_address
        }}
      </div>
      <div class="mt-2 mb-4 text-lg text-900 dark:text-0">
        <a :href="`tel:+1${$fp(customer?.phone)}`">{{
          $fp(customer?.phone)
        }}</a>
      </div>
      <template v-if="props.isDelivery">
        <div class="mb-4 text-xl font-medium text-500 dark:text-300"
          >DELIVERY</div
        >
        <div
          v-if="hasContainerAddresses"
          class="text-lg text-900 dark:text-0"
          v-for="(line_item, index) in props.orderDetails.line_items"
          :key="index"
        >
          {{
            line_item?.inventory_address.length != 0
              ? line_item?.inventory_address[0].address.full_address
              : ""
          }},
        </div>
        <div v-else class="text-lg text-900 dark:text-0">
          {{ props.orderDetails?.address?.full_address }}
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
  import { reactive, computed, inject } from "vue"
  import { dfl, dfm } from "@/service/DateFormat.js"
  import CustomerApi from "@/api/customers"

  const $d = inject("$DateTime")
  const $fp = inject("$formatPhone")
  const $isObjectPopulated = inject("$isObjectPopulated")
  const customerApi = new CustomerApi()

  const props = defineProps({
    orderDetails: {
      type: Object,
      required: true
    },
    cms: {
      type: Object,
      required: true
    },
    isDelivery: {
      type: Boolean,
      required: true
    },
    displayMessage: {
      type: String,
      required: true
    },
    selectedRentPeriodId: {
      type: String,
      default: ""
    }
  })

  const customer = computed(() => {
    return props.orderDetails?.customer !== null
      ? props.orderDetails.customer
      : props.orderDetails?.single_customer
  })

  const hasContainerAddresses = computed(() => {
    return props.orderDetails?.line_items?.some(
      (line_item) => line_item?.inventory_address?.length > 0
    )
  })

  const printRentalPage = async () => {
    state.isLoading = true

    const { data, error } = await customerApi.downloadRentalInvoice(
      props.orderDetails?.id,
      props.selectedRentPeriodId
    )
    if (error.value) {
      console.error("There was a problem with the request:", error.value)
      return
    }

    if (data.value) {
      if (data.value.pdf_url) {
        window.open(data.value.pdf_url, "_blank")
        return
      }
      const blob = new Blob([data.value], { type: "application/pdf" })
      const url = URL.createObjectURL(blob)

      const a = document.createElement("a")
      a.href = url
      a.download = "invoice.pdf"

      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)

      URL.revokeObjectURL(url)
    }
    state.isLoading = false
  }

  const printPage = async () => {
    state.isLoading = true

    const { data, error } = await customerApi.downloadInvoice(
      props.orderDetails?.id,
      props?.cms?.use_paid_pdf_generator
    )
    if (error.value) {
      console.error("There was a problem with the request:", error.value)
      return
    }

    if (data.value) {
      if (data.value.pdf_url) {
        window.open(data.value.pdf_url, "_blank")
        return
      }
      const blob = new Blob([data.value], { type: "application/pdf" })
      const url = URL.createObjectURL(blob)

      const a = document.createElement("a")
      a.href = url
      a.download = "invoice.pdf"

      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)

      URL.revokeObjectURL(url)
    }
    state.isLoading = false
  }
  const isRental = computed(() => {
    return props.orderDetails?.type == "RENT"
  })
  const displayQuoteOrInvoice = computed(() => {
    return props.orderDetails?.attributes?.is_quote_title ? "Quote" : "Invoice"
  })
  const displayRentalTitle = computed(() => {
    return `Rental ${displayQuoteOrInvoice.value}`
  })

  const expirationDate = computed(() => {
    return dfm(
      $d
        .fromISO(props.orderDetails.created_at)
        .plus({ days: props.cms?.order_expire_days || 5 })
    )
  })

  const selectedRentPeriod = computed(() => {
    if (props.orderDetails.rent_periods.length == 0) {
      return null
    }
    return props.orderDetails.rent_periods.find(
      (rentPeriod) => rentPeriod.id === props.selectedRentPeriodId
    )
  })
  const lastPaymentDate = computed(() => {
    return selectedRentPeriod.value.transaction_type_rent_period.reduce(
      (latest, obj) => {
        return new Date(obj.created_at) > new Date(latest)
          ? obj.created_at
          : latest
      },
      selectedRentPeriod.value.transaction_type_rent_period[0]?.created_at
    )
  })

  const selectedRentPeriodNumber = computed(() => {
    return (
      props.orderDetails.rent_periods
        .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
        .findIndex(
          (rentPeriod) => rentPeriod.id === props.selectedRentPeriodId
        ) + 1
    )
  })

  const state = reactive({
    message: "Hello World",
    isLoading: false
  })
</script>
