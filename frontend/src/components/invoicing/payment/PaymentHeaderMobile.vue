<template>
  <div class="mt-4">
    <div v-html="props.displayMessage"></div>
  </div>

  <div class="flex justify-center">
    <Message
      v-if="cms?.invoice_message"
      class="w-9/12"
      severity="info"
      :closable="false"
    >
      {{ cms?.invoice_message }}
    </Message>
  </div>

  <div class="">
    <div class="flex justify-center">
      <!-- <img src="/images/blocks/hyper-cyan.svg" alt="Image" height="75" /> -->
      <img :src="props.cms.logo_settings.logo_path" alt="Image" height="100" />
    </div>
    <!-- <div class="col-span-12 md:col-span-3"></div> -->
    <div class="flex justify-center p-2 mt-2">
      <div
        class="mb-2 text-2xl font-medium text-900 dark:text-0"
        v-if="isRental"
      >
        {{ displayRentalTitle }} #{{ props.orderDetails.display_order_id }}-{{
          selectedRentPeriodNumber
        }}
      </div>
      <div v-else class="mb-2 text-2xl font-medium text-900 dark:text-0">
        {{ displayQuoteOrInvoice }} #{{ props.orderDetails.display_order_id }}
      </div>
    </div>
    <div class="flex justify-center">
      <button
        @click="printPage"
        class="p-button-sm p-button-rounded"
        :loading="state.isLoading"
      >
        Print
      </button>
    </div>

    <div class="col-span-12 p-2"></div>
    <!-- <div class="col-span-12 md:col-span-2 p"></div> -->
    <div class="mt-2">
      <div
        class="flex justify-center mb-2 text-xl font-medium text-500 dark:text-300"
      >
        {{ cms.account_name }}
      </div>
      <div
        v-if="props?.cms?.show_office_contact_details_header"
        class="flex justify-center mt-4 mb-2 text-lg text-500 dark:text-300"
      >
        Office Contact Details:
      </div>
      <div class="flex justify-center mb-2 text-lg text-500 dark:text-300">
        {{ props.cms.company_mailing_address }}
      </div>
      <div class="flex justify-center mb-2 text-lg text-500 dark:text-300">
        {{ props.cms.quote_contact_email }}
      </div>
      <div class="flex justify-center mb-2 text-lg text-500 dark:text-300">
        <a :href="`tel:+1${$fp(props.cms.quote_contact_phone)}`">{{
          $fp(props.cms.quote_contact_phone)
        }}</a>
      </div>
      <br />
      <div
        v-if="props.orderDetails?.user?.display_name"
        class="flex justify-center mb-2 text-lg font-bold"
      >
        Sales Rep Details:
      </div>
      <div
        v-if="props.orderDetails?.user?.display_name"
        class="flex justify-center mb-2 text-lg font-bold"
      >
        {{ props.orderDetails.user.display_name }}
      </div>
      <div
        v-if="props.orderDetails?.user?.phone"
        class="flex justify-center mb-2 text-lg font-bold"
      >
        <a :href="`tel:+1${$fp(props.orderDetails.user.phone)}`">{{
          $fp(props.orderDetails.user.phone)
        }}</a>
      </div>
    </div>
    <div v-if="!isRental" class="mt-6">
      <div
        class="flex justify-center mb-2 text-xl font-medium text-500 dark:text-300"
      >
        ORDER DATES
      </div>
      <div class="flex justify-center mb-2 text-lg text-900 dark:text-0">
        {{ displayQuoteOrInvoice }}d on:
        {{ dfm(props.orderDetails.created_at) }}
      </div>
      <div class="flex justify-center text-lg text-900 dark:text-0">
        Valid through: {{ expirationDate }}
      </div>
    </div>
    <div v-if="isRental">
      <div
        class="flex justify-center mb-2 text-xl font-medium text-500 dark:text-300"
        v-if="selectedRentPeriod.calculated_rent_period_total_balance === 0"
        ><strong>Paid on {{ dfm(lastPaymentDate) }}</strong></div
      >

      <div
        class="flex justify-center mb-2 text-xl font-medium text-500 dark:text-300"
      >
        ORDER DATES
      </div>
      <div class="flex justify-center mb-2 text-lg text-900 dark:text-0">
        {{ displayQuoteOrInvoice }}d for:
        {{ selectedRentPeriod?.calculated_rent_period_display_dates }}
      </div>
    </div>

    <div class="mt-6">
      <div
        class="flex justify-center mb-2 text-xl font-medium text-500 dark:text-300"
      >
        BILLING
      </div>
      <div class="flex justify-center mb-2 text-lg text-900 dark:text-0">
        {{ customer?.first_name }}
        {{ customer?.last_name }}
      </div>
      <div class="flex justify-center mb-2 text-lg text-900 dark:text-0">
        {{ customer?.company_name }}
      </div>
      <div class="flex justify-center mt-2 mb-2 text-lg text-900 dark:text-0">
        <a :href="`tel:+1${$fp(customer?.phone)}`">{{
          $fp(customer?.phone)
        }}</a>
      </div>
      <template v-if="props.isDelivery">
        <div
          class="flex justify-center mt-6 mb-2 text-xl font-medium text-500 dark:text-300"
        >
          DELIVERY
        </div>
        <div
          v-if="!hasContainerAddresses"
          class="flex justify-center text-lg text-900 dark:text-0"
        >
          {{ props.orderDetails.address?.full_address }}
        </div>
        <div
          v-else
          class="flex justify-center text-lg text-900 dark:text-0"
          v-for="(line_item, index) in props.orderDetails.line_items"
          :key="index"
        >
          {{
            line_item?.inventory_address.length != 0
              ? line_item?.inventory_address[0].address.full_address
              : ""
          }},
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
    isCancelled: {
      type: Boolean,
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
  const lastPaymentDate = computed(() => {
    return selectedRentPeriod.value.transaction_type_rent_period.reduce(
      (latest, obj) => {
        return new Date(obj.created_at) > new Date(latest)
          ? obj.created_at
          : latest
      },
      selectedRentPeriod.value.transaction_type_rent_period[0].created_at
    )
  })

  const isRental = computed(() => {
    return props.orderDetails.type === "RENT"
  })

  const selectedRentPeriod = computed(() => {
    return props.orderDetails.rent_periods.find(
      (rentPeriod) => rentPeriod.id === props.selectedRentPeriodId
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

  const displayMessage = () => {
    const termsMessage = `Terms and conditions read and accepted on ${dfl(
      props.orderDetails.paid_at
    )}`

    const termsHtml = `<div class='flex justify-center mt-2 flex-nowrap md:text-2xl'>
      ${termsMessage}
      </div>`
    if (props.isPaidFully) {
      let paidMessage = isRentToOwn.value
        ? props.cms.rto_paid_message
        : props.cms.paid_message

      return `<div class='flex justify-center flex-nowrap md:text-2xl'>
        ${paidMessage} .
        </div>
        ${termsHtml}`
    }
    if (props.orderDetails.status.toLowerCase() === "partially paid") {
      return termsHtml
    }
    if (props.isCancelled) {
      return `<div class='flex justify-center flex-nowrap md:text-2xl'>
        ${props.cms.quote_cancelled_message}
        </div>`
    }
    if (
      props.orderDetails.status.toLowerCase() === "expired" &&
      Number(props.orderDetails.calculated_remaining_order_balance) !== 0
    ) {
      return `<div class='flex justify-center flex-nowrap md:text-2xl'>
        ${props.cms.quote_expired_message}
        </div>`
    }
  }

  const isRentToOwn = computed(() => {
    return props.orderDetails.type === "RENT_TO_OWN"
  })

  const displayQuoteOrInvoice = computed(() => {
    return props.orderDetails.attributes?.is_quote_title ? "Quote" : "Invoice"
  })

  const expirationDate = computed(() => {
    return dfm(
      $d
        .fromISO(props.orderDetails.created_at)
        .plus({ days: props.cms?.order_expire_days || 5 })
    )
  })

  const state = reactive({
    message: "Hello World",
    isLoading: false
  })
</script>

<style scoped></style>
