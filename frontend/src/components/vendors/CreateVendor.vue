<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Name</label
          >
          <InputText
            placeholder="Name"
            v-model="state.vendor.name"
            :class="{ 'p-invalid': v$.vendor.name.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="country" class="font-medium text-900 dark:text-0"
            >Country</label
          >
          <Select
            v-model="state.vendor.country"
            placeholder="Country"
            :options="state.countriesList"
            class="p-component p-inputtext-fluid"
            optionLabel="name"
            optionValue="code"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="state" class="font-medium text-900 dark:text-0">{{
            stateProvinceText
          }}</label>
          <Select
            v-model="state.vendor.state"
            :placeholder="stateProvinceText"
            class="p-component p-inputtext-fluid"
            :options="
              getCountry == 'Canada' ? state.provinceList : state.statesList
            "
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0">City</label>
          <InputText
            placeholder="City"
            class="p-component p-inputtext-fluid"
            v-model="state.vendor.city"
            id="city"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0"
            >Address</label
          >
          <InputText
            placeholder="Address"
            v-model="state.vendor.address"
            class="p-component p-inputtext-fluid"
            id="address"
            type="text"
            maxlength="60"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0">{{
            postalZipText
          }}</label>
          <InputText
            :useGrouping="false"
            :placeholder="postalZipText"
            class="p-component p-inputtext-fluid"
            :class="{ 'p-invalid': v$.vendor.zip.$invalid }"
            v-model="state.vendor.zip"
            id="zip"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="country" class="font-medium text-900 dark:text-0"
            >Country code</label
          >
          <Select
            v-model="state.vendor.country_code_primary"
            :options="state.country_codes"
            class="p-component p-inputtext-fluid"
            optionLabel="name"
            optionValue="code"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Primary phone</label
          >
          <InputMask
            mask="(999) 999-9999"
            mode="decimal"
            :useGrouping="false"
            class="p-component p-inputtext-fluid"
            placeholder="Primary phone"
            v-model="state.vendor.primary_phone"
            id="primary_phone"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Secondary phone</label
          >
          <InputMask
            mask="(999) 999-9999"
            mode="decimal"
            :useGrouping="false"
            class="p-component p-inputtext-fluid"
            placeholder="Secondary phone"
            v-model="state.vendor.secondary_phone"
            id="secondary_phone"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0"
            >Primary Email</label
          >
          <InputText
            placeholder="Primary Email"
            v-model="state.vendor.primary_email"
            class="p-component p-inputtext-fluid"
            id="primary_email"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0"
            >Secondary Email</label
          >
          <InputText
            placeholder="Secondary Email"
            v-model="state.vendor.secondary_email"
            class="p-component p-inputtext-fluid"
            id="secondary_email"
            type="text"
          />
        </div>
      </div>
      <div class="col-span-12 mb-4 field md:col-span-2">
        <label for="type" class="font-medium text-900 dark:text-0"
          >Vendor Type</label
        >
        <Select
          v-model="state.vendor.type.id"
          :options="state.vendor_types"
          class="p-component p-inputtext-fluid"
          optionLabel="name"
          optionValue="code"
        />
      </div>
    </div>
    <Button
      :label="
        $isObjectPopulated(vendorProp) ? 'Update Vendor' : 'Create Vendor'
      "
      @click="createUpdateVendor"
      :loading="state.loading"
      icon="pi pi-file"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, defineEmits } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email, helpers } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"

  import VendorsService from "@/service/Vendors"
  import VendorsApi from "@/api/vendors"
  import InventoryService from "@/service/Inventory"

  import { useToast } from "primevue/usetoast"
  import { useVendors } from "@/store/modules/vendors"
  import CustomerApi from "@/api/customers"
  import { useUsers } from "@/store/modules/users"

  const toast = useToast()

  const userStore = useUsers()

  const vendorService = new VendorsService()
  const vendorApi = new VendorsApi()
  const vendorStore = useVendors()
  const inventoryService = new InventoryService()

  const stateService = new StateService()
  const postalZipText = computed(() => {
    return state.vendor?.country && state.vendor?.country == "Canada"
      ? "Postal Code"
      : "Zip Code"
  })

  const stateProvinceText = computed(() => {
    return state.vendor?.country && state.vendor?.country == "Canada"
      ? "Province"
      : "State"
  })
  const getCountry = computed(() => {
    return state.vendor?.country
  })

  const { vendorProp } = defineProps({
    vendorProp: {
      type: Object,
      default: () => ({})
    }
  })

  const customerApi = new CustomerApi()

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const swapOldVendor = (updatedVendor) => {
    const index = cloneDeep(vendorStore.vendors)
      .map((u) => u.id)
      .indexOf(updatedVendor.id)
    let clonedVendors = cloneDeep(vendorStore.vendors)
    clonedVendors[index] = vendorService.dtoVendor(updatedVendor)
    vendorStore.setVendors(clonedVendors)
  }
  const fetchCountries = async () => {
    const { data } = await customerApi.getCountries()
    return data.value.map((e) => {
      return { name: e.country_name, code: e.code }
    })
  }

  onMounted(async () => {
    state.statesList = stateService.getStates()
    state.provinceList = stateService.getProvinces()

    let accountId = userStore?.cms?.account_id

    const countries = await fetchCountries()

    state.country_codes = [
      { name: "+1", code: "+1" },
      { name: "+86", code: "+86" }
    ]

    state.countriesList = countries

    const { data } = await customerApi.getVendorTypes()
    state.vendor_types = data.value.map((el) => {
      return {
        name: el.type,
        code: el.id
      }
    })
    resetVendor()
  })

  const emptyVendor = {
    name: "",
    city: "",
    state: "",
    zip: "",
    address: "",
    primary_phone: "",
    secondary_phone: "",
    primary_email: "",
    secondary_email: "",
    country: "",
    country_code_primary: "+1",
    country_code_secondary: "+1",
    type: { id: 1 }
  }

  const state = reactive({
    loading: false,
    vendor: cloneDeep(emptyVendor),
    statesList: [],
    provinceList: [],
    originalVendor: null,
    countriesList: [],
    country_codes: [],
    vendor_types: []
  })
  const isInUSA = computed(
    () => !state.vendor?.country || state.vendor?.country != "Canada"
  )
  const zipRegex = /^\d{5}(?:[-\s]\d{4})?$/

  const rules = computed(() => ({
    vendor: {
      name: { required, $lazy: true },
      zip: {
        validZip: helpers.withMessage(
          "ZIP Code must be at least 5 characters.",
          (value) => {
            if (!isInUSA.value) {
              return true
            }
            return zipRegex.test(value) //minLength(5)(value)
          }
        ),
        $lazy: true
      }
      //city: { required, $lazy: true },
      //state: { required, $lazy: true },
      //zip: { required, $lazy: true },
      //address: { required, $lazy: true },
      //primary_phone: { required, $lazy: true },
      //primary_email: { required, $lazy: true },
    }
  }))

  const v$ = useVuelidate(rules, state)

  const resetVendor = () => {
    let vendor = null
    if (vendorProp) {
      vendor = vendorService.dtoVendor(vendorProp)
      if (vendor.type == null) {
        vendor.type = { id: 3 }
      }
    } else {
      vendor = emptyVendor
    }
    state.originalVendor = cloneDeep(vendor)
    state.vendor = cloneDeep(vendor)
    v$.value.$reset()
  }

  const createUpdateVendor = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    state.loading = true

    if (state.vendor.id) {
      let requestData = $removeUnusedProps(state.vendor, state.originalVendor)

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "Vendor Unchanged",
          detail: "Vendor Unchanged",
          group: "br",
          life: 5000
        })
        return
      }

      const { data, error } = await vendorApi.updateVendor(
        state.vendor.id,
        requestData
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Vendor Updated",
          detail: "Successfully updated vendor",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating vendor",
          group: "br",
          life: 5000
        })
      }
      swapOldVendor(data.value)
    } else {
      console.log(state.vendor)
      const { data } = await vendorApi.createVendor(state.vendor)

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Vendor Saved",
          detail: "Successfully saved vendor",
          group: "br",
          life: 5000
        })
      }
      let updatedVendors = cloneDeep(vendorStore.vendors)
      updatedVendors.unshift(vendorService.dtoVendor(data.value))
      vendorStore.setVendors(updatedVendors)
      resetVendor()
    }
    state.loading = false
    emit("hide")
  }
</script>

<style></style>
