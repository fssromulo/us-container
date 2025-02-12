<template>
  <section class="flex flex-col w-full">
    <DataTable
      v-if="!props.verticalTable"
      :value="state.cart"
      responsiveLayout="scroll"
    >
      <Column
        v-if="!props.isAccessory"
        :field="abrev_title"
        header="Shipping Container"
        style="width: 260px"
      >
        <template #body="slotProps">
          <p class="cursor-pointer text-black-600">
            <!--@click="
              loadContainerImage(
                slotProps.data.attributes,
                slotProps.data.container_size
              )
            "-->
            {{
              itemTitle(
                slotProps.data?.title,
                props.showAbbrevTitleWContainerNumber
                  ? slotProps.data?.abbrev_title_w_container_number
                  : slotProps.data?.abrev_title,
                slotProps.data?.calculated_rental_name
              )
            }}
          </p>
        </template>
      </Column>

      <Column
        :key="i"
        v-for="(c, i) in filteredCols"
        :field="c.field"
        :header="c.label"
      ></Column>
    </DataTable>
    <div
      v-if="props.verticalTable"
      :key="i"
      v-for="(cartItem, i) in state.cart"
    >
      <Divider class="mb-4" />
      <div class="mt-2"></div>
      <table class="flex flex-wrap justify-center ml-12 text-left">
        <template :key="colIdx" v-for="(col, colIdx) in filteredCols">
          <div class="mt-2"></div>
          <tr
            v-if="
              (col.label == 'Shipping Container' || col.label == 'Container') &&
              !props.isAccessory
            "
            style="width: 100%"
          >
            <td class="text-xl">
              <div class="text-lg font-bold text-700 dark:text-100">
                {{ colIdx === 0 ? `${col.label}` : col.label }}
              </div>
              <p
                class="text-blue-600 underline cursor-pointer text-900 dark:text-0 hover:text-blue-800"
                @click="
                  loadContainerImage(
                    cartItem['attributes'],
                    cartItem['container_size']
                  )
                "
              >
                {{ itemTitle(cartItem[col.field], cartItem["abrev_title"]) }}
              </p>
            </td>
          </tr>
          <tr v-else style="width: 100%">
            <td class="text-xl">
              <div class="text-lg font-bold text-700 dark:text-100">
                {{ colIdx === 0 ? `${col.label}` : col.label }}
              </div>
            </td>
            <td>
              <p class="text-xl text-right text-900 dark:text-0">
                {{ cartItem[col.field] }}
              </p>
            </td>
          </tr>
          <hr />
        </template>
      </table>
    </div>

    <Dialog
      v-model:visible="state.loadContainerImage"
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
            <p class="text-3xl">Container Image</p>
          </div>
        </div>
      </template>
      <template #default>
        <div style="overflow: none !important" class="p-6 card">
          <img
            style="max-width: 100%; max-height: 100%; margin: auto"
            :src="state.containerImage"
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
  import { useDownpaymentStrategyStore } from "@/store/modules/downpaymentStrategyHelper"
  import CustomerApi from "@/api/customers"

  const downpaymentStrategyStore = useDownpaymentStrategyStore()

  const customerApi = new CustomerApi()

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
    },
    showAbbrevTitleWContainerNumber: {
      type: Boolean,
      default: false
    }
  })

  const state = reactive({
    loadContainerImage: false,
    containerImage: "",
    cart_price_overwrite: {},
    cart: [],
    pairs: []
  })

  onMounted(async () => {
    const { data } = await customerApi.get_all_container_attributes()
    state.pairs = data.value
    state.cart = await cart()
  })

  const itemTitle = (title, abrev) => {
    if (props.inCreateInvoiceWizard) {
      return title
    } else {
      return abrev
    }
  }
  const isStandardSize = (attributes) => {
    let isStandardSize = false

    if (typeof attributes.high_cube != "undefined") {
      if (attributes.high_cube) {
        isStandardSize = false
      } else {
        isStandardSize =
          typeof attributes.standard != "undefined" && attributes.standard
      }
    } else {
      isStandardSize =
        typeof attributes.standard != "undefined" && attributes.standard
    }
    return isStandardSize
  }

  const loadContainerImage = (attributes, container_size) => {
    let containers = cartService.containerImages.filter(
      (container) => container.container_size == container_size
    )
    let image = ""
    if (containers.length == 1) {
      image = containers[0].image
    } else if (isStandardSize(attributes)) {
      image = containers.filter(
        (container) => container.attributes === "standard"
      )[0].image
    } else if (
      typeof attributes.high_cube != "undefined" &&
      attributes.high_cube
    ) {
      image = containers.filter(
        (container) => container.attributes === "high_cube"
      )[0].image
    }

    state.loadContainerImage = true
    if (attributes.high_cube == true && container_size == "20") {
      state.containerImage = null
      return
    }
    state.containerImage = image
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
  const isRental = computed(() => {
    return props.cart.some((i) => i.type === "RENT")
  })
  const filteredCols = computed(() => {
    let cart

    if (props.cart.some((i) => i.type === "RENT_TO_OWN")) {
      cart = cartService.cartColumnsRTO
    }

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
          return c.field !== "container_plus_shipping"
        }
      })
      .filter((c) => {
        if (c.field === "tax") {
          return props.showTax
        }
        return true
      })
  })

  const cart = async () => {
    const cart = cloneDeep(props.cart)

    for (var i = 0; i < cart.length; i++) {
      cart[i].attributes = {}
      const numericRevenue = parseFloat(
        cart[i].revenue.replace(/[^0-9.-]+/g, "")
      )

      const sum = props.appliedCoupons.reduce((accumulator, currentObject) => {
        return numericRevenue >= currentObject.coupon.minimum_discount_threshold
          ? accumulator + currentObject.coupon.amount
          : accumulator
      }, 0)

      cart[i].revenue = $fc(numericRevenue + cart[i].quantity * sum)
      const total =
        cart[i].subTotal == 0
          ? 0
          : parseFloat(cart[i].subTotal.replace(/[^0-9.-]+/g, ""))
      cart[i].subTotal = $fc(total + cart[i].quantity * sum)

      if (state.cart_price_overwrite[cart[i].id]) {
        if (state.cart_price_overwrite[cart[i].id]) {
          let price = state.cart_price_overwrite[cart[i].id]

          if (cart[i].product_type == "SHIPPING_CONTAINER") {
            cart[i].revenue = $fc(price + cart[i].quantity * sum)
          } else {
            cart[i].price = $fc(state.cart_price_overwrite[cart[i].id])
          }
          cart[i].subTotal = $fc(
            price * cart[i].quantity + cart[i].quantity * sum
          )
        }
      }

      state.pairs.forEach((pair) => {
        if (cart[i].title.includes(pair.name)) {
          cart[i].attributes[pair.value] = true
        }
      })

      cart[i].abrev_title = cart[i].title
    }
    return cart
  }

  watch(
    () => invoiceHelperStore.cart,
    async (newVal) => {
      let count = {}
      for (var i = 0; i < props.cart.length; i++) {
        count[props.cart[i].title] = 0
        state.cart_price_overwrite[props.cart[i].title] = 0
      }

      newVal.forEach((element) => {
        for (var i = 0; i < props.cart.length; i++) {
          if (element.title == props.cart[i].title) {
            state.cart_price_overwrite[element.title] += element.revenue
            count[props.cart[i].title] += 1
          }
        }
      })
      for (let key in state.cart_price_overwrite) {
        state.cart_price_overwrite[key] =
          state.cart_price_overwrite[key] / count[key]
      }

      state.cart = await cart()
    },
    { deep: true, immediate: true }
  )
</script>

<style scoped>
  .p-datepicker-current-day {
    background-color: blue !important;
  }
</style>
