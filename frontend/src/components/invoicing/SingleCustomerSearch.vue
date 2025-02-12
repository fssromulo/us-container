<template>
  <div
    class="grid mt-2 mb-2 mb-5 md:col-offset-1"
    v-if="$ability.can('merge', 'customer')"
  >
    <div class="flex flex-wrap gap-2 ml-3 mr-2 col-12" v-if="displaySearchMode">
      <div class="flex align-items-center">
        <RadioButton
          v-model="state.searchMode"
          inputId="searchExisting"
          name="searchMode"
          value="existing"
        />
        <label for="searchExisting" class="ml-2"
          >Search Existing Single Customers</label
        >
      </div>
      <div class="flex align-items-center">
        <RadioButton
          v-model="state.searchMode"
          inputId="createNew"
          name="searchMode"
          value="new"
        />
        <label for="createNew" class="ml-2">Create New Single Customer</label>
      </div>
    </div>
    <div class="flex flex-wrap gap-2 ml-3 mr-2">
      <div class="flex align-items-center">
        <RadioButton
          v-model="state.searchType"
          inputId="customerName"
          name="customerName"
          value="name"
        />
        <label for="customerName" class="ml-2">Customer Name</label>
      </div>
      <div class="flex align-items-center">
        <RadioButton
          v-model="state.searchType"
          inputId="customerPhone"
          name="customerPhone"
          value="phone"
        />
        <label for="customerPhone" class="ml-2">Customer Phone</label>
      </div>
      <div class="flex align-items-center">
        <RadioButton
          v-model="state.searchType"
          inputId="customerEmail"
          name="customerEmail"
          value="email"
        />
        <label for="customerEmail" class="ml-2">Customer Email</label>
      </div>
      <div class="flex align-items-center">
        <RadioButton
          v-model="state.searchType"
          inputId="companyName"
          name="companyName"
          value="companyName"
        />
        <label for="companyName" class="ml-2">Company Name</label>
      </div>

      <InputText
        style="min-width: 10em"
        v-model="state.search"
        placeholder="Search customer"
      />
      <Button
        class="ml-1"
        icon="pi pi-search"
        slot="right-icon"
        :loading="state.loading"
        @click="searchCustomer()"
      />
    </div>
  </div>
  <section>
    <DataTable
      v-if="state.retrievedCustomers.length > 0"
      ref="dt"
      selectionMode="single"
      :value="state.retrievedCustomers"
    >
      <Column field="button" header="Button" style="width: 160px">
        <template #body="slotProps">
          <Button
            class="p-button-rounded"
            :loading="state.isLoading"
            @click="createCustomerProfile(slotProps.data)"
            >Create customer Profile</Button
          >
        </template>
      </Column>
      <Column field="id" header="Container Id" style="display: none"></Column>
      <Column field="order_type" header="Order Type"></Column>
      <Column field="first_name" header="First Name"></Column>
      <Column field="last_name" header="Last Name"></Column>
      <Column field="email" header="Email"></Column>
      <Column field="phone" header="Phone"></Column>
      <Column field="street_address" header="Street Address"></Column>
      <Column field="zip" :header="postalZipText"></Column>
      <Column field="state" header="State"></Column>
      <Column field="city" header="City"></Column>
      <Column field="county" header="County"></Column>
    </DataTable>

    <DataTable
      v-if="state.singleCustomerContacts.length > 0"
      ref="dt"
      selectionMode="single"
      :value="state.singleCustomerContacts"
    >
      <Column field="id" header="Single customer" style="width: 160px">
        <template #body="slotProps">
          <Button
            class="p-button-rounded"
            :loading="state.isLoading"
            @click="selectSingleCustomer(slotProps.data)"
            >Use single customer</Button
          >
        </template>
      </Column>
      <Column field="first_name" header="First Name"></Column>
      <Column field="last_name" header="Last Name"></Column>
      <Column field="email" header="Email"></Column>
      <Column field="phone" header="Phone"></Column>
      <Column field="company_name" header="Company Name"></Column>
    </DataTable>
  </section>
</template>

<script setup>
  import { reactive, onMounted, inject, computed, defineEmits } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"

  const toast = useToast()

  const customerApi = new CustomerApi()

  const $ability = inject("$ability")
  const customerStore = useCustomerOrder()

  const props = defineProps({
    displaySearchMode: {
      type: Boolean,
      default: false
    }
  })

  const state = reactive({
    customer: {},
    originalCustomer: {},
    address: {},
    originalAddress: {},
    statesList: [],
    provinceList: [],
    isLoading: false,
    isEditing: false,
    searchType: "name",
    selectedCustomer: {},
    retrievedCustomers: [],
    customerProfile: {},
    originalCustomerProfile: {},
    delivery_address_same: false,
    searchMode: "new",
    singleCustomerContacts: []
  })

  const emit = defineEmits(["success", "selected_single_customer"])

  const selectSingleCustomer = async (data) => {
    emit("selected_single_customer", data.id)
  }

  const searchCustomer = async () => {
    state.loading = true

    if (state.searchMode == "new") {
      state.retrievedCustomers = []
      const searchUrl = constructSearchUrl()
      const { data, error } = await customerApi.customerSearch(searchUrl)
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error loading customers",
          group: "br",
          life: 5000
        })
        state.loading = false
        return
      }
      if (data.value.length === 0) {
        toast.add({
          severity: "info",
          summary: "Info",
          detail: "No customers found",
          group: "br",
          life: 5000
        })
        state.loading = false
        return
      }

      state.retrievedCustomers = data.value
        .map((dt) => {
          let order = dt.order[0]
          if (!order) {
            return null
          }
          return {
            id: dt.id,
            first_name: dt.first_name || "",
            last_name: dt.last_name || "",
            email: dt.email || "",
            phone: dt.phone || "",
            street_address: order.address?.street_address || "",
            zip: order.address?.zip || "",
            state: order.address?.state || "",
            city: order.address?.city || "",
            county: order.address?.county || "",
            order_type: order.type || ""
          }
        })
        .filter((dt) => dt !== null)
        .sort((a, b) => {
          if (a.order_type === "RENT" && b.order_type !== "RENT") {
            return -1 // a comes before b
          }
          if (a.order_type !== "RENT" && b.order_type === "RENT") {
            return 1 // b comes before a
          }
          return 0 // no change in order
        })
      state.loading = false
    } else if (state.searchMode == "existing") {
      state.singleCustomerContacts = []
      const searchUrl = constructSearchUrl()
      const { data, error } = await customerApi.singleCustomerSearch(searchUrl)
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error loading customers",
          group: "br",
          life: 5000
        })
        state.loading = false
        return
      }
      if (data.value.length === 0) {
        toast.add({
          severity: "info",
          summary: "Info",
          detail: "No customers found",
          group: "br",
          life: 5000
        })
        state.loading = false
        return
      }
      console.log(data.value)
      state.singleCustomerContacts = data.value.map((dt) => {
        return {
          id: dt.customer.id,
          first_name: dt.customer.first_name || "",
          last_name: dt.customer.last_name || "",
          email: dt.email || "",
          phone: dt.phone || "",
          company_name: dt.customer.company_name || ""
        }
      })
      state.loading = false
    }
  }

  const constructSearchUrl = () => {
    let filters = {}
    filters[state.searchType] = state.search

    const filteredNulls = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v != null)
    )

    const searchParams = new URLSearchParams(Object.entries(filteredNulls))
    return searchParams.toString()
  }

  const createCustomerProfile = async (customerOrder) => {
    state.isLoading = true
    const { error, data } = await customerApi.mergeCustomers(customerOrder)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Couldn't create customer profile",
        group: "br",
        life: 5000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Creating customer profile successfull",
        group: "br",
        life: 5000
      })

      emit("success", data.value)
    }
    state.isLoading = false
  }
</script>
