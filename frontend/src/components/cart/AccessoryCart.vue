<template>
  <section class="flex flex-col w-full">
    <DataTable
      v-if="!props.verticalTable"
      :value="cart"
      responsiveLayout="scroll"
    >
      <Column
        :key="i"
        v-for="(c, i) in filteredCols"
        :field="c.field"
        :header="c.label"
      >
        <template #body="{ data, field }">
          <p
            v-if="c.field == 'title'"
            class="flex flex-wrap items-center text-xl text-900"
            style="max-width: 80vw !important; overflow-wrap: break-word"
          >
            <a class="mr-5" target="_blank" :href="data['product_link']">{{
              data[c.field]
            }}</a>
          </p>
          <p
            v-else-if="c.field == 'image_link' && data['image_link']"
            class="flex flex-wrap items-center text-xl text-900"
            style="max-width: 80vw !important; overflow-wrap: break-word"
          >
            <img
              :src="data['image_link']"
              @click="loadAccessoryImage(data['image_link'])"
              class="m-5"
              style="max-width: 100px"
            />
          </p>
          <Button
            v-else-if="c.field == 'product_link'"
            as="a"
            class="ml-5 p-button-sm p-button-rounded"
            style="color: white"
            :href="data['product_link']"
            target="_blank"
            >View Details</Button
          >
          <p v-else>{{ data[c.field] }}</p>
        </template>
      </Column>
    </DataTable>
    <div v-if="props.verticalTable" :key="i" v-for="(cartItem, i) in cart">
      <Divider class="mb-4" />
      <div class="mt-2"></div>
      <table class="flex flex-wrap justify-center ml-12">
        <template :key="colIdx" v-for="(col, colIdx) in filteredCols">
          <div class="mt-2"></div>
          <tr v-if="col.label == 'Accessory'" style="width: 100%">
            <td class="text-xl">
              <div
                class="text-lg font-bold text-700 dark:text-100"
                v-if="col.label != 'Accessory'"
                style="overflow-wrap: break-word"
              >
                {{ colIdx === 0 ? `${col.label}` : col.label }}
              </div>
              <p
                v-if="col.label == 'Accessory'"
                class="flex flex-wrap items-center text-xl text-900"
                style="overflow-wrap: break-word"
              >
                <a
                  target="_blank"
                  :href="cartItem['product_link']"
                  class="mr-5"
                  >{{ cartItem[col.field] }}</a
                >
              </p>
            </td>
          </tr>
          <tr
            v-else-if="col.field == 'image_link' && cartItem['image_link']"
            style="width: 100%"
          >
            <td class="text-xl">
              <img
                :src="cartItem['image_link']"
                @click="loadAccessoryImage(cartItem['image_link'])"
                class="m-5"
                style="max-width: 100px"
              />
            </td>
          </tr>
          <tr v-else-if="col.field == 'product_link'" style="width: 100%">
            <td class="text-xl">
              <Button
                as="a"
                class="ml-5 p-button-sm p-button-rounded"
                style="color: white"
                :href="cartItem['product_link']"
                target="_blank"
                >View Details</Button
              >
            </td>
          </tr>

          <tr v-else style="width: 100%">
            <td class="text-xl">
              <div
                class="text-lg font-bold text-700 dark:text-100"
                style="overflow-wrap: break-word"
              >
                {{ colIdx === 0 ? `${col.label}` : col.label }}
              </div>
            </td>
            <td>
              <p
                class="text-xl text-right text-900 dark:text-0"
                style="overflow-wrap: break-word"
              >
                {{ cartItem[col.field] }}
              </p>
            </td>
          </tr>
          <hr />
        </template>
      </table>
    </div>

    <Dialog
      v-model:visible="state.loadAccessoryImage"
      modal
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
    >
      <template #header>
        <div class="flex items-stretch">
          <div class="flex">
            <p class="text-3xl">Accessory Image</p>
          </div>
        </div>
      </template>
      <template #default>
        <div
          style="overflow: none !important"
          class="flex items-center p-6 card flex-cols"
        >
          <img
            style="max-width: 100%; max-height: 100%; margin: auto"
            :src="state.accessoryImage"
          />
        </div>
      </template>
    </Dialog>
  </section>
</template>

<script setup>
  import { reactive, inject, computed, watch, onMounted } from "vue"
  import CartService from "@/service/Cart"
  import { useUsers } from "@/store/modules/users"
  import cloneDeep from "lodash.clonedeep"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useInvoiceHelper } from "@/store/modules/invoiceHelper"
  import UploadApi from "@/api/upload.js" // Import the UploadApi class

  const uploadApi = new UploadApi()
  const $isPublic = inject("$isPublic")

  const invoiceHelperStore = useInvoiceHelper()
  const customerStore = useCustomerOrder()

  const cartService = new CartService()
  const $fc = inject("$formatCurrency")
  const userStore = useUsers()

  const props = defineProps({
    customerOrderProp: {
      type: Object,
      default: () => ({})
    },
    cart: {
      type: Object,
      default: () => ({})
    },
    showConvenienceFee: {
      type: Boolean,
      default: false
    },
    showTax: {
      type: Boolean,
      default: false
    },
    showContainerPlusShipping: {
      type: Boolean,
      default: false
    },
    verticalTable: {
      type: Boolean,
      default: false
    },
    isAccessory: {
      type: Boolean,
      default: false
    },
    accountId: {
      type: Number,
      default: 1
    },
    appliedCoupons: {
      type: Array,
      default: []
    },
    inCreateInvoiceWizard: {
      type: Boolean,
      default: false
    },
    stateCart: {
      type: Object,
      default: {}
    },
    isPaymentPage: {
      type: Boolean,
      default: false
    }
  })

  const state = reactive({
    loadAccessoryImage: false,
    accessoryImage: "",
    accessoryImages: [],
    cart_price_overwrite: {},
    shipping_overwrite: {}
  })
  const itemTitle = (title, abrev) => {
    if (props.inCreateInvoiceWizard) {
      return title
    } else {
      return abrev
    }
  }

  const loadAccessoryImage = (imageUrl) => {
    state.loadAccessoryImage = true
    state.accessoryImage = imageUrl
    return
  }

  const isPickup = computed(() => {
    return (
      props.cart.every((i) => Number(i.shipping_revenue) === 0) ||
      props.customerOrderProp?.is_pickup
    )
  })

  const account_id = computed(() => {
    if ($isPublic) return customerStore.publicCms?.account_id
    return userStore?.cms?.account_id
  })

  const filteredCols = computed(() => {
    let cart

    cart = cartService.cartColumnsPurchase

    if (isPickup.value) {
      cart = cartService.cartColumnsPickup
    }

    cart = cart.filter((obj) => obj["field"] !== "title")

    if (props.cart.some((i) => i.product_type == "CONTAINER_ACCESSORY"))
      cart = cartService.cartColumnsAccessories
    if (props.isAccessory) cart = cartService.cartOrderColumnsAccessories

    if (cart.some((i) => i.field === "abrev_title") && !props.verticalTable) {
      // delete each instance of the field
      cart = cart.filter((i) => i.field !== "abrev_title")
    }

    if (userStore?.cms?.show_container_number_on_invoice) {
      cart.splice(0, 0, {
        label: "Container number",
        field: "container_number"
      })
    }

    return cart
      .filter((c) => {
        if (c.field === "convenience_fee") {
          return props.showConvenienceFee
        }
        return true
      })
      .filter((c) => {
        if (props.showContainerPlusShipping) {
          return c.field !== "revenue" && c.field !== "shipping_revenue"
        } else {
          return c.field !== "subTotal"
        }
      })
      .filter((c) => {
        if (c.field === "tax") {
          return props.showTax
        }
        return true
      })
  })

  const cart = computed(() => {
    const cart = cloneDeep(props.cart)

    for (var i = 0; i < cart.length; i++) {
      cart[i].attributes = {}
      const numericRevenue = parseFloat(
        cart[i].revenue != 0
          ? cart[i].revenue.replace(/[^0-9.-]+/g, "")
          : cart[i].revenue
      )

      cart[i].revenue = $fc(numericRevenue)
      cart[i].image_link =
        state.accessoryImages.filter(
          (e) => e.id == cart[i].file_upload?.other_product_id
        )[0]?.image_link || null
      const total =
        cart[i].subTotal == 0
          ? 0
          : parseFloat(
              cart[i].revenue != 0
                ? cart[i].subTotal.replace(/[^0-9.-]+/g, "")
                : cart[i].revenue
            )
      cart[i].subTotal = $fc(total)

      if (
        state.cart_price_overwrite[cart[i].id] ||
        state.shipping_overwrite[cart[i].id]
      ) {
        let price = state.cart_price_overwrite[cart[i].id]

        if (cart[i].product_type == "SHIPPING_CONTAINER") {
          cart[i].revenue = $fc(price * cart[i].quantity)
        } else {
          cart[i].price = $fc(state.cart_price_overwrite[cart[i].id])
        }

        if (state.shipping_overwrite[cart[i].id]) {
          let shipping = state.shipping_overwrite[cart[i].id]
          cart[i].shipping_revenue = $fc(shipping)
          cart[i].shipping_revenue_calculated = $fc(shipping)
        }

        cart[i].subTotal = $fc(
          price * cart[i].quantity +
            cart[i].quantity *
              parseFloat(
                cart[i].shipping_revenue == 0
                  ? 0
                  : cart[i].shipping_revenue.replace(/[^0-9.-]+/g, "")
              )
        )
        console.log(cart[i].subTotal)
      }

      if (cart[i].abrev_title == undefined) {
        cart[i].abrev_title = cartService.abrevTitle(cart[i])
      }
    }
    return cart
  })

  watch(
    () => invoiceHelperStore.cart,
    (newVal) => {
      let count = {}
      for (var i = 0; i < props.cart.length; i++) {
        count[props.cart[i].title] = 0
        state.cart_price_overwrite[props.cart[i].title] = 0
        state.shipping_overwrite[props.cart[i].title] = 0
      }

      newVal.forEach((element) => {
        for (var i = 0; i < props.cart.length; i++) {
          if (element.title == props.cart[i].title) {
            state.cart_price_overwrite[element.title] += element.revenue
            state.shipping_overwrite[element.title] += element.shipping_revenue
            count[props.cart[i].title] += 1
          }
        }
      })
      for (let key in state.cart_price_overwrite) {
        state.cart_price_overwrite[key] =
          state.cart_price_overwrite[key] / count[key]
      }
    },
    { deep: true, immediate: true }
  )
  onMounted(async () => {
    const promises = []
    for (var i = 0; i < props.cart?.length; i++) {
      promises.push(generateAccessoryImageUrl(props.cart[i]))
    }
    await Promise.allSettled(promises)
  })

  const generateAccessoryImageUrl = async (cart) => {
    if (Object.keys(cart.file_upload).length > 0) {
      console.log(cart.file_upload)
      const { data } = await uploadApi.getPresignedGetUrl(
        cart.file_upload.filename,
        cart.file_upload.folder_type,
        cart.file_upload.account_id,
        null,
        cart.file_upload.other_product_id
      )
      // return data.value
      state.accessoryImages.push({
        id: cart.file_upload.other_product_id,
        image_link: data.value
      })
    } else {
      state.accessoryImages.push({
        id: cart.file_upload.other_product_id,
        image_link: null
      })
    }
  }
</script>

<style scoped>
  .p-datepicker-current-day {
    background-color: blue !important;
  }
</style>
