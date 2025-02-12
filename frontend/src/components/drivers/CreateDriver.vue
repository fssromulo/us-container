<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Company Name</label
          >
          <InputText
            placeholder="Company Name"
            v-model="state.driver.company_name"
            :class="{ 'p-invalid': v$.driver.company_name.$invalid }"
            id="cost"
            class="p-component p-inputtext-fluid"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="city" class="font-medium text-900 dark:text-0"
            >City</label
          >
          <Select
            v-model="state.driver.city"
            placeholder="Select City"
            :class="{ 'p-invalid': v$.driver.city.$invalid }"
            :options="mappedCities"
            class="p-component p-inputtext-fluid"
            optionLabel="label"
            optionValue="value"
          />
        </div>
        <div
          v-if="getAccountCountry == 'Canada'"
          class="col-span-12 mb-4 field md:col-span-2"
        >
          <label for="state" class="font-medium text-900 dark:text-0"
            >Province</label
          >
          <Select
            v-model="state.driver.province"
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
            v-model="state.driver.state"
            placeholder="State"
            class="p-component p-inputtext-fluid"
            :options="state.statesList"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label
            for="price_per_mile"
            class="font-medium text-900 dark:text-0"
            >{{ `Cost per ${metrics}` }}</label
          >
          <InputText
            mode="decimal"
            :useGrouping="false"
            :placeholder="`Cost per ${metrics}`"
            v-model="state.driver.cost_per_mile"
            :class="{ 'p-invalid': v$.driver.cost_per_mile.$invalid }"
            id="cost"
            class="p-component p-inputtext-fluid"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Cost per 100 {{ metrics }}</label
          >
          <InputNumber
            mode="decimal"
            :useGrouping="false"
            placeholder="Cost per 100 miles"
            v-model="state.driver.cost_per_100_miles"
            :class="{ 'p-invalid': v$.driver.cost_per_100_miles.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Phone Number</label
          >
          <InputMask
            mode="decimal"
            mask="(999) 999-9999"
            placeholder="(999) 999-9999"
            :useGrouping="false"
            v-model="state.driver.phone_number"
            :class="{ 'p-invalid': v$.driver.phone_number.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Email</label
          >
          <InputText
            placeholder="Email"
            v-model="state.driver.email"
            :class="{ 'p-invalid': v$.driver.email.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
      </div>
    </div>
    <Button
      :label="
        $isObjectPopulated(driverProp) ? 'Update Driver' : 'Create Driver'
      "
      @click="createUpdateDriver"
      :loading="state.loading"
      icon="pi pi-file"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"

  import DriverService from "@/service/Drivers"
  import DriveApi from "@/api/drivers"
  import InventoryService from "@/service/Inventory"
  import { useContainerPrices } from "@/store/modules/pricing"

  import { useToast } from "primevue/usetoast"
  import { useDrivers } from "@/store/modules/drivers"
  import PricingService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import { useUsers } from "@/store/modules/users"

  const pricingService = new PricingService()
  const pricingApi = new PricingApi()
  const usersStore = useUsers()

  const toast = useToast()
  const containerPrices = useContainerPrices()

  const driverService = new DriverService()
  const driverApi = new DriveApi()
  const driverStore = useDrivers()
  const inventoryService = new InventoryService()

  const stateService = new StateService()

  const { driverProp } = defineProps({
    driverProp: {
      type: Object,
      default: () => ({})
    }
  })

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const getAccountCountry = computed(() => {
    let account_country = usersStore.cms.account_country
    return account_country
  })

  const metrics = computed(() => {
    let account_country = usersStore.cms.account_country
    if (account_country == "Canada") {
      return "km"
    } else {
      return "mile"
    }
  })

  const swapOldDriver = (updatedDriver) => {
    const index = cloneDeep(driverStore.drivers)
      .map((u) => u.id)
      .indexOf(updatedDriver.id)
    let clonedDrivers = cloneDeep(driverStore.drivers)
    clonedDrivers[index] = driverService.dtoDriver(updatedDriver)
    driverStore.setDrivers(clonedDrivers)
  }

  onMounted(async () => {
    state.statesList = stateService.getStates()
    state.provinceList = stateService.getProvinces()
    if (containerPrices.locations.length === 0) {
      const { data } = await pricingApi.getLocations()
      containerPrices.setLocations(
        data.value.map((location) => pricingService.dtoLocation(location))
      )
    }
    resetDriver()
  })

  const emptyDriver = {
    company_name: "",
    city: "",
    state: "",
    province: "",
    cost_per_mile: 0,
    cost_per_100_miles: 0,
    phone_number: 0,
    email: ""
  }

  const state = reactive({
    loading: false,
    driver: cloneDeep(emptyDriver),
    statesList: [],
    provinceList: [],
    originalDriver: null
  })

  const rules = computed(() => ({
    driver: {
      company_name: { required, $lazy: true },
      city: { required, $lazy: true },
      cost_per_mile: { required, $lazy: true },
      cost_per_100_miles: { required, $lazy: true },
      phone_number: { required, $lazy: true },
      email: { required, email, $lazy: true }
    }
  }))

  const mappedCities = computed(() => {
    return containerPrices.locations.map((c) => {
      return {
        label: c.city,
        value: c.city
      }
    })
  })

  const v$ = useVuelidate(rules, state)

  const resetDriver = () => {
    let driver = null
    if (driverProp) {
      driver = driverService.dtoDriver(driverProp)
    } else {
      driver = emptyContainer
    }
    state.originalDriver = cloneDeep(driver)
    state.driver = cloneDeep(driver)
    v$.value.$reset()
  }

  const createUpdateDriver = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    state.loading = true

    if (getAccountCountry.value == "Canada") {
      if (state.driver.province == null) {
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
      if (state.driver.state == null) {
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

    if (state.driver.id) {
      let requestData = $removeUnusedProps(state.driver, state.originalDriver)

      if (requestData.phone_number) {
        requestData.phone_number = requestData.phone_number.replace(
          /[^0-9]/g,
          ""
        )
      }

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "Driver Unchanged",
          detail: "Driver Unchanged",
          group: "br",
          life: 5000
        })
        return
      }

      const { data, error } = await driverApi.updateDriver(
        state.driver.id,
        requestData
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Driver Updated",
          detail: "Successfully updated driver",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating driver",
          group: "br",
          life: 5000
        })
      }
      swapOldDriver(data.value)
    } else {
      const { data } = await driverApi.createDriver(state.driver)

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Driver Saved",
          detail: "Successfully saved driver",
          group: "br",
          life: 5000
        })
      }
      let updatedDrivers = cloneDeep(driverStore.drivers)
      updatedDrivers.unshift(driverService.dtoDriver(data.value))
      driverStore.setDrivers(updatedDrivers)
      resetDriver()
    }
    state.loading = false
    emit("hide")
  }
</script>

<style></style>
