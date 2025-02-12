<template>
  <div class="container">
    <h3 class="text-center">Countries</h3>
    <div class="row">
      <div class="mb-4 field col-sm-12 col-md-12">
        <label class="font-medium text-900 dark:text-0">Country Name</label>
        <InputText class="w-full" v-model="state.country.country_name" />
      </div>
      <div class="mb-4 field col-sm-12 col-md-12">
        <label class="font-medium text-900 dark:text-0">Country Code</label>
        <InputText class="w-full" v-model="state.country.code" />
      </div>
    </div>
    <div class="row">
      <div class="mb-6 field col-sm-6 col-md-3">
        <Button
          class="p-button-rounded p-button-successsave"
          label="Save Country"
          :disabled="
            state.country.country_name.length == 0 ||
            state.country.code.length == 0
          "
          :loading="state.loading"
          @click="save"
        />
      </div>
    </div>
    <div class="row">
      <DataTable :value="state.countries">
        <Column field="name" header="Country Name"></Column>
        <Column field="code" header="Country Code"></Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
  import AccountApi from "@/api/account"
  import { reactive, onMounted } from "vue"
  import UsersService from "@/service/User"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useDrivers } from "@/store/modules/drivers"
  import { useUsers } from "@/store/modules/users"
  import cloneDeep from "lodash.clonedeep"
  import { useToast } from "primevue/usetoast"
  import CustomerApi from "@/api/customers"

  const customerOrderStore = useCustomerOrder()
  const customerApi = new CustomerApi()

  const accountApi = new AccountApi()

  const userStore = useUsers()
  const toast = useToast()

  const state = reactive({
    cms: null,
    loading: false,
    cmsId: null,
    countries: [],
    country: {
      country_name: "",
      code: ""
    }
  })

  const save = async () => {
    state.loading = true
    const { data, error } = await customerApi.addCountry(state.country)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error adding country",
        detail: error.message,
        life: 3000,
        group: "br"
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Country Saved",
        life: 3000,
        group: "br"
      })
    }
    state.countries = await fetchCountries()
    state.country.code = ""
    ;(state.country.country_name = ""), (state.loading = false)
  }
  const fetchCountries = async () => {
    const { data } = await customerApi.getCountries()
    return data.value.map((e) => {
      return { name: e.country_name, code: e.code }
    })
  }

  onMounted(async () => {
    state.countries = await fetchCountries()
  })
</script>
