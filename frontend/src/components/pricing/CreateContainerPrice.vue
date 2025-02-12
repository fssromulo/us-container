<template>
  <div>
    <div>
      <div class="grid grid-cols-1 gap-4 md:grid-cols-4 formgrid p-fluid">
        <div
          v-if="$isObjectPopulated(containerPriceProp)"
          class="col-span-12 mb-2 text-2xl"
        >
          {{ state.container.title }}
        </div>
        <div class="grid grid-cols-12 col-span-12 gap-4 formgrid p-fluid">
          <div class="col-span-12 mb-3 field md:col-span-4">
            <label for="product_type" class="font-medium text-900"
              >Product type</label
            >
            <Select
              placeholder="Select type"
              :options="state.productTypes"
              v-model="state.container.product_type"
              class="p-component p-inputtext-fluid"
              id="condition"
              type="text"
              optionLabel="label"
              optionValue="value"
            />
          </div>
          <div class="col-span-12 mb-3 field md:col-span-4">
            <label for="type" class="font-medium text-900">Type</label>
            <MultiSelect
              icon="pi pi-plus"
              v-model="state.container.displayAttributes"
              class="p-component p-inputtext-fluid"
              :class="{ 'p-invalid': v$.container.displayAttributes.$invalid }"
              placeholder="Select type"
              :options="inventoryService.types"
              optionLabel="label"
              optionValue="value"
            />
          </div>
          <div class="col-span-12 mb-3 field md:col-span-4">
            <label for="condition" class="font-medium text-900"
              >Condition</label
            >
            <Select
              placeholder="Select condition"
              :options="inventoryService.conditions"
              v-model="state.container.condition"
              class="p-component p-inputtext-fluid"
              id="condition"
              type="text"
              optionLabel="label"
              optionValue="value"
            />
          </div>
        </div>
        <div class="grid grid-cols-12 col-span-12 gap-4 formgrid p-fluid">
          <div class="col-span-12 mb-3 field md:col-span-4">
            <label for="container_size" class="font-medium text-900"
              >Container size</label
            >
            <Select
              icon="pi pi-plus"
              v-model="state.container.container_size"
              :class="{ 'p-invalid': v$.container.container_size.$invalid }"
              placeholder="Select size"
              optionLabel="label"
              class="p-component p-inputtext-fluid"
              optionValue="value"
              :options="inventoryService.sizes"
            />
          </div>
          <div class="col-span-12 mb-3 field md:col-span-4">
            <label for="sale_price" class="font-medium text-900 dark:text-0"
              >Sale price</label
            >
            <InputText
              placeholder="Sale price"
              v-model="state.container.price"
              class="p-inputtext p-component p-inputtext-fluid"
              id="cost"
              type="text"
            />
          </div>
          <div class="col-span-12 mb-3 field md:col-span-4">
            <label for="sale_price" class="font-medium text-900 dark:text-0"
              >Monthly price</label
            >
            <InputText
              placeholder="Monthly price"
              v-model="state.container.monthly_price"
              class="p-inputtext p-component p-inputtext-fluid"
              id="monthly_price"
              type="text"
            />
          </div>
        </div>
        <div class="grid grid-cols-12 col-span-12 gap-4 formgrid p-fluid">
          <div class="col-span-12 mb-4 field md:col-span-3">
            <label
              for="cost_per_mile"
              class="font-medium text-900 dark:text-0"
              >{{ metrics }}</label
            >
            <InputText
              :placeholder="metrics"
              v-model="state.container.cost_per_mile"
              class="p-inputtext p-component p-inputtext-fluid"
              id="cost_per_mile"
              type="text"
            />
          </div>
          <div class="col-span-12 mb-4 field md:col-span-3">
            <label for="cost_per_mile" class="font-medium text-900 dark:text-0"
              >Minimum shipping cost</label
            >
            <InputText
              placeholder="Minimum shipping cost"
              v-model="state.container.minimum_shipping_cost"
              class="p-inputtext p-component p-inputtext-fluid"
              id="minimum_shipping_cost"
              type="text"
            />
          </div>
        </div>

        <div
          class="col-span-12 mb-3 opacity-50 surface-border border-top-1"
        ></div>
        <div class="col-span-12 mb-3 text-xl font-medium text-900"
          >Coming from</div
        >
        <div class="col-span-12 mb-3 field md:col-span-4">
          <Select
            placeholder="Select location"
            optionLabel="label"
            optionValue="value"
            :options="locationsList"
            v-model="state.container.location_id"
            class="p-component p-inputtext-fluid"
            @change="handleLocationChange"
            id="location_id"
            type="text"
          />
        </div>

        <div class="col-span-12 mb-4 border border-t opacity-50"></div>
      </div>
      <div class="col-span-12 mb-4 border border-t opacity-50"></div>
      <div class="col-span-6 mb-4 field">
        <label for="description" class="font-medium text-900 dark:text-0"
          >Description</label
        >
        <Textarea
          v-model="state.container.description"
          id="description"
          :autoResize="true"
          ::rows="5"
          class="p-inputtext p-component p-inputtext-fluid"
        ></Textarea>
      </div>
      <div class="col-span-12 mb-3 field md:col-span-4">
        <Select
          placeholder="Payment on delivery"
          optionLabel="label"
          optionValue="value"
          :options="podsOptions"
          v-model="state.container.pod"
          class="p-component p-inputtext-fluid"
          id="location_id"
          type="text"
        />
      </div>
      <div class="col-span-12 mb-4 border border-t opacity-50"></div>
    </div>
    <Button
      :label="
        $isObjectPopulated(containerPriceProp)
          ? 'Update Container'
          : 'Create Container'
      "
      @click="createUpdateContainer"
      icon="pi pi-file"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, defineEmits } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"

  import PricingService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import InventoryService from "@/service/Inventory"

  import { useToast } from "primevue/usetoast"
  import { useContainerPrices } from "@/store/modules/pricing"
  import { useUsers } from "@/store/modules/users"
  import CustomerApi from "@/api/customers"
  const customerApi = new CustomerApi()

  const usersStore = useUsers()

  const toast = useToast()

  const pricingService = new PricingService()
  const pricingApi = new PricingApi()
  const pricingStore = useContainerPrices()
  const inventoryService = new InventoryService()

  const stateService = new StateService()

  const { containerPriceProp } = defineProps({
    containerPriceProp: {
      type: Object,
      default: () => ({})
    }
  })

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const metrics = computed(() => {
    let account_country = usersStore.cms.account_country
    if (account_country == "Canada") {
      return "Cost per km"
    } else {
      return "Cost per mile"
    }
  })

  const swapOldContainer = (updatedContainer) => {
    const index = cloneDeep(pricingStore.containerPrices)
      .map((u) => u.id)
      .indexOf(updatedContainer.id)
    let clonedContainers = cloneDeep(pricingStore.containerPrices)
    clonedContainers[index] =
      pricingService.dtoContainerPricing(updatedContainer)
    pricingStore.setContainerPrices(clonedContainers)
  }

  onMounted(async () => {
    state.statesList = stateService.getStates()
    resetContainer()
  })

  const locationsList = computed(() => {
    return pricingStore?.locations
      ?.map((v) => {
        return { label: v.city, value: v.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const podsOptions = computed(() => {
    return [
      {
        label: "Enabled",
        value: true
      },
      {
        label: "Disabled",
        value: false
      }
    ]
  })

  const resetContainer = async () => {
    let container = null
    if ($isObjectPopulated(containerPriceProp)) {
      container = cloneDeep(containerPriceProp)
    } else {
      container = emptyContainer
    }

    state.originalContainer = cloneDeep(container)
    state.container = cloneDeep(container)
    state.container.displayAttributes = []

    if (state.container.container_product_attributes) {
      const { data } = await customerApi.get_all_container_attributes()
      let pairs = data.value
      pairs.forEach((pair) => {
        for (
          var i = 0;
          i < state.container.container_product_attributes.length;
          i++
        ) {
          if (
            state.container.container_product_attributes[i].container_attribute[
              "name"
            ] == pair.name
          ) {
            state.container.displayAttributes.push(pair.value)
            break
          }
        }
      })
    }

    if (state.container.product_type == "ContainerTypes.SHIPPING_CONTAINER") {
      state.container.product_type == "SHIPPING_CONTAINER"
    } else {
      state.container.product_type == "PORTABLE_CONTAINER"
    }

    v$.value.$reset()
  }

  const emptyContainer = {
    attributes: inventoryService.defaultContainerType,
    product_type: "",
    sale_price: "",
    container_size: "",
    condition: "",
    description: "",
    location_id: ""
  }

  const state = reactive({
    loading: false,
    container: cloneDeep(emptyContainer),
    originalContainer: null,
    isRental: false,
    productTypes: [
      {
        label: "Shipping Container",
        value: "SHIPPING_CONTAINER"
      },
      {
        label: "Portable Container",
        value: "PORTABLE_CONTAINER"
      }
    ],
    selectedCategory: { name: "Rental", code: "rental" },
    categorys: [
      { name: "Rental", code: "rental" },
      { name: "Rent to Own", code: "rto" },
      { name: "Sale", code: "purchase" }
    ],
    selectedCategory: { name: "Rental", code: "rental" }
  })

  const rules = computed(() => ({
    container: {
      price: { required, $lazy: true },
      container_size: { required, $lazy: true },
      condition: { required, $lazy: true },
      displayAttributes: { required, $lazy: true }
    }
  }))

  const v$ = useVuelidate(rules, state)

  const handleLocationChange = () => {
    const element = pricingStore.locations.find(
      (obj) => obj.id === state.container.location_id
    )
    if (element.cost_per_mile != undefined) {
      state.container.cost_per_mile = element.cost_per_mile
    }

    if (element.minimum_shipping_cost != undefined) {
      state.container.minimum_shipping_cost = element.minimum_shipping_cost
    }
  }

  const createUpdateContainer = async () => {
    if (
      state.container.monthly_price == "" ||
      state.container.monthly_price == null
    ) {
      toast.add({
        severity: "warn",
        summary: "Monthly price not set",
        detail: "Please set monthly price.",
        group: "br",
        life: 5000
      })
      return
    }

    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    state.loading = true

    if (state.container.id) {
      let requestData = $removeUnusedProps(
        cloneDeep(state.container),
        cloneDeep(state.originalContainer)
      )

      requestData.attributes =
        pricingService.convertDisplayAttributesToAttributes(
          cloneDeep(state.originalContainer.attributes),
          cloneDeep(state.container.displayAttributes)
        )
      delete requestData.displayAttributes

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "Container Unchanged",
          detail: "Container Unchanged",
          group: "br",
          life: 5000
        })
        return
      }

      const { data, error } = await pricingApi.updateContainerPricing(
        state.container.id,
        requestData
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Container Price Updated",
          detail: "Successfully updated container",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating container price",
          group: "br",
          life: 5000
        })
      }
      swapOldContainer(data.value)
    } else {
      state.container.attributes =
        pricingService.convertDisplayAttributesToAttributes(
          state.container.attributes,
          state.container.displayAttributes
        )

      delete state.container.displayAttributes
      const { data } = await pricingApi.createContainerPricing(state.container)

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Container Saved",
          detail: "Successfully saved container",
          group: "br",
          life: 5000
        })
      }
      let updatedContainerPrices = cloneDeep(pricingStore.containerPrices)
      updatedContainerPrices.unshift(
        pricingService.dtoContainerPricing(data.value)
      )
      pricingStore.setContainerPrices(updatedContainerPrices)
      resetContainer()
    }
    state.loading = false
    emit("hide")
  }
</script>

<style></style>
