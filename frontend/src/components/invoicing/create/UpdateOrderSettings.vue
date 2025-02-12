<template>
  <div class="flex flex-wrap justify-center">
    <div
      class="flex flex-wrap justify-center w-full mb-4"
      :class="
        showShippingContainerToggle &&
        customerOrderStore?.customer?.order?.type !== 'RENT' &&
        usersStore.cms?.quote_options?.invoice_as_title_option
          ? 'grid-cols-2'
          : 'grid-cols-1'
      "
    >
      <div
        class="m-4"
        v-if="
          showShippingContainerToggle &&
          customerOrderStore?.customer?.order?.type !== 'RENT'
        "
      >
        <ToggleButton
          v-model="state.attributes.show_subtotal_only"
          onLabel="Container & Shipping Combined"
          offLabel="Container & Shipping Separated"
          class="flex items-center flex-cols"
        />
      </div>
      <div
        class="m-4"
        v-if="usersStore.cms?.quote_options?.invoice_as_title_option"
      >
        <ToggleButton
          v-model="state.attributes.is_quote_title"
          onLabel="Quote is title"
          offLabel="Invoice is title"
        />
      </div>
    </div>
    <div class="flex flex-wrap justify-center w-full mb-4">
      <div v-if="props.showOrderStatus" class="m-4">
        <label for="state" class="ml-1 font-medium text-900 dark:text-0"
          >Create as</label
        >
        <Select
          v-model="state.status"
          :options="statusOptions"
          placeholder="Select Status"
          optionLabel="label"
          class="p-component p-inputtext-fluid"
          optionValue="value"
        />
      </div>
      <div
        class="m-4"
        v-if="customerOrderStore?.customer?.order?.type === 'RENT'"
      >
        <label for="state" class="m-1 font-medium text-900 dark:text-0"
          >First payment strategy</label
        >
        <Select
          :disabled="!$ability.can('update', 'first_payment_strategy')"
          v-model="state.first_payment_strategy"
          :options="state.first_payment_strategies"
          placeholder="Select downpayment strategy"
          optionLabel="label"
          class="p-component p-inputtext-fluid"
          optionValue="value"
        />
      </div>
    </div>
    <div
      class="flex flex-wrap justify-center w-full mb-4"
      v-if="customerOrderStore?.customer?.order?.type === 'RENT'"
    >
      <div>
        <label for="state" class="ml-1 font-medium text-900 dark:text-0"
          >Note</label
        >
        <Textarea
          v-model="state.down_payment_strategy_note_content"
          :autoResize="true"
          rows="2"
          cols="38"
          class="p-inputtext-fluid"
        />
      </div>
    </div>
    <hr />
  </div>
</template>

<script setup>
  import { reactive, onMounted, watch, inject, computed } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"

  const usersStore = useUsers()
  const customerOrderStore = useCustomerOrder()

  const statusOptions = computed(() => {
    if (!props.showOrderStatus) {
      return []
    }
    let statusOptionsList = []
    if (customerOrderStore?.customer?.order?.type === "RENT") {
      if (!usersStore.cms?.order_status_selection?.salesStatusOptions) {
        statusOptionsList =
          usersStore.cms?.order_status_options?.salesStatusOptions
      } else {
        statusOptionsList =
          usersStore.cms?.order_status_selection?.order_status_selection
      }
    } else if (customerOrderStore?.customer?.order?.type === "RENT_TO_OWN") {
      if (!usersStore.cms?.order_status_selection?.rentToOwnStatusOptions) {
        statusOptionsList =
          usersStore.cms?.order_status_options?.rentToOwnStatusOptions
      } else {
        statusOptionsList =
          usersStore.cms?.order_status_selection?.rentToOwnStatusOptions
      }
    } else if (
      customerOrderStore?.customer?.order?.type === "PURCHASE" ||
      customerOrderStore?.customer?.order?.type === "PURCHASE_ACCESSORY"
    ) {
      if (!usersStore.cms?.order_status_selection?.salesStatusOptions) {
        statusOptionsList =
          usersStore.cms?.order_status_options?.salesStatusOptions
      } else {
        statusOptionsList =
          usersStore.cms?.order_status_selection?.salesStatusOptions
      }
    }

    const excludeOrderStatusList = [
      "Paid",
      "Cancelled",
      "Expired",
      "Completed",
      "Delivered",
      "Partially Paid",
      "Delayed",
      "Purchase Order"
    ]

    if (statusOptionsList == undefined) {
      statusOptionsList = []
    }

    return statusOptionsList.filter((status) => {
      return !excludeOrderStatusList.includes(status.value)
    })
  })

  const $isObjectPopulated = inject("$isObjectPopulated")
  const $ability = inject("$ability")

  const state = reactive({
    attributes: {},
    status: "",
    first_payment_strategies: [
      {
        label: "First month",
        value: "FIRST_MONTH"
      },
      {
        label: "First month plus delivery",
        value: "FIRST_MONTH_PLUS_DELIVERY"
      },
      {
        label: "First month plus delivery & pickup",
        value: "FIRST_MONTH_PLUS_DELIVERY_&_PICKUP"
      }
    ],
    first_payment_strategy: "",
    down_payment_strategy_note_content: ""
  })

  const emit = defineEmits(["updatedAttributes"])

  const props = defineProps({
    attributes: {
      type: Object
    },
    showOrderStatus: {
      type: Boolean,
      default: false
    },
    showShippingContainerToggle: {
      type: Boolean,
      default: true
    }
  })

  onMounted(async () => {
    if ($isObjectPopulated(props.attributes)) {
      state.attributes = cloneDeep(props.attributes)
    }

    const down_payment_strategy =
      usersStore.cms?.rent_options.down_payment_strategy
    state.first_payment_strategy = down_payment_strategy
  })

  watch(
    () => statusOptions.value,
    (newValue) => {
      if (state.status === "" && props.showOrderStatus) {
        state.status = newValue[0]?.value
      }
    },
    { deep: true, immediate: true }
  )

  watch(
    () => state.down_payment_strategy_note_content,
    (newValue) => {
      emit("savePaymentStrategyNote", state.down_payment_strategy_note_content)
    }
  )

  watch(
    () => state.status,
    (newValue) => {
      if (state.status !== undefined) {
        customerOrderStore.setCustomer({
          ...cloneDeep(customerOrderStore.customer || {}),
          order: {
            ...cloneDeep(customerOrderStore.customer?.order || {}),
            status: newValue
          }
        })
      }
    },
    { deep: true, immediate: true }
  )

  watch(
    () => state.attributes,
    (newValue) => {
      emit("updatedAttributes", newValue)
    },
    { deep: true }
  )

  watch(
    () => state.first_payment_strategy,
    (newValue) => {
      emit("updateFirstPaymentStrategy", newValue)
    },
    { deep: true }
  )
</script>
