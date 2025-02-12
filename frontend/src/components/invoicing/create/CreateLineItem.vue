<template>
  <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
    <div class="col-span-3 mb-4 field md:col-span-3">
      <label for="due_date" class="font-medium text-900 dark:text-0"
        >Due Date (default 5 days)</label
      >
      <DatePicker
        v-model="state.customerOrder.due_date"
        id="due_date"
        :showIcon="true"
      ></DatePicker>
    </div>
    <div class="col-span-2 mt-6 mt-8 ml-6 field md:col-span-2">
      <Checkbox v-model="state.isTaxable" :binary="true"></Checkbox>
      <span class="ml-2 text-xl text-900 dark:text-0">Taxable</span>
    </div>
    <div class="flex col-span-6 mt-6 mb-4 field md:col-span-6">
      <label
        for="order_type"
        class="mt-4 mr-4 font-medium text-900 dark:text-0"
      >
        Order Type
      </label>
      <SelectButton
        class="w-full sm:w-80"
        v-model="state.selectedCategory"
        :options="state.categorys"
        optionLabel="name"
      />
    </div>
    <div class="col-span-12 mb-4 border-t border"></div>
    <template v-for="(li, i) in state.lineItems" :key="i">
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="container" class="font-medium text-900 dark:text-0"
            >Container</label
          >
          <Select
            icon="pi pi-plus"
            v-model="li.container"
            placeholder="Select container"
            :options="state.sizes"
          />
        </div>
        <div class="col-span-6 mb-4 field md:col-span-1">
          <label for="quantity" class="font-medium text-900 dark:text-0"
            >Quantity</label
          >
          <InputText id="quantity" v-model="li.quantity" type="text" />
        </div>
        <div class="col-span-6 mb-4 field md:col-span-2">
          <label for="price" class="font-medium text-900 dark:text-0">{{
            state.selectedCategory.code !== "purchase"
              ? "Price per Month"
              : "Price"
          }}</label>
          <InputNumber
            mode="currency"
            currency="USD"
            v-model="li.revenue"
            id="price"
            type="text"
            class="flex-1"
          ></InputNumber>
        </div>
        <div class="col-span-6 mb-4 field md:col-span-1">
          <label for="price" class="font-medium text-900 dark:text-0"
            >Shipping</label
          >
          <InputNumber
            mode="currency"
            v-model="li.shipping_revenue"
            currency="USD"
            id="shipping_revenue"
            type="text"
            class="flex-1"
          ></InputNumber>
        </div>
        <div
          v-if="state.isTaxable"
          class="col-span-12 mb-4 field md:col-span-1"
        >
          <!-- <label
        for="price"
        :class="
          state.selectedCategory.code !== 'purchase'
            ? 'font-medium text-900 dark:text-0 text-xs'
            : 'font-medium text-900 dark:text-0'
        "
        >
        {{
          state.selectedCategory.code !== "purchase" ? "Tax per Month" : "Tax"
        }}</label
      >
      <InputNumber
        mode="currency"
        currency="USD"
        v-model="li.tax"
        id="tax"
        type="text"
        class="flex-1"
      ></InputNumber> -->
        </div>
        <div class="col-span-12 mb-4 field md:col-span-1">
          <label
            for="convenience_fee"
            class="text-xs font-medium text-900 dark:text-0"
            >Credit Card Fee</label
          >
          <InputNumber
            mode="currency"
            currency="USD"
            v-model="li.convenience_fee"
            id="tax"
            type="text"
            class="flex-1"
          ></InputNumber>
        </div>

        <div
          v-if="state.isTaxable"
          class="col-span-12 mb-4 field md:col-span-1"
        >
          <label
            for="price"
            :class="
              state.selectedCategory.code !== 'purchase'
                ? 'font-medium text-900 dark:text-0 text-xs'
                : 'font-medium text-900 dark:text-0'
            "
            >{{ rentOrSaleText }}</label
          >
          <p class="text-xl font-heavy text-900 dark:text-0">
            {{ $formatCurrency(li.total) }}
          </p>
        </div>
        <div class="col-span-6 mb-4 field md:col-span-3">
          <label for="price" class="font-medium text-900 dark:text-0"></label>
          <div class="flex content-center">
            <ToggleButton
              v-model="li.door_orientation"
              class="w-full mt-2 sm:w-48"
              onLabel="Facing cab"
              offLabel="Opposite of cab"
            />
            <Button
              v-if="state.customerOrder.line_items.length > 1"
              icon="pi pi-trash"
              @click="removeLineItem(i)"
              class="ml-2 p-button-danger p-button-text"
            ></Button>
          </div>
        </div>
      </div>
    </template>
  </div>

  <div class="flex mb-6 align-content-centet">
    <Button
      icon="pi pi-plus"
      label="Add Container"
      class="w-auto mt-6 mb-6 p-button-help"
      @click="addLineItem()"
    ></Button>
    <span
      class="mt-8 mb-6 ml-6 mr-2 font-medium text-600 dark:text-200"
      :class="
        state.selectedCategory.code !== 'purchase' ? 'text-md' : 'text-xl'
      "
      >{{ rentOrSaleText }}</span
    >
    <span class="mt-8 mb-6 text-xl font-medium text-900 dark:text-0">{{
      calculateOrderTotal()
    }}</span>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, watchEffect } from "vue"
  import StateService from "../../../service/StateService"
  import cloneDeep from "lodash.clonedeep"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import LineItemsService from "@/service/LineItem"

  const customerStore = useCustomerOrder()
  const lineItemService = new LineItemsService()

  const defaultLineItem = {
    container: null,
    quantity: null,
    revenue: null,
    shipping_revenue: null,
    tax: null,
    total: null,
    door_orientation: "Facing cab"
  }

  const $isObjectPopulated = inject("$isObjectPopulated")
  const $formatCurrency = inject("$formatCurrency")
  const $removeUnusedProps = inject("$removeUnusedProps")

  const { stepsEnabled, customerOrderProp } = defineProps({
    stepsEnabled: {
      type: Boolean,
      default: false
    },
    customerOrderProp: {
      type: Object,
      default: () => ({})
    }
  })

  onMounted(() => {
    if ($isObjectPopulated(customerOrderProp)) {
      state.lineItems = cloneDeep(customerOrderProp.line_items)
      state.customerOrder = cloneDeep(customerOrderProp)
    }
  })

  const state = reactive({
    selectedStep: 0,
    lineItems: [],
    containerTypes: ["40Ft HC", "20ft HC", "40ft Std", "20ft Std"],
    sizes: [
      "20 STD",
      "20 HC",
      "40 STD",
      "40 HC",
      "45 HC",
      "20 STD DD",
      "20 HC DD",
      "40 STD DD",
      "40 HC DD",
      "45 HC DD",
      "20' STD Portable",
      "20' HC Portable",
      "40' STD Portable",
      "40' HC Portable",
      "20' DD STD Portable",
      "20' DD HC Portable",
      "40' DD STD Portable",
      "40' DD HC Portable"
    ],
    customerOrder: {},
    isDeliveryAddress: true,
    selectedCategory: {},
    due_date: null,
    selectedCategory: { name: "Sale", code: "purchase" },
    categorys: [
      { name: "Sale", code: "purchase" },
      { name: "Rental", code: "rental" },
      { name: "Rent to Own", code: "rto" }
    ]
  })

  const rentOrSaleText = computed(() => {
    return state.selectedCategory.code !== "purchase"
      ? "Monthly Total"
      : "Total"
  })

  watchEffect(() => {
    state.lineItems.forEach((li) => {
      li.total = li.revenue + li.shipping_revenue // + li.tax
    })
  })

  const addLineItem = () => {
    state.lineItems.push(cloneDeep(defaultLineItem))
  }

  const removeLineItem = (index) => {
    if (state.lineItems.length > 1) {
      state.lineItems.splice(index, 1)
    }
  }

  const calculateOrderTotal = () => {
    if (!state.lineItems) {
      return $formatCurrency(0)
    }
    const total = state.lineItems.reduce((acc, li) => {
      return acc + li.total
    }, 0)
    return $formatCurrency(total ? total : 0)
  }
</script>
