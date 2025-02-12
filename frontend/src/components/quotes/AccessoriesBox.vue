<template>
  <div
    class="col-span-12 p-4 xs:col-10 md:col-span-6 xl:col-span-4"
    :class="$isPublic ? '' : 'md:col-6 xl:col-3'"
  >
    <div
      class="p-4 shadow bg-0 dark:bg-900 rounded-border"
      style="border-radius: 6px"
    >
      <div class="flex items-start justify-between">
        <div class="grid grid-cols-12 gap-4">
          <div
            class="col-span-12 mb-2 text-xl font-medium md:col-span-11 xl:col-span-11 text-900 dark:text-0"
          >
            {{ quote.title }}
          </div>
          <div class="grid grid-cols-12 col-span-12 gap-2">
            <div class="grid grid-cols-6 col-span-8 mr-2">
              <div class="col-span-6">
                <Button
                  as="a"
                  class="mt-2 p-button-rounded p-button-xs md:col-span-4"
                  :href="quote.link"
                  target="_blank"
                  style="color: white"
                  >Product Page</Button
                >
                <div class="grid grid-cols-12 col-span-6 px-0 py-2 mt-5">
                  <span
                    class="col-span-6 font-medium text-left text-600 dark:text-200 text-md"
                    >Price</span
                  >
                  <strong class="col-span-6 text-right dark:text-0 text-md">{{
                    $fc(quote.price)
                  }}</strong>
                </div>
              </div>
            </div>
            <div class="col-span-4">
              <img
                v-if="state.quoteImage != null"
                :src="state.quoteImage"
                style="max-width: 120px"
              />
            </div>
          </div>
          <!-- <div class="col-span-12 mt-2 md:col-span-11 xl:col-span-11">
            <p class="text-l">
              (
              {{ category.name }}
              )
            </p>
          </div> -->
        </div>
      </div>
      <div
        v-if="openButtonMenu"
        class="flex items-center justify-between px-0 border border-b"
      ></div>
      <div v-if="openButtonMenu" class="flex items-center mt-2 flex-cols">
        <div
          v-if="
            quote.type === 'PURCHASE' ||
            quote.type === 'PURCHASE_ACCESSORY' ||
            quote.type === 'RENT'
          "
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
          class="w-full mt-2 p-button-outlined p-button-rounded p-button-xs md:col-span-4"
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
  import { defineProps, inject, ref, onMounted, reactive } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import CartService from "@/service/Cart"
  import UploadApi from "@/api/upload.js" // Import the UploadApi class

  const uploadApi = new UploadApi()

  const toast = useToast()
  const cartService = new CartService()

  const $fc = inject("$formatCurrency")
  const customerOrderStore = useCustomerOrder()

  const $isPublic = inject("$isPublic")
  const orderQuantity = ref(1)

  const state = reactive({
    quoteImage: null
  })

  const { quote, openButtonMenu, category } = defineProps({
    quote: {
      type: Object,
      default: () => ({})
    },
    category: {
      type: Object,
      default: () => ({})
    },
    openButtonMenu: {
      type: Boolean,
      default: () => false
    }
  })
  const addToCart = (rentPeriod = null, quantity = 1) => {
    let currentLen =
      customerOrderStore.cart.containers.length +
      customerOrderStore.cart.accessories.length
    for (let i = 0; i < quantity; i++) {
      updateCart(rentPeriod)
    }
    if (
      currentLen <
      customerOrderStore.cart.containers.length +
        customerOrderStore.cart.accessories.length
    ) {
      toast.add({
        severity: "success",
        summary: "Added to Cart",
        detail: `${quantity} ${quote.title}(s) has been added to your cart`,
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

  const updateCart = (rentPeriod = null) => {
    if (rentPeriod) {
    } else {
      const quoteWithId = Object.assign({}, quote, {
        id: quote.id,
        quantity: 1,
        subTotal: quote.price
      })
      customerOrderStore.addToAccessoriesCart(quoteWithId)
    }
  }
  const loadAccessoryImage = async () => {
    if (quote.file_upload.length > 0) {
      const { data } = await uploadApi.getPresignedGetUrl(
        quote.file_upload[0].filename,
        quote.file_upload[0].folder_type,
        quote.account_id,
        null,
        quote.id
      )
      state.quoteImage = data.value
    }
  }
  onMounted(async () => {
    await loadAccessoryImage()
  })

  const removeFromCart = () => {
    let currentLen =
      customerOrderStore.cart.containers.length +
      customerOrderStore.cart.accessories.length
    customerOrderStore.removeFromAccessoriesCart(quote)
    if (
      currentLen >
      customerOrderStore.cart.containers.length +
        customerOrderStore.cart.accessories.length
    ) {
      toast.add({
        severity: "error",
        summary: "Removed from Cart",
        detail: `${quote.name} has been removed from your cart`,
        group: "br",
        life: "5000"
      })
    }
    orderQuantity.value = 1
  }
</script>
