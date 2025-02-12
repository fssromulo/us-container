<template>
  <div
    v-if="
      (!customerOrderStore.publicOrder || !customerOrderStore.publicCms) &&
      state.loading
    "
    class="flex-auto surface-border border-round surface-section"
  >
    <div class="flex flex-col items-center pt-8 mt-8">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
    </div>
  </div>
  <div
    v-if="customerOrderStore.publicOrder && customerOrderStore.publicCms"
    class="flex-auto surface-border border-round surface-section"
  >
    <PaymentHeader
      v-if="!mdAndSmaller"
      :orderDetails="customerOrderStore.publicOrder"
      :cms="customerOrderStore.publicCms"
      :isDelivery="isDelivery()"
      :displayMessage="displayMessage"
    />
    <PaymentHeaderMobile
      v-if="mdAndSmaller"
      :isCancelled="isCancelled"
      :orderDetails="customerOrderStore.publicOrder"
      :cms="customerOrderStore.publicCms"
      :isDelivery="isDelivery()"
      :displayMessage="displayMessage"
    />
    <div class="mt-3 surface-border border-top-1 col-12"></div>
    <div
      v-if="isEstimate"
      class="flex flex-col items-center my-4 mt-1 mb-2 text-2xl"
    >
      This is an estimate. Please contact us to finalize your order.
    </div>
    <div
      v-if="isQuote"
      class="flex flex-col items-center my-4 mt-1 mb-2 text-2xl"
    >
      This is a quote. Please accept the quote to recieve an invoice.
    </div>
    <div
      v-if="isQuote"
      class="flex flex-col items-center my-4 mt-1 mb-2 text-2xl"
    >
      <Button
        label="Accept Quote"
        @click="acceptQuote"
        :loading="state.loading"
        class="mt-3 row p-button-secondary p-button-lg"
      />
    </div>

    <PaymentWarranties
      :currentOrder="customerOrderStore.publicOrder"
      v-if="canDisplayGurantee"
    />
    <div
      class="flex flex-col items-center ml-1"
      v-if="convertOrderToCart.formattedCart.length > 0"
    >
      <div class="mb-3 md:col-8 col-12">
        <RentalCart
          v-if="isRental"
          :verticalTable="smAndSmaller"
          :cart="convertOrderToCart.formattedCart"
          :showContainerPlusShipping="
            customerOrderStore.publicOrder?.attributes?.show_subtotal_only
          "
          :showConvenienceFee="
            state.creditCardSelected ||
            customerOrderStore.publicOrder.line_items[0].convenience_fee > 0
          "
          :customerOrderProp="customerOrderStore?.publicOrder"
          :thirtyDayPrice="state.summaryGrandTotal"
          :accountId="customerOrderStore?.order?.account_id"
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
          :isPaymentPage="true"
        />
        <PurchaseCart
          v-if="isPurchase"
          :verticalTable="smAndSmaller"
          :cart="convertOrderToCart.formattedCart"
          :showContainerPlusShipping="
            customerOrderStore.publicOrder?.attributes?.show_subtotal_only
          "
          :showConvenienceFee="
            state.creditCardSelected ||
            customerOrderStore.publicOrder.line_items[0].convenience_fee > 0
          "
          :customerOrderProp="customerOrderStore?.publicOrder"
          :thirtyDayPrice="state.summaryGrandTotal"
          :accountId="customerOrderStore?.order?.account_id"
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
          :isPaymentPage="true"
        />
        <AccessoryCart
          v-if="isAccessory"
          :verticalTable="smAndSmaller"
          :cart="convertOrderToCart.formattedCart"
          :showContainerPlusShipping="
            customerOrderStore.publicOrder?.attributes?.show_subtotal_only
          "
          :showConvenienceFee="
            state.creditCardSelected ||
            customerOrderStore.publicOrder.line_items[0].convenience_fee > 0
          "
          :customerOrderProp="customerOrderStore?.publicOrder"
          :thirtyDayPrice="state.summaryGrandTotal"
          :accountId="customerOrderStore?.order?.account_id"
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
          :isPaymentPage="true"
        />
        <RentToOwnCart
          v-if="isRentToOwn"
          :verticalTable="smAndSmaller"
          :cart="convertOrderToCart.formattedCart"
          :showContainerPlusShipping="
            customerOrderStore.publicOrder?.attributes?.show_subtotal_only
          "
          :showConvenienceFee="
            state.creditCardSelected ||
            customerOrderStore.publicOrder.line_items[0].convenience_fee > 0
          "
          :customerOrderProp="customerOrderStore?.publicOrder"
          :thirtyDayPrice="state.summaryGrandTotal"
          :accountId="customerOrderStore?.order?.account_id"
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
          :isPaymentPage="true"
        />
      </div>
    </div>

    <div
      v-if="
        cartService.cartColumnsAccessories.length &&
        convertOrderAccessoryToCart.formattedCart.length > 0
      "
      class="flex flex-col items-center my-4 mt-1 mb-2 text-2xl"
    >
      *Accessories shipped separately
    </div>

    <div
      class="flex flex-col items-center ml-1"
      v-if="convertOrderAccessoryToCart.formattedCart.length > 0"
    >
      <div class="mb-3 md:col-8 col-12">
        <RentalCart
          v-if="isRental"
          :verticalTable="smAndSmaller"
          :columnsFieldMap="cartService.cartColumnsAccessories"
          :cart="convertOrderAccessoryToCart.formattedCart"
          :showContainerPlusShipping="
            customerOrderStore.publicOrder?.attributes?.show_subtotal_only
          "
          :customerOrderProp="customerOrderStore?.publicOrder"
          :showConvenienceFee="false"
          :isAccessory="true"
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
        />
        <PurchaseCart
          v-if="isPurchase"
          :verticalTable="smAndSmaller"
          :columnsFieldMap="cartService.cartColumnsAccessories"
          :cart="convertOrderAccessoryToCart.formattedCart"
          :showContainerPlusShipping="
            customerOrderStore.publicOrder?.attributes?.show_subtotal_only
          "
          :customerOrderProp="customerOrderStore?.publicOrder"
          :showConvenienceFee="false"
          :isAccessory="true"
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
        />
        <AccessoryCart
          v-if="isAccessory"
          :verticalTable="smAndSmaller"
          :columnsFieldMap="cartService.cartColumnsAccessories"
          :cart="convertOrderAccessoryToCart.formattedCart"
          :showContainerPlusShipping="
            customerOrderStore.publicOrder?.attributes?.show_subtotal_only
          "
          :customerOrderProp="customerOrderStore?.publicOrder"
          :showConvenienceFee="false"
          :isAccessory="true"
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
        />
        <RentToOwn
          v-if="isRentToOwn"
          :verticalTable="smAndSmaller"
          :columnsFieldMap="cartService.cartColumnsAccessories"
          :cart="convertOrderAccessoryToCart.formattedCart"
          :showContainerPlusShipping="
            customerOrderStore.publicOrder?.attributes?.show_subtotal_only
          "
          :customerOrderProp="customerOrderStore?.publicOrder"
          :showConvenienceFee="false"
          :isAccessory="true"
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
        />
      </div>
    </div>

    <div
      class="flex flex-col items-center"
      :class="{ 'ml-6': smAndSmaller || mdAndSmaller }"
    >
      <div class="mb-3 md:col-4 col-12">
        <CartSummary
          v-if="$isObjectPopulated(customerOrderStore.publicOrder)"
          :verticalTable="smAndSmaller"
          :summaryItemsDict="summaryItems"
          :sumGrandTotal="state.summaryGrandTotal"
          :totalRtoPrice="state.totalRtoPrice"
          :isRentToOwn="isRentToOwn"
          :isRent="isRental"
          :remainingBalance="
            remainingBalanceCalc < getPriceAndBalance.totalPrice
              ? remainingBalanceCalc
              : null
          "
          :monthlyPrice="state.monthlyTotal"
          :estimatedSalesTax="
            customerOrderStore.publicOrder.calculated_order_tax
          "
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
          :downPayment="
            $fc(customerOrderStore.publicOrder.calculated_down_payment)
          "
        />
      </div>
    </div>
    <!-- added the && state.creditcardselected so that the parent controls whether or not this gets displayed for
      the credit/debit card selection button. This way, it will reset the props passed to the child-->
    <div class="flex flex-col flex-auto" v-if="boxesDropDown.length > 0">
      <div class="flex flex-col items-center mt-3">
        <div class="w-1/4">
          <label for="cvv" class="font-medium text-900">Boxes To Pay For</label
          ><br />
          <MultiSelect
            v-model="state.box_index_to_pay_for"
            class="w-full text-md"
            :options="boxesDropDown"
            optionLabel="label"
            optionValue="value"
          />
        </div>
      </div>
    </div>
    <PaymentFields
      v-if="
        state.can_use_credit_card &&
        customerOrderStore.publicOrder &&
        customerOrderStore.publicCms
      "
      :creditCardSelected="state.creditCardSelected"
      :bank-fee="state.toBeAssessedBankFee"
      :is-partial="false"
      :overridePaymentAmount="state.overridePaymentAmount"
      :update-from-payment-fields="updateFromPaymentFields"
      :boxesBeingPaidFor="state.boxes_to_pay_for"
      :disable-all-fields="state.disableAllFields"
      :is-internal="state.isInternal"
      :creditCardFeeToggleEnabled="creditCardFeeToggleEnabled"
      :updateOrderAfterFeeToggle="updateOrderAfterFeeToggle"
      :hasStripeEnabled="
        hasStripeEnabled &&
        customerOrderStore.publicOrder &&
        customerOrderStore.publicCms
      "
      :isDriverPayment="true"
      :canPartialPay="false"
    />

    <div
      v-if="shouldDisplayTermsAndConditions"
      class="flex flex-col items-center mt-4"
    >
      <p class="text-2xl">Terms & Conditions</p>
    </div>

    <div v-if="shouldDisplayTermsAndConditions">
      <div
        class="flex flex-col items-center terms-conditions"
        style="max-width: 98vw"
        v-html="mappedTermsAndConditions"
      ></div>
    </div>
  </div>
  <Teleport to="#target-footer">
    <Footer
      :class="state.creditCardSelected ? '' : 'mt-4'"
      :cms="customerOrderStore.publicCms"
    />
  </Teleport>
</template>
<script setup>
  import {
    reactive,
    onMounted,
    inject,
    computed,
    watch,
    ref,
    onBeforeMount
  } from "vue"
  import Footer from "@/components/footer/Footer.vue"
  import PaymentHeader from "./PaymentHeader.vue"
  import ApplyCouponCode from "./ApplyCouponCode.vue"
  import AppliedCoupons from "./AppliedCoupons.vue"

  import PaymentHeaderMobile from "./PaymentHeaderMobile.vue"
  import PaymentFields from "./PaymentFields.vue"
  import AchFields from "./AchFields.vue"
  import PaymentWarranties from "./PaymentWarranties.vue"
  import { dfl } from "@/service/DateFormat.js"

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import CustomerApi from "@/api/customers"
  import AccountApi from "@/api/account"
  import CartService from "@/service/Cart"
  import PurchaseCart from "@/components/cart/PurchaseCart.vue"
  import AccessoryCart from "@/components/cart/AccessoryCart.vue"
  import RentalCart from "@/components/cart/RentalCart.vue"
  import RentToOwnCart from "@/components/cart/RentToOwnCart.vue"
  import CartSummary from "@/components/cart/CartSummary.vue"
  import CreditApplication from "@/components/applications/CreditApplication.vue"
  import { useTaxes } from "@/store/modules/taxes"
  import TaxApi from "@/api/tax"
  import { accountMap } from "../../../utils/accountMap"
  import PricingService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"

  import AccountService from "@/service/Account.js"
  import { useUsers } from "@/store/modules/users.js"
  import { changeCountry } from "@/utils/formatCurrency.js"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import isObjectPopulated from "../../../utils/isObjectPopulated"
  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const mdAndSmaller = breakpoints.isSmaller("lg") // md and larger
  import CouponApi from "@/api/coupon"
  import { useContainerPrices } from "@/store/modules/pricing"
  import { useToast } from "primevue/usetoast"
  import MultiSelect from "primevue/multiselect"
  import { roundHalfUp } from "@/utils/formatCurrency.js"

  const toast = useToast()
  const couponApi = new CouponApi()
  const $isPayment = inject("$isPayment")
  const pricingStore = useContainerPrices()

  const $route = inject("$route")
  const $fc = inject("$formatCurrency")
  const $isPublic = inject("$isPublic")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const pricingService = new PricingService()
  const pricingApi = new PricingApi()
  const containerPriceStore = useContainerPrices()
  const userStore = useUsers()
  const accountService = new AccountService()
  const customerOrderStore = useCustomerOrder()
  const taxStore = useTaxes()
  const customerApi = new CustomerApi()
  const accountApi = new AccountApi()
  const cartService = new CartService()
  const taxApi = new TaxApi()
  const imgWidth = computed(() => {
    if (smAndSmaller) return 80
    return 100
  })
  const state = reactive({
    applyCoupon: false,
    showApplciation: false,
    paymentMethodDialog: false,
    paymentDialogContent: null,
    isPartial: false,
    error: null,
    selectedStep: 0,
    isDeliveryAddress: true,
    alwaysTrue: true,
    paymentMessage: null,
    user: null,
    agreeToTerms: false,
    totalRtoPrice: null,
    paymentStarted: false,
    loading: false,
    customerPaidDialog: false,
    partialPayAmount: 0,
    showTermsConditions: false,
    creditCardSelected: true,
    orderDetails: null,
    cms: null,
    summaryGrandTotal: null,
    bankFee: 0,
    toBeAssessedBankFee: 0,
    estimatedSalesTax: 0,
    couponDiscount: null,
    allCoupons: [],
    disableAllFields: false,
    isInternal: false,
    show_pay_and_start_auto_pay: false,
    pay_and_store_card: false,
    achSelected: false,
    applicationSchemas: [],
    selectedApplicationType: null,
    selectedSchema: [],
    line_item_container_number: {},
    prepay: false,
    pay_on_delivery_visible: false,
    sending_pod_contract: false,
    boxes_to_pay_for: [],
    box_index_to_pay_for: [],
    overridePaymentAmount: 0,
    can_use_credit_card: false,

    delivery_days: null
  })
  const isPickup = computed(() => {
    return customerOrderStore?.publicOrder?.is_pickup
  })

  const isRentalsFeatureVisible = computed(() => {
    return customerOrderStore.publicCms?.feature_flags?.rentals_enabled
  })

  const creditCardFeeToggleEnabled = computed(() => {
    return userStore.cms?.credit_card_fees.enable_toggle_credit_card_fees
  })

  const updateFromPaymentFields = (newData) => {
    if (newData.isPartial !== undefined) {
      state.isPartial = newData.isPartial
    }
    if (newData.partialPayAmount !== undefined) {
      state.partialPayAmount = newData.partialPayAmount
    }
  }

  const fetchSchema = async () => {
    const result = await customerApi.getApplicationSchemasByName(
      customerOrderStore.publicOrder.type,
      customerOrderStore.publicOrder.id
    )
    if (result.data.value) {
      state.applicationSchemas = result.data.value
    }
  }

  const applicationTypeOptions = computed(() => {
    return state.applicationSchemas.map((el) => {
      return {
        name: el.full_schema_name,
        value: el.id
      }
    })
  })
  const canPayWithCreditCard = computed(() => {
    return customerOrderStore.publicOrder.calculated_sub_total_price < 20000
  })
  const mappedTermsAndConditions = computed(() => {
    if (!customerOrderStore.publicCms) return null
    if (paidInFull()) {
      return `<div style="width: 95vw; word-wrap: break-word;">${customerOrderStore.publicCms.terms_and_conditions_paid}</div>`
    } else {
      return `<div style="word-wrap: break-word;">${customerOrderStore.publicCms.terms_and_conditions}</div>`
    }
  })
  const roundIt = (number, decimalPlaces = null) => {
    let returnNum = 0
    decimalPlaces == null
      ? (returnNum = Math.round(number))
      : (returnNum = Math.round(number * 10 ** decimalPlaces) / 100)
    return returnNum
  }

  const subHeadingMessage = computed(() => {
    if (isRentToOwn.value) {
      return customerOrderStore.publicCms?.rto_subheading_message
    }
    if (isRental.value) {
      return customerOrderStore.publicCms?.rental_payment_message
    }
    return customerOrderStore.publicCms?.bank_fee_message
  })

  const isRentToOwn = computed(() => {
    return customerOrderStore.publicOrder.type === "RENT_TO_OWN"
  })

  const isRental = computed(() => {
    return customerOrderStore.publicOrder.type === "RENT"
  })

  const isPurchase = computed(() => {
    return customerOrderStore.publicOrder.type === "PURCHASE"
  })

  const isAccessory = computed(() => {
    return customerOrderStore.publicOrder.type === "PURCHASE_ACCESSORY"
  })

  const totalPrice = computed(() => {
    let total = 0
    customerOrderStore.publicOrder.line_items.forEach((l) => {
      if (isRentToOwn.value || isRental.value) {
        total += Number(l.monthly_owed)
      } else {
        total += cartService.addTotalForItem(l)
      }
    })
    return $fc(total)
  })

  const applicationResponse = computed(() => {
    return (
      customerOrderStore.publicOrder?.application_response?.response_content ||
      {}
    )
  })

  const isCancelled = computed(() => {
    return customerOrderStore.publicOrder?.status?.toLowerCase() === "cancelled"
  })

  const isEstimate = computed(() => {
    return customerOrderStore.publicOrder?.status?.toLowerCase() === "estimate"
  })

  const isQuote = computed(() => {
    return customerOrderStore.publicOrder?.status?.toLowerCase() === "quote"
  })

  const isInvoice = computed(() => {
    return customerOrderStore.publicOrder?.status?.toLowerCase() === "invoiced"
  })

  const convertOrderToCart = computed(() => {
    if (!customerOrderStore.publicOrder || !customerOrderStore.publicCms)
      return {}
    let cart
    if (customerOrderStore.publicOrder.type != "RENT") {
      cart = cartService.dtoOrderToCart(
        customerOrderStore.publicOrder,
        state.creditCardSelected,
        customerOrderStore.publicCms.convenience_fee_rate,
        null,
        customerOrderStore.publicCms.account_country
      )
    } else {
      cart = cartService.dtoOrderToCart(
        customerOrderStore.publicOrder,
        state.creditCardSelected,
        customerOrderStore.publicCms.convenience_fee_rate,
        customerOrderStore.publicOrder.first_payment_strategy,
        customerOrderStore.publicCms.account_country
      )
    }
    cart.forEach((el, index) => {
      el.container_number = state.line_item_container_number[el.product_id]
    })

    return {
      cart: cart,
      formattedCart: cartService.formatCart(cart)
    }
  })
  const convertOrderAccessoryToCart = computed(() => {
    if (!customerOrderStore.publicOrder || !customerOrderStore.publicCms)
      return {}
    let cart = cartService.dtoOrderAccessoryToCart(
      customerOrderStore.publicOrder,
      state.creditCardSelected,
      customerOrderStore.publicCms.convenience_fee_rate
    )
    return {
      cart: cart,
      formattedCart: cartService.formatCart(cart)
    }
  })

  const displayMessage = computed(() => {
    let termsMessage = ""
    if (paidInFull()) {
      termsMessage = `Terms and conditions read and accepted on ${dfl(
        customerOrderStore.publicOrder.paid_at
      )}`
    } else if (
      customerOrderStore.publicOrder.status.toLowerCase() === "partially paid"
    ) {
      customerOrderStore.publicOrder.credit_card.sort((a, b) => {
        const dateA = new Date(a.created_at)
        const dateB = new Date(b.created_at)
        return dateA - dateB
      })
      if (customerOrderStore.publicOrder.credit_card.length > 0) {
        let firstCreditCardPayment =
          customerOrderStore.publicOrder.credit_card[0]
        let acceptedTermsAndCondDate = firstCreditCardPayment.created_at
        termsMessage = `Terms and conditions read and accepted on ${dfl(
          acceptedTermsAndCondDate
        )}`
      }
    }

    const termsHtml = `<div class='flex mt-2 justify-content-center flex-nowrap md:text-2xl'>
        ${termsMessage}
        </div>`
    if (
      $isObjectPopulated(
        customerOrderStore.publicOrder.application_response?.response_content
      ) &&
      !paidInFull()
    ) {
      if (customerOrderStore.publicOrder?.application_response?.date_rejected) {
        return `<div class='flex justify-content-center flex-nowrap md:text-2xl'>
        Application Rejected - ${dfl(
          customerOrderStore.publicOrder?.application_response?.date_rejected
        )}
        </div>`
      } else if (
        customerOrderStore.publicOrder?.application_response?.date_accepted
      ) {
        return `<div class='flex justify-content-center flex-nowrap md:text-2xl'>
        Application Accepted - ${dfl(
          customerOrderStore.publicOrder?.application_response?.date_accepted
        )}
        </div>`
      } else if (pod_signed.value) {
        return `Contract Signed - ${dfl(
          customerOrderStore.publicOrder?.application_response?.created_at
        )}`
      } else {
        return `<div class='flex justify-content-center flex-nowrap md:text-2xl'>
        Application Submitted - ${dfl(
          customerOrderStore.publicOrder?.application_response?.created_at
        )}
        </div>`
      }
    }

    if (
      $isObjectPopulated(
        customerOrderStore.publicOrder.application_response?.response_content
      ) &&
      paidInFull() &&
      customerOrderStore.publicOrder.type === "RENT"
    ) {
      return `<div class='flex justify-content-center flex-nowrap md:text-2xl'>
        Down payment paid - Next rent payment due on
        </div>`
    }

    if (
      customerOrderStore.publicOrder.status.toLowerCase() === "paid" ||
      customerOrderStore.publicOrder.status.toLowerCase() === "completed" ||
      customerOrderStore.publicOrder.status.toLowerCase() === "delivered" ||
      (customerOrderStore.publicOrder.status.toLowerCase() === "delayed" &&
        customerOrderStore.publicOrder.calculated_remaining_order_balance == 0)
    ) {
      let paidMessage = isRentToOwn.value
        ? customerOrderStore.publicCms.rto_paid_message
        : customerOrderStore.publicCms.paid_message

      return `<div class='flex justify-content-center flex-nowrap md:text-2xl'>
        ${paidMessage}
        </div>
        ${termsHtml}`
    }
    if (
      customerOrderStore.publicOrder.status.toLowerCase() === "partially paid"
    ) {
      return termsHtml
    }

    if (isCancelled.value) {
      let termsMessage = ""
      if (customerOrderStore.publicOrder.paid_at) {
        termsMessage = `Terms and conditions read and accepted on ${dfl(
          customerOrderStore.publicOrder.paid_at
        )}`
      }

      return `<div class='flex justify-content-center flex-nowrap md:text-2xl'>
        ${customerOrderStore.publicCms.quote_cancelled_message}
        </div>
        <div class='flex mt-2 justify-content-center flex-nowrap md:text-2xl'>
        ${termsMessage}
        </div>`
    }

    if (customerOrderStore.publicOrder.status.toLowerCase() === "expired") {
      return `<div class='flex justify-content-center flex-nowrap md:text-2xl'>
        ${customerOrderStore.publicCms.quote_expired_message}
        </div>`
    }
  })

  const capitalizeFirstLetter = (inputString) => {
    return (
      inputString.charAt(0).toUpperCase() + inputString.slice(1).toLowerCase()
    )
  }

  const deliveryPeriodTexts = computed(() => {
    return `Delivery within ${state.delivery_days?.delivery_days} business days`
  })

  const canApplyCoupon = computed(() => {
    let canApplyCoupon = false
    state.allCoupons?.forEach(function (coupon) {
      const date = Date.now()
      const coupon_start_date = new Date(coupon.start_date)
      const coupon_end_date = new Date(coupon.end_date)
      const res = customerOrderStore.publicOrder.line_items.filter((item) => {
        return (
          (coupon.type == "external" || coupon.type == "both") &&
          (Object.keys(coupon.size).length === 0 ||
            coupon.size?.hasOwnProperty(item.title)) &&
          (Object.keys(coupon.city).length == 0 ||
            coupon.city.hasOwnProperty(item.product_city)) &&
          ((date >= coupon_start_date && date <= coupon_end_date) ||
            coupon.is_permanent)
        )
      })
      canApplyCoupon = canApplyCoupon || res.length > 0
    })
    return canApplyCoupon
  })

  const hasCoupon = computed(() => {
    return customerOrderStore.publicOrder.coupon_code_order.length > 0
  })

  const boxesDropDown = computed(() => {
    return customerOrderStore.publicOrder.line_items
      .filter(
        (e) =>
          e.product_type !== "CONTAINER_ACCESSORY" &&
          (!e.paid_at || e.paid_at == null)
      )
      .map((li, index) => {
        return {
          value: li.id,
          price: li.shipping_revenue + li.revenue,
          tax: li.tax,
          label: `Pay for ${li.title} @ ${$fc(
            li.shipping_revenue + li.revenue
          )} `
        }
      })
  })
  const getCalculatedDiscount = computed(() => {
    return customerOrderStore.publicOrder?.calculated_discount
  })

  const updateOrderAfterFeeToggle = (val) => {
    customerOrderStore.publicOrder.credit_card_fee = val
  }

  const summaryItems = computed(() => {
    if (!customerOrderStore.publicOrder || !customerOrderStore.publicCms) {
      return {}
    }

    const cart = convertOrderToCart.value.cart
    const accessoryCart = convertOrderAccessoryToCart.value.cart

    const subTotal = customerOrderStore.publicOrder.calculated_sub_total_price
    const calculatedRevenueExcludingShipping =
      customerOrderStore.publicOrder.calculated_revenue_excluding_shipping
    const estimatedSalesTax = calculateEstimatedSalesTax()
    const shipping = calculateShipping(cart, accessoryCart)
    const fees = customerOrderStore.publicOrder.fees
    const totalFeesWithoutBankFee =
      customerOrderStore.publicOrder.calculated_fees_without_bank_fee

    resetStateVars()

    const bankFees = calculateBankFees(fees)
    if (customerOrderStore.publicOrder.credit_card_fee) {
      state.bankFee = bankFees
      state.toBeAssessedBankFee = 0
    } else {
      state.bankFee = 0
    }
    if (
      state.creditCardSelected &&
      customerOrderStore.publicOrder.credit_card_fee
    ) {
      const assessedBankFee = calculateAssessedBankFee()
      if (isRental.value) {
        state.bankFee = 0
        state.toBeAssessedBankFee = 0
      } else {
        state.toBeAssessedBankFee += assessedBankFee
        state.bankFee += assessedBankFee
      }
      if (!isRental.value) {
        state.partialPayAmount += assessedBankFee
      }
    }

    state.summaryGrandTotal = calculateGrandTotal(
      calculatedRevenueExcludingShipping + shipping,
      estimatedSalesTax,
      totalFeesWithoutBankFee,
      state.bankFee
    )

    if (isRentToOwn.value) {
      handleRentToOwn(
        subTotal,
        estimatedSalesTax,
        shipping,
        totalFeesWithoutBankFee
      )
    }

    if (isRental.value) {
      handleRental(estimatedSalesTax)
    }

    return generateReturnList(
      subTotal,
      calculatedRevenueExcludingShipping,
      shipping,
      estimatedSalesTax,
      state.bankFee,
      fees
    )
  })

  function calculateEstimatedSalesTax() {
    return customerOrderStore.publicOrder.type === "RENT"
      ? customerOrderStore.publicOrder.calculated_rent_order_tax
      : customerOrderStore.publicOrder.calculated_order_tax
  }

  function calculateShipping(cart, accessoryCart) {
    return (
      (cart?.reduce((acc, item) => acc + item.shipping_revenue, 0) || 0) +
      (accessoryCart?.reduce((acc, item) => acc + item.shipping_revenue, 0) ||
        0)
    )
  }

  function resetStateVars() {
    state.bankFee = 0
    state.toBeAssessedBankFee = 0
    state.couponDiscount = getCalculatedDiscount.value
  }

  function calculateBankFees(fees) {
    if (fees.some((item) => item.type.name === "CREDIT_CARD")) {
      return fees.reduce(
        (acc, item) =>
          item.type.name === "CREDIT_CARD" ? acc + item.fee_amount : acc,
        0
      )
    }
    return 0
  }

  function calculateAssessedBankFee() {
    let amtToAssess = state.isPartial
      ? state.partialPayAmount /
        (1 + customerOrderStore.publicCms.convenience_fee_rate)
      : customerOrderStore.publicOrder.calculated_remaining_order_balance

    return roundHalfUp(
      amtToAssess * customerOrderStore.publicCms.convenience_fee_rate
    )
  }
  const pod_signed = computed(() => {
    return customerOrderStore.publicOrder.signed_at ? true : false
  })

  function calculateGrandTotal(
    subTotal,
    estimatedSalesTax,
    totalFeesWithoutBankFee,
    bankFee
  ) {
    return $fc(
      subTotal +
        estimatedSalesTax +
        totalFeesWithoutBankFee +
        (customerOrderStore.publicOrder.credit_card_fee ? bankFee : 0)
    )
  }

  function handleRentToOwn(
    subTotal,
    estimatedSalesTax,
    shipping,
    totalFeesWithoutBankFee
  ) {
    state.monthlyTotal = $fc(
      customerOrderStore.publicOrder.calculated_monthly_price
    )
    state.summaryGrandTotal = calculateGrandTotal(
      subTotal,
      estimatedSalesTax,
      totalFeesWithoutBankFee,
      state.bankFee
    )
    state.totalRtoPrice = $fc(
      customerOrderStore.publicOrder.calculated_rto_price
    )
    state.estimatedSalesTax = estimatedSalesTax
  }

  function handleRental(estimatedSalesTax) {
    state.summaryGrandTotal = $fc(
      customerOrderStore.publicOrder.rent_periods[0]
        ?.calculated_rent_period_total_balance
    )
    state.estimatedSalesTax = estimatedSalesTax
  }

  function generateReturnList(
    subTotal,
    revenueExcludingShipping,
    shipping,
    estimatedSalesTax,
    bankFees,
    fees
  ) {
    let returnList = []
    if (
      customerOrderStore?.publicOrder?.attributes?.show_subtotal_only &&
      isPurchase.value &&
      isAccessory.value &&
      revenueExcludingShipping + shipping > 0
    ) {
      returnList.push({
        rowTitle: "Subtotal",
        rowContent: $fc(revenueExcludingShipping + shipping)
      })
    } else {
      if (!isRental.value && revenueExcludingShipping > 0) {
        returnList.push({
          rowTitle: "Subtotal",
          rowContent: $fc(revenueExcludingShipping)
        })
        if (shipping > 0) {
          returnList.push({
            rowTitle: "Shipping Subtotal",
            rowContent: $fc(shipping)
          })
        }
      }
    }

    if (isRental.value) {
      handleRentalReturnList(returnList, shipping)
    }

    addFeesToReturnList(returnList, fees)
    addCouponsToReturnList(returnList)
    adjustSubtotalForCoupons(returnList)

    if (isRental.value) {
      returnList = returnList.filter(
        (el) => el.rowTitle !== "Container Subtotal"
      )
    }

    if (bankFees > 0) {
      returnList.push({
        rowTitle: "Convenience Fee",
        rowContent: $fc(bankFees)
      })
    }

    if (estimatedSalesTax > 0) {
      returnList.push({
        rowTitle: "Sales Tax",
        rowContent: $fc(estimatedSalesTax)
      })
    }

    state.partialPayAmount = 0

    return returnList
  }

  function handleRentalReturnList(returnList, shipping) {
    const firstPaymentStrategy =
      customerOrderStore?.publicOrder?.first_payment_strategy ||
      getDownPaymentStrategy()
    if (
      firstPaymentStrategy === "FIRST_MONTH_PLUS_DELIVERY_&_PICKUP" ||
      firstPaymentStrategy === "FIRST_MONTH_PLUS_DELIVERY"
    ) {
      returnList.push({
        rowTitle: "Drop Off/Pickup",
        rowContent: $fc(shipping)
      })
    }
    returnList.push({
      rowTitle: "Rental Subtotal",
      rowContent: $fc(
        customerOrderStore.publicOrder.rent_periods[0]?.amount_owed
      )
    })
  }

  function getDownPaymentStrategy() {
    return $isPublic
      ? customerOrderStore.publicCms?.rent_options.down_payment_strategy
      : userStore?.cms?.rent_options.down_payment_strategy
  }

  function addFeesToReturnList(returnList, fees) {
    const tempFeeDict = fees.reduce((acc, item) => {
      if (item.type.name !== "CREDIT_CARD") {
        acc[item.type.name] = (acc[item.type.name] || 0) + item.fee_amount
      }
      return acc
    }, {})

    for (const [key, value] of Object.entries(tempFeeDict)) {
      returnList.push({
        rowTitle: `${capitalizeFirstLetter(key)} Fee`,
        rowContent: $fc(value)
      })
    }
  }

  function addCouponsToReturnList(returnList) {
    customerOrderStore.publicOrder.coupon_code_order.forEach((coupon) => {
      returnList.push({
        rowTitle: coupon.coupon.name,
        rowContent: `- ${$fc(fetchAppliedDiscount(coupon))}`,
        isCoupon: true
      })
    })
  }

  function adjustSubtotalForCoupons(returnList) {
    const sumCoupons = calculateSumCoupons()
    const element = returnList.find((el) => el.rowTitle === "Subtotal")
    if (element) {
      const subTotal =
        element.rowContent != 0
          ? element.rowContent?.replace(/[^0-9.-]+/g, "")
          : element.rowContent
      const actualSubtotal = parseFloat(subTotal) + sumCoupons
      element.rowContent = $fc(actualSubtotal)
    }
  }

  function calculateSumCoupons() {
    return customerOrderStore.publicOrder.coupon_code_order.reduce(
      (acc, coupon) => {
        return acc + fetchAppliedDiscount(coupon)
      },
      0
    )
  }
  const fetchAppliedDiscount = (coupon) => {
    let appliedAmount = 0
    coupon.coupon_line_item_value.forEach((value) => {
      appliedAmount = appliedAmount + value.amount
    })
    return appliedAmount
  }

  const getPriceAndBalance = computed(() => {
    let totalPrice = customerOrderStore.publicOrder.calculated_total_price
    let remainingBalance = Number(
      customerOrderStore.publicOrder.calculated_remaining_order_balance
    )

    // if credit card is selected and there are no convenience fees on existing order, add bank fee to remaining balance
    if (
      state.creditCardSelected &&
      !customerOrderStore.publicOrder.fees.some((item) => {
        return item["type"]["name"] === "CREDIT_CARD"
      })
    ) {
      remainingBalance = remainingBalance + state.bankFee
    }

    if (customerOrderStore.publicOrder.status === "Paid") {
      remainingBalance = 0
    }

    return {
      totalPrice: totalPrice,
      remainingBalance: remainingBalance
    }
  })

  const remainingBalanceCalc = computed(() => {
    const balances = getPriceAndBalance.value
    let rb =
      balances.remainingBalance > 0
        ? balances.remainingBalance - state.partialPayAmount
        : balances.totalPrice - state.partialPayAmount
    return Number(rb).toFixed(2)
  })

  const hasActiveCoupon = computed(() => {
    return state.allCoupons?.some(
      (coupon) =>
        (coupon.type == "external" || coupon.type == "both") &&
        (!coupon.is_expired || coupon.is_permanent) &&
        new Date(coupon.start_date).setHours(0, 0, 0, 0) <=
          new Date().setHours(0, 0, 0, 0) &&
        new Date(coupon.end_date).setHours(23, 59, 59, 999) >=
          new Date().setHours(0, 0, 0, 0)
    )
  })

  const hasStripeEnabled = computed(() => {
    return customerOrderStore.publicCms?.stripe_enabled
  })

  const loadCoupons = async () => {
    let { data } = await couponApi.getAllCouponsInsecure(
      customerOrderStore.publicOrder.account_id
    )
    state.allCoupons = data.value
    console.log(state.allCoupons)
  }
  const loadDeliveryDays = async () => {
    let availableCity = customerOrderStore.publicOrder.line_items.filter(
      (e) => e.product_city != null
    )
    if (availableCity.length > 0) {
      const { data } = await customerApi.getPublicDaysToDeliver(
        customerOrderStore.publicOrder.account_id,
        availableCity[0].product_city.split(",")
      )
      return data.value
    }
    return { delivery_days: "15" }
  }

  onMounted(async () => {
    if ($route.currentRoute.value.name === "Quote") {
      return
    }

    let dataLoc = await pricingApi.getLocationsPublic(
      accountMap[window.location.host].account_id
    )
    containerPriceStore.setLocations(
      dataLoc.data.value.map((location) => pricingService.dtoLocation(location))
    )

    if (taxStore.taxes.length === 0) {
      const { data } = await taxApi.getTaxesPublic(
        accountMap[window.location.host].account_id
      )
      taxStore.setTaxes(data.value)
    }
    state.loading = true
    const { data } = await customerApi.getOrderByIdPublic(
      $route.currentRoute.value.params.orderId
    )

    if (data.value == undefined) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Order does not exist or it was deleted.",
        group: "br",
        life: 5000
      })
      state.loading = false
      return
    }

    customerOrderStore.setPublicOrder(data.value)
    state.selectedApplicationType =
      data.value?.customer_application_schema?.id || null

    const res = await accountApi.getPublicAccount(
      customerOrderStore.publicOrder.account_id
    )
    state.delivery_days = await loadDeliveryDays()
    await loadCoupons()
    customerOrderStore.setPublicCms(res.data.value)

    if (hasStripeEnabled.value) {
      console.log("Setting up stripe")
      let stripeScript = document.createElement("script")
      stripeScript.setAttribute("src", "https://js.stripe.com/v3/")
      document.head.appendChild(stripeScript)
    }

    state.loading = false
    // if ($isPublic && customerOrderStore.publicCms?.has_analytics) {
    //   insertGoogleScript();
    //   insertGoogleScriptPayments();
    //   gtag("event", "quotecreation_data", {
    //     email_address: customerOrderStore.publicOrder.customer.email,
    //   });
    //   window.dataLayer = window.dataLayer || [];
    //   window.dataLayer.push({
    //     event: "quotecreation_data",
    //     email_address: customerOrderStore.publicOrder.customer.email,
    //   });

    // }

    let account_country = customerOrderStore.publicCms.account_country
    changeCountry(account_country)

    await fetchSchema()
    state.selectedSchema =
      state.selectedApplicationType === null
        ? []
        : state?.applicationSchemas
            ?.filter((el) => el.id === state.selectedApplicationType)
            .map((e) => e.content)[0] || []

    state.line_item_container_number = {}
    if (customerOrderStore.publicCms?.show_container_number_on_invoice) {
      customerOrderStore.publicOrder.line_items.forEach(async (el) => {
        const { data, error } = await customerApi.getLineItem(
          customerOrderStore.publicOrder.account_id,
          el.id
        )
        if (error.value == undefined && data.value.inventory != null)
          state.line_item_container_number[el.id] =
            data.value.inventory.container_number
      })
    }
    // const selectedOption = boxesDropDown.value[0]
    state.overridePaymentAmount = boxesDropDown.value.reduce(
      (sum, obj) => sum + obj.price + obj.tax,
      0
    )
    state.boxes_to_pay_for = [
      ...boxesDropDown.value.map((li) => {
        return li.value
      })
    ]
    state.box_index_to_pay_for = [...boxesDropDown.value.map((li) => li.value)]
    state.can_use_credit_card = orderCanUseCreditCard(
      customerOrderStore.publicOrder
    )
  })

  const acceptQuote = async () => {
    state.loading = true
    const { data } = await customerApi.acceptQuote(
      $route.currentRoute.value.params.orderId
    )
    const res = await accountApi.getPublicAccount(
      customerOrderStore.publicOrder.account_id
    )
    customerOrderStore.setPublicCms(res.data.value)
    state.loading = false
    window.location.reload()
  }

  const paidInFull = () => {
    return (
      customerOrderStore.publicOrder &&
      Number(
        customerOrderStore.publicOrder.calculated_remaining_order_balance
      ) === 0 &&
      (customerOrderStore.publicOrder.status === "Paid" ||
        customerOrderStore.publicOrder.status === "Current" ||
        customerOrderStore.publicOrder.status === "Completed" ||
        customerOrderStore.publicOrder.status === "Cancelled" ||
        customerOrderStore.publicOrder.status === "Partially Paid" ||
        customerOrderStore.publicOrder.status === "Delivered")
    )
  }

  const isExpired = () => {
    return (
      customerOrderStore.publicOrder &&
      customerOrderStore.publicOrder.status.toLowerCase() === "expired"
    )
  }
  const canDisplayGurantee = computed(() => {
    if (isEstimate.value || isQuote.value) {
      return true
    }
    let cms = customerOrderStore.publicCms.gurantees_present_on_status
    console.log(cms)
    let cms_status = Object.keys(cms).filter((status) => {
      return (
        convertFromSnakeCase(status).toLowerCase() ===
        customerOrderStore.publicOrder?.status?.toLowerCase()
      )
    })
    return cms_status.length > 0 && cms[cms_status[0]]
  })

  const isDelivery = () => {
    return customerOrderStore.publicOrder?.line_items?.some(
      (l) => Number(l.shipping_revenue) > 0
    )
  }
  watch(
    () => customerOrderStore.publicOrder,
    (newVal, oldValue) => {
      state.can_use_credit_card = orderCanUseCreditCard(
        customerOrderStore.publicOrder
      )
    }
  )
  watch(
    () => state.box_index_to_pay_for,
    (newVal, oldValue) => {
      if (newVal.length == 0) {
        // Reset it if nothing is selected
        state.box_index_to_pay_for = boxesDropDown.value.map((li) => li.value)
      }
      console.log("Boxes", boxesDropDown.value)
      state.overridePaymentAmount = boxesDropDown.value
        .filter((li) => {
          console.log(li.value)
          console.log(state.box_index_to_pay_for)
          return state.box_index_to_pay_for.includes(li.value)
        })
        .reduce((sum, obj) => sum + obj.price + obj.tax, 0)
      console.log("O", state.overridePaymentAmount)
      state.boxes_to_pay_for = [...state.box_index_to_pay_for]
    }
  )
  watch(
    () => state.selectedApplicationType,
    (newVal, oldValue) => {
      state.selectedSchema = []
      state.selectedSchema =
        newVal === null
          ? []
          : state?.applicationSchemas
              ?.filter((el) => el.id === newVal)
              .map((e) => e.content)[0] || []

      state.selectedSchemas = state?.applicationSchemas.map((e) => e.content)
      state.applicationSchemasObjectsType = state?.applicationSchemas
    }
  )
  const setupAch = () => {
    state.achSelected = !state.achSelected
  }

  const zelleLink = () => {
    // window.open(, "_blank");
    state.paymentDialogContent = customerOrderStore?.publicCms?.zelle_link
    state.paymentMethodDialog = true
  }
  const wireTransferLink = () => {
    // window.open(customerOrderStore.publicCms.wire_transfer_link, "_blank");
    state.paymentDialogContent =
      customerOrderStore?.publicCms?.wire_transfer_link
    state.paymentMethodDialog = true
  }
  const mailCheckLink = () => {
    // window.open(customerOrderStore.publicCms.mail_check_link, "_blank");
    state.paymentDialogContent = customerOrderStore?.publicCms?.mail_check_link
    state.paymentMethodDialog = true
  }
  const eCheckLink = () => {
    window.open(customerOrderStore.publicCms.echeck_link, "_blank")
    // // https://docs.google.com/forms/d/16gwUd2xjZ0ZOMitxLmVnF9M7axAoVZ8htMsv6fk8n3A/viewform?edit_requested=true
    // state.paymentDialogContent = '<div class="p-4 card" style="overflow: auto!important; -webkit-overflow-scrolling: touch!important;"><iframe scrolling="no" src="https://docs.google.com/forms/d/e/1FAIpQLSetnyRicTYIeHp-JIJ8DY5FzIM7r85ITxenW_CeSQeK004_Jw/viewform?embedded=true" width="100%" height="1300" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe><div class="p-4 card">'
    // state.paymentMethodDialog = true;
  }
  const rentToOwnApplicationLink = () => {
    state.showApplciation = !state.showApplciation
    if (isRentToOwn) {
      window.open(
        customerOrderStore.publicCms.rent_to_own_application_link,
        "_blank"
      )
    }
  }
  const rentApplicationLink = () => {
    state.showApplciation = !state.showApplciation
    if (!isRentalsFeatureVisible.value) {
      window.open(customerOrderStore.publicCms.rent_application_link, "_blank")
    }
  }
  const financeLink = () => {
    window.open(customerOrderStore.publicCms.finance_link, "_blank")
  }
  const openAccessorriesLink = () => {
    window.open(customerOrderStore.publicCms.accessories_link, "_blank")
  }
  const openRentLink = () => {
    window.open(customerOrderStore.publicCms.rent_link, "_blank")
  }
  const openRentToOwnLink = () => {
    window.open(customerOrderStore.publicCms.rto_link, "_blank")
  }
  const convertFromSnakeCase = (k) => {
    k = k.replace(/_/g, " ")
    k = k.replace(/\w\S*/g, function (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    })
    return k
  }
</script>
