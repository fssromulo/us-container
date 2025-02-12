<template>
  <div>
    <div class="grid grid-cols-1 gap-4 formgrid p-fluid">
      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="street_address" class="font-medium text-900 dark:text-0"
          >Street Address
        </label>
        <InputText
          :useGrouping="false"
          v-model="state.street_address"
          id="street_address"
          class="p-component p-inputtext-fluid"
          :class="{ 'border-red-500': v$.street_address.$invalid }"
          type="text"
        />
      </div>

      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="zip" class="font-medium text-900 dark:text-0"
          >{{ postalZipText }}
        </label>
        <InputText
          :useGrouping="false"
          v-model="state.zip"
          class="p-component p-inputtext-fluid"
          id="zip"
          type="text"
          :class="{ 'border-red-500': v$.zip.$invalid }"
        />
      </div>

      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="state" class="font-medium text-900 dark:text-0"
          >{{ stateProvinceText }}
        </label>
        <Select
          :useGrouping="false"
          v-model="state.state"
          :options="
            getAccountCountry == 'Canada'
              ? state.provinceList
              : state.statesList
          "
          optionLabel="name"
          class="p-component p-inputtext-fluid"
          optionValue="code"
          id="state"
          :class="{ 'border-red-500': v$.state.$invalid }"
        />
      </div>

      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="city" class="font-medium text-900 dark:text-0">City </label>
        <InputText
          :useGrouping="false"
          v-model="state.city"
          class="p-component p-inputtext-fluid"
          id="city"
          type="text"
          :class="{ 'border-red-500': v$.city.$invalid }"
        />
      </div>

      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="county" class="font-medium text-900 dark:text-0"
          >County
        </label>
        <InputText
          :useGrouping="false"
          v-model="state.county"
          class="p-component p-inputtext-fluid"
          :class="{ 'border-red-500': v$.county.$invalid }"
          id="county"
          type="text"
        />
      </div>

      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="Type" class="font-medium text-900 dark:text-0">Type </label>
        <Select
          :useGrouping="false"
          v-model="state.selectedType"
          optionLabel="name"
          optionValue="code"
          :options="state.types"
          class="p-component p-inputtext-fluid"
          id="type"
          type="text"
        />
      </div>

      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="county" class="font-medium text-900 dark:text-0"
          >Longitude
        </label>
        <InputText
          :useGrouping="false"
          v-model="state.longitude"
          class="p-component p-inputtext-fluid"
          id="longitude"
          type="text"
        />
      </div>

      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="county" class="font-medium text-900 dark:text-0"
          >Latitude
        </label>
        <InputText
          :useGrouping="false"
          v-model="state.latitude"
          class="p-component p-inputtext-fluid"
          id="latitude"
          type="text"
        />
      </div>
    </div>
    <br />

    <Button
      clas="mb-4 col-span-12 md:col-span-4"
      :label="props.isUpdate ? 'Update Address' : 'Add address'"
      @click="createUpdateAddressInventory()"
      :loading="state.loading"
    ></Button>
    <Message v-if="state.error" class="mt-5" severity="error">{{
      state.error
    }}</Message>
  </div>
</template>

<script setup>
  import { reactive, onMounted, computed } from "vue"
  import InventoryApi from "@/api/inventory"
  import { useToast } from "primevue/usetoast"
  import StateService from "../../service/StateService"
  import { useUsers } from "@/store/modules/users"
  import { useVuelidate } from "@vuelidate/core"
  import { required, email, integer, maxLength } from "@vuelidate/validators"

  const userStore = useUsers()

  const stateService = new StateService()

  const toast = useToast()
  const postalZipText = computed(() => {
    return userStore.cms?.account_country &&
      userStore.cms?.account_country == "Canada"
      ? "Postal Code"
      : "Zip"
  })
  const stateProvinceText = computed(() => {
    return userStore.cms?.account_country &&
      userStore.cms?.account_country == "Canada"
      ? "Province"
      : "State"
  })

  const getAccountCountry = computed(() => {
    let account_country = userStore.cms.account_country
    return account_country
  })

  const props = defineProps({
    line_item_id: {
      type: String
    },
    inventory_id: {
      type: String
    },
    state: {
      type: Object,
      default: {}
    },
    isUpdate: {
      type: Boolean,
      default: false
    },
    address_id: {
      type: String,
      default: null
    },
    resetFunction: {
      type: Function,
      default: () => {}
    }
  })

  const inventoryApi = new InventoryApi()

  const rules = computed(() => ({
    street_address: { required, $lazy: true },
    zip: { required, $lazy: true },
    state: { required, $lazy: true },
    city: { required, $lazy: true },
    county: { required, $lazy: true }
  }))

  const state = reactive({
    street_address: "",
    zip: "",
    state: "",
    statesList: [],
    provinceList: [],
    city: "",
    county: "",
    selectedType: { name: "test", code: "test" },
    types: [
      { name: "Personal", code: "rental" },
      { name: "Business", code: "rto" },
      { name: "Delivery", code: "purchase" },
      { name: "Secondary", code: "purchase" }
    ],
    longitude: "",
    latitude: "",
    loading: false,
    error: null
  })
  const v$ = useVuelidate(rules, state)

  onMounted(() => {
    state.street_address = props.state.street_address
    state.zip = props.state.zip
    state.city = props.state.city
    state.state = props.state.state
    state.county = props.state.county
    state.longitude = props.state.longitude
    state.latitude = props.state.latitude
    state.selectedType = {
      name: props.state.type,
      code: props.state.type
    }

    state.statesList = stateService.getStates().map((el) => {
      return {
        name: el,
        code: el
      }
    })
    state.provinceList = stateService.getProvinces().map((el) => {
      return {
        name: el,
        code: el
      }
    })
  })

  const createUpdateAddressInventory = async () => {
    state.error = null
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      state.error = "Please fill out all required fields"
      return
    }

    state.loading = true
    let address_inventory_obj = {
      street_address: state.street_address,
      zip: state.zip,
      state: state.state,
      city: state.city,
      county: state.county,
      tpye: state.selectedType,
      longitude: state.longitude,
      latitude: state.latitude,
      line_item_id: props.line_item_id,
      inventory_id: props.inventory_id
    }
    let resLineItem, response
    if (props.isUpdate) {
      response = await inventoryApi.updateInventoryAddress(
        props.address_id,
        address_inventory_obj
      )
    } else {
      response = await inventoryApi.createInventoryAddress(
        address_inventory_obj
      )
    }

    if (response.error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error saving inventory address.",
        life: 4000,
        group: "br"
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Inventory address successfully saved.",
        life: 4000,
        group: "br"
      })
    }

    await props.resetFunction(response.data.value)
    state.loading = false
  }
</script>
