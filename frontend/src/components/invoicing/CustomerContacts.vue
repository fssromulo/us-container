<template>
  <Toolbar class="mb-6">
    <template #start>
      <Button
        label="Add Contact"
        icon="pi pi-plus"
        class="ml-4 p-button-success"
        @click="clickAddContact()"
      />
    </template>
    <template #end>
      <Button
        label="Export"
        icon="pi pi-upload"
        class="p-button-help"
        @click="exportCSV($event)"
      />
    </template>
  </Toolbar>
  <DataTable
    v-if="!state.loading"
    ref="dt"
    :value="state.contacts"
    :style="`max-width: 90%`"
    scrollHeight="60vh"
    dataKey="id"
    :paginator="true"
    scrollDirection="both"
    :rows="25"
    :filters="state.filters"
    paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
    :rowsPerPageOptions="[10, 25, 50]"
    currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Drivers"
    responsiveLayout="scroll"
  >
    <Column field="id" header="Contact Id" style="width: 20px">
      <template #body="slotProps">
        <Button class="p-button-rounded" @click="clickEditCustomer()">{{
          slotProps.data.id.substring(0, 4)
        }}</Button>
      </template>
    </Column>
    <Column field="first_name" header="First Name" style="width: 80px">
      <template #body="slotProps">
        {{ slotProps.data.first_name }}
      </template>
    </Column>
    <Column field="last_name" header="Last Name" style="width: 80px">
      <template #body="slotProps">
        {{ slotProps.data.last_name }}
      </template>
    </Column>

    <Column field="email" header="Email" style="width: 80px">
      <template #body="slotProps">
        {{ slotProps.data.email }}
      </template>
    </Column>
    <Column field="full_address" header="Full Address" style="width: 80px">
      <template #body="slotProps">
        {{ slotProps.data.customer_address.full_address }}
      </template>
    </Column>
    <Column field="phone" header="Phone" style="width: 80px">
      <template #body="slotProps">
        {{ slotProps.data.phone }}
      </template>
    </Column>
    <Column field="id" header="Delete contact" style="width: 30px">
      <template #body="slotProps">
        <Button
          type="button"
          icon="pi pi-trash text-sm"
          :loading="state.loading"
          @click="deleteContacts(slotProps.data, $event)"
          class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
        ></Button>
      </template>
    </Column>
    <Column field="id" header="Resend Invoice" style="width: 30px">
      <template #body="slotProps">
        <Button
          label="Resend"
          class="text-sm p-button-secondary p-button-sm"
          :loading="state.resendLoading[slotProps.data.id] || false"
          @click="resendInvoice(slotProps.data, $event)"
        />
      </template>
    </Column>
  </DataTable>
  <Dialog
    v-model:visible="state.addCustomerContact"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ width: '50rem' }"
    header="Add Contacts"
    :modal="true"
    class="p-fluid"
  >
    <div class="flex flex-col items-center w-full">
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0"
          >First Name</label
        >
        <InputText
          placeholder="First Name"
          v-model="state.contact.first_name"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0"
          >Last Name</label
        >
        <InputText
          placeholder="Last Name"
          v-model="state.contact.last_name"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>

      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0">Email</label>
        <InputText
          placeholder="Email"
          v-model="state.contact.email"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="phone" class="font-medium text-900 dark:text-0"
          >Phone</label
        >
        <InputMask
          id="phone"
          v-model="state.contact.phone"
          class="p-component p-inputtext-fluid"
          mask="(999)-999-9999"
          placeholder="999-99-9999"
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0">City</label>
        <InputText
          placeholder="City"
          v-model="state.contact.city"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0"
          >Street Address</label
        >
        <InputText
          placeholder="Street Address"
          v-model="state.contact.street_address"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0">Zip</label>
        <InputText
          placeholder="Zip"
          v-model="state.contact.zip"
          id="cost"
          :class="{ 'p-invalid': v$.contact.zip.$invalid }"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="state" class="font-medium text-900 dark:text-0">
          {{ stateProvinceText }}</label
        ><br />
        <Select
          v-model="state.contact.state"
          :disabled="props.disableAllFields"
          :placeholder="stateProvinceText"
          class="w-full"
          :options="
            getCountry == 'Canada'
              ? stateService.getProvinces()
              : stateService.getStates()
          "
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0"
          >County</label
        >
        <InputText
          placeholder="County"
          v-model="state.contact.county"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
    </div>
    <Message v-if="state.error" class="m-5" severity="error">{{
      state.error
    }}</Message>
    <Button
      label="Add Contact"
      @click="addUserContact"
      :loading="state.loading"
      icon="pi pi-user"
      class="w-auto"
    ></Button>
  </Dialog>

  <Dialog
    v-model:visible="state.editCustomerContact"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ width: '50rem' }"
    header="Edit Contact"
    :modal="true"
    class="p-fluid"
  >
    <div class="flex flex-col items-center w-full">
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0"
          >First Name</label
        >
        <InputText
          placeholder="First Name"
          v-model="state.contact.first_name"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0"
          >Last Name</label
        >
        <InputText
          placeholder="Last Name"
          v-model="state.contact.last_name"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>

      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0">Email</label>
        <InputText
          placeholder="Email"
          v-model="state.contact.email"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="phone" class="font-medium text-900 dark:text-0"
          >Phone</label
        >
        <InputMask
          id="phone"
          v-model="state.contact.phone"
          class="p-component p-inputtext-fluid"
          mask="(999)-999-9999"
          placeholder="999-99-9999"
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0">City</label>
        <InputText
          placeholder="City"
          v-model="state.contact.city"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0"
          >Street Address</label
        >
        <InputText
          placeholder="Street Address"
          v-model="state.contact.street_address"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0">Zip</label>
        <InputText
          placeholder="Zip"
          v-model="state.contact.zip"
          :class="{ 'p-invalid': v$.contact.zip.$invalid }"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
      <div class="w-full mb-4">
        <label for="state" class="font-medium text-900 dark:text-0">
          {{ stateProvinceText }}</label
        ><br />
        <Select
          v-model="state.contact.state"
          :disabled="props.disableAllFields"
          :placeholder="stateProvinceText"
          class="w-full"
          :options="
            getCountry == 'Canada'
              ? stateService.getProvinces()
              : stateService.getStates()
          "
        />
      </div>
      <div class="w-full mb-4">
        <label for="cost" class="font-medium text-900 dark:text-0"
          >County</label
        >
        <InputText
          placeholder="County"
          v-model="state.contact.county"
          id="cost"
          class="p-component p-inputtext-fluid"
          type="text"
        />
      </div>
    </div>
    <Message v-if="state.error" class="m-5" severity="error">{{
      state.error
    }}</Message>
    <Button
      label="Edit Contact"
      @click="editUserContact"
      :loading="state.loading"
      icon="pi pi-user"
      class="w-auto"
    ></Button>
  </Dialog>
</template>

<script setup>
  import { reactive, computed, onMounted, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import CustomerApi from "@/api/customers"
  import { useUsers } from "@/store/modules/users"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import StateService from "@/service/StateService"
  import { useVuelidate } from "@vuelidate/core"
  import { helpers } from "@vuelidate/validators"
  const toast = useToast()
  const userStore = useUsers()

  const customerApi = new CustomerApi()
  const props = defineProps({
    order: {
      type: Object,
      default: {}
    },
    customerId: {
      type: String,
      default: ""
    }
  })
  const stateService = new StateService()
  const getCountry = computed(() => {
    userStore.cms?.account_country
  })
  const stateProvinceText = computed(() => {
    let account_country = getCountry.value
    return account_country && account_country == "Canada" ? "Province" : "State"
  })
  const state = reactive({
    contact: {},
    contacts: [],
    loading: false,
    resendLoading: [],
    addCustomerContact: false,
    editCustomerContact: false,
    error: null
  })

  const clickAddContact = () => {
    state.addCustomerContact = true
    initContact()
  }

  const isInUSA = computed(
    () =>
      !userStore.cms?.account_country ||
      userStore.cms?.account_country != "Canada"
  )
  const zipRegex = /^\d{5}(?:[-\s]\d{4})?$/
  const rules = computed(() => ({
    contact: {
      zip: {
        $lazy: true,
        validZip: helpers.withMessage(
          "ZIP Code must be at least 5 characters.",
          (value) => {
            if (!isInUSA.value) {
              return true
            }
            return zipRegex.test(value) //minLength(5)(value)
          }
        )
      }
    }
  }))
  const v$ = useVuelidate(rules, state)

  const dt = ref()

  const clearContact = () => {
    state.contact = {}
  }
  const initContact = () => {
    clearContact()
    state.error = null
    state.contact = {
      email: "",
      phone: "",
      first_name: "",
      last_name: "",
      customer_id: "",
      city: "",
      street_address: "",
      zip: "",
      state: "",
      county: ""
    }
  }

  const clickEditCustomer = () => {
    state.editCustomerContact = true
    setContact(slotProps.data)
  }

  const isValidContact = () => {
    state.error = null
    for (const [key, value] of Object.entries(state.contact)) {
      if (
        value === null ||
        value === undefined ||
        (typeof value === "string" && value.trim() === "")
      ) {
        console.log(`Validation failed: ${key} is invalid.`)
        state.error = "All fields are required"
        return false
      }
    }
    return true
  }

  const resendInvoice = async (_data) => {
    console.log(_data)
    state.resendLoading[_data.id] = true
    const { data, isLoading, error } = await customerApi.resendContactInvoice(
      _data.id,
      props.order.id
    )

    if (error.value) {
      state.resendLoading[_data.id] = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error resending invoice",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.resendLoading[_data.id] = false
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Invoice resent",
        group: "br",
        life: 5000
      })
    }
  }

  const setContact = (data) => {
    clearContact()
    state.error = null
    state.contact = {
      email: data.email,
      phone: data.phone,
      first_name: data.first_name,
      last_name: data.last_name,
      customer_address_id: data.customer_address.id,
      customer_id: data.customer.id,
      id: data.id,
      account_id: data.account_id,
      city: data.customer_address.city,
      street_address: data.customer_address.street_address,
      zip: data.customer_address.zip,
      state: data.customer_address.state,
      county: data.customer_address.county
    }
  }

  const deleteContacts = async (_data) => {
    state.loading = true
    const { data } = await customerApi.deleteCustomerContact(
      _data.id,
      _data.customer_address.id
    )
    await fetchContacts()
    state.loading = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Customer contact deleted",
      group: "br",
      life: 5000
    })
  }
  const addUserContact = async () => {
    state.contact["customer_id"] = props.customerId
    state.contact["account_id"] = userStore.cms?.account_id || ""
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    if (!isValidContact()) return false
    state.loading = true
    const { data } = await customerApi.addCustomerContact(state.contact)

    await fetchContacts()
    state.loading = false
    state.editCustomerContact = false
    state.addCustomerContact = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Customer contact added",
      group: "br",
      life: 5000
    })
  }

  const editUserContact = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    if (!isValidContact()) return false
    state.loading = true
    const { data } = await customerApi.editCustomerContact(state.contact)

    await fetchContacts()
    state.loading = false
    state.editCustomerContact = false
    state.addCustomerContact = false

    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Customer contact updated",
      group: "br",
      life: 5000
    })
  }

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()
  const fetchContacts = async () => {
    state.loading = true
    const { data } = await customerApi.getCustomerContact(props.customerId)
    if (data.value) {
      state.contacts = [...data.value]
    }
    state.loading = false
  }
  onMounted(async () => {
    if (state.contacts.length === 0) {
      await fetchContacts()
    }
  })

  const exportCSV = () => dt.value.exportCSV()
</script>
