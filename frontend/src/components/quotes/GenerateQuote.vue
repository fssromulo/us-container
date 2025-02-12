<template>
  <div
    class="w-full p-6 m-4 shadow-xl surface-card md:w-1/3 bg-0 dark:bg-900 rounded-border"
  >
    <div class="grid grid-cols-12 gap-4 mt-2 formgrid p-fluid">
      <div class="col-span-12 mt-4 md:col-span-1 xl:col-span-1">
        <OverlayBadge
          :value="
            customerOrderStore.cart.containers.length +
            customerOrderStore.cart.accessories.length
          "
          severity="danger"
          v-if="
            customerOrderStore.cart.containers.length +
            customerOrderStore.cart.accessories.length
          "
        >
          <i
            @click="viewCart"
            class="pi pi-shopping-cart p-text-secondary"
            style="font-size: 2rem; float: right"
          />
        </OverlayBadge>
        <!-- <cart-mini class="z-99" /> -->
      </div>
    </div>

    <div class="flex flex-col items-center mb-2">
      <div
        class="flex flex-wrap justify-content-center col-12"
        style="position: relative"
      >
        <img
          v-if="!state.load_logo && account_is_usac"
          id="low-res-image"
          src="/images/blocks/usac_logo_small.png"
          alt="Preview"
          :height="$isPublic ? 150 : 75"
        />

        <img
          id="high-res-image"
          style="display: none"
          :src="usersStore.cms?.logo_settings.logo_path"
          @load="onImageLoad"
          alt="Image"
          :height="$isPublic ? 150 : 75"
        />
      </div>
      <div class="flex flex-wrap justify-content-center">
        <p class="text-3xl col-12">
          {{ $isPublic ? "Get A Container Quote" : "Quotes" }}
        </p>
      </div>
      <br />
      <br />
      <div
        class="flex flex-wrap col-12 justify-content-center"
        v-if="$isPublic && accountUSACorCanada"
      >
        <b>
          <p class="text-xl"> We cover USA and Canada. </p>
        </b>
      </div>
      <div
        class="flex flex-wrap col-12 justify-content-center"
        v-if="$isPublic && accountUSACorCanada"
      >
        <p class="text-2xl"> Choose Country: </p>
      </div>
      <div
        class="flex col-12 justify-content-center"
        v-if="$isPublic && accountUSACorCanada"
      >
        <button
          class="flag-button usa-flag"
          :class="{
            selected: state.selectedFlag === 'USA' || getAccountCountry == 'USA'
          }"
          aria-label="Select USA flag"
          @click="selectFlag('USA')"
        ></button>
        <button
          class="flag-button canada-flag"
          :class="{
            selected:
              state.selectedFlag === 'Canada' || getAccountCountry == 'Canada'
          }"
          @click="selectFlag('Canada')"
          aria-label="Select Canada flag"
        ></button>
      </div>
    </div>

    <div class="flex flex-col items-center w-full">
      <div class="w-full mb-3 field col-12 md:col-7">
        <InputText
          mode="decimal"
          v-model="state.quote.searchZip"
          :class="{ 'p-invalid': v$.quote.searchZip.$invalid }"
          class="p-inputtext-lg"
          style="width: 100%"
          :placeholder="
            state.quote.isPickupOrDelivery === 'Delivery'
              ? `Enter the delivery ${postalZipText} code`
              : `Enter your ${postalZipText} code`
          "
        />
      </div>
      <!-- <div class="flex flex-col items-center w-full mb-2" v-if="$isPublic">
      <div class="mt-2" style="width: 100%;">
        <SelectButton v-model="state.quote.buyType" :options="orderTypes" optionLabel="label" optionValue="value"
          optionDisabled="disabled"

          :pt="{
              root: ({ context }) => ({
                class: `order-type-btn grid grid-cols-${orderTypes.length}`,
              }),
            }" />
      </div>
    </div> -->
      <div class="mb-3 surface-100 col-12" style="height: 2px"></div>
      <div v-if="$isPublic" class="w-full mb-3 field col-7">
        <Select
          placeholder="Select container "
          class="w-full p-inputtext-lg"
          scrollHeight="500px"
          v-model="state.quote.selectedSize"
          optionLabel="text"
          optionValue="value"
          :options="orderedUniqueTitles"
        >
          <template #content="option"> </template>
        </Select>
      </div>
      <div class="flex flex-col items-center w-full">
        <div class="mt-4 pickup-delivery-btn" style="width: 100%">
          <SelectButton
            v-model="state.quote.isPickupOrDelivery"
            :options="deliveryTypes"
            optionLabel="label"
            optionValue="value"
            optionDisabled="disabled"
            :pt="{
              root: ({ context }) => ({
                class: `pickup-delivery-btn grid grid-cols-${deliveryTypes.length}`
              })
            }"
          />
        </div>
        <div class="mt-6" style="width: 100%">
          <SelectButton
            v-model="state.quote.buyType"
            :options="orderTypes"
            optionLabel="label"
            optionValue="value"
            optionDisabled="disabled"
            :pt="{
              root: ({ context }) => ({
                class: `order-type-btn grid grid-cols-${orderTypes.length}`
              })
            }"
          />
        </div>
      </div>

      <div
        class="my-3 mb-2 opacity-50 surface-border border-top-2 col-12"
      ></div>
      <div
        :class="`grid grid-cols-${numOfQuoteButtons} gap-2`"
        style="min-width: 80%"
      >
        <div :class="$isPublic ? 'field col-span-1 mt-1' : 'field col-span-1'">
          <Button
            @click="generateQuote"
            :loading="state.loading"
            :disabled="
              ($isPublic && state.quote.selectedSize == undefined) ||
              state.quote.searchZip == undefined ||
              state.quote.searchZip == ''
            "
            class="w-full mr-2 p-button-raised"
            label="Get Quote"
          >
          </Button>
        </div>
        <div v-if="!$isPublic && canUseQuickSale" class="col-span-1 field">
          <Button
            @click="state.quickSale = true"
            class="w-full p-button-raised"
            label="Quick Sale"
          >
          </Button>
        </div>
        <div v-if="!$isPublic && canUseQuickSale" class="col-span-1 field">
          <Button
            @click="state.quickRent = true"
            class="w-full p-button-raised"
            label="Quick Rent"
          >
          </Button>
        </div>
        <div v-if="!$isPublic" class="col-span-1 field">
          <Button
            @click="copyLinkToClipboard"
            class="w-full p-button-raised p-button-secondary"
            label="Sales Link"
          >
          </Button>
        </div>
      </div>
    </div>

    <Message
      @close="state.copiedLink = null"
      v-if="state.copiedLink"
      severity="info"
      >Link copied! Here it is {{ state.copiedLink }}</Message
    >
    <Message v-if="v$.quote.searchZip.$invalid" life="3000" severity="error"
      >Must enter valid {{ postalZipText }} code and select container
    </Message>
    <Dialog
      class="w-full"
      :class="{ 'md:w-3/4': largeQuoteDialog, 'md:w-1/4': smallQuoteDialog }"
      v-model:visible="state.quoteIsVisible"
      maximizable
      @after-hide="cancel"
      closeOnEscape
      header="Quotes"
      :modal="true"
      :dismissableMask="true"
      style="height: 60rem"
    >
      <quotes-main
        v-if="!orderInProgress"
        @hide="state.quoteIsVisible = false"
        :quotesList="state.quotesList"
        :buyType="state.quote.buyType"
        :accessoryList="state.accessoriesList"
        :pageSize="
          $isPublic && state.quote.isPickupOrDelivery != 'Pickup'
            ? 0
            : state.quote.buyType == 'RENT'
            ? 3
            : state.quote.isPickupOrDelivery == 'Pickup'
            ? 4
            : 12
        "
        :isPickup="state.quote.isPickupOrDelivery === 'Pickup'"
        :visibleQuoteOption="state.visibleQuoteOption"
        :isRental="state.quote.buyType == 'RENT'"
        :payOnDeliveryContract="payOnDeliveryContract"
        :dupplicationMode="props.dupplicationMode"
        :line_items="props.line_items"
        :duplicationMode="props.duplicationMode"
      />
      <CreateInvoiceWizard
        v-if="orderInProgress"
        :customer="props.customer"
        :address="props.address"
        :dupplicationMode="props.dupplicationMode"
        :overridden_user_id="props.overridden_user_id"
      />
    </Dialog>
    <Dialog
      v-model:visible="state.quickSale"
      class="w-full md:w-3/4"
      maximizable
      @after-hide="cancel"
      closeOnEscape
      :breakpoints="{
        '2000px': '75vw',
        '1400px': '85vw',
        '1200px': '85vw',
        '992px': '85vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
      header="Quick Sale"
      :modal="true"
      :dismissableMask="true"
    >
      <quick-sale
        v-if="state.quickSale"
        :quotesList="state.quotesList"
        :accessoryList="state.accessoriesList"
        :pageSize="12"
        :isPickup="state.quote.isPickupOrDelivery === 'Pickup'"
      />
    </Dialog>
    <Dialog
      v-model:visible="state.quickRent"
      class="w-full md:w-3/4"
      maximizable
      @after-hide="cancel"
      closeOnEscape
      :breakpoints="{
        '2000px': '75vw',
        '1400px': '85vw',
        '1200px': '85vw',
        '992px': '85vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
      header="Quick Rent"
      :modal="true"
      :dismissableMask="true"
    >
      <quick-rent
        v-if="state.quickRent"
        :quotesList="state.quotesList"
        :accessoryList="state.accessoriesList"
        :pageSize="12"
        :isPickup="state.quote.isPickupOrDelivery === 'Pickup'"
      />
    </Dialog>
  </div>
  <div
    class="flex justify-center mt-4 sm:col-span-12 xl:col-span-12"
    v-if="hasSaleContactText"
  >
    <p>Sales Team - Call/Text</p>
  </div>
  <div
    class="flex justify-center mt-4 sm:col-span-12 xl:col-span-12"
    v-if="hasAgentCode"
  >
    <p>{{ sales_text }}</p>
  </div>
  <span v-if="hasSaleContactText">&nbsp; </span>
  <div
    class="flex justify-center mt-4 sm:col-span-12 xl:col-span-12"
    v-if="hasSaleContactText"
  >
    <p>
      <a :href="'tel:' + usersStore?.cms['quote_contact_phone']">{{
        usersStore?.cms["quote_contact_phone"]
      }}</a>
    </p>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, watch, ref } from "vue"

  import _groupBy from "lodash.groupby"
  import cloneDeep from "lodash.clonedeep"
  import { useVuelidate } from "@vuelidate/core"
  import { required, maxValue, helpers } from "@vuelidate/validators"
  import QuotesMain from "./QuotesMain.vue"
  import QuickSale from "./QuickSale.vue"
  import QuickRent from "./QuickRent.vue"

  import CreateInvoiceWizard from "@/components/invoicing/create/CreateInvoiceWizard.vue"
  import { useAuth0 } from "@auth0/auth0-vue"
  import { useUsers } from "@/store/modules/users"

  import PricingService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import TaxApi from "@/api/tax"
  import AccountApi from "@/api/account"
  import QuoteGenerationService from "@/service/QuoteGeneration"

  import { useContainerPrices } from "@/store/modules/pricing"
  import { useInventory } from "@/store/modules/inventory"

  import { useTaxes } from "@/store/modules/taxes"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import CartService from "@/service/Cart"
  import { accountMap } from "../../utils/accountMap"
  import QuoteSearchesApi from "@/api/search_quotes"
  import UserApi from "@/api/user"

  const userApi = new UserApi()
  import { useRoute } from "vue-router"
  import { country } from "../../utils/formatCurrency"
  import CustomerApi from "@/api/customers"
  const customerApi = new CustomerApi()

  const props = defineProps({
    zip_code: {
      type: String,
      default: null
    },
    address: {
      type: Object,
      default: null
    },
    customer: {
      type: Object,
      default: null
    },
    dupplicationMode: {
      type: Boolean,
      default: false
    },
    order_type: {
      type: String,
      default: null
    },
    is_pickup: {
      type: Boolean,
      default: false
    },
    line_items: {
      type: Array,
      default: []
    },
    overridden_user_id: {
      type: String,
      default: null
    }
  })

  const emit = defineEmits(["hide"])

  const useRouteVar = useRoute()
  const route = inject("$route")
  const $isPublic = inject("$isPublic") || useRouteVar.path.includes("/quoting")
  const $isObjectPopulated = inject("$isObjectPopulated")
  const $fp = inject("$formatPhone")

  const toast = useToast()
  const { user } = useAuth0()
  const authUser = user
  const usersStore = useUsers()

  const customerOrderStore = useCustomerOrder()
  const cartService = new CartService()
  const accountApi = new AccountApi()

  const pricingService = new PricingService()
  const pricingApi = new PricingApi()
  const quoteGenerationService = new QuoteGenerationService()
  const taxApi = new TaxApi()

  const pricingStore = useContainerPrices()
  const inventoryStore = useInventory()

  const quoteSearchesApi = new QuoteSearchesApi()

  const taxStore = useTaxes()

  const viewCart = () => {
    customerOrderStore.setCreateOrderStatus("IN_PROGRESS")
    state.quoteIsVisible = true
  }
  const postalZipText = computed(() => {
    return usersStore.cms?.account_country &&
      usersStore.cms?.account_country == "Canada"
      ? "postal"
      : "zip"
  })

  const getAccountId = computed(() => {
    return accountMap[window.location.host].account_id
  })

  const getAccountCountry = computed(() => {
    let account_country = usersStore.cms?.account_country
    return account_country == null ? "USA" : account_country
  })

  const onImageLoad = (event) => {
    state.load_logo = true
    var highResImage = document.getElementById("high-res-image")

    highResImage.style.display = "block"
  }

  const sales_text = computed(() => {
    if (state.user_name != "" && state.user_number) {
      const text = `Text or Call your sales rep ${state.user_name} at ${state.user_number} for the best price`
      return text
    } else {
      return ""
    }
  })
  const cartMini = ref()
  const toggle = (event) => {
    cartMini.value.toggle(event)
  }

  const numOfQuoteButtons = computed(() => {
    if ($isPublic) return 1
    if (canUseQuickSale.value) return 3
    return 2
  })
  const insertGoogleScript = () => {
    console.log("inserting google script (GenerateQuote.vue)")
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
  }

  // CHANGE THIS - remove the 1, need to check the page url and have an account map instead
  onMounted(async () => {
    insertGoogleScript()

    if (taxStore.taxes.length === 0) {
      const { data } = $isPublic
        ? await taxApi.getTaxesPublic(
            accountMap[window.location.host].account_id
          )
        : await taxApi.getTaxes()
      taxStore.setTaxes(data.value)
    }

    if (pricingStore?.locations?.length === 0) {
      const { data } = $isPublic
        ? await pricingApi.getLocationsPublic(
            accountMap[window.location.host].account_id
          )
        : await pricingApi.getLocations()
      pricingStore.setLocations(
        data?.value?.map((v) => pricingService.dtoLocation(v))
      )
    }

    if (pricingStore?.containerPrices?.length === 0) {
      const { data } = $isPublic
        ? await pricingApi.getContainerPricingPublic(
            accountMap[window.location.host].account_id
          )
        : await pricingApi.getContainerPricing()
      pricingStore.setContainerPrices(
        data?.value?.map((v) => pricingService.dtoContainerPricing(v))
      )
    }
    if (pricingStore.accessoryPrices.length === 0) {
      const { data } = await pricingApi.getProductPublic(
        accountMap[window.location.host].account_id
      )
      const prices = data.value.map((p) => pricingService.dtoProductPricing(p))
      pricingStore.setAccessoryPrices(prices)
    }

    if (!$isObjectPopulated(usersStore?.cms)) {
      const { data } =
        $isPublic &&
        (await accountApi.getPublicAccount(
          accountMap[window.location.host].account_id
        ))
      usersStore.setCms(data.value)
      userStore.setIntegrations(data.value.integrations)
    }
    resetQuote()

    if (props.zip_code != null) {
      state.quote.searchZip = props.zip_code
      state.quote.buyType = props.order_type
      state.quote.isPickupOrDelivery = props.is_pickup ? "Pickup" : "Delivery"
      await generateQuote()
    }

    const { data } = await userApi.getPublicUserById(
      route.currentRoute.value.query.code,
      usersStore?.cms?.id
    )
    if (data.value) {
      state.user_name = data.value.full_name

      state.user_number = $fp(data.value.phone)
    }
  })
  const payOnDeliveryContract = computed(() => {
    return usersStore.cms?.pay_on_delivery_contract || {}
  })
  const emptyQuote = {
    searchZip: null,
    isPickupOrDelivery: "Delivery",
    quantity: 1,
    buyType: "PURCHASE"
  }

  const hasAgentCode = computed(() => {
    return route.currentRoute.value.query.code ? true : false
  })
  const canUseQuickSale = computed(() => {
    let canUseQuickSale = userStore.cms.can_use_quick_sale == true
    return canUseQuickSale
  })
  const hasSaleContactText = computed(() => {
    let account_id = accountMap[window.location.host].account_id
    return (
      $isPublic &&
      userStore.cms != null &&
      !hasAgentCode.value &&
      usersStore.cms["quote_contact_phone"] != "" &&
      usersStore.cms["has_sales_contact_text"]
    )
  })
  const cancel = () => {
    customerOrderStore.setCreateOrderStatus("NOT_STARTED")
  }
  const mergedAccessoryLocationPrices = computed(() => {
    const accessoryPrices = cloneDeep(pricingStore.accessoryPrices)
    // remove duplicates from list of objects
    const mappedAccessories = accessoryPrices
      .map((accessory) => {
        const location = accessory.location
        delete accessory.location
        return Object.assign(accessory, location, {
          accessoryId: accessory.id,
          type: state.quote.buyType || "PURCHASE"
        })
      })
      .sort((a, b) => a.title.localeCompare(b.title))
    pricingStore.setFilteredAccessories(mappedAccessories)
    return mappedAccessories
  })
  const mergedContainerLocationPrices = computed(() => {
    const containerPrices = cloneDeep(pricingStore.containerPrices)
    // remove duplicates from list of objects
    const mappedContainers = containerPrices
      .map((container) => {
        const location = container.location
        delete container.location
        return Object.assign(container, location, {
          containerId: container.id
        })
      })
      .sort((a, b) => a.title?.localeCompare(b.title))

    return mappedContainers
  })

  const mergedInventoryPricing = computed(() => {
    const availableInventory = cloneDeep(
      inventoryStore.availableInventory
    ).sort((a, b) => a.title.localeCompare(b.title))
    return availableInventory
  })

  const isRentalsFeatureVisible = computed(() => {
    return usersStore.cms?.feature_flags?.rentals_enabled
  })

  const orderTypes = computed(() => {
    let return_list = [
      {
        label: "Purchase",
        value: "PURCHASE",
        disabled: false
      }
    ]

    if (
      usersStore.cms?.feature_flags?.rto_enabled == true ||
      usersStore.cms?.feature_flags?.rto_enabled == null
    ) {
      return_list.push({
        label: "RTO",
        value: "RENT_TO_OWN",
        disabled: false
      })
    }

    if (
      usersStore.cms?.feature_flags?.rentals_enabled == true ||
      usersStore.cms?.feature_flags?.rentals_enabled == null
    ) {
      return_list.push({
        label: "Rent",
        value: "RENT",
        disabled:
          !isRentalsFeatureVisible.value ||
          (state.quote.isPickupOrDelivery === "Pickup" ? true : false)
      })
    }

    return return_list
  })
  const deliveryTypes = computed(() => {
    return [
      {
        label: "Delivery",
        value: "Delivery",
        disabled: false
      },
      {
        label: "Pickup",
        value: "Pickup",
        disabled: state.quote.buyType === "RENT" ? true : false
      }
    ]
  })

  const accountUSACorCanada = computed(() => {
    return (
      accountMap[window.location.host].account_id == 1 ||
      accountMap[window.location.host].account_id == 5
    )
  })

  const state = reactive({
    loading: false,
    isPublic: window.location.origin.includes("localhost"),
    copiedLink: false,
    selectedSize: null,
    quoteIsVisible: false,
    quickSale: false,
    quickRent: false,
    quotesList: [],
    accessoriesList: [],
    quote: emptyQuote,
    originalQuote: null,
    isRental: false,
    visibleQuoteOption: "Container",
    productTypes: [
      {
        label: "Shipping Quote",
        value: "SHIPPING_CONTAINER"
      },
      {
        label: "Portable Quote",
        value: "PORTABLE_CONTAINER"
      }
    ],
    load_logo: false,
    user_name: "",
    user_number: "",
    country: "",
    countries: [
      {
        label: "USA",
        value: "USA"
      },
      {
        label: "Canada",
        value: "Canada"
      }
    ]
  })

  const copyLinkToClipboard = () => {
    const salesLink = `${
      userStore.cms?.sales_link_base_url &&
      userStore.cms?.sales_link_base_url != ""
        ? userStore.cms?.sales_link_base_url
        : ""
    }${usersStore.currentUser.id}`
    navigator.clipboard.writeText(salesLink).then(
      () => {
        state.copiedLink = salesLink
      },
      () => {}
    )
  }

  const orderInProgress = computed(() => {
    return customerOrderStore.createOrderStatus === "IN_PROGRESS"
  })
  const isInUSA = computed(
    () =>
      !usersStore.cms?.account_country ||
      usersStore.cms?.account_country != "Canada"
  )
  const zipRegex = /^\d{5}(?:[-\s]\d{4})?$/

  const rules = computed(() => {
    let q = {
      quote: {
        searchZip: { required, maxValue: maxValue(99999), $lazy: true },
        isPickupOrDelivery: { required, $lazy: true },
        quantity: { required, $lazy: true }
      }
    }
    q.quote.searchZip = {
      required,
      $lazy: true,
      validZip: helpers.withMessage(
        "ZIP Code must be at least 5 characters.",
        (value) => {
          if (!isInUSA.value) {
            return true
          }
          return zipRegex.test(value) //minLength(5)(value)
        }
      )
    }

    if ($isPublic) {
      q.quote.buyType = { required, $lazy: true }
    }
    return q
  })

  const v$ = useVuelidate(rules, state)

  const accessoriesTitles = computed(() => {
    return mergedAccessoryLocationPrices.value
      .map((p) => {
        return {
          text: p.title,
          value: p
        }
      })
      .sort((a, b) => a.text.localeCompare(b.text))
  })

  const productsTitles = computed(() => {
    return mergedContainerLocationPrices.value
      .map((p) => {
        return {
          text: p.title,
          value: p
        }
      })
      .sort((a, b) => a.text.localeCompare(b.text))
      .filter((a) => {
        return a.value.monthly_rental_price != 0
      })
  })

  const inventoryProductTitles = computed(() => {
    return mergedContainerLocationPrices.value
      .map((p) => {
        return {
          text: p.title,
          value: p
        }
      })
      .sort((a, b) => a.text.localeCompare(b.text))
  })

  const uniqueTitles = computed(() => {
    return Array.from(new Set(productsTitles.value.map((m) => m.text))).map(
      (text) => {
        return productsTitles.value.find((p) => p.text === text)
      }
    )
  })

  const sortAndDeduplicate = (list) => {
    return [...new Set(list)].sort()
  }

  const orderedUniqueTitles = computed(() => {
    let orderedUniqueTitlesVar = quoteGenerationService.orderedTitles
      .map((o) => {
        return uniqueTitles.value.find((t) => t.text === o)
      })
      .filter((p) => p)

    if (account_is_usac && state.quote.buyType == "RENT") {
      let element_20 = orderedUniqueTitlesVar.find(
        (element) => element.text == "20' Used Standard"
      )
      let element_40 = orderedUniqueTitlesVar.find(
        (element) => element.text == "40' Used High Cube"
      )

      element_20 = cloneDeep(element_20)
      element_40 = cloneDeep(element_40)

      element_20.text = "20 ft"
      element_40.text = "40 ft"

      return [element_20, element_40]
    }
    return orderedUniqueTitlesVar
  })

  const userStore = useUsers()

  const calculateRentalPrice = (container) => {
    return Object.assign(container, {
      monthly_owed: cartService.roundIt(container.monthly_price, 2)
    })
  }

  const largeQuoteDialog = computed(() => {
    return (
      state.quotesList.length > 1 ||
      (state.quotesList.length == 1 && state.quotesList[0].length > 1) ||
      orderInProgress.value
    )
  })
  const smallQuoteDialog = computed(() => {
    return (
      state.quotesList.length == 1 &&
      state.quotesList[0].length == 1 &&
      !orderInProgress.value
    )
  })

  const account_is_usac = computed(() => {
    return accountMap[window.location.host].account_id == 1
  })

  const selectFlag = async (country) => {
    if (country == "USA") {
      const { data } = await accountApi.getPublicAccount(1)
      const attributes = data.value
      attributes.id = data.value.id
      usersStore.setCms(attributes)
    } else {
      const { data } = await accountApi.getPublicAccount(5)
      const attributes = data.value
      attributes.id = data.value.id
      usersStore.setCms(attributes)
    }
  }

  const generateQuote = async () => {
    await quoteGenerationService.generateQuote(
      state,
      mergedContainerLocationPrices,
      mergedAccessoryLocationPrices,
      resetQuote,
      toast,
      v$,
      accountMap,
      userStore,
      $isPublic
    )
  }

  watch(
    () => customerOrderStore.createOrderStatus,
    (newVal, oldVal) => {
      if (newVal === "NOT_STARTED") {
        state.quoteIsVisible = false
      }
    }
  )

  watch(
    () => usersStore.cms?.id,
    async (newVal, oldVal) => {
      const { data } = await userApi.getPublicUserById(
        route.currentRoute.value.query.code,
        usersStore?.cms?.id
      )
      if (data.value) {
        state.user_name = data.value.full_name

        state.user_number = $fp(data.value.phone)
      }
    }
  )

  watch(
    () => pricingStore.accessoryPrices,
    async (newVal, oldVal) => {
      if (newVal.length === 0) {
        const mappedAccessories = pricingStore.accessoryPrices
          .map((accessory) => {
            const location = accessory.location
            delete accessory.location
            return Object.assign(accessory, location, {
              accessoryId: accessory.id,
              type: buyType
            })
          })
          .sort((a, b) => a.title.localeCompare(b.title))
        pricingStore.setFilteredAccessories(mappedAccessories)
      }
    }
  )

  watch(
    () => usersStore?.cms?.id,
    async (newVal, oldVal) => {
      const { data } = await pricingApi.getContainerPricingPublic(
        usersStore?.cms?.id
      )
      pricingStore.setContainerPrices(
        data?.value?.map((v) => pricingService.dtoContainerPricing(v))
      )
    }
  )

  watch(
    () => state.quoteIsVisible,
    (value, oldVal) => {
      if (props.dupplicationMode && oldVal == true && value == false) {
        customerOrderStore.resetCreateOrderStatus()
        emit("hide")
      }
    }
  )

  const resetQuote = () => {
    state.loading = false
    v$.value.$reset()
  }
</script>

<style scoped>
  .flag-buttons {
    display: flex;
    gap: 1rem;
  }

  .flag-button {
    width: 4.5rem;
    height: 2.5rem;
    background-size: cover;
    background-position: center;
    border: none;
    cursor: pointer;
    border: 3px solid #ccc;
    border-radius: 8px;
  }

  .flag-button:focus {
    outline: none;
  }

  .usa-flag {
    background-image: url("/images/blocks/usa_flag.webp");
  }

  .canada-flag {
    background-image: url("/images/blocks/canada_flag.png");
    margin-left: 20px;
  }

  .usa-flag:hover,
  .selected.usa-flag {
    border-color: #2824ff;
    box-shadow: 0 0 10px #3c3b6e;
  }

  .canada-flag:hover,
  .selected.canada-flag {
    border-color: #ff0000;
    box-shadow: 0 0 10px #ff0000;
  }
  .order-type-btn {
    width: 100%;
  }
</style>
