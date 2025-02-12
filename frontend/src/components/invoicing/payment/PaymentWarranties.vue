<template>
  <div class="flex flex-wrap justify-center">
    <ul class="p-0 m-0 list-none">
      <li
        v-if="computedWarranties?.length < 6"
        class="flex items-center mb-4"
        v-for="warranty in computedWarranties"
      >
        <i class="mr-2 text-green-500 pi pi-check-circle"></i>
        <span class="!text-lg !text-500 dark:!text-300">{{ warranty }}</span>
      </li>
      <table
        class="p-datatable-table"
        style="border: none"
        v-if="computedWarranties?.length == 6"
      >
        <tbody class="p-datatable-tbody">
          <tr>
            <td>
              <ul>
                <li
                  class="flex items-center mb-4"
                  v-for="(warranty, index) in firstColumnWarranties"
                  :key="index"
                >
                  <i
                    :style="{ 'font-size': some_as_is ? '0.5rem' : '' }"
                    :class="
                      some_as_is
                        ? 'mr-2 text-black-200 pi pi-circle-fill'
                        : 'mr-2 text-green-500 pi pi-check-circle'
                    "
                  ></i>
                  <div class="!text-lg !text-500 dark:!text-300">{{
                    warranty
                  }}</div>
                </li>
              </ul>
            </td>
            <td>
              <ul>
                <li
                  class="flex items-center mb-4"
                  v-for="(warranty, index) in secondColumnWarranties"
                  :key="index"
                >
                  <i
                    :style="{ 'font-size': some_as_is ? '0.5rem' : '' }"
                    :class="
                      some_as_is
                        ? 'mr-2 text-black-200 pi pi-circle-fill'
                        : 'mr-2 text-green-500 pi pi-check-circle'
                    "
                  ></i>
                  <div class="!text-lg !text-500 dark:!text-300">{{
                    warranty
                  }}</div>
                </li>
              </ul>
            </td>
          </tr>
        </tbody>
      </table>

      <li
        class="flex items-center mb-4"
        v-if="
          currentOrder.purchase_order_number &&
          customerOrderStore?.publicCms?.uses_purchase_order
        "
      >
        <span class="!text-2xl !font-medium !text-500 dark:!text-300"
          >P.O No : {{ currentOrder.purchase_order_number }}</span
        >
      </li>
      <li
        class="flex items-center mb-4"
        v-if="
          currentOrder.purchased_order_job_id &&
          customerOrderStore?.publicCms?.uses_purchase_order
        "
      >
        <span class="!text-2xl !font-medium !text-500 dark:!text-300"
          >Job Id : {{ currentOrder.purchased_order_job_id }}</span
        >
      </li>
    </ul>
  </div>
</template>

<script setup>
  import { computed, onMounted, reactive } from "vue"
  import { useUsers } from "@/store/modules/users"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const customerOrderStore = useCustomerOrder()
  const usersStore = useUsers()

  const { currentOrder, convertOrderToCart } = defineProps({
    currentOrder: {
      type: Object,
      default: {},
      required: true
    },
    convertOrderToCart: {
      type: Object,
      default: {},
      required: true
    }
  })
  const computedWarranties = computed(() => {
    if (currentOrder.type == "RENT") {
      return (
        customerOrderStore?.publicCms?.rental_warranties ||
        usersStore?.cms?.rental_warranties
      )
    }

    if (!some_as_is.value) {
      return (
        customerOrderStore?.publicCms?.payment_warranties ||
        usersStore?.cms?.payment_warranties
      )
    } else {
      return computedASISWarranties.value
    }
  })

  const some_as_is = computed(() => {
    return convertOrderToCart.cart.some((el) => el.attributes["as_is"] == true)
  })

  const computedASISWarranties = computed(() => {
    return customerOrderStore?.publicCms?.payment_as_is_warranties
  })

  const firstColumnWarranties = computed(() => {
    return computedWarranties.value.slice(0, 3)
  })

  const secondColumnWarranties = computed(() => {
    return computedWarranties.value.slice(3, 6)
  })

  onMounted(() => {
    state.payment_warranties = usersStore?.cms?.payment_warranties
  })

  const state = reactive({
    payment_warranties: []
  })
</script>
