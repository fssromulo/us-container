<template>
  <div class="pb-4 text-xl border border-b text-900 dark:text-0">
    Your Cart
  </div>
  <ul
    class="p-0 m-0 list-none"
    v-for="(cartTypes, index) in customerOrderStore.cart.cartTypes"
    :key="index"
  >
    <li
      :key="i"
      v-for="(c, i) in cartService.reducedCart(
        cloneDeep(customerOrderStore.cart[cartTypes.property])
      )"
      class="flex items-center py-4"
    >
      <div class="pl-4 mr-20">
        <span class="font-medium text-900 dark:text-0"
          >{{
            cartTypes.name == "Accessory" ? c.title : c.container_size + " ft"
          }}
          ({{ c.quantity }})</span
        >
        <div class="mt-2 text-600 dark:text-200">{{ cartTypes.name }}</div>
      </div>
      <div
        v-if="c.monthly_owed !== undefined"
        class="ml-auto font-medium text-900 dark:text-0"
      >
        {{ $fc(c.monthly_owed) }}
      </div>
      <div
        v-else-if="c.monthly_price !== undefined && props.isRental == true"
        class="ml-auto font-medium text-900 dark:text-0"
      >
        {{ $fc(c.monthly_price) }}
      </div>
      <div v-else class="ml-auto font-medium text-900 dark:text-0">
        {{ $fc(c.price * c.quantity) }}
      </div>
      <!-- <div class="ml-auto text-900 dark:text-0 font-med/ium">{{ c.sale_price }}</div> -->
    </li>
  </ul>
  <ul class="p-0 m-0 list-none">
    <li class="flex items-center py-4 p-fluid">
      <Button
        class="ml-2"
        label="View Cart"
        @click="startQuote"
        v-styleclass="{
          selector: '#popover-cart',
          leaveToClass: 'hidden',
          leaveActiveClass: 'animate-fadeout'
        }"
      ></Button>
    </li>
  </ul>
</template>

<script setup>
  import cloneDeep from "lodash.clonedeep"
  import { inject } from "vue"

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import CartService from "@/service/Cart"
  const $fc = inject("$formatCurrency")

  const customerOrderStore = useCustomerOrder()
  const cartService = new CartService()

  const startQuote = () => {
    customerOrderStore.setCreateOrderStatus("IN_PROGRESS")
  }

  const removeConditionIfRental = (title) => {
    if (props.isRental) {
      return title.replace("Used", "").replace("One-Trip", "")
    } else {
      return title
    }
  }

  const props = defineProps({
    isRental: {
      type: Boolean,
      default: false
    }
  })
</script>
