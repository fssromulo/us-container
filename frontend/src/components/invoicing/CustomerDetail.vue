<template>
  <section class="flex flex-col w-full">
    <div class="flex items-center justify-between w-full">
      <p class="mt-0 mb-0 text-xl font-semibold text-900 dark:text-0">
        <span class=""> Customer Info </span>
        <Button
          class="p-button-rounded p-button-primary"
          @click="duplicate"
          v-if="$ability.can('update', 'duplicate_order_with_new_prices')"
          >Duplicate
        </Button>

        <Button
          class="p-button-rounded p-button-primary"
          @click="duplicate_original"
          v-if="$ability.can('update', 'duplicate_order')"
          >Duplicate Original
        </Button>
      </p>
      <Button
        v-if="customerStore.order.single_customer !== null"
        class="p-button-rounded p-button-primary"
        @click="unlink"
        >Unlink
      </Button>
      <Button
        v-if="customerStore.order.single_customer !== null"
        type="button"
        @click="state.viewCustomerContact = true"
        class="p-button-rounded p-button-primary"
        label="Contacts"
      ></Button>
      <Button
        type="button"
        icon="pi pi-pencil text-sm"
        @click="toggleEdit"
        class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
      ></Button>
    </div>
    <div class="col-span-12 mt-2 border border-t"></div>
    <table class="table-fixed">
      <tbody>
        <tr style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Name</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{
              state.customer
                ? state.customer.calculated_full_name
                : state.customerProfile?.calculated_full_name
            }}
          </td>
          <td v-else>
            <div
              class="grid grid-cols-12 gap-4 formgrid p-fluid"
              v-if="state.customer != null"
            >
              <div class="col-span-12 mb-4 field md:col-span-4">
                <label for="first_name" class="text-sm text-700 dark:text-100"
                  >First Name</label
                >
                <InputText
                  :disabled="!$ability.can('update', 'order_column-customer')"
                  v-model="state.customer.first_name"
                  id="first_name"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
              </div>
              <div class="col-span-12 mb-4 field md:col-span-4">
                <label for="last_name" class="text-sm text-700 dark:text-100"
                  >Last Name</label
                >
                <InputText
                  :disabled="!$ability.can('update', 'order_column-customer')"
                  v-model="state.customer.last_name"
                  id="last_name"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
              </div>
            </div>
            <div class="grid grid-cols-12 gap-4 formgrid p-fluid" v-else>
              <div class="col-span-12 mb-4 field md:col-span-4">
                <label for="first_name" class="text-sm text-700 dark:text-100"
                  >First Name</label
                >
                <InputText
                  :disabled="!$ability.can('update', 'order_column-customer')"
                  v-model="state.customerProfile.first_name"
                  id="first_name"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
              </div>
              <div class="col-span-12 mb-4 field md:col-span-4">
                <label for="last_name" class="text-sm text-700 dark:text-100"
                  >Last Name</label
                >
                <InputText
                  :disabled="!$ability.can('update', 'order_column-customer')"
                  v-model="state.customerProfile.last_name"
                  id="last_name"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
              </div>
            </div>
          </td>
        </tr>
        <tr style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Company Name</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{ computedCustomer.company_name || "" }}
          </td>
          <td v-else>
            <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
              <div class="col-span-12 mb-4 field md:col-span-4">
                <label for="first_name" class="text-sm text-700 dark:text-100"
                  >Company Name</label
                >
                <InputText
                  v-if="
                    state.customerProfile != null &&
                    Object.keys(state.customerProfile).length != 0
                  "
                  :disabled="!$ability.can('update', 'order_column-customer')"
                  v-model="state.customerProfile.company_name"
                  id="first_name"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
                <InputText
                  v-if="state.customer !== null"
                  :disabled="!$ability.can('update', 'order_column-customer')"
                  v-model="state.customer.company_name"
                  id="first_name"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
              </div>
            </div>
          </td>
        </tr>

        <tr style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Email</td>

          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{
              state.customer
                ? state.customer.email
                : state.customerProfile?.customer_contacts[0].email
            }}
          </td>
          <td v-else class="text-sm text-900 dark:text-0">
            <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
              <div class="col-span-12 mb-4 field md:col-span-6">
                <InputText
                  :disabled="!$ability.can('update', 'order_column-email')"
                  v-model="state.customer.email"
                  v-if="state.customer != null"
                  id="email"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
                <InputText
                  :disabled="!$ability.can('update', 'order_column-email')"
                  class="p-component p-inputtext-fluid"
                  v-model="state.customerProfile.customer_contacts[0].email"
                  v-else
                  id="email"
                  type="text"
                />
              </div>
            </div>
          </td>
        </tr>
        <tr style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Phone</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{
              state.customer
                ? $fp(state.customer.phone)
                : $fp(state.customerProfile?.customer_contacts[0].phone)
            }}
          </td>
          <td v-else class="text-sm text-900 dark:text-0">
            <InputMask
              v-if="state.customer != null"
              :disabled="!$ability.can('update', 'order_column-phone')"
              mask="(999) 999-9999"
              placeholder="(999) 999-9999"
              class="p-component p-inputtext-fluid"
              v-model="state.customer.phone"
              id="phone"
              type="text"
            />
            <InputMask
              v-else
              :disabled="!$ability.can('update', 'order_column-phone')"
              mask="(999) 999-9999"
              placeholder="(999) 999-9999"
              v-model="state.customerProfile.customer_contacts[0].phone"
              id="phone"
              type="text"
              class="p-component p-inputtext-fluid"
            />
          </td>
        </tr>
        <tr style="height: 2rem">
          <td class="text-xl text-700 dark:text-100"
            >Address <p v-if="cms.billing_address">(delivery address)</p></td
          >
          <td
            v-if="
              !state.isEditing &&
              $ability.can('update', 'order_column-customerAddress')
            "
            class="text-xl text-900 dark:text-0"
          >
            <span v-if="state.customer != null">{{
              state.address.full_address
            }}</span>
            <span v-else>
              {{
                state.customerProfile?.customer_contacts[0].customer_address
                  .full_address
              }}</span
            >
          </td>
          <td v-else class="text-xl text-900 dark:text-0">
            <div class="grid grid-cols-12 gap-4 mt-4 formgrid p-fluid">
              <div class="col-span-12 mb-4 field md:col-span-4">
                <label
                  for="street_address"
                  class="text-sm text-700 dark:text-100"
                  >Street address</label
                >
                <InputText
                  v-if="state.customer != null"
                  v-model="state.address.street_address"
                  id="street_address"
                  class="p-component p-inputtext-fluid"
                  type="text"
                  maxlength="60"
                />
                <InputText
                  v-else
                  v-model="
                    state.customerProfile.customer_contacts[0].customer_address
                      .street_address
                  "
                  id="street_address"
                  type="text"
                  class="p-component p-inputtext-fluid"
                  maxlength="60"
                />
              </div>
              <div class="col-span-12 mb-4 field md:col-span-3">
                <label for="city" class="text-xs text-700 dark:text-100"
                  >City</label
                >
                <InputText
                  v-if="state.customer != null"
                  :disabled="!$ability.can('update', 'order_column-city')"
                  v-model="state.address.city"
                  class="p-component p-inputtext-fluid"
                  id="city"
                  type="text"
                />
                <InputText
                  v-else
                  :disabled="!$ability.can('update', 'order_column-city')"
                  v-model="
                    state.customerProfile.customer_contacts[0].customer_address
                      .city
                  "
                  id="city"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
              </div>
              <div class="col-span-12 mb-4 field md:col-span-3">
                <label for="state" class="text-xs text-700 dark:text-100">{{
                  stateProvinceText
                }}</label>
                <Select
                  v-if="state.customer != null"
                  :disabled="!$ability.can('update', 'order_column-state')"
                  v-model="state.address.state"
                  placeholder="State"
                  class="p-component p-inputtext-fluid"
                  :options="
                    getAccountCountry == 'Canada'
                      ? state.provinceList
                      : state.statesList
                  "
                />
                <Select
                  v-else
                  :disabled="!$ability.can('update', 'order_column-state')"
                  v-model="
                    state.customerProfile.customer_contacts[0].customer_address
                      .state
                  "
                  placeholder="State"
                  class="p-component p-inputtext-fluid"
                  :options="
                    getAccountCountry == 'Canada'
                      ? state.provinceList
                      : state.statesList
                  "
                />
              </div>
              <div class="col-span-12 mb-4 field md:col-span-2">
                <label for="zip" class="text-xs text-700 dark:text-100">{{
                  postalZipText
                }}</label>
                <InputText
                  v-if="state.customer != null"
                  :disabled="!$ability.can('update', 'order_column-zip')"
                  v-model="state.address.zip"
                  class="p-component p-inputtext-fluid"
                  id="zip"
                  type="text"
                />
                <InputText
                  v-else
                  :disabled="!$ability.can('update', 'order_column-zip')"
                  v-model="
                    state.customerProfile.customer_contacts[0].customer_address
                      .zip
                  "
                  id="zip"
                  class="p-component p-inputtext-fluid"
                  type="text"
                />
              </div>
              <div class="col-span-12 mb-4 field md:col-span-2">
                <label for="county" class="text-xs text-700 dark:text-100"
                  >County</label
                >
                <InputText
                  v-if="state.customer != null"
                  :disabled="!$ability.can('update', 'order_column-county')"
                  v-model="state.address.county"
                  class="p-component p-inputtext-fluid"
                  id="county"
                  type="text"
                />
                <InputText
                  v-else
                  :disabled="!$ability.can('update', 'order_column-county')"
                  class="p-component p-inputtext-fluid"
                  v-model="
                    state.customerProfile.customer_contacts[0].customer_address
                      .county
                  "
                  id="county"
                  type="text"
                />
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="cms.billing_address">
          <td class="text-xl text-700 dark:text-100"
            >Address (billing address)</td
          >
          <td
            v-if="
              !state.isEditing &&
              $ability.can('update', 'order_column-customerAddress')
            "
            class="text-xl text-900 dark:text-0"
          >
            {{ state.billing_address?.full_address }}
          </td>
        </tr>
        <tr style="height: 2rem">
          <td class="text-xl text-700">Delivery address same?</td>
          <td v-if="!state.isEditing" class="text-xl text-900">
            {{ state.delivery_address_same ? "Yes" : "No" }}
          </td>
          <td v-if="state.isEditing" class="text-xl text-900">
            <ToggleSwitch v-model="state.delivery_address_same" type="text" />
          </td>
        </tr>
      </tbody>
    </table>
    <div class="col-span-12 mt-2 border border-t"></div>
    <div class="grid grid-cols-6 gap-2">
      <Button
        v-if="state.isEditing"
        @click="toggleEdit"
        label="Cancel"
        class="col-span-2 p-button-raised p-button-secondary"
      />
      <Button
        v-if="state.isEditing"
        @click="saveCustomer"
        :loading="state.isLoading"
        class="col-span-2 p-button-raised"
        label="Save"
      />
    </div>
    <br />
    <SingleCustomerSearch
      @success="refreshOrder"
      v-if="customerStore.order?.single_customer == null"
    />
  </section>
  <Dialog
    v-model:visible="state.duplicateDialog"
    class="w-full"
    maximizable
    @after-hide="cancel"
    closeOnEscape
    :breakpoints="{
      '2000px': '75vw',
      '1400px': '85vw',
      '1200px': '85vw',
      '992px': '85vw',
      '600px': '100vw',
      '480px': '100vw',
      '320px': '100vw'
    }"
    header="Quotes"
    :modal="true"
    :dismissableMask="true"
  >
    <GenerateQuote
      class="mt-2"
      :zip_code="state.address.zip.trim()"
      :address="state.address"
      :customer="state.customer"
      :order_type="customerStore.order.type"
      :is_pickup="isPickup"
      :dupplicationMode="true"
      :line_items="customerStore.order.line_items"
      :overridden_user_id="customerStore.order.user.id"
      @hide="hideGenerateQuote"
    />
  </Dialog>

  <Dialog
    v-model:visible="state.viewCustomerContact"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ width: '70rem' }"
    header="Customer Contacts"
    :modal="true"
    class="p-fluid"
  >
    <CustomerContacts
      :customerId="customerStore.order?.single_customer.id"
      :order="customerStore.order"
    ></CustomerContacts>
  </Dialog>
</template>

<script setup>
  import { reactive, onMounted, inject, computed } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import isEqual from "lodash.isequal"
  import CustomerService from "@/service/Customers"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import StateService from "../../service/StateService"
  import { salesStatusOptions } from "@/utils/constants"
  import { watch } from "vue"
  import { useUsers } from "@/store/modules/users"
  import { useConfirm } from "primevue/useconfirm"
  import SingleCustomerSearch from "./SingleCustomerSearch.vue"
  import GenerateQuote from "@/components/quotes/GenerateQuote.vue"
  import CustomerContacts from "./CustomerContacts.vue"

  const confirm = useConfirm()
  const stateService = new StateService()
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")

  const toast = useToast()
  const $isObjectPopulated = inject("$isObjectPopulated")
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $fp = inject("$formatPhone")
  const $ability = inject("$ability")
  const customerStore = useCustomerOrder()

  const emit = defineEmits(["updateCustomerOrder"])

  const customerService = new CustomerService()
  const customerApi = new CustomerApi()

  const userStore = useUsers()
  const $isPublic = inject("$isPublic")

  const addressFields = ["street_address", "city", "zip", "state", "county"]
  const stateProvinceText = computed(() => {
    return userStore.cms?.account_country &&
      userStore.cms?.account_country == "Canada"
      ? "Province"
      : "State"
  })
  const postalZipText = computed(() => {
    return userStore.cms?.account_country &&
      userStore.cms?.account_country == "Canada"
      ? "Postal Code"
      : "Zip"
  })

  const isPickup = computed(() => {
    return (
      customerStore.order.line_items.every(
        (i) => Number(i.shipping_revenue) === 0
      ) || customerStore.order?.is_pickup
    )
  })

  const getAccountCountry = computed(() => {
    let account_country = userStore.cms.account_country
    return account_country
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
    statusOptions: salesStatusOptions,
    searchType: "name",
    selectedCustomer: {},
    retrievedCustomers: [],
    customerProfile: {},
    originalCustomerProfile: {},
    delivery_address_same: false,
    duplicateDialog: false,
    viewCustomerContact: false
  })

  const refreshOrder = async (single_customer_id) => {
    const { error, data } = await customerApi.getOrderById(
      customerStore.order.id
    )
    customerStore.setOrder(data.value)
    resetCustomer()
  }

  const props = defineProps({
    swapCustomerOrder: {}
  })

  const unlink = async (event) => {
    confirm.require({
      target: event.currentTarget,
      message:
        "Warning: This will put original customer records back on orders",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        const { data, error } = await customerApi.unlink_single_customer(
          customerStore.order.id
        )
        if (error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Error unlinking single customer",
            group: "br",
            life: 5000
          })
          state.loading = false
          return
        } else {
          toast.add({
            severity: "sucess",
            summary: "Success",
            detail: "Customer unlinking successfull",
            group: "br",
            life: 5000
          })
          state.loading = false
          refreshOrder()
          return
        }
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Canceled",
          detail: "Customer unlinking canceled.",
          group: "br",
          life: 2000
        })
      }
    })
  }
  const computedCustomer = computed(() => {
    if (customerStore.order?.single_customer == null)
      return customerStore.order?.customer
    return customerStore.order?.single_customer
  })

  const resetCustomer = async () => {
    state.address = cloneDeep(customerStore.order?.address)
    state.originalAddress = cloneDeep(customerStore.order?.address)

    if (customerStore.order?.single_customer != null) {
      state.customer = null
      state.originalCustomer = null
    } else {
      state.customer = cloneDeep(customerStore.order?.customer)
      state.originalCustomer = cloneDeep(customerStore.order?.customer)
    }

    if (customerStore.order?.single_customer != null) {
      state.customerProfile = cloneDeep(customerStore.order?.single_customer)
      state.originalCustomerProfile = cloneDeep(
        customerStore.order?.single_customer
      )
    }
    state.delivery_address_same = customerStore.order.delivery_address_same
    state.isLoading = false
    state.isEditing = false
  }

  onMounted(() => {
    state.statesList = stateService.getStates()
    state.provinceList = stateService.getProvinces()
    state.billing_address = cloneDeep(customerStore.order?.billing_address)
    state.delivery_address_same = customerStore.order.delivery_address_same
  })

  const toggleEdit = () => {
    state.isEditing = !state.isEditing
  }

  const saveCustomer = async () => {
    if (
      isEqual(state.customer, state.originalCustomer) &&
      isEqual(state.customerProfile, state.originalCustomerProfile) &&
      isEqual(state.address, state.originalAddress) &&
      isEqual(
        state.delivery_address_same,
        customerStore.order?.delivery_address_same
      )
    ) {
      toast.add({
        severity: "warn",
        summary: "Warn",
        detail: "Customer unchanged",
        group: "br",
        life: 2000
      })
      return
    }
    state.isLoading = true
    if (
      !isEqual(
        state.delivery_address_same,
        customerStore.order?.delivery_address_same
      )
    ) {
      // Save status change
      const response = await customerApi.updateOrder(customerStore.order.id, {
        delivery_address_same: state.delivery_address_same
      })
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Deliver address updated",
        group: "br",
        life: 2000
      })
      props.swapCustomerOrder(response.data.value.id)
      state.isLoading = false
    }
    state.isLoading = true
    if (state.customer != null) {
      const requsetData = $removeUnusedProps(
        state.customer,
        state.originalCustomer
      )

      const addressRequest = $removeUnusedProps(
        state.address,
        state.originalAddress
      )

      if (requsetData.phone) {
        requsetData.phone = requsetData.phone.replace(/\D/g, "")
      }

      if (addressRequest && Object.keys(addressRequest).length > 0) {
        const { data } = await customerApi.updateAddress(
          customerStore.order.address.id,
          customerStore.order.id,
          addressRequest
        )
      }

      requsetData.email = state.customer.email
      customerApi
        .updateCustomer(state.customer.id, requsetData)
        .then(async (response) => {
          customerStore.setOrder(response.data.value)
          toast.add({
            severity: "success",
            summary: "Success",
            detail: "Customer updated",
            group: "br",
            life: 2000
          })
          props.swapCustomerOrder(response.data.value.id)
        })
    } else {
      const requsetData = $removeUnusedProps(
        state.customerProfile,
        state.originalCustomerProfile
      )

      let customerContacts = null
      if (requsetData.customer_contacts != null) {
        customerContacts = requsetData.customer_contacts
      }

      if (customerContacts !== null) {
        customerContacts[0].customer_address_id =
          customerContacts[0].customer_address.id
        customerContacts[0].customer_id = state.customerProfile.id
        customerApi.updateCustomerContacts(
          customerContacts[0].id,
          customerContacts[0]
        )
      }

      let customer_address = null
      if (requsetData.customer_contacts != null) {
        customer_address = customerContacts[0].customer_address
        customerApi.updateCustomerAddress(customer_address.id, customer_address)
      }

      if (customerContacts != null) {
        delete requsetData.customer_contacts
      }

      if (requsetData.phone) {
        requsetData.phone = requsetData.phone.replace(/\D/g, "")
      }

      customerApi
        .updateCustomerProfile(state.customerProfile.id, requsetData)
        .then(async (response) => {
          customerStore.setOrder(response.data.value)
          toast.add({
            severity: "success",
            summary: "Success",
            detail: "Customer updated",
            group: "br",
            life: 2000
          })
          props.swapCustomerOrder(response.data.value.id)
        })
      state.isLoading = false
    }
  }

  watch(
    () => customerStore.order,
    () => {
      resetCustomer()
    },
    { deep: true, immediate: true }
  )

  const cms = computed(() => {
    if ($isPublic) return customerStore.publicCms
    return userStore?.cms
  })

  const duplicate = () => {
    state.duplicateDialog = true
  }

  const hideGenerateQuote = () => {
    state.duplicateDialog = false
  }

  const duplicate_original = async () => {
    const { data, error } = await customerApi.duplicateOrder(
      customerStore.order.id
    )

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed duplicating order.",
        group: "br",
        life: 5000
      })
      return
    } else {
      toast.add({
        severity: "sucess",
        summary: "Success",
        detail: "Order duplicated successfully.",
        group: "br",
        life: 5000
      })
      return
    }
  }
</script>
