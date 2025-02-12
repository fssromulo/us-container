<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >City</label
          >
          <InputText
            placeholder="City"
            class="p-component p-inputtext-fluid"
            v-model="state.location.city"
            :class="{ 'p-invalid': v$.location.city.$invalid }"
            id="cost"
            type="text"
          />
        </div>
        <div
          class="col-span-12 mb-4 field md:col-span-2"
          v-if="getAccountCountry == 'Canada'"
        >
          <label for="state" class="font-medium text-900 dark:text-0"
            >Province
          </label>
          <Select
            v-model="state.location.province"
            placeholder="Province"
            class="p-component p-inputtext-fluid"
            :options="state.provinceList"
          />
        </div>
        <div v-else class="col-span-12 mb-4 field md:col-span-2">
          <label for="state" class="font-medium text-900 dark:text-0"
            >State</label
          >
          <Select
            v-model="state.location.state"
            placeholder="State"
            class="p-component p-inputtext-fluid"
            :options="state.statesList"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0">{{
            postalZipText
          }}</label>
          <InputText
            :placeholder="postalZipText"
            v-model="state.location.zip"
            :class="{ 'p-invalid': v$.location.zip.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label
            for="price_per_mile"
            class="font-medium text-900 dark:text-0"
            >{{ metrics }}</label
          >
          <InputNumber
            mode="currency"
            currency="USD"
            locale="en-US"
            :placeholder="metrics"
            v-model="state.location.cost_per_mile"
            class="p-component p-inputtext-fluid"
            :class="{ 'p-invalid': v$.location.cost_per_mile.$invalid }"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Min shipping cost</label
          >
          <InputNumber
            mode="currency"
            currency="USD"
            locale="en-US"
            placeholder="Minimum shipping price"
            v-model="state.location.minimum_shipping_cost"
            :class="{ 'p-invalid': v$.location.minimum_shipping_cost.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="region" class="font-medium text-900 dark:text-0"
            >Region</label
          >
          <Select
            v-model="state.location.region"
            :class="{ 'p-invalid': v$.location.region.$invalid }"
            class="p-component p-inputtext-fluid"
            placeholder="Region"
            :options="['A', 'B', 'C']"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="pickup_region" class="font-medium text-900 dark:text-0"
            >Pickup region</label
          >
          <Select
            v-model="state.location.pickup_region"
            class="p-component p-inputtext-fluid"
            placeholder="Pickup region"
            :options="['PU A', 'PU B', 'PU C']"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="pickup_region" class="font-medium text-900 dark:text-0"
            >Average Delivery Days</label
          >
          <InputNumber
            placeholder="Average Delivery Days"
            v-model="state.location.average_delivery_days"
            class="p-component p-inputtext-fluid is_pay_on_delivery"
            id="cost"
            type="text"
          />
        </div>
      </div>
    </div>
  </div>
  <Button
    :label="locationProp?.id ? 'Update Location' : 'Create Location'"
    @click="createUpdateLocation"
    :loading="state.loading"
    icon="pi pi-file"
    class="w-auto"
  ></Button>
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

  const toast = useToast()
  const usersStore = useUsers()

  const pricingService = new PricingService()
  const pricingApi = new PricingApi()
  const pricingStore = useContainerPrices()
  const inventoryService = new InventoryService()

  const stateService = new StateService()

  const { locationProp } = defineProps({
    locationProp: {
      type: Object,
      default: () => ({})
    }
  })
  const postalZipText = computed(() => {
    return usersStore.cms?.account_country &&
      usersStore.cms?.account_country == "Canada"
      ? "Postal Code"
      : "Zip"
  })

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const getAccountCountry = computed(() => {
    let account_country = usersStore.cms.account_country
    return account_country
  })

  const swapOldLocation = (updatedLocation) => {
    const index = cloneDeep(pricingStore.locations)
      .map((u) => u.id)
      .indexOf(updatedLocation.id)
    let clonedLocations = cloneDeep(pricingStore.locations)
    clonedLocations[index] = pricingService.dtoLocation(updatedLocation)
    pricingStore.setLocations(clonedLocations)
  }

  const metrics = computed(() => {
    let account_country = usersStore.cms.account_country
    if (account_country == "Canada") {
      return "Price per km"
    } else {
      return "Price per mile"
    }
  })

  onMounted(async () => {
    state.statesList = stateService.getStates()
    let account_country = usersStore.cms.account_country
    if (account_country == "Canada") {
      state.provinceList = stateService.getProvinces()
    }
    resetLocation()
  })

  const emptyLocation = {
    city: "",
    state: "",
    zip: "",
    cost_per_mile: 0,
    minimum_shipping_cost: 0,
    region: "",
    province: ""
  }

  const state = reactive({
    loading: false,
    location: cloneDeep(emptyLocation),
    statesList: [],
    originalLocation: null
  })

  const rules = computed(() => ({
    location: {
      city: { required, $lazy: true },
      zip: { required, $lazy: true },
      cost_per_mile: { required, $lazy: true },
      minimum_shipping_cost: { required, $lazy: true },
      region: { required, $lazy: true }
    }
  }))

  const v$ = useVuelidate(rules, state)

  const resetLocation = () => {
    let location = null
    if (locationProp) {
      location = pricingService.dtoLocation(locationProp)
    } else {
      location = emptyContainer
    }
    state.originalLocation = cloneDeep(location)
    state.location = cloneDeep(location)
    v$.value.$reset()
  }

  const createUpdateLocation = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    state.loading = true

    if (getAccountCountry.value == "Canada") {
      if (state.location.province == null) {
        toast.add({
          severity: "error",
          summary: "Province required",
          detail: "Province required",
          group: "br",
          life: 5000
        })
        return
      }
    } else {
      if (state.location.state == null) {
        toast.add({
          severity: "error",
          summary: "State required",
          detail: "State required",
          group: "br",
          life: 5000
        })
        return
      }
    }

    if (state.location.id) {
      let requestData = $removeUnusedProps(
        state.location,
        state.originalLocation
      )

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "Location Unchanged",
          detail: "Location Unchanged",
          group: "br",
          life: 5000
        })
        return
      }

      const { data, error } = await pricingApi.updateLocation(
        state.location.id,
        requestData
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Location Updated",
          detail: "Successfully updated location",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating location price",
          group: "br",
          life: 5000
        })
      }
      swapOldLocation(data.value)
    } else {
      const { data } = await pricingApi.createLocation(state.location)

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Location Saved",
          detail: "Successfully saved location",
          group: "br",
          life: 5000
        })
      }
      let updatedLocations = cloneDeep(pricingStore.locations)
      updatedLocations.unshift(pricingService.dtoLocation(data.value))
      pricingStore.setLocations(updatedLocations)
      resetLocation()
    }
    state.loading = false
    emit("hide")
  }
</script>

<style></style>
