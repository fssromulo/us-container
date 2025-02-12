<template>
  <div class="col-span-12 p-4 xs:col-10 md:col-span-6 xl:col-span-4">
    <div
      class="p-4 shadow bg-0 dark:bg-900 rounded-border"
      style="border-radius: 6px"
    >
      <div class="flex items-start justify-between">
        <div>
          <div class="mb-2 text-xl font-medium text-900 dark:text-0">
            <span v-if="quote.is_single == false">(2) </span>{{ quoteTitle() }}
          </div>
          <p
            class="mt-0 mb-4 text-600 dark:text-200"
            :class="{
              'border-blue-500 text-blue-500 hover:border-blue-500':
                state.can_pay_on_delivery_order
            }"
          >
            {{ quote.location_name }} | ~{{ quote.distance }} {{ metrics }}
          </p>
        </div>
        <p style="font-size: 12px" v-if="quote.type === 'RENT_TO_OWN'"
          >CASH PRICE -
          {{ $fc(quote.price + quote.shipping_revenue + quote.tax) }}
        </p>
      </div>
      <ul v-if="quote.type === 'PURCHASE'" class="p-0 m-0 list-none">
        <li class="flex items-center justify-between px-0 py-2 border-b border">
          <span class="font-medium text-600 dark:text-200 text-md"
            >Container</span
          >
          <span class="font-medium text-900 dark:text-0 text-md">
            {{ $fc(quote.price) }}</span
          >
        </li>
        <li class="flex items-center justify-between px-0 py-2 border-b border">
          <span class="font-medium text-600 dark:text-200 text-md"
            >Shipping</span
          >
          <span class="font-medium text-900 dark:text-0 text-md">{{
            $fc(quote.shipping_revenue)
          }}</span>
        </li>
        <li
          class="flex items-center justify-between px-0 py-2"
          v-if="quote.tax > 0"
        >
          <span class="font-medium text-600 dark:text-200 text-md"
            >Sales Tax</span
          >
          <span class="font-medium text-900 dark:text-0 text-md">{{
            $fc(quote.tax)
          }}</span>
        </li>
        <li class="flex items-center justify-between px-0 py-2">
          <span class="font-medium text-600 dark:text-200 text-md">Total</span>
          <span class="font-medium text-900 dark:text-0 text-md">{{
            $fc(quote.price + quote.shipping_revenue + quote.tax)
          }}</span>
        </li>
      </ul>
      <DataTable
        v-if="quote.type === 'RENT_TO_OWN'"
        :value="quote.rent_to_own"
        class="p-datatable-sm"
      >
        <Column field="rent_period" header="Rent period (months)"></Column>
        <Column field="monthly_owed" header="Monthly Rate">
          <template #body="{ data }">
            <p>{{
              quote.is_single == false
                ? $fc(2 * data.monthly_owed)
                : $fc(data.monthly_owed)
            }}</p>
          </template>
        </Column>
        <Column field="total_rental_price" header="Total Contract">
          <template #body="{ data }">
            <p>{{
              quote.is_single == false
                ? $fc(2 * data.total_rental_price)
                : $fc(data.total_rental_price)
            }}</p>
          </template>
        </Column>
      </DataTable>

      <DataTable
        v-if="quote.type === 'RENT'"
        :value="[quote]"
        class="p-datatable-sm"
      >
        <Column field="monthly_owed" header="Monthly Rate">
          <template #body="{ data }">
            <p>{{ $fc(data.monthly_price) }}</p>
          </template>
        </Column>
        <Column
          v-if="account_is_usac"
          field="shipping_revenue"
          header="Delivery/Pick Up"
        >
          <template #body="{ data }">
            <p>{{ $fc(data.shipping_revenue) }}</p>
          </template>
        </Column>
      </DataTable>
      <div
        v-if="openButtonMenu"
        class="flex items-center justify-between px-0 border-b border"
      ></div>
      <div v-if="openButtonMenu" class="flex items-center mt-2 flex-cols">
        <div
          v-if="quote.type === 'PURCHASE' || quote.type === 'RENT'"
          class="grid items-center w-full grid-cols-12 gap-4 formgrid"
        >
          <Button
            class="col-span-4 p-button-outlined p-button-rounded p-button-xs"
            icon="pi pi-minus"
            @click="removeFromCart()"
          ></Button>
          <Select
            class="col-span-8 mr-2 p-inputtext-sm"
            v-model="orderQuantity"
            :options="
              Array.from({ length: 30 }, (_, i) => ({
                label: `${i + 1}`,
                value: i + 1
              }))
            "
            optionLabel="label"
            optionValue="value"
            placeholder="Qty"
          />
        </div>

        <Button
          class="mt-2 p-button-outlined p-button-rounded p-button-xs md:col-span-4"
          :label="`Add (${orderQuantity}) To Cart`"
          size="small"
          @click="addToCart(null, orderQuantity)"
          icon="pi pi-shopping-cart"
        ></Button>
        <div v-if="quote.type === 'RENT_TO_OWN'" class="flex items-center">
          <Button
            class="p-button-outlined p-button-rounded p-button-xs"
            label="12"
            @click="addToCart(12)"
          ></Button>
          <div class="px-2"></div>
          <Button
            class="p-button-outlined p-button-rounded p-button-xs"
            label="24"
            @click="addToCart(24)"
          ></Button>
          <div class="px-2"></div>
          <Button
            class="p-button-outlined p-button-rounded p-button-xs"
            label="36"
            @click="addToCart(36)"
          ></Button>
          <div class="px-2"></div>
          <Button
            class="p-button-outlined p-button-rounded p-button-xs"
            label="48"
            @click="addToCart(48)"
          ></Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {
    inject,
    ref,
    computed,
    onMounted,
    onBeforeMount,
    reactive
  } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import CartService from "@/service/Cart"
  import { accountMap } from "@/utils/accountMap"
  import { useUsers } from "@/store/modules/users"
  import { changeCountry } from "@/utils/formatCurrency.js"
  import { useContainerPrices } from "@/store/modules/pricing"
  import CustomerApi from "@/api/customers"

  const pricingStore = useContainerPrices()

  const usersStore = useUsers()

  const toast = useToast()
  const cartService = new CartService()

  const $fc = inject("$formatCurrency")
  const customerOrderStore = useCustomerOrder()
  const customerApi = new CustomerApi()

  const state = reactive({
    can_pay_on_delivery_order: false
  })

  const $isPublic = inject("$isPublic")
  const orderQuantity = ref(1)
  const {
    quote,
    openButtonMenu,
    payOnDeliveryContract,
    line_items,
    duplicationMode
  } = defineProps({
    quote: {
      type: Object,
      default: () => ({})
    },
    openButtonMenu: {
      type: Boolean,
      default: () => false
    },
    payOnDeliveryContract: {
      type: Object,
      default: () => ({})
    },
    line_items: {
      type: Array,
      default: []
    },
    duplicationMode: {
      type: Boolean,
      default: true
    }
  })

  const metrics = computed(() => {
    let account_country = usersStore.cms.account_country
    if (account_country == "Canada") {
      return "km"
    } else {
      return "miles"
    }
  })

  onBeforeMount(async () => {
    let account_country = usersStore.cms.account_country
    await can_pay_on_delivery()
    changeCountry(account_country)
  })

  const quoteTitle = () => {
    if (quote.type == "RENT") {
      return quote.container_size + " ft"
    }
    return quote.title
  }
  const can_pay_on_delivery = async () => {
    if (quote?.type != "PURCHASE" || $isPublic) {
      state.can_pay_on_delivery_order = false
      return
    }
    if (payOnDeliveryContract && payOnDeliveryContract?.is_enabled) {
      if (payOnDeliveryContract.max_allowed_miles >= (quote.distance || 0)) {
        let requestData = {
          product_name: quote.title,
          location_name: quote.location_name
        }
        const { data } = await customerApi.is_pay_on_delivery(requestData)
        state.can_pay_on_delivery_order =
          state.can_pay_on_delivery_order || data.value
      }
    } else {
      state.can_pay_on_delivery_order = false
    }
  }

  const addToCart = (rentPeriod = null, quantity = 1) => {
    let currentLen =
      customerOrderStore.cart.containers.length +
      customerOrderStore.cart.accessories.length
    for (let i = 0; i < quantity; i++) {
      if (quote.is_single == false) {
        updateCart(rentPeriod, true)
      } else {
        updateCart(rentPeriod)
      }
    }
    if (
      currentLen <
      customerOrderStore.cart.containers.length +
        customerOrderStore.cart.accessories.length
    ) {
      toast.add({
        severity: "success",
        summary: "Added to Cart",
        detail: `${quantity} ${quoteTitle()} (s) has been added to your cart`,
        group: "br",
        life: "5000"
      })
      if (customerOrderStore?.publicCms?.has_analytics) {
        gtag("event", "quote_in_cart", {
          zipcode: quote.zip,
          size: quote.title,
          logistics:
            Number(cartService.shipping_revenue) === 0 ? "pickup" : "delivery",
          ordertype: quote.type
        })
      }
    }
    orderQuantity.value = 1
  }

  const updateCart = (rentPeriod = null, two_20s = false) => {
    if (rentPeriod) {
      const selectedRentPeriod = quote.rent_to_own.find(
        (rto) => rto.rent_period === rentPeriod
      )
      const rtoQuote = Object.assign({}, quote, {
        rent_to_own: selectedRentPeriod
      })
      const quoteWithId = Object.assign({}, rtoQuote, {
        id: cartService.generateId(rtoQuote),
        quantity: 1
      })
      customerOrderStore.addToConatainerCart(quoteWithId)

      if (two_20s) {
        const quoteWithIdSecondItem = Object.assign({}, rtoQuote, {
          id: cartService.generateId(rtoQuote),
          quantity: 1
        })
        quoteWithIdSecondItem.shipping_revenue =
          usersStore?.cms?.ship_two_twenties_added_fee == undefined
            ? 100
            : usersStore?.cms?.ship_two_twenties_added_fee
        customerOrderStore.addToConatainerCart(quoteWithIdSecondItem)
      }
    } else {
      if (!two_20s) {
        addQuoteToCart(false, false)
      } else {
        //first 20'
        addQuoteToCart(true, false)

        //second 20'
        addQuoteToCart(true, true)
      }
    }
  }

  const addQuoteToCart = (divided_by_2 = false, shipping_zero = false) => {
    const quoteWithId = Object.assign({}, quote, {
      id: cartService.generateId(quote),
      quantity: 1
    })
    if (quoteWithId.province != null && quoteWithId.province != "") {
      quoteWithId.state = quoteWithId.province
    }
    if (divided_by_2) {
      quoteWithId.price = quoteWithId.price / 2
      quoteWithId.tax = quoteWithId.tax / 2
    }
    if (shipping_zero) {
      quoteWithId.shipping_revenue =
        usersStore?.cms?.ship_two_twenties_added_fee == undefined
          ? 100
          : usersStore?.cms?.ship_two_twenties_added_fee
    } else if (divided_by_2) {
      quoteWithId.shipping_revenue =
        quoteWithId.shipping_revenue -
        (usersStore?.cms?.ship_two_twenties_added_fee == undefined
          ? 100
          : usersStore?.cms?.ship_two_twenties_added_fee)
    }
    customerOrderStore.addToConatainerCart(quoteWithId)
  }

  const removeFromCart = () => {
    let currentLen =
      customerOrderStore.cart.containers.length +
      customerOrderStore.cart.accessories.length
    customerOrderStore.removeFromContainerCart(quote)
    if (
      currentLen >
      customerOrderStore.cart.containers.length +
        customerOrderStore.cart.accessories.length
    ) {
      toast.add({
        severity: "error",
        summary: "Removed from Cart",
        detail: `${quoteTitle()} has been removed from your cart`,
        group: "br",
        life: "5000"
      })
    }
    orderQuantity.value = 1
  }

  const account_is_usac = computed(() => {
    return accountMap[window.location.host].account_id == 1
  })
</script>
