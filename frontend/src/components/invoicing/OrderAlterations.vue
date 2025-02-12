<template>
  <div class="grid grid-cols-12 gap-4 mb-6">
    <div class="col-span-12 text-xl text-700 dark:text-100">{{
      props.headingName
    }}</div>
  </div>
  <div class="grid grid-cols-12 gap-4 d-flex">
    <div class="col-span-12">
      <div class="grid grid-cols-12 gap-4 mt-2">
        <label class="col-span-8 mt-4 md:col-span-4"> </label>
        <label class="col-span-8 mt-4 md:col-span-5"> Created At </label>
      </div>
      <div v-for="item in props.itemsProp" class="grid grid-cols-12 gap-4 mt-2">
        <InputNumber
          mode="currency"
          currency="USD"
          v-model="item[props.amountFieldName]"
          id="tax"
          type="text"
          class="col-span-8 mt-4 md:col-span-4"
        />
        <span class="col-span-4 mt-4 md:col-span-2">
          {{ dfc(item.created_at) }}
        </span>
        <Select
          :disabled="!$ability.can('update', 'order_column-status')"
          class="col-span-8 mt-4 md:col-span-5"
          v-model="item[props.categoryFieldName]"
          scrollHeight="330px"
          :options="state.categoryOptionsList"
          optionLabel="label"
          optionValue="value"
          :placeholder="props.placeholderText"
          v-if="checkIfEmptyString(props.categoryFieldName2)"
        />

        <Select
          :disabled="!$ability.can('update', 'order_column-status')"
          class="col-span-8 mt-4 md:col-span-5"
          v-model="item[props.categoryFieldName][props.categoryFieldName2]"
          scrollHeight="330px"
          :options="state.categoryOptionsList"
          optionLabel="label"
          optionValue="value"
          :placeholder="props.placeholderText"
          v-else
        />

        <Button
          type="button"
          icon="pi pi-trash text-md "
          class="w-8 h-8 col-span-2 mb-1 ml-4 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
          @click="
            showConfirmToast(
              () => handleDeleteClickFunc(item.id),
              closeConfirmationToastFunc
            )
          "
        ></Button>
      </div>
      <!-- This is the addition portion of the add misc costs -->
      <div
        v-if="customersStore.addedOrderItems[props.headingName]?.length > 0"
        class="grid grid-cols-12 gap-4 mt-2"
      >
        <div
          v-for="(item, index) in customersStore.addedOrderItems[
            props.headingName
          ]"
          :key="index"
          class="grid grid-cols-12 col-span-12 gap-4 mt-2"
        >
          <InputNumber
            mode="currency"
            currency="USD"
            v-model="item[props.amountFieldName]"
            :id="'tax-' + index"
            type="text"
            class="col-span-8 md:col-span-4"
          />
          <Select
            :disabled="!$ability.can('update', 'order_column-status')"
            class="col-span-8 md:col-span-5"
            v-model="item[props.categoryFieldName]"
            scrollHeight="330px"
            :options="state.categoryOptionsList"
            optionLabel="label"
            optionValue="value"
            :placeholder="props.placeholderText"
          />
          <!-- Add a "Remove" button for each added misc cost -->
          <Button
            type="button"
            icon="pi pi-minus text-md"
            class="w-8 h-8 col-span-2 m-1 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
            @click="handleRemoveItemClick(index)"
          ></Button>
        </div>
      </div>
      <!-- Add a "Add" button to add new misc cost fields -->
      <div>
        <Button
          type="button"
          icon="pi pi-plus text-md"
          class="w-8 h-8 m-1 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
          @click="handleAddItemClick"
        ></Button>
      </div>
      <div v-if="customersStore.addedOrderItems[props.headingName]?.length > 0">
        <!-- Add "Save" and "Cancel" buttons -->
        <div>
          <Button
            type="button"
            :label="props.addButtonText"
            class="m-1 p-button-success"
            @click="handleAddItemSaveClickFunc"
            :loading="props.isLoading"
          ></Button>
          <Button
            type="button"
            label="Cancel"
            class="m-1 p-button-secondary"
            @click="handleCancelItemClick"
          ></Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  const $ability = inject("$ability")
  import { reactive, onMounted, inject, computed } from "vue"
  import CustomerApi from "@/api/customers"
  import { ref, watch } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import cloneDeep from "lodash.clonedeep"
  import { dfc } from "@/service/DateFormat.js"

  const customersStore = useCustomerOrder()
  const customerApi = new CustomerApi()

  const fetchOptions = async () => {
    try {
      // Assuming customerApi.getAllCostTypes() returns a promise
      const response = await customerApi.getAllCostTypes()
      state.costTypeOptions.value = response.data // Adjust this based on your actual API response structure
    } catch (error) {
      console.error(error)
    }
  }

  onMounted(async () => {
    customersStore.setAddedOrderItems(props.headingName, [])
  })

  const props = defineProps({
    itemsProp: {
      type: Object,
      default: () => []
    },
    amountFieldName: {
      type: String,
      default: "amount"
    },
    categoryFieldName: {
      type: String,
      default: "cost_type"
    },
    categoryFieldName2: {
      type: String,
      default: "id"
    },
    placeholderText: {
      type: String,
      default: "Select a cost type"
    },
    handleDeleteClickFunc: {
      type: Function,
      default: () => () => true
    },
    closeConfirmationToastFunc: {
      type: Function,
      default: () => () => true
    },
    freshDictForAdd: {
      type: Object,
      default: () => ({})
    },
    addButtonText: {
      type: String,
      default: "Add Cost(s)"
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    isEditing: {
      type: Boolean,
      default: false
    },
    handleAddItemSaveClickFunc: {
      type: Function,
      default: () => () => true
    },
    showConfirmToast: {
      type: Function,
      default: () => () => true
    },
    headingName: {
      type: String,
      default: "Misc. Costs"
    }
  })

  /**
   * This function will remove the to-be-added items so that there is a dynamic feel to the editability
   * @param {*} index This is the index of the new items that is to be added.
   */
  const handleRemoveItemClick = (index) => {
    customersStore.addedOrderItems[props.headingName].splice(index, 1)
  }

  /**
   * This function will be used to add new fields for the items. it will put a blank new fee option for the user
   * allowing them to edit them as they wish. They can add as many as they would like.
   */
  const handleAddItemClick = () => {
    // Push a new object into the 'addedFees' array
    customersStore.addToOrderItemList(
      props.headingName,
      Object.assign({}, props.freshDictForAdd)
    )
  }

  /**
   * This function will clear all of the to-be-added misc costs from the list so they will all go away
   */
  const handleCancelItemClick = () => {
    customersStore.setAddedOrderItems(props.headingName, [])
  }

  //These options are the options for cost type that come from the cost_type table
  const miscCostOptionList = computed(() => {
    return state.costTypeOptions.value.map((option) => ({
      label: option.name,
      value: option.id
    }))
  })
  // const feeTypeOptions = [
  //   { label: "LATE", value: "LATE" },
  //   { label: "CREDIT_CARD", value: "CREDIT_CARD" },
  //   { label: "RUSH", value: "RUSH" },
  // ];

  // const rentPeriodFeeTypeOptions = [
  //   { label: "LATE", value: "LATE" },
  //   { label: "CREDIT_CARD", value: "CREDIT_CARD" },
  //   { label: "RUSH", value: "RUSH" },
  //   { label: "DOWN_PAYMENT", value: "DOWN_PAYMENT" },
  // ]

  const feeTypeOptions = computed(() => {
    return customersStore.feeTypes
      ?.filter((type) => !type.is_archived)
      .map((type) => {
        return {
          label: type.is_taxable
            ? `${type.name} (Is Taxed)`
            : `${type.name} (Not Taxed)`,
          value: type.id
        }
      })
  })

  const checkIfEmptyString = (prop) => {
    let bool = false
    if (prop == "") bool = true
    return bool
  }

  const state = reactive({
    addedToList: [], // to-be-added items that will be sent in a post request to the api,
    categoryOptionsList: [],
    costTypeOptions: [],
    itemsProp: [],
    headingName: null
  })

  // Took this watch code out that would prevent us from modifying the passed by reference props object because
  // i do need the original object to be modified for when we are updating the items. The parent needs to have those
  // changes in order to grab all of them at once without having to worry about passing data back from the child.
  // watch(
  //   () => props.itemsProp, // watching
  //   (newVal) => {
  //     // new value coming through
  //     state.itemsProp = cloneDeep(newVal);
  //   },
  //   { immediate: true, deep: true } // options you might need
  // );

  watch(
    () => props.headingName, // watching
    async (headingName) => {
      if (headingName === "Misc. Costs") {
        await fetchOptions()
        state.categoryOptionsList = miscCostOptionList
      } else if (headingName == "Fees") {
        state.categoryOptionsList = feeTypeOptions
      } else if (headingName == "Rent Period Fees") {
        state.categoryOptionsList = feeTypeOptions
      }
    },
    { immediate: true, deep: true } // options you might need
  )
</script>
