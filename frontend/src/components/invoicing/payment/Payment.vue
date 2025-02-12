<template>
  <div
    v-if="
      (!customerOrderStore.publicOrder || !customerOrderStore.publicCms) &&
      state.loading
    "
    class="flex-auto border rounded-border bg-0 dark:bg-950"
  >
    <div class="flex flex-wrap justify-center pt-20 mt-20">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
    </div>
  </div>
  <div
    v-if="customerOrderStore.publicOrder && customerOrderStore.publicCms"
    class="flex-auto border rounded-border bg-0 dark:bg-950"
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
    <div class="col-span-12 mt-4 border border-t"></div>
    <div
      v-if="isEstimate"
      class="flex flex-wrap justify-center my-6 mt-1 mb-2 text-2xl"
    >
      This is an estimate. Please contact us to finalize your order.
    </div>
    <div
      v-if="isQuote"
      class="flex flex-wrap justify-center my-6 mt-1 mb-2 text-2xl"
    >
      This is a quote. Please accept the quote to recieve an invoice.
    </div>
    <div
      v-if="isQuote"
      class="flex flex-wrap justify-center my-6 mt-1 mb-2 text-2xl"
    >
      <Button
        label="Accept Quote"
        @click="acceptQuote"
        :loading="state.loading"
        class="mt-4 row p-button-secondary p-button-lg"
      />
    </div>

    <PaymentWarranties
      :currentOrder="customerOrderStore.publicOrder"
      :convertOrderToCart="convertOrderToCart"
      v-if="canDisplayGurantee"
    />
    <div
      class="flex flex-wrap justify-center ml-1"
      v-if="convertOrderToCart.formattedCart.length > 0"
    >
      <div class="col-span-12 mb-4 md:col-span-8">
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
          :showAbbrevTitleWContainerNumber="
            userStore?.cms?.container_number_on_invoice
          "
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
          :showAbbrevTitleWContainerNumber="
            userStore?.cms?.container_number_on_invoice
          "
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
          :showAbbrevTitleWContainerNumber="
            userStore?.cms?.container_number_on_invoice
          "
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
      class="flex flex-wrap justify-center my-6 mt-1 mb-2 text-2xl"
    >
      *Accessories shipped separately
    </div>

    <div
      class="flex flex-wrap justify-center ml-1"
      v-if="convertOrderAccessoryToCart.formattedCart.length > 0"
    >
      <div class="col-span-12 mb-4 md:col-span-8">
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

        <!-- <RentToOwnCart
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
        /> -->
      </div>
    </div>

    <div
      class="flex flex-wrap justify-center"
      :class="{ 'ml-6': smAndSmaller || mdAndSmaller }"
    >
      <div class="col-span-12 mb-4 md:col-span-4">
        <CartSummary
          v-if="$isObjectPopulated(customerOrderStore.publicOrder)"
          :verticalTable="smAndSmaller"
          :summaryItemsDict="summaryItems"
          :sumGrandTotal="state.summaryGrandTotal || 0"
          :totalRtoPrice="state.totalRtoPrice || 0"
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
    <div
      class="flex grid justify-center grid-cols-12 gap-4"
      v-if="
        isRentalsFeatureVisible &&
        showApplication &&
        !isObjectPopulated(applicationResponse) &&
        isRental &&
        !customerOrderStore.publicOrder['override_application_process']
      "
    >
      <div class="flex justify-center col-span-12 mb-2">
        <div class="text-center">
          <label class="text-2xl font-medium text-900">Apply Now!</label>
          <Select
            v-model="state.selectedApplicationType"
            style="height: 40px"
            icon="pi pi-plus"
            class="w-full mt-1"
            optionLabel="name"
            optionValue="value"
            placeholder="Select application type"
            :options="applicationTypeOptions"
          />
        </div>
      </div>
      <div class="flex justify-center col-span-12 mb-2">
        <CreditApplication
          :orderId="$route.currentRoute.value.params.orderId"
          :selectedSchema="state.selectedSchema"
          :selectedSchemaId="state.selectedApplicationType"
          style="max-width: 80vw"
        />
      </div>
    </div>
    <div class="flex flex-wrap justify-center ml-20">
      <div
        class="col-span-12 mb-4 md:col-span-4"
        v-if="$isObjectPopulated(customerOrderStore.publicOrder)"
      >
        <AppliedCoupons
          :appliedCoupons="customerOrderStore.publicOrder.coupon_code_order"
          :verticalTable="smAndSmaller"
        />
      </div>
    </div>
    <div class="flex flex-wrap justify-center ml-20" v-if="hasActiveCoupon">
      <div class="col-span-12 mb-4 md:col-span-4"></div>
      <div class="col-span-12 mb-4 md:col-span-2">
        <Button
          @click="applyCoupon"
          v-if="canApplyCoupon"
          :disabled="invoiceExpired"
          >Apply Coupon</Button
        >
      </div>
    </div>

    <div
      v-if="state.can_pay_on_delivery_order && !hasPrePaidCoupon"
      class="flex flex-wrap justify-center mb-4"
    >
      <Button
        class="justify-center mr-2 md:w-1/4 p-button-secondary p-button-lg"
        @click="state.prepay = !state.prepay"
      >
        Pay Now
      </Button>
      <Button
        class="justify-center ml-2 md:w-1/4 p-button-secondary p-button-lg"
        @click="state.pay_on_delivery_visible = true"
      >
        {{ pod_signed ? `View Contract` : `Pay On Delivery` }}
      </Button>
    </div>

    <div
      class="flex flex-wrap justify-center w-full gap-2"
      v-if="
        !isRentToOwn &&
        !isRental &&
        notPaidCancelledExpiredEstimateQuote &&
        (!state.can_pay_on_delivery_order || state.prepay)
      "
    >
      <div
        class="m-4"
        style="min-width: 20rem"
        v-if="customerOrderStore.publicCms.echeck_link"
      >
        <Button
          @click="eCheckLink"
          class="w-full p-button-secondary p-button-lg"
        >
          <div class="flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 512 512"
              class="mr-1"
            >
              <path
                d="M243.4 2.6l-224 96c-14 6-21.8 21-18.7 35.8S16.8 160 32 160v8c0 13.3 10.7 24 24 24H456c13.3 0 24-10.7 24-24v-8c15.2 0 28.3-10.7 31.3-25.6s-4.8-29.9-18.7-35.8l-224-96c-8-3.4-17.2-3.4-25.2 0zM128 224H64V420.3c-.6 .3-1.2 .7-1.8 1.1l-48 32c-11.7 7.8-17 22.4-12.9 35.9S17.9 512 32 512H480c14.1 0 26.5-9.2 30.6-22.7s-1.1-28.1-12.9-35.9l-48-32c-.6-.4-1.2-.7-1.8-1.1V224H384V416H344V224H280V416H232V224H168V416H128V224zM256 64a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"
                fill="white"
              />
            </svg>
            <span class="mx-4 text-2xl">eCheck</span>
          </div>
        </Button>
      </div>

      <div
        class="m-4"
        style="min-width: 20rem"
        v-if="customerOrderStore.publicCms.zelle_link"
      >
        <Button
          @click="zelleLink"
          class="w-full p-button-secondary p-button-lg"
        >
          <div class="flex items-center justify-center">
            <svg
              role="img"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              class="mr-1"
            >
              <title>Zelle</title>
              <path
                d="M13.559 24h-2.841a.483.483 0 0 1-.483-.483v-2.765H5.638a.667.667 0 0 1-.666-.666v-2.234a.67.67 0 0 1 .142-.412l8.139-10.382h-7.25a.667.667 0 0 1-.667-.667V3.914c0-.367.299-.666.666-.666h4.23V.483c0-.266.217-.483.483-.483h2.841c.266 0 .483.217.483.483v2.765h4.323c.367 0 .666.299.666.666v2.137a.67.67 0 0 1-.141.41l-8.19 10.481h7.665c.367 0 .666.299.666.666v2.477a.667.667 0 0 1-.666.667h-4.32v2.765a.483.483 0 0 1-.483.483"
                fill="#6D1ED4"
              />
            </svg>
            <span class="mx-4 text-2xl">Zelle</span>
          </div>
        </Button>
      </div>

      <div
        class="m-4"
        style="min-width: 20rem"
        v-if="customerOrderStore.publicCms.wire_transfer_link"
      >
        <Button
          label="Wire / ACH"
          @click="wireTransferLink"
          class="w-full p-button-secondary p-button-lg"
        >
          <div class="flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 640 512"
            >
              <path
                d="M535 41c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l64 64c4.5 4.5 7 10.6 7 17s-2.5 12.5-7 17l-64 64c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l23-23L384 112c-13.3 0-24-10.7-24-24s10.7-24 24-24l174.1 0L535 41zM105 377l-23 23L256 400c13.3 0 24 10.7 24 24s-10.7 24-24 24L81.9 448l23 23c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0L7 441c-4.5-4.5-7-10.6-7-17s2.5-12.5 7-17l64-64c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9zM96 64H337.9c-3.7 7.2-5.9 15.3-5.9 24c0 28.7 23.3 52 52 52l117.4 0c-4 17 .6 35.5 13.8 48.8c20.3 20.3 53.2 20.3 73.5 0L608 169.5V384c0 35.3-28.7 64-64 64H302.1c3.7-7.2 5.9-15.3 5.9-24c0-28.7-23.3-52-52-52l-117.4 0c4-17-.6-35.5-13.8-48.8c-20.3-20.3-53.2-20.3-73.5 0L32 342.5V128c0-35.3 28.7-64 64-64zm64 64H96v64c35.3 0 64-28.7 64-64zM544 320c-35.3 0-64 28.7-64 64h64V320zM320 352a96 96 0 1 0 0-192 96 96 0 1 0 0 192z"
                fill="white"
              />
            </svg>
            <span
              class="mx-4 text-2xl"
              v-if="customerOrderStore.publicCms.wire_ach_button_text"
              >{{ customerOrderStore.publicCms.wire_ach_button_text }}</span
            >
            <span class="mx-4 text-2xl" v-else>Wire / ACH</span>
          </div>
        </Button>
      </div>

      <div
        class="m-4"
        style="min-width: 20rem"
        v-if="customerOrderStore.publicCms.mail_check_link"
      >
        <Button
          @click="mailCheckLink"
          class="w-full p-button-secondary p-button-lg"
        >
          <div class="flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 576 512"
            >
              <path
                d="M64 64C28.7 64 0 92.7 0 128V384c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V128c0-35.3-28.7-64-64-64H64zM272 192H496c8.8 0 16 7.2 16 16s-7.2 16-16 16H272c-8.8 0-16-7.2-16-16s7.2-16 16-16zM256 304c0-8.8 7.2-16 16-16H496c8.8 0 16 7.2 16 16s-7.2 16-16 16H272c-8.8 0-16-7.2-16-16zM164 152v13.9c7.5 1.2 14.6 2.9 21.1 4.7c10.7 2.8 17 13.8 14.2 24.5s-13.8 17-24.5 14.2c-11-2.9-21.6-5-31.2-5.2c-7.9-.1-16 1.8-21.5 5c-4.8 2.8-6.2 5.6-6.2 9.3c0 1.8 .1 3.5 5.3 6.7c6.3 3.8 15.5 6.7 28.3 10.5l.7 .2c11.2 3.4 25.6 7.7 37.1 15c12.9 8.1 24.3 21.3 24.6 41.6c.3 20.9-10.5 36.1-24.8 45c-7.2 4.5-15.2 7.3-23.2 9V360c0 11-9 20-20 20s-20-9-20-20V345.4c-10.3-2.2-20-5.5-28.2-8.4l0 0 0 0c-2.1-.7-4.1-1.4-6.1-2.1c-10.5-3.5-16.1-14.8-12.6-25.3s14.8-16.1 25.3-12.6c2.5 .8 4.9 1.7 7.2 2.4c13.6 4.6 24 8.1 35.1 8.5c8.6 .3 16.5-1.6 21.4-4.7c4.1-2.5 6-5.5 5.9-10.5c0-2.9-.8-5-5.9-8.2c-6.3-4-15.4-6.9-28-10.7l-1.7-.5c-10.9-3.3-24.6-7.4-35.6-14c-12.7-7.7-24.6-20.5-24.7-40.7c-.1-21.1 11.8-35.7 25.8-43.9c6.9-4.1 14.5-6.8 22.2-8.5V152c0-11 9-20 20-20s20 9 20 20z"
                fill="white"
              />
            </svg>
            <span class="mx-4 text-2xl">Mail Check</span>
          </div>
        </Button>
      </div>

      <div
        class="m-4"
        style="min-width: 20rem"
        v-if="customerOrderStore.publicCms.wire_transfer_link && isRental"
      >
        <Button
          label="Setup ACH"
          @click="setupAch"
          class="w-full p-button-secondary p-button-lg"
        >
          <div class="flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 640 512"
            >
              <path
                d="M535 41c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l64 64c4.5 4.5 7 10.6 7 17s-2.5 12.5-7 17l-64 64c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l23-23L384 112c-13.3 0-24-10.7-24-24s10.7-24 24-24l174.1 0L535 41zM105 377l-23 23L256 400c13.3 0 24 10.7 24 24s-10.7 24-24 24L81.9 448l23 23c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0L7 441c-4.5-4.5-7-10.6-7-17s2.5-12.5 7-17l64-64c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9zM96 64H337.9c-3.7 7.2-5.9 15.3-5.9 24c0 28.7 23.3 52 52 52l117.4 0c-4 17 .6 35.5 13.8 48.8c20.3 20.3 53.2 20.3 73.5 0L608 169.5V384c0 35.3-28.7 64-64 64H302.1c3.7-7.2 5.9-15.3 5.9-24c0-28.7-23.3-52-52-52l-117.4 0c4-17-.6-35.5-13.8-48.8c-20.3-20.3-53.2-20.3-73.5 0L32 342.5V128c0-35.3 28.7-64 64-64zm64 64H96v64c35.3 0 64-28.7 64-64zM544 320c-35.3 0-64 28.7-64 64h64V320zM320 352a96 96 0 1 0 0-192 96 96 0 1 0 0 192z"
                fill="white"
              />
            </svg>
            <span class="mx-4 text-2xl">Setup ACH</span>
          </div>
        </Button>
      </div>

      <div
        class="m-4"
        style="min-width: 20rem"
        v-if="
          (!isRentalsFeatureVisible ||
            customerOrderStore.publicOrder.allow_external_payments) &&
          canPayWithCreditCard &&
          state.can_use_credit_card &&
          !hasPrePaidCoupon
        "
        :class="{
          'xl:col-span-3':
            !isRentToOwn && !isRental && notPaidCancelledExpiredEstimateQuote,
          'xl:col-span-2': !(
            !isRentToOwn &&
            !isRental &&
            notPaidCancelledExpiredEstimateQuote
          )
        }"
      >
        <Button
          @click="handleCreditCardSelection(false)"
          class="w-full p-button-secondary p-button-lg"
        >
          <div class="flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 576 512"
            >
              <path
                d="M512 80c8.8 0 16 7.2 16 16v32H48V96c0-8.8 7.2-16 16-16H512zm16 144V416c0 8.8-7.2 16-16 16H64c-8.8 0-16-7.2-16-16V224H528zM64 32C28.7 32 0 60.7 0 96V416c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V96c0-35.3-28.7-64-64-64H64zm56 304c-13.3 0-24 10.7-24 24s10.7 24 24 24h48c13.3 0 24-10.7 24-24s-10.7-24-24-24H120zm128 0c-13.3 0-24 10.7-24 24s10.7 24 24 24H360c13.3 0 24-10.7 24-24s-10.7-24-24-24H248z"
                fill="white"
              />
            </svg>
            <span class="mx-4 text-2xl">Credit/Debit Card</span>
          </div>
        </Button>
      </div>
    </div>

    <div
      v-if="notPaidCancelledExpiredEstimateQuote && isRentToOwn"
      class="flex flex-wrap justify-center mb-4"
    >
      <table>
        <tbody>
          <tr>
            <td>
              <p
                class="text-2xl"
                v-if="
                  customerOrderStore.publicCms?.provides_no_obligation_quote
                "
              >
                Click here to apply for a no obligation quote with no credit
                check.
              </p>
            </td>
          </tr>
          <tr>
            <td style="text-align: center">
              <Button
                label="Apply"
                @click="rentToOwnApplicationLink"
                class="p-button-secondary p-button-lg"
              ></Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- <div
      v-if="notPaidCancelledExpiredEstimateQuote && isRental"
      class="flex flex-wrap justify-center mb-4"
    >
      <Button
        label="Apply"
        @click="rentApplicationLink"
        class="p-button-secondary p-button-lg"
      ></Button>
    </div> -->
    <div
      class="flex flex-col items-center w-full"
      v-if="
        customerOrderStore.publicCms?.displays_delivery_period &&
        isPickup &&
        customerOrderStore.publicOrder.account_id == 1 &&
        customerOrderStore.publicOrder.type != 'PURCHASE_ACCESSORY'
      "
    >
      <small class="mx-5 my-2">{{
        customerOrderStore.publicCms?.pickup_public_message
      }}</small>
    </div>
    <div
      class="flex flex-col items-center w-full"
      v-else-if="
        customerOrderStore.publicCms?.displays_delivery_period &&
        customerOrderStore.publicOrder.type != 'PURCHASE_ACCESSORY'
      "
    >
      <small class="mx-5 my-2">{{ deliveryPeriodTexts }}</small>
    </div>
    <div class="flex flex-col items-center w-full">
      <small class="mx-8 my-4">{{ subHeadingMessage }}</small>
    </div>
    <div
      class="flex flex-col items-center w-full"
      v-if="
        customerOrderStore.publicCms?.accessories_link &&
        !['Paid', 'Completed', 'Delivered', 'Driver Paid'].includes(
          customerOrderStore.publicOrder.status
        )
      "
    >
      <p v-html="customerOrderStore.publicCms?.other_product_message"></p>
    </div>
    <div
      v-if="customerOrderStore.publicCms?.accessories_link"
      class="flex flex-wrap justify-center mt-6"
    >
      <p class="text-2xl">Container Accessories</p>
    </div>
    <div class="flex flex-wrap justify-center mt-2 mb-6">
      <Button
        v-if="customerOrderStore.publicCms?.accessories_link"
        label="Accessories"
        @click="openAccessorriesLink"
        class="p-button-accent p-button-rounded p-button-sm"
      ></Button>
      <!-- <Button
        label="Rentals"
        @click="openRentLink"
        class="ml-4 p-button-accent p-button-rounded p-button-sm"
      ></Button>
      <Button
        label="Rent to own"
        @click="openRentToOwnLink"
        class="ml-4 p-button-accent p-button-rounded p-button-sm"
      ></Button> -->
    </div>

    <!-- added the && state.creditcardselected so that the parent controls whether or not this gets displayed for
    the credit/debit card selection button. This way, it will reset the props passed to the child-->
    <PaymentFields
      v-if="
        state.can_use_credit_card &&
        customerOrderStore.publicOrder &&
        customerOrderStore.publicCms &&
        state.creditCardSelected &&
        customerOrderStore.publicOrder.allow_external_payments &&
        !state.achSelected
      "
      :creditCardSelected="state.creditCardSelected"
      :bank-fee="state.toBeAssessedBankFee"
      :is-partial="state.isPartial"
      :partial-pay-amount="state.partialPayAmount"
      :update-from-payment-fields="updateFromPaymentFields"
      :disable-all-fields="state.disableAllFields"
      :is-internal="state.isInternal"
      :creditCardFeeToggleEnabled="creditCardFeeToggleEnabled"
      :updateOrderAfterFeeToggle="updateOrderAfterFeeToggle"
      :hasStripeEnabled="
        hasStripeEnabled &&
        customerOrderStore.publicOrder &&
        customerOrderStore.publicCms
      "
      :hasCardPointeEnabled="
        hasCardPointeEnabled &&
        customerOrderStore.publicOrder &&
        customerOrderStore.publicCms
      "
    />
    <PaymentFields
      v-if="state.can_use_credit_card && state.pay_and_store_card"
      :creditCardSelected="state.creditCardSelected"
      :bank-fee="state.toBeAssessedBankFee"
      :is-partial="state.isPartial"
      :partial-pay-amount="state.partialPayAmount"
      :update-from-payment-fields="updateFromPaymentFields"
      :disable-all-fields="state.disableAllFields"
      :is-internal="state.isInternal"
      :creditCardFeeToggleEnabled="creditCardFeeToggleEnabled"
      :updateOrderAfterFeeToggle="updateOrderAfterFeeToggle"
      :pay_and_store_card="true"
      :customizable_auto_pay_date="true"
    />

    <PaymentFields
      v-if="state.can_use_credit_card && state.show_pay_and_start_auto_pay"
      :creditCardSelected="state.creditCardSelected"
      :bank-fee="state.toBeAssessedBankFee"
      :is-partial="state.isPartial"
      :partial-pay-amount="state.partialPayAmount"
      :update-from-payment-fields="updateFromPaymentFields"
      :disable-all-fields="state.disableAllFields"
      :is-internal="state.isInternal"
      :creditCardFeeToggleEnabled="creditCardFeeToggleEnabled"
      :updateOrderAfterFeeToggle="updateOrderAfterFeeToggle"
      :pay_and_start_auto_pay="true"
      :customizable_auto_pay_date="true"
    />

    <AchFields v-if="state.achSelected" :isPayMode="true"></AchFields>
    <div
      v-if="shouldDisplayTermsAndConditions && state.showTermsTimer"
      class="flex flex-wrap justify-center mt-6"
    >
      <p class="text-2xl">Terms & Conditions</p>
    </div>

    <div v-if="shouldDisplayTermsAndConditions && state.showTermsTimer">
      <div
        class="flex flex-wrap justify-center terms-conditions"
        style="max-width: 98vw"
        v-html="mappedTermsAndConditions"
      ></div>
    </div>

    <Dialog
      v-model:visible="state.paymentMethodDialog"
      dismissableMask
      closeOnEscape
      :breakpoints="{
        '2000px': '45vw',
        '1400px': '55vw',
        '1200px': '65vw',
        '992px': '75vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
      :modal="true"
    >
      <template #header>
        <div class="flex items-stretch">
          <div class="flex"></div>
        </div>
      </template>
      <template #default>
        <div v-html="state.paymentDialogContent" style="height: 70vh"></div>
      </template>
    </Dialog>
    <Dialog
      v-model:visible="state.applyCoupon"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="New Coupon"
      :modal="true"
      class="p-fluid"
    >
      <ApplyCouponCode
        @couponApplied="state.applyCoupon = !state.applyCoupon"
      ></ApplyCouponCode>
    </Dialog>

    <Dialog
      v-model:visible="state.pay_on_delivery_visible"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Pay On Delivery Contract"
      :modal="true"
      class="p-fluid"
    >
      <div class="justify-content-center">
        <PodContract
          :orderId="$route.currentRoute.value.params.orderId"
          :selectedSchema="state.applicationSchemas[0].content"
          :selectedSchemaId="state.applicationSchemas[0].id"
          :podContractFields="podContractFields"
          :podSigned="pod_signed"
          :podContract="customerOrderStore.publicCms?.pod_contract"
          :contractResponse="
            customerOrderStore.publicOrder?.application_response[0] || null
          "
          :oldSignedDate="dfc(customerOrderStore.publicOrder.signed_at)"
          style="max-width: 80vw"
        />
      </div>
    </Dialog>
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
  import { dfl, dfc } from "@/service/DateFormat.js"

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
  import PodContract from "@/components/applications/PodContract.vue"
  import { useTaxes } from "@/store/modules/taxes"
  import TaxApi from "@/api/tax"
  import { accountMap } from "../../../utils/accountMap"
  import PricingService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"

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
  import orderCanUseCreditCard from "@/utils/canUseCreditCard"
  import { roundHalfUp } from "@/utils/formatCurrency.js"

  const toast = useToast()

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
    showTermsTimer: false,
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
    creditCardSelected: false,
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
    delivery_days: null,
    selectedSchemas: [],
    can_use_credit_card: false,
    can_pay_on_delivery_order: false
  })

  watch(
    () => customerOrderStore.publicOrder,
    (newVal, oldVal) => {
      state.can_use_credit_card = orderCanUseCreditCard(
        customerOrderStore.publicOrder
      )
    }
  )

  const applyCoupon = () => {
    state.applyCoupon = true
  }
  const isPickup = computed(() => {
    return (
      customerOrderStore?.publicOrder.line_items.every(
        (i) => Number(i.shipping_revenue) === 0
      ) || customerOrderStore?.publicOrder?.is_pickup
    )
  })

  const couponApi = new CouponApi()
  const showApplication = computed(() => {
    const allowRentApplications =
      customerOrderStore.publicCms?.applications?.rent

    console.log("showApplication", allowRentApplications)
    if (isRental.value) {
      return allowRentApplications
    }
    return false
  })
  const acceptSignPod = async () => {
    state.sending_pod_contract = true
    let data

    data = await customerApi.publicSignPodContract(
      customerOrderStore.publicOrder.id
    )
    state.sending_pod_contract = false
    if (data.error.value != undefined) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error accepting payment on delivery contract",
        group: "br",
        life: 5000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail:
          "The contract was just accepted! We will start the delivery process. Thank you!",
        group: "br",
        life: 10000
      })
      window.location.reload()
    }
  }
  const podContractFields = computed(() => {
    const today = new Date()
    const readableDate = today.toDateString()
    return {
      date: readableDate,
      fullname: customerOrderStore.publicOrder.customer?.full_name,
      address: customerOrderStore.publicOrder.address?.full_address,
      company_name: customerOrderStore.publicCms?.company_name,
      invoice: customerOrderStore.publicOrder.display_order_id,
      invoice_price: $fc(
        customerOrderStore.publicOrder?.calculated_sub_total_price +
          customerOrderStore.publicOrder?.calculated_order_tax
      ),
      qty_size:
        customerOrderStore.publicOrder?.calculated_line_items_title_with_type,
      customer: customerOrderStore.publicOrder?.customer
    }
  })
  const sendPaymentOnDeliveryContract = async () => {
    state.sending_pod_contract = true
    let data
    if ($isPayment) {
      data = await customerApi.sendPaymentOnDeliveryContractFromPayment(
        customerOrderStore.publicOrder.id
      )
    } else {
      data = await customerApi.sendPaymentOnDeliveryContract(
        customerOrderStore.publicOrder.id
      )
    }
    state.sending_pod_contract = false
    if (data.error.value != undefined) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error sending payment on delivery contract",
        group: "br",
        life: 5000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail:
          "The contract was just emailed!Once you sign the contract, we will start the delivery process.Thank you!",
        group: "br",
        life: 10000
      })
    }
  }

  const sendPodOrRedirect = async () => {
    if (customerOrderStore.publicOrder.pod_sign_page_url) {
      window.location.href = customerOrderStore.publicOrder.pod_sign_page_url
    } else {
      await sendPaymentOnDeliveryContract()
    }
  }

  const can_pay_on_delivery = async () => {
    if (
      isPickup.value == true ||
      customerOrderStore.publicOrder.status == "Expired" ||
      !customerOrderStore.publicOrder ||
      (customerOrderStore.publicOrder?.type != "PURCHASE" &&
        customerOrderStore.publicOrder?.type != "PURCHASE_ACCESSORY")
    ) {
      state.can_pay_on_delivery_order = false
      return
    }
    const cms_pay_on_deliver =
      customerOrderStore.publicCms?.pay_on_delivery_contract

    if (cms_pay_on_deliver && cms_pay_on_deliver.is_enabled) {
      customerOrderStore.publicOrder?.line_items?.filter(async (e) => {
        if (cms_pay_on_deliver.max_allowed_miles >= (e.potential_miles || 0)) {
          let requestData = {
            product_name: e.title,
            location_name: e.product_city
          }
          const { data } = await customerApi.is_pay_on_delivery(requestData)
          state.can_pay_on_delivery_order =
            state.can_pay_on_delivery_order || data.value
        }
      })
    } else {
      state.can_pay_on_delivery_order = false
    }
  }

  const isRentalsFeatureVisible = computed(() => {
    return customerOrderStore.publicCms?.feature_flags?.rentals_enabled
  })

  const creditCardFeeToggleEnabled = computed(() => {
    return userStore.cms?.credit_card_fees.enable_toggle_credit_card_fees
  })

  const updateFromPaymentFields = (newData, callback = null) => {
    if (newData.isPartial !== undefined) {
      state.isPartial = newData.isPartial
    }
    if (newData.partialPayAmount !== undefined) {
      state.partialPayAmount = newData.partialPayAmount
    }

    handleCreditCardSelection(true)

    if (callback) {
      callback(state.assessedBankFee)
    }
  }

  const fetchSchema = async () => {
    const result = await customerApi.getApplicationSchemasByName(
      state.can_pay_on_delivery_order
        ? "POD"
        : customerOrderStore.publicOrder.type,
      customerOrderStore.publicOrder.id
    )

    if (result.data.value) {
      console.log("setting application schemas")
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
    return (
      pod_signed.value ||
      customerOrderStore.publicOrder.calculated_sub_total_price < 21000
    )
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
      customerOrderStore.publicOrder?.application_response[0]
        ?.response_content || {}
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

    if (customerOrderStore.publicCms.show_container_number_on_invoice) {
      cart.forEach((el) => {
        el.container_number = state.line_item_container_number[el.product_id]
      })
    }

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

  const pod_signed = computed(() => {
    return customerOrderStore.publicOrder.signed_at ? true : false
  })

  const displayMessage = computed(() => {
    let termsMessage = ""
    if (paidInFull()) {
      if (
        pod_signed.value &&
        (customerOrderStore.publicOrder.type == "PURCHASE" ||
          customerOrderStore.publicOrder.type == "PURCHASE_ACCESSORY")
      ) {
        termsMessage = `POD Terms and conditions read and accepted on ${dfl(
          customerOrderStore.publicOrder.signed_at
        )}`
      } else {
        termsMessage = `Terms and conditions read and accepted on ${dfl(
          customerOrderStore.publicOrder.paid_at
        )}`
      }
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
    } else if (
      pod_signed.value &&
      (customerOrderStore.publicOrder.type == "PURCHASE" ||
        customerOrderStore.publicOrder.type == "PURCHASE_ACCESSORY")
    ) {
      termsMessage = `Contract Signed - ${dfl(
        customerOrderStore.publicOrder.signed_at
      )}`
    }

    const termsHtml = `<div class='flex justify-center mt-2 flex-nowrap md:text-2xl'>
      ${termsMessage}
      </div>`
    if (
      $isObjectPopulated(
        customerOrderStore.publicOrder.application_response[0]?.response_content
      ) &&
      !paidInFull()
    ) {
      if (
        customerOrderStore.publicOrder?.application_response[0]?.date_rejected
      ) {
        return `<div class='flex justify-center flex-nowrap md:text-2xl'>
      Application Rejected - ${dfl(
        customerOrderStore.publicOrder?.application_response[0]?.date_rejected
      )}
      </div>`
      } else if (
        customerOrderStore.publicOrder?.application_response[0]?.date_accepted
      ) {
        return `<div class='flex justify-center flex-nowrap md:text-2xl'>
      Application Accepted - ${dfl(
        customerOrderStore.publicOrder?.application_response[0]?.date_accepted
      )}
      </div>`
      } else if (pod_signed.value) {
        termsMessage = `Contract Signed - ${dfl(
          customerOrderStore.publicOrder?.application_response[0]?.created_at
        )}`
      } else {
        return `<div class='flex justify-center flex-nowrap md:text-2xl'>
      Application Submitted - ${dfl(
        customerOrderStore.publicOrder?.application_response[0]?.created_at
      )}
      </div>`
      }
    }

    if (
      customerOrderStore.publicOrder.calculated_remaining_order_balance == 0
    ) {
      let paidMessage = isRentToOwn.value
        ? customerOrderStore.publicCms.rto_paid_message
        : customerOrderStore.publicCms.paid_message

      return `<div class='flex justify-center flex-nowrap md:text-2xl'>
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

      return `<div class='flex justify-center flex-nowrap md:text-2xl'>
      ${customerOrderStore.publicCms.quote_cancelled_message}
      </div>
      <div class='flex justify-center mt-2 flex-nowrap md:text-2xl'>
      ${termsMessage}
      </div>`
    }

    if (customerOrderStore.publicOrder.status.toLowerCase() === "expired") {
      return `<div class='flex justify-center flex-nowrap md:text-2xl'>
      ${customerOrderStore.publicCms.quote_expired_message}
      </div>`
    }
    if (pod_signed.value) {
      return termsHtml
    }
  })

  const capitalizeFirstLetter = (inputString) => {
    return (
      inputString.charAt(0).toUpperCase() + inputString.slice(1).toLowerCase()
    )
  }

  const deliveryPeriodTexts = computed(() => {
    return `Delivery within ${state.delivery_days} business days`
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
    return customerOrderStore.publicOrder?.coupon_code_order.length > 0
  })
  const hasPrePaidCoupon = computed(() => {
    if (hasCoupon.value) {
      return customerOrderStore.publicOrder.coupon_code_order.some(
        (coupon_item) => coupon_item.coupon?.attributes?.is_pre_paid === true
      )
    }
    return false
  })

  const invoiceExpired = computed(() => {
    const activeStatus = ["Invoiced"]
    return !activeStatus.includes(customerOrderStore.publicOrder.status)
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

    // resetStateVars();

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

  const handleCreditCardSelection = (dont_switch = false) => {
    if (!dont_switch) {
      state.creditCardSelected = !state.creditCardSelected
    }
    const fees = customerOrderStore.publicOrder.fees

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
  }

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

    return returnList.filter((item) => item.rowContent != $fc(0))
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

  const hasCardPointeEnabled = computed(() => {
    return customerOrderStore.publicCms?.card_pointe_enabled
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
    return "15"
  }

  onMounted(async () => {
    if ($route.currentRoute.value.name === "Quote") {
      return
    }

    setTimeout(() => {
      state.showTermsTimer = true
    }, 5000)

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
    state.delivery_days = (await loadDeliveryDays()).delivery_days
    await loadCoupons()
    customerOrderStore.setPublicCms(res.data.value)
    await can_pay_on_delivery()

    if (hasStripeEnabled.value) {
      console.log("Setting up stripe")
      let stripeScript = document.createElement("script")
      stripeScript.setAttribute("src", "https://js.stripe.com/v3/")
      document.head.appendChild(stripeScript)
    }

    state.loading = false
    if ($isPublic && customerOrderStore.publicCms?.has_analytics) {
      // TODO: THESE AREN'T DEFINED? NEED TO IMPORT
      insertGoogleScript()

      gtag("event", "quotecreation_data", {
        email_address: customerOrderStore.publicOrder.customer.email
      })
      window.dataLayer = window.dataLayer || []
      window.dataLayer.push({
        event: "quotecreation_data",
        email_address: customerOrderStore.publicOrder.customer.email
      })
    }

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

    state.bankFee =
      customerOrderStore.publicOrder.fees.find(
        (fee) => fee.type.name === "CREDIT_CARD"
      )?.fee_amount || 0
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

  const insertGoogleScript = () => {
    // if (publicCms.company_name === 'USA Containers' || publicCms.company_name === 'USA Containers Canada') {
    console.log("Inserting Google Script ", publicCms?.company_name)
    const googleAdScript = document.createElement("script")
    googleAdScript.innerHTML = `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
      new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
      j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
      'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','');`

    window.document.body.appendChild(googleAdScript)
    const googleIframeScript = document.createElement("noscript")
    googleIframeScript.innerHTML = `<iframe src="https://www.googletagmanager.com/ns.html?id=" height="0" width="0" style="display:none;visibility:hidden"></iframe>`
    window.document.body.appendChild(googleIframeScript)
    // }
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
  const notPaidCancelledExpiredEstimateQuote = computed(() => {
    if (!customerOrderStore.publicOrder) return false
    return (
      !paidInFull() &&
      !isCancelled.value &&
      !isExpired() &&
      !isEstimate.value &&
      !isQuote.value
    )
  })
  const shouldDisplayTermsAndConditions = computed(() => {
    let allowedStatuses = [
      "Paid",
      "Partially Paid",
      "Cancelled",
      "Delivered",
      "Driver Paid",
      "Purchase Order",
      "Invoiced"
    ]
    return (
      (!state.creditCardSelected ||
        customerOrderStore.publicOrder.payment_type === "CC" ||
        allowedStatuses.includes(customerOrderStore.publicOrder.status)) &&
      customerOrderStore.publicOrder.type != "RENT"
    )
  })

  const isDelivery = () => {
    return customerOrderStore.publicOrder?.line_items?.some(
      (l) => Number(l.shipping_revenue) > 0
    )
  }
  watch(hasPrePaidCoupon, (newValue) => {
    if (newValue == true) state.prepay = true
  })
  watch(
    () => state.selectedApplicationType,
    (newVal, oldValue) => {
      state.selectedSchema = []
      state.selectedSchema = {}
      state.selectedSchema = null
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
