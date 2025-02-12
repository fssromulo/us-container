<template>
  <div
    class="flex flex-wrap justify-center mt-2 mb-6"
    v-if="props.hasStripeEnabled && stripeInitialized"
  >
    <div class="flex flex-col flex-auto" style="max-width: 700px">
      <div class="flex flex-col flex-auto">
        <div
          v-if="!props.isInternal && !isRental && !isRentToOwn"
          class="col-span-12"
        >
          <div class="flex flex-wrap justify-center field-checkbox">
            <label for="zip" class="block font-medium text-900 dark:text-0">{{
              state.isPartial ? "Pay partial Amount" : "Pay in full"
            }}</label>
          </div>
          <div class="flex flex-wrap justify-center field-checkbox">
            <ToggleSwitch id="zip" v-model="state.isPartial" type="text" />
          </div>
        </div>
        <div class="col-span-12 px-20">
          <div
            v-if="state.isPartial"
            class="flex flex-wrap justify-center field-checkbox"
          >
            <label
              v-if="remainingBalanceCalc < 0"
              for="name"
              :class="{ 'p-error': v$.partialPayAmount.$invalid }"
              >Remaining balance cannot be negative.</label
            >
          </div>
          <div
            v-if="state.isPartial"
            class="flex flex-wrap justify-center field-checkbox"
          >
            <InputNumber
              :disabled="props.disableAllFields"
              placeholder="Partial"
              mode="currency"
              style="width: 60%"
              currency="USD"
              :class="{ 'p-invalid': v$.partialPayAmount.$invalid }"
              id="partialPay"
              v-model="state.partialPayAmount"
              type="text"
            />
            <Button
              v-if="!state.confirmedPartialAmount"
              type="button"
              icon="pi pi-check text-sm"
              @click="
                state.confirmedPartialAmount = !state.confirmedPartialAmount
              "
              class="w-8 h-8 ml-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100 p-button-primary"
            ></Button>
            <br />
            <p class="mt-2">Remaining Balance: ${{ remainingBalanceCalc }}</p>
          </div>
        </div>
      </div>
      <div class="flex flex-col flex-auto">
        <div class="flex justify-center mt-4">
          <StripePayment
            v-if="!state.isPartial || state.confirmedPartialAmount"
            :clientSecret="state.stripeSecret"
            :publicKey="state.stripePublicKey"
            :amountToPay="paymentAmount"
            :orderToken="state.orderToken"
            :accountId="computedOrder.account_id"
            :paymentIntentId="state.paymentIntentId"
          />
        </div>
      </div>
    </div>
  </div>
  <div v-if="props.showTransactionCreatedAt">
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
  </div>
  <div
    class="flex flex-wrap justify-center mt-2 mb-6"
    v-if="props.hasStripeEnabled && !stripeInitialized"
  >
    <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
  </div>

  <div
    class="flex flex-wrap justify-center mt-2 mb-6"
    v-else-if="!props.hasStripeEnabled"
  >
    <div class="">
      <div
        v-if="!paidInFull() && !isCancelled() && computedOrder"
        class="flex flex-wrap justify-center"
      >
        <div></div>
        <div class="grid grid-cols-12 col-span-12" style="max-width: 800px">
          <p v-if="props.disableAllFields" class="col-span-12">
            *All parties must have signed to submit payment & all containers
            must be assigned to the order.
          </p>

          <p
            v-if="
              props.isInternal &&
              !props.disableAllFields &&
              !props.isUpdateCreditCard &&
              !props.isAddCardOnFile
            "
            class="col-span-12"
          >
            {{ paymentTitle }}
          </p>
          <div
            v-if="!state.payCustomerProfile"
            class="grid grid-cols-2 col-span-12 gap-2"
          >
            <div class="md:col-span-1 sm:col-span-2">
              <label for="first_name" class="font-medium text-900 dark:text-0"
                >First Name</label
              ><br />
              <InputText
                v-model="state.customer.first_name"
                class="p-inputtext p-component p-inputtext-fluid"
                :class="{ 'p-invalid': v$.customer.first_name.$invalid }"
                :disabled="props.disableAllFields"
                id="first_name"
                type="text"
                maxLength="50"
              />
            </div>
            <div class="md:col-span-1 sm:col-span-2">
              <label for="last_name" class="font-medium text-900 dark:text-0"
                >Last Name</label
              >
              <br />
              <InputText
                class="w-full"
                v-model="state.customer.last_name"
                :class="{ 'p-invalid': v$.customer.last_name.$invalid }"
                :disabled="props.disableAllFields"
                id="last_name"
                type="text"
                maxLength="50"
              />
            </div>
          </div>
          <div
            v-if="!state.payCustomerProfile"
            class="grid grid-cols-12 col-span-12 gap-2"
          >
            <div
              class="flex flex-col col-span-12 mt-4 items-left sm:col-span-12"
              v-if="hasCardPointeEnabled"
              style="margin-left: -5px"
            >
              <div class="w-full">
                <label
                  for="cc_number"
                  class="ml-2 font-medium text-900 dark:text-0"
                  >Card Number</label
                ><br />
                <iframe
                  id="tokenFrame"
                  name="tokenFrame"
                  :src="
                    card_pointe_url +
                    '?useexpiry=false&usecvv=false&tokenizewheninactive=true&css=%23ccnumfield%2C%23ccexpirymonth%2C%23ccexpiryyear%2C%23cccvvfield%7Bborder%3A1px%20solid%20black%3Bborder-radius%3A4px%3B-webkit-border-radius%3A4px%3B-moz-border-radius%3A4px%3Bpadding%3A8px%2012px%3Bfont-size%3A16px%3Bfont-family%3AArial%2Csans-serif%3Bcolor%3A%23333%3Bbackground-color%3A%23fff%3Bbox-sizing%3Aborder-box%3B-webkit-box-shadow%3Ainset%200%201px%203px%20rgba%280%2C0%2C0%2C0.1%29%3B-moz-box-shadow%3Ainset%200%201px%203px%20rgba%280%2C0%2C0%2C0.1%29%3Bbox-shadow%3Ainset%200%201px%203px%20rgba%280%2C0%2C0%2C0.1%29%3Boutline%3Anone%3Bwidth%3A100%25%3Bmax-width%3A300px%3Bmargin-bottom%3A15px%3B%7D%23ccnumfield%7Bletter-spacing%3A1px%3B%7D%23ccexpirymonth%2C%23ccexpiryyear%7Bappearance%3Anone%3B-webkit-appearance%3Anone%3B-moz-appearance%3Anone%3Bbackground-repeat%3Ano-repeat%3Bbackground-position%3Aright%208px%20center%3Bpadding-right%3A30px%3B%7D%23ccexpiryyear%7Bmargin-left%3A0px%3B%7D%23cccvvfield%7Bmax-width%3A100px%3B%7D%23ccnumfield%3Afocus%2C%23ccexpirymonth%3Afocus%2C%23ccexpiryyear%3Afocus%2C%23cccvvfield%3Afocus%7Bborder-color%3A%234a90e2%3Bbox-shadow%3A0%200%205px%20rgba%2874%2C144%2C226%2C0.3%29%3B-webkit-box-shadow%3A0%200%205px%20rgba%2874%2C144%2C226%2C0.3%29%3B-moz-box-shadow%3A0%200%205px%20rgba%2874%2C144%2C226%2C0.3%29%3B%7D%23ccnumfield%3A%3Aplaceholder%2C%23cccvvfield%3A%3Aplaceholder%7Bcolor%3A%23999%3B%7D%23ccnumfield%3A%3A-ms-input-placeholder%2C%23cccvvfield%3A%3A-ms-input-placeholder%7Bcolor%3A%23999%3B%7D%23ccnumfield%3A-ms-input-placeholder%2C%23cccvvfield%3A-ms-input-placeholder%7Bcolor%3A%23999%3B%7D'
                  "
                  height="50px"
                  frameborder="0"
                  scrolling="no"
                ></iframe>
              </div>
            </div>
            <div class="col-span-12 mt-4 sm:col-span-12" v-else>
              <label for="cc_number" class="font-medium text-900 dark:text-0"
                >Card Number</label
              ><br />
              <InputNumber
                v-model="state.cardInfo.cardNumber"
                :useGrouping="false"
                class="p-component p-inputtext-fluid"
                :class="{ 'p-invalid': v$.cardInfo.cardNumber.$invalid }"
                :disabled="props.disableAllFields"
                id="cc_number"
                type="text"
              />
            </div>
            <div
              class="col-span-12 mb-4 md:col-span-12"
              v-if="props.hasTransactionDate"
            >
              <div>
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
                  class="text-xl"
                ></DatePicker>
              </div>
            </div>
            <div class="grid grid-cols-2 col-span-12 gap-4 mt-2 md:col-span-12">
              <div class="col-span-2 md:col-span-1">
                <label for="exp" class="font-medium text-900 dark:text-0"
                  >Expiration</label
                ><br />
                <InputMask
                  placeholder="MM/YY"
                  class="w-full"
                  :class="{ 'p-invalid': v$.cardInfo.expirationDate.$invalid }"
                  :disabled="props.disableAllFields"
                  v-model="state.cardInfo.expirationDate"
                  mask="99/99"
                  id="exp"
                />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label for="cvv" class="font-medium text-900 dark:text-0"
                  >CVV</label
                ><br />
                <InputText
                  v-model="state.cardInfo.cvv"
                  :class="{ 'p-invalid': v$.cardInfo.cvv.$invalid }"
                  class="w-full"
                  :disabled="props.disableAllFields"
                  :useGrouping="false"
                  placeholder="CVV"
                  id="cvv"
                />
              </div>
            </div>
            <div class="grid grid-cols-2 col-span-12 gap-4 mt-2 md:col-span-12">
              <div class="col-span-2 md:col-span-1">
                <label for="cvv" class="font-medium text-900 dark:text-0"
                  >Type</label
                ><br />
                <Select
                  class="w-full"
                  v-model="state.cardInfo.type"
                  :disabled="props.disableAllFields"
                  placeholder="Type"
                  :options="CARD_TYPE"
                />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label for="cvv" class="font-medium text-900 dark:text-0"
                  >Card Brand</label
                ><br />
                <Select
                  v-model="state.cardInfo.merchant_name"
                  :disabled="props.disableAllFields"
                  placeholder="Card Brand"
                  scrollHeight="300px"
                  class="w-full"
                  :options="MERCHANT_TYPES"
                />
              </div>
            </div>

            <div class="col-span-12 mt-2 mb-4 field md:col-span-12">
              <label for="avs_street" class="font-medium text-900 dark:text-0"
                >Billing Street Address</label
              ><br />
              <InputText
                :class="{ 'p-invalid': v$.customer.avs_street.$invalid }"
                :disabled="props.disableAllFields"
                id="avs_street"
                class="w-full"
                v-model="state.customer.avs_street"
                type="text"
                maxlength="60"
              />
            </div>

            <div class="col-span-12 mt-2 mb-4 field md:col-span-4">
              <label for="city" class="font-medium text-900 dark:text-0"
                >Billing City</label
              ><br />
              <InputText
                v-model="state.customer.city"
                :disabled="props.disableAllFields"
                :class="{ 'p-invalid': v$.customer.city.$invalid }"
                :useGrouping="false"
                class="w-full"
                placeholder="City"
                id="City"
              />
            </div>
            <div
              class="grid grid-cols-6 col-span-12 gap-4 mt-2 mb-4 field md:col-span-8"
            >
              <div class="col-span-3">
                <label for="state" class="font-medium text-900 dark:text-0"
                  >Billing {{ stateProvinceText }}</label
                ><br />
                <Select
                  v-model="state.customer.state"
                  :disabled="props.disableAllFields"
                  :placeholder="stateProvinceText"
                  class="w-full"
                  :options="
                    getCountry == 'Canada'
                      ? stateService.getProvinces()
                      : stateService.getStates()
                  "
                />
              </div>
              <div class="col-span-3">
                <label for="zip" class="font-medium text-900 dark:text-0"
                  >Billing {{ postalZipText }}</label
                ><br />
                <InputText
                  :class="{ 'p-invalid': v$.customer.zip.$invalid }"
                  :disabled="props.disableAllFields"
                  id="zip"
                  v-model="state.customer.zip"
                  class="w-full"
                  type="text"
                />
              </div>
            </div>
          </div>
          <div
            v-if="
              !props.isInternal &&
              !isRental &&
              !isRentToOwn &&
              props.canPartialPay
            "
            class="col-span-12"
          >
            <div class="flex flex-wrap justify-center field-checkbox">
              <label for="zip" class="block font-medium text-900 dark:text-0">{{
                state.isPartial ? "Pay partial Amount" : "Pay in full"
              }}</label>
            </div>
            <div class="flex flex-wrap justify-center field-checkbox">
              <ToggleSwitch id="zip" v-model="state.isPartial" type="text" />
            </div>
          </div>
          <div class="col-span-12 px-20">
            <div
              v-if="state.isPartial"
              class="flex flex-wrap justify-center field-checkbox"
            >
              <label
                v-if="remainingBalanceCalc < 0"
                for="name"
                :class="{ 'p-error': v$.partialPayAmount.$invalid }"
                >Remaining balance cannot be negative.</label
              >
            </div>

            <div
              v-if="state.isPartial"
              class="flex flex-wrap justify-center field-checkbox"
            >
              <InputNumber
                :disabled="props.disableAllFields"
                placeholder="Partial"
                mode="currency"
                style="width: 100%"
                currency="USD"
                :class="{ 'p-invalid': v$.partialPayAmount.$invalid }"
                id="partialPay"
                v-model="state.partialPayAmount"
                type="text"
              />
              <p class="mt-2">Remaining Balance: ${{ remainingBalanceCalc }}</p>
            </div>
          </div>
          <div class="col-span-4" v-if="false">
            <label> Auto-Pay date </label>
            <InputNumber
              class="col-span-4"
              v-model="state.autopay_day"
              :min="1"
              :max="28"
            />
          </div>
          <div class="col-span-12">
            <div
              v-if="!props.isInternal"
              class="flex flex-wrap justify-center field-checkbox"
            >
              <Checkbox
                class="mt-1 mr-2"
                :disabled="props.disableAllFields"
                inputId="binary"
                v-model="state.agreeToTerms"
                :binary="true"
              />
              <label class="text-lg" for="binary"
                >I agree to the terms and conditions below</label
              >
            </div>
            <Message v-if="state.error" severity="error">{{
              state.error
            }}</Message>
            <div
              v-if="
                isRental &&
                customerOrderStore.order.customer_profile_id !== null &&
                !props.isUpdateCreditCard &&
                !props.isAddCardOnFile
              "
              class="col-span-12"
            >
              <div class="flex flex-wrap justify-center field-checkbox">
                <label
                  for="payCustomerProfile"
                  class="block font-medium text-900 dark:text-0"
                  >{{
                    state.payCustomerProfile
                      ? "Pay using customer profile"
                      : "Pay without customer profile"
                  }}</label
                >
              </div>
              <div class="flex flex-wrap justify-center field-checkbox">
                <ToggleSwitch
                  id="payCustomerProfile"
                  v-model="state.payCustomerProfile"
                  type="text"
                />
              </div>
            </div>
            <div class="flex flex-wrap justify-center mt-5 field-checkbox">
              <Button
                v-if="!props.isUpdateCreditCard && !props.isAddCardOnFile"
                :label="`Pay ${$fc(paymentAmount)}`"
                :disabled="state.loading"
                :loading="state.loading"
                style="max-width: 200px"
                @click="payOrder"
                class="p-button-primary p-button-rounded p-button-lg"
              ></Button>
              <Button
                v-if="
                  props.isUpdateCreditCard &&
                  $ability.can('update', 'rental_payments')
                "
                :label="`Update Card on File`"
                :loading="state.update_card_loading"
                style="max-width: 200px"
                @click="changeCreditCard"
                class="p-button-primary p-button-rounded p-button-lg"
              ></Button>
              <Button
                v-if="
                  props.isUpdateCreditCard &&
                  $ability.can('update', 'rental_payments')
                "
                :label="`Remove Card on File`"
                :loading="state.remove_card_loading"
                style="max-width: 200px; margin-left: 20px"
                @click="removeCardOnFile"
                class="p-button-primary p-button-rounded p-button-lg"
              ></Button>
              <Button
                v-if="
                  props.isAddCardOnFile &&
                  $ability.can('update', 'rental_payments')
                "
                :label="`Add Card on File`"
                :loading="state.loading"
                style="max-width: 200px"
                @click="addCardOnFile"
                class="p-button-primary p-button-rounded p-button-lg"
              ></Button>
            </div>
            <div
              class="flex flex-wrap justify-center text-sm"
              v-if="props.creditCardSelected && show_bank_fee_message"
            >
              <p>(Bank fee always added when paying with credit/debit card)</p>
            </div>
          </div>
          <div
            v-if="
              props.isInternal &&
              computedOrder.type === 'RENT' &&
              !state.hideRentPayDay
            "
            class="col-span-12"
          >
            <label
              for="rental_payment_day_of_month"
              class="font-medium text-900 dark:text-0"
              >Rent Payment Day of Month (optional)</label
            >
            <DatePicker
              :disabled="props.disableAllFields"
              v-tooltip="
                'Rent Payment Day of Month (otherwise will charge on the day of payment)'
              "
              class="w-full"
              inputId="basic"
              dateFormat="m/d/y"
              placeholder="Select Rent Payment Date"
              v-model="state.rental_payment_day_of_month"
            />
          </div>
        </div>
      </div>
      <div
        v-if="
          !props.isInternal &&
          (props.creditCardSelected || computedOrder?.payment_type === 'CC')
        "
        class="flex flex-wrap justify-center mt-6"
      >
        <p class="text-2xl">Terms & Conditions</p>
      </div>

      <div
        v-if="props.creditCardSelected || computedOrder?.payment_type === 'CC'"
        class="flex flex-wrap justify-center mt-6"
      >
        <div
          class="flex flex-wrap justify-center"
          :class="smAndSmaller ? 'mx-1' : 'mx-7'"
          v-html="mappedTermsAndConditions"
        ></div>
      </div>
    </div>
    <Dialog
      v-model:visible="state.customerPaidDialog"
      :dismissableMask="true"
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Thank you for your payment!"
      :modal="true"
      class="p-fluid"
      @after-hide="afterHide"
      :breakpoints="{
        '2000px': '45vw',
        '1400px': '55vw',
        '1200px': '65vw',
        '992px': '75vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
    >
      <div class="ml-1 mr-1">{{ state.paymentMessage }}</div>
    </Dialog>

    <Dialog
      v-model:visible="state.customerRemoveCardOnFile"
      :dismissableMask="true"
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :modal="true"
      header="Warning"
      class="p-fluid"
      @after-hide="afterHide"
      :breakpoints="{
        '2000px': '45vw',
        '1400px': '55vw',
        '1200px': '65vw',
        '992px': '75vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
    >
      <p>Are you sure you want to remove the card on file?</p>
      <Button
        :label="`Yes`"
        :loading="state.loading"
        style="max-width: 100px"
        @click="removeCardOnFileFinal"
        class="p-button-primary p-button-rounded p-button-lg"
      ></Button>
      <Button
        :label="`No`"
        style="max-width: 100px; margin-left: 20px"
        @click="removeCardOnFileCancel"
        class="p-button-primary p-button-rounded p-button-lg"
      ></Button>
    </Dialog>
  </div>
</template>

<script setup>
  import {
    reactive,
    inject,
    computed,
    onMounted,
    onBeforeMount,
    onUnmounted
  } from "vue"
  import Footer from "@/components/footer/Footer.vue"
  import CustomerApi from "@/api/customers"
  import StateService from "@/service/StateService"
  import CartService from "@/service/Cart"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import StripePayment from "./StripePayment.vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email, integer, maxLength } from "@vuelidate/validators"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import { watch } from "vue"
  import { useToast } from "primevue/usetoast"
  import { useTransactionTypeStore } from "../../../store/modules/transactionTypeStore"
  import { useRoute } from "vue-router"

  const $ability = inject("$ability")

  const useRouteVar = useRoute()

  const transactionTypeStore = useTransactionTypeStore()
  const toast = useToast()

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")

  const customerOrderStore = useCustomerOrder()
  const usersStore = useUsers()

  const $fc = inject("$formatCurrency")
  const $isPublic =
    inject("$isPublic") || useRouteVar.path.includes("/prices/payment")

  const customerApi = new CustomerApi()
  const stateService = new StateService()
  const cartService = new CartService()
  const emit = defineEmits(["handleSuccessFeedback"])

  const card_pointe_url = computed(() => {
    let url = $isPublic
      ? customerOrderStore?.publicCms?.card_pointe_token_url
      : usersStore.cms?.card_pointe_token_url
    return url
  })

  const postalZipText = computed(() => {
    let account_country = $isPublic
      ? customerOrderStore?.publicCms?.account_country
      : usersStore.cms?.account_country
    return account_country && account_country == "Canada"
      ? "Postal Code"
      : "Zip"
  })
  const show_bank_fee_message = computed(() => {
    let bankfee_message = $isPublic
      ? customerOrderStore?.publicCms?.bank_fee_message
      : usersStore.cms?.bank_fee_message
    return bankfee_message
  })
  const stateProvinceText = computed(() => {
    let account_country = $isPublic
      ? customerOrderStore?.publicCms?.account_country
      : usersStore.cms?.account_country
    return account_country && account_country == "Canada" ? "Province" : "State"
  })
  const getCountry = computed(() => {
    return $isPublic
      ? customerOrderStore?.publicCms?.account_country
      : usersStore.cms?.account_country
  })

  const props = defineProps({
    canPartialPay: {
      type: Boolean,
      default: true
    },
    isDriverPayment: {
      type: Boolean,
      default: false
    },
    hasStripeEnabled: {
      type: Boolean,
      default: false
    },
    hasCardPointeEnabled: {
      type: Boolean,
      default: false
    },
    hasTransactionDate: {
      type: Boolean,
      default: false
    },
    sendSuccessFeedBack: {
      type: Boolean,
      default: false
    },
    creditCardSelected: {
      type: Boolean,
      default: false
    },
    isInternal: {
      type: Boolean,
      default: false
    },
    bankFee: {
      type: Number,
      default: 0
    },
    partialPayAmount: {
      type: Boolean,
      default: false
    },
    isPartial: {
      type: Boolean,
      default: false
    },
    updateFromPaymentFields: {
      type: Function,
      default: () => {}
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
    isAddCardOnFile: {
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
    taxPaymentAmount: {
      type: Number,
      default: 0
    },
    rentalAfterPayReset: {
      type: Function,
      default: () => {}
    },
    updateOrderAfterFeeToggle: {
      type: Function,
      default: () => {}
    },
    applyBankFee: {
      type: Boolean,
      default: false
    },
    overridePaymentMethod: {
      type: Function,
      default: undefined
    },
    pay_and_store_card: {
      type: Boolean,
      default: false
    },
    pay_and_start_auto_pay: {
      type: Boolean,
      default: false
    },
    customizable_auto_pay_date: {
      type: Boolean,
      default: false
    },
    refreshFunction: {
      type: Function,
      default: () => {}
    },
    multipleOrders: {
      type: Boolean,
      default: false
    },
    boxesBeingPaidFor: {
      default: []
    },
    showTransactionCreatedAt: {
      type: Boolean,
      default: false
    }
  })

  const state = reactive({
    showApplciation: false,
    paid_at: new Date(),
    isPartial: false,
    error: null,
    selectedStep: 0,
    isDeliveryAddress: true,
    alwaysTrue: true,
    paymentMessage: null,
    user: null,
    agreeToTerms: false,
    paymentStarted: false,
    loading: false,
    customerPaidDialog: false,
    partialPayAmount: 0,
    rental_payment_day_of_month: null,
    showTermsConditions: false,
    credit_card_fee: true,
    changed_credit_card_fee_on_mounted: false,
    confirmedPartialAmount: false,
    cms: null,
    customer: {
      first_name: "",
      last_name: "",
      email: "",
      zip: null,
      avs_street: "",
      city: "",
      state: ""
    },
    cardInfo: {
      cardNumber: null,
      expirationDate: "",
      cvv: null,
      type: "",
      merchant_name: ""
    },
    hideRentPayDay: true,
    customerRemoveCardOnFile: false,
    payCustomerProfile: false,
    autopay_day: 0,
    bank_name: "",
    account_number: "",
    routing_number: "",
    remove_card_loading: false,
    update_card_loading: false,
    stripeSecret: "",
    stripePublicKey: "",
    orderToken: "",
    paymentIntentId: "",
    stripeInit: false,
    lineItemsPaid: [],
    card_pointe_token: "",
    transaction_paid_at: null
  })

  const ccRule = (v) =>
    /^(?:4[0-9]{12}(?:[0-9]{3})?|[25][1-7][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$/.test(
      v
    )
  const expirationRule = (v) =>
    /^(0[1-9]|1[0-2])\/?([0-9]{4}|[0-9]{2})$/.test(v)
  const cvvRule = (v) => /^[0-9]{3,4}$/.test(v)
  const zipRule = (v) => /^[0-9]{5}(?:-[0-9]{4})?$/.test(v)

  const MERCHANT_TYPES = ["AMEX", "Discover", "Visa", "Mastercard"]

  const CARD_TYPE = ["DEBIT", "CREDIT"]

  const initStripePayment = async () => {
    let account_country = $isPublic
      ? customerOrderStore?.publicCms?.account_country
      : usersStore.cms?.account_country

    state.stripeInit = false
    state.loading = true
    const result = await customerApi.initStripe({
      amount: paymentAmount.value * 100,
      account_id: computedOrder.value.account_id,
      order_id: computedOrder.value.id,
      currency: account_country === "Canada" ? "cad" : "usd"
    })
    if (result.data.value) {
      state.stripeSecret = result.data.value.client_secret
      state.stripePublicKey = result.data.value.public_key
      state.orderToken = result.data.value.order_token
      state.paymentIntentId = result.data.value.payment_intent_id
    }
    state.stripeInit = true
    state.loading = false
  }
  const stripeInitialized = computed(() => {
    return state.stripeInit
  })
  onBeforeMount(async () => {
    if (props.hasStripeEnabled) {
      await initStripePayment()
    }
  })
  onMounted(async () => {
    console.log("Payment field loaded")
    state.credit_card_fee = computedOrder.value?.credit_card_fee
    state.changed_credit_card_fee_on_mounted = true
    if (props.hasCardPointeEnabled) {
      window.addEventListener("message", setToken, false)
    }
    // props.disableAllFields = props.disableAllFields;
  })

  onUnmounted(() => {
    window.removeEventListener("message", setToken, false)
  })

  const setToken = (event) => {
    if (typeof event.data != "object" && event.data != null) {
      var token = JSON.parse(event.data)
      state.card_pointe_token = token.message
    }
  }

  const rules = computed(() => ({
    customer: {
      first_name: { required, $lazy: true },
      last_name: { required, $lazy: true },
      zip: { required, $lazy: true },
      avs_street: { required, $lazy: true },
      city: { required, $lazy: true },
      state: { required, $lazy: true }
    },
    cardInfo: {
      cardNumber: { required, ccRule, $lazy: true },
      expirationDate: { required, expirationRule, $lazy: true },
      cvv: { required, cvvRule, $lazy: true },
      type: { required, $lazy: true },
      merchant_name: { required, $lazy: true }
    },
    partialPayAmount: state.isPartial ? { required, $lazy: true } : {}
  }))

  const cardPointrules = computed(() => ({
    customer: {
      first_name: { required, $lazy: true },
      last_name: { required, $lazy: true },
      zip: { required, $lazy: true },
      avs_street: { required, $lazy: true },
      city: { required, $lazy: true },
      state: { required, $lazy: true }
    },
    cardInfo: {
      expirationDate: { required, expirationRule, $lazy: true },
      cvv: { required, cvvRule, $lazy: true },
      type: { required, $lazy: true },
      merchant_name: { required, $lazy: true }
    },
    partialPayAmount: state.isPartial ? { required, $lazy: true } : {}
  }))

  const payButtonDisabled = computed(() => {
    if (props.disableAllFields) {
      return true
    } else {
      return (
        !props.isInternal && (!state.agreeToTerms || paymentAmount.value < 0)
      )
    }
  })

  const paymentTitle = computed(() => {
    if (
      props.isInternal &&
      (computedOrder.value?.status === "Invoiced" ||
        computedOrder.value?.status === "Approved")
    ) {
      if (computedOrder.value?.type === "RENT") {
        return "Charge down payment on rental"
      }
      if (computedOrder.value?.type === "RENT_TO_OWN") {
        return "Charge down payment on rent to own"
      }
      if (
        computedOrder.value?.type === "PURCHASE" ||
        computedOrder.value?.type === "PURCHASE_ACCESSORY"
      ) {
        return "Charge for purchase"
      }
    }
  })

  const v$ = useVuelidate(rules, state)
  const cpv$ = useVuelidate(cardPointrules, state)

  const afterHide = () => {
    if (!props.isInternal) {
      window.location.reload()
    }
  }

  const handleBankAccountInfo = (bank_name, account_number, routing_number) => {
    state.bank_name = bank_name
    state.account_number = account_number
    state.routing_number = routing_number
  }

  const initialCustomerState = {
    first_name: "",
    last_name: "",
    email: "",
    zip: null,
    avs_street: "",
    city: "",
    state: ""
  }

  const initialCardInfoState = {
    cardNumber: null,
    expirationDate: "",
    cvv: null,
    type: "",
    merchant_name: ""
  }

  const clearAllFields = () => {
    state.customer = { ...initialCustomerState }
    state.cardInfo = { ...initialCardInfoState }
  }

  const handlePostPaymentPublic = async (paymentResponse) => {
    if (
      Number(paymentResponse.calculated_remaining_order_balance).toFixed(2) > 0
    ) {
      state.paymentMessage = `We have received your payment. Your remaining balance is ${$fc(
        Number(paymentResponse.calculated_remaining_order_balance)
      )}. Please pay the remaining balance to complete your order.`
    } else {
      state.paymentMessage = customerOrderStore.publicCms.afterPaymentMessage
    }
    if (props.isDriverPayment) {
      console.log(state.lineItemsPaid)
      const { data, isLoading, error } =
        await customerApi.driverPaymentNotification({
          order_id: computedOrder.value.id,
          containers_paid_for: [...state.lineItemsPaid]
        })
    }
    setTimeout(() => {
      state.customerPaidDialog = false
      window.location.reload()
    }, 10000)
  }

  const handlePayingPurchaseOrders = async (paymentObj) => {
    state.error = null
    const paidOrderResponse = await customerApi.payByCreditCard(paymentObj)
    if (paidOrderResponse.error.value !== undefined) {
      if (
        paidOrderResponse?.error?.value?.response?.data?.detail.includes(
          "Suspected Fraud"
        )
      ) {
        state.error =
          "Your payment was declined. Please try again or contact your bank."
        return
      }
      state.error = paidOrderResponse.error.value.response.data.detail
      return
    }
    customerOrderStore.setPublicOrder(paidOrderResponse.data.value)
    state.partialPayAmount = 0
    return paidOrderResponse.data.value
  }

  const addCardOnFile = async () => {
    state.error = null
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      state.error = "Please fill out all required fields"
      return
    }

    state.loading = true
    let creditCardObj = {
      first_name: state.customer.first_name,
      last_name: state.customer.last_name,
      zip: state.customer.zip,
      avs_street: state.customer.avs_street,
      city: state.customer.city,
      state: state.customer.state,
      cardNumber: state.cardInfo.cardNumber,
      expirationDate: state.cardInfo.expirationDate,
      cardCode: state.cardInfo.cvv,
      merchant_name: state.cardInfo.merchant_name,
      type: state.cardInfo.type,
      order_id: computedOrder.value?.id
    }

    if (state.bank_name !== "") {
      creditCardObj["bank_name"] = state.bank_name
      creditCardObj["account_number"] = state.account_number
      creditCardObj["routing_number"] = state.routing_number
    }

    const { error } = await customerApi.addCardOnFile(creditCardObj)
    state.loading = false
    if (!error.value) {
      const { data, isLoading, error } = await customerApi.getOrderByDisplayId(
        customerOrderStore.order.display_order_id
      )
      customerOrderStore.setOrder(data.value)
      props.isAddCardOnFile = false
      props.changeCreditCard = true
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Added Card on File.",
        group: "br",
        life: 2000
      })
      props.refreshFunction()
    } else {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to Add Card on File.",
        group: "br",
        life: 2000
      })
    }
  }

  const removeCardOnFileCancel = async () => {
    state.customerRemoveCardOnFile = false
  }

  const removeCardOnFileFinal = async () => {
    state.remove_card_loading = true
    await customerApi.removeCustomerPaymentProfile(
      customerOrderStore.order.id,
      "CREDIT_CARD"
    )
    /*await customerApi.updateOrder(customerOrderStore.order.id, {
    customer_profile_id: null,
    is_autopay: false,
  });*/
    const { data, isLoading, error } = await customerApi.getOrderByDisplayId(
      customerOrderStore.order.display_order_id
    )
    customerOrderStore.setOrder(data.value)
    state.customerRemoveCardOnFile = false
    state.remove_card_loading = false

    props.refreshFunction()
  }

  const removeCardOnFile = async () => {
    state.customerRemoveCardOnFile = true
  }

  const changeCreditCard = async () => {
    state.error = null
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      state.error = "Please fill out all required fields"
      return
    }

    state.update_card_loading = true
    let changeCreditCardObj = {
      first_name: state.customer.first_name,
      last_name: state.customer.last_name,
      zip: state.customer.zip,
      avs_street: state.customer.avs_street,
      city: state.customer.city,
      state: state.customer.state,
      cardNumber: state.cardInfo.cardNumber,
      expirationDate: state.cardInfo.expirationDate,
      cardCode: state.cardInfo.cvv,
      merchant_name: state.cardInfo.merchant_name,
      type: state.cardInfo.type,
      order_id: computedOrder.value?.id
    }

    const { changeCreditCardResponse, error } =
      await customerApi.changeCreditCard(changeCreditCardObj)
    state.update_card_loading = false

    if (!error.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Changed the card on file successfully",
        group: "br",
        life: 2000
      })
      props.refreshFunction()
    } else {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Changing the card on file failed.",
        group: "br",
        life: 2000
      })
    }
  }
  const isOverridePaymentPresent = computed(() => {
    return props.overridePaymentAmount > 0
  })
  const isBoolean = (val) => "boolean" === typeof val

  const payOrder = async () => {
    state.loading = true
    state.error = null
    state.lineItemsPaid = [...props.boxesBeingPaidFor]
    // if(!state.payCustomerProfile){

    // }

    if (!props.hasCardPointeEnabled) {
      const isFormCorrect = await v$.value.$validate()
      if (!isFormCorrect && !state.payCustomerProfile) {
        state.error = "Please fill out all required fields"
        state.loading = false
        return
      }
    }
    if (props.hasCardPointeEnabled) {
      const isFormCorrect = await cpv$.value.$validate()
      if (!isFormCorrect && !state.payCustomerProfile) {
        state.error = "Please fill out all required fields"
        state.loading = false
        return
      }
    }
    if (state.isPartial && state.partialPayAmount == 0) {
      state.error = "Please enter a partial payment amount"
      state.loading = false
      return
    }

    state.loading = true

    let paymentObj = {
      paid_at: state.paid_at,
      first_name: state.customer.first_name,
      last_name: state.customer.last_name,
      zip: state.customer.zip,
      cardNumber: state.cardInfo.cardNumber,
      expirationDate: state.cardInfo.expirationDate,
      type: state.cardInfo.type,
      merchant_name: state.cardInfo.merchant_name,
      avs_street: state.customer.avs_street,
      state: state.customer.state,
      city: state.customer.city,
      cardCode: state.cardInfo.cvv,
      card_pointe_token: state.card_pointe_token,
      total_paid:
        state.credit_card_fee && props.bankFee > 0
          ? paymentAmount.value - props.bankFee
          : paymentAmount.value,
      transaction_created_at: state.transaction_paid_at
    }

    if (props.customizable_auto_pay_date && state.autopay_day != 0) {
      paymentObj["autopay_day"] = state.autopay_day
    }

    paymentObj = Object.assign(paymentObj, {
      display_order_id: computedOrder.value?.display_order_id,
      order_id: computedOrder.value?.id,
      convenience_fee_total:
        state.credit_card_fee || props.bankFee > 0 ? props.bankFee : 0,
      pay_with_customer_profile: state.payCustomerProfile
    })

    if (props.overridePaymentMethod !== undefined) {
      await props.overridePaymentMethod(paymentObj)
      state.loading = false
      return
    }

    let currentDate = new Date()
    let date = currentDate.getDate()

    if (isRental.value) {
      if (computedOrder.value?.rent_periods.length == 1) {
        paymentObj.rent_period_ids = [computedOrder.value?.rent_periods[0].id]
      } else {
        paymentObj.rent_period_ids = props.selectedRentPeriodsIds
      }
      if (isOverridePaymentPresent.value) {
        // if this is an override payement payment fields, then that means we are inserting our payment amount for the
        // rent period and then we need to check if they have inputted either one of these amounts and determine if those
        // paymentobj fields should be populated
        if (props.rentPaymentAmount > 0) {
          paymentObj.rent_period_paid_amt = props.rentPaymentAmount
        }
        if (props.feePaymentAmount > 0) {
          paymentObj.rent_period_fee_paid_amt = props.feePaymentAmount
        }

        if (props.taxPaymentAmount) {
          paymentObj.rent_period_tax_paid_amt = props.taxPaymentAmount
        }
      }
      paymentObj.rent_due_on_day = date
    }

    if (state.rental_payment_day_of_month !== null) {
      console.log(state.rental_payment_day_of_month)
      paymentObj.rent_due_on_day = state.rental_payment_day_of_month
    }

    const gLineItems = computedOrder.value?.line_items.map((item) => {
      return {
        item_id: item.id,
        item_name: item.title,
        coupon: null,
        discount: null,
        item_category: "CONTAINER",
        price: item.calculated_total_revenue,
        quantity: 1
      }
    })

    if (!props.isDriverPayment && $isPublic) {
      if (customerOrderStore?.publicCms?.has_analytics && gtag != undefined) {
        gtag("event", "purchase", {
          transaction_id: paymentObj?.display_order_id,
          value: paymentAmount.value,
          tax: paymentObj?.calculated_order_tax,
          shipping: paymentObj?.calculated_shipping_revenue_total,
          currency: "USD",
          coupon: null,
          items: gLineItems
        })
      }
    }

    if (isRental.value) {
      if (state.payCustomerProfile) {
        paymentObj.cardNumber = ""
        paymentObj.cardCode = ""
        paymentObj.zip = ""
        paymentObj.pay_with_customer_profile = true
      }
      let rentalOrderResponse = await customerApi.payRentalOrder(paymentObj)
      if (rentalOrderResponse.error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Payment was Unsuccessful",
          group: "br",
          life: 2000
        })
        state.loading = false
        return
      } else {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Payment Successful",
          group: "br",
          life: 2000
        })
        if (props.sendSuccessFeedBack) {
          const amount = []
          paymentObj.rent_period_ids.forEach((id) => {
            computedOrder.value?.rent_periods.forEach((rent_period) => {
              if (id == rent_period.id) {
                amount.push(rent_period.calculated_rent_period_total_balance)
              }
            })
          })
          transactionTypeStore.setAmount(amount)
          emit("handleSuccessFeedback", {})
        }
        setTimeout(() => {
          props.rentalAfterPayReset(rentalOrderResponse.data.value)
        }, 1000)
        clearAllFields()
      }
    }

    if (isRentToOwn.value) {
    }

    if (isPurchase.value) {
      let paymentResponse = await handlePayingPurchaseOrders(paymentObj)
      if (!props.isInternal && state.error === null) {
        handlePostPaymentPublic(paymentResponse)
        state.customerPaidDialog = true
      }
    }

    state.loading = false
    if (state.error === null && !isRental.value) {
      state.customerPaidDialog = true

      let data = await customerApi.getOrderByIdPublic(computedOrder.value.id)
      data = data.data
      if (
        Number(data.value.calculated_remaining_order_balance).toFixed(2) > 0
      ) {
        state.paymentMessage = `We have received your payment. Your remaining balance is ${$fc(
          Number(data.value.calculated_remaining_order_balance).toFixed(2)
        )}. Please pay the remaining balance to complete your order.`
      } else {
        state.paymentMessage =
          customerOrderStore.publicCms?.afterPaymentMessage ||
          usersStore.cms.afterPaymentMessage
      }
    }
  }

  const isCancelled = () => {
    let data =
      computedOrder.value &&
      computedOrder.value?.status?.toLowerCase() === "cancelled"
    return isBoolean(data) ? data : false
  }

  const paidInFull = () => {
    let data =
      computedOrder.value &&
      computedOrder.value?.status !== "Cancelled" &&
      Number(computedOrder.value?.calculated_remaining_order_balance) === 0 &&
      (computedOrder.value?.status === "Paid" ||
        computedOrder.value?.status === "Completed" ||
        computedOrder.value?.status === "Delivered") &&
      internalOrderPaidInFull()
    return isBoolean(data) ? data : false
  }

  const internalOrderPaidInFull = () => {
    return (
      computedOrder.value &&
      computedOrder.value?.status !== "Cancelled" &&
      Number(computedOrder.value?.calculated_remaining_order_balance) === 0 &&
      (computedOrder.value?.status === "Paid" ||
        computedOrder.value?.status === "Completed" ||
        computedOrder.value?.status === "Delivered")
    )
  }

  const computedOrder = computed(() => {
    const order = customerOrderStore.order
    const publicOrder = customerOrderStore.publicOrder

    if (props.isInternal && order !== undefined && order !== null) {
      return order
    }

    return publicOrder
  })

  const isRentToOwn = computed(() => {
    return computedOrder.value?.type === "RENT_TO_OWN"
  })

  const isRental = computed(() => {
    return computedOrder.value?.type === "RENT"
  })

  const isPurchase = computed(() => {
    return (
      computedOrder.value?.type === "PURCHASE" ||
      computedOrder.value?.type === "PURCHASE_ACCESSORY"
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

  const getPriceAndBalance = computed(() => {
    let totalPrice = Number(computedOrder.value?.calculated_total_price)
    let remainingBalance = Number(
      computedOrder.value?.calculated_remaining_order_balance
    )

    // if card is selected add bank fee to remaining balance
    if (props.creditCardSelected && computedOrder.value?.type !== "RENT") {
      remainingBalance = remainingBalance + props.bankFee
    }
    if (computedOrder.value?.type === "RENT") {
      // will always be populated with rent orders
      let current_rent_period_id = computedOrder.value?.current_rent_period.id
      // we want to display the current rent period's total balance
      for (let i = 0; i < computedOrder.value?.rent_periods.length; i++) {
        let period = computedOrder.value?.rent_periods[i]
        if (period.id === current_rent_period_id) {
          remainingBalance = Number(period.calculated_rent_period_total_balance)
          break // Exit the loop once a match is found
        }
      }
    }

    if (computedOrder.value?.status === "Paid") {
      remainingBalance = 0
    }

    return {
      totalPrice: totalPrice,
      remainingBalance: remainingBalance
    }
  })

  const paymentAmount = computed(() => {
    const balances = getPriceAndBalance.value
    let rb = 0

    if (computedOrder.value?.type === "RENT") {
      let realBankFee = state.credit_card_fee ? props.bankFee : 0

      if (isOverridePaymentPresent.value) {
        return !props.applyBankFee
          ? props.overridePaymentAmount
          : props.overridePaymentAmount + realBankFee
      }

      return Number(
        !props.applyBankFee
          ? balances.remainingBalance
          : balances.remainingBalance + realBankFee
      ).toFixed(2)
    }

    if (isOverridePaymentPresent.value) {
      let realBankFee = props.bankFee
      return !props.applyBankFee
        ? props.overridePaymentAmount
        : props.overridePaymentAmount + realBankFee
    }
    rb = props.isPartial
      ? state.partialPayAmount
      : !props.applyBankFee
      ? balances.remainingBalance
      : balances.remainingBalance + props.bankFee

    return Number(rb).toFixed(2)
  })

  const remainingBalanceCalc = computed(() => {
    if (props.overridePaymentAmount) {
      return props.overridePaymentAmount
    }
    const balances = getPriceAndBalance.value
    let rb =
      balances.remainingBalance > 0
        ? balances.remainingBalance - paymentAmount.value
        : balances.totalPrice - paymentAmount.value
    return Number(rb).toFixed(2)
  })

  const update_bank_fee = (bank_fee) => {
    props.bankFee = bank_fee
  }

  watch(
    () => state.isPartial,
    (newVal, oldVal) => {
      // if it is false, then we need to wipe the partial payment
      let data = { isPartial: newVal }
      if (!newVal) {
        state.partialPayAmount = 0
      }
      props.updateFromPaymentFields(data, update_bank_fee)
    }
  )

  watch(
    () => state.partialPayAmount,
    (newVal, oldVal) => {
      let data = { partialPayAmount: newVal }
      props.updateFromPaymentFields(data)
      state.confirmedPartialAmount = false
    }
  )
  watch(
    () => state.confirmedPartialAmount,
    async (newVal) => {
      if (newVal) {
        await initStripePayment()
      }
    }
  )

  watch(
    () => state.rental_payment_day_of_month,
    (newVal, oldVal) => {
      console.log(newVal)
    }
  )

  watch(
    () => state.credit_card_fee,
    async (newVal, oldVal) => {
      if (!state.changed_credit_card_fee_on_mounted) {
        return
      }
    }
  )

  watch(
    () => state.payCustomerProfile,
    (newVal, oldVal) => {
      if (newVal) {
        state.disableAllInputFields = true
      } else {
        state.disableAllInputFields = false
      }
    }
  )
</script>

<style scoped>
  div#container {
    width: 800px;
    /* or whatever width you want */
    overflow: hidden;
    /* if you don't want a scrollbar, set to hidden */
    overflow-x: hidden;
    /* hides horizontal scrollbar on newer browsers */

    /* resize and min-height are optional, allows user to resize viewable area */
    -webkit-resize: vertical;
    -moz-resize: vertical;
    resize: vertical;
  }

  @media screen and (max-width: 600px) {
    div#container {
      width: 95vw;
      /* or whatever width you want */
    }
  }

  iframe#embed {
    width: 1000px;
    /* set this to approximate width of entire page you're embedding */
    margin-left: -183px;
    /* clipping left side of page */
    /* clipping top of page */
    margin-bottom: -244px;
    /* clipping bottom of page */
    overflow: hidden;

    /* resize seems to inherit in at least Firefox */
    -webkit-resize: none;
    -moz-resize: none;
    resize: none;
  }
</style>
