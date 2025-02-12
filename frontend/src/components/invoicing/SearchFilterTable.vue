<template>
  <Accordion value="0" class="mb-8">
    <AccordionPanel value="0">
      <AccordionHeader>Search & Filters</AccordionHeader>
      <AccordionContent>
        <div class="grid grid-cols-12 col-span-12 gap-4">
          <div class="col-span-12 md:col-span-3">
            <span class="ml-4 p-input-icon-left">
              <IconField>
                <InputIcon class="pi pi-search" />
                <InputText
                  style="min-width: 20em"
                  v-model="state.mainSearch"
                  placeholder="Main search"
                  class="py-2 pl-8 ml-4 rounded-lg"
                />
              </IconField>
            </span>
          </div>
          <div
            class="col-span-12 mt-2 md:col-span-2"
            :class="smAndSmaller ? 'w-full' : ''"
          >
            <Button
              @click="search"
              :loading="state.loading"
              :disabled="!canRunSearch"
              icon="pi pi-search"
              label="Search & Filter"
            ></Button>
          </div>
          <div
            class="col-span-12 mt-2 md:col-span-2"
            :class="smAndSmaller ? 'w-full' : ''"
          >
            <Button
              @click="resetSearch"
              icon="pi pi-refresh"
              class="p-button-help"
              label="Reset"
            ></Button>
          </div>
          <div class="col-span-12 mt-4 md:col-span-5" v-if="hasErrors">
            <Message
              v-for="(message, index) in allErrors"
              :key="index"
              severity="error"
              >{{ message }}</Message
            >
          </div>
        </div>
        <div class="col-span-4" v-if="!hasErrors">
          <Message>Note Fields that starts with (*) are all required </Message>
        </div>
        <div class="col-span-12">
          <p class="text-2xl">Search criteria</p>
          <div :key="i" v-for="(filter, i) in searchFilters">
            <FilterGroup
              :title="filter.title"
              :defaultSelected="0"
              :checkBoxes="filter.options"
              :reset="state.reset"
            />
          </div>
          <hr />
        </div>
        <div class="col-span-12">
          <div class="flex flex-wrap gap-4">
            <div class="col-span-12">
              <strong> Product Type</strong>
            </div>
            <div class="col-span-12">
              <SelectButton
                class="p-12 ml-2"
                v-model="state.productType"
                :options="state.productTypes"
                optionLabel="label"
                optionValue="value"
              />
            </div>
          </div>
        </div>
        <div class="col-span-12">
          <p class="text-2xl">Filters</p>
        </div>
        <div class="grid grid-cols-12 col-span-12 gap-4">
          <div
            class="col-span-12 xs:col-10 md:col-span-4 xl:col-span-4"
            :key="i"
            v-for="(filter, i) in state.filterValues"
          >
            <FilterGroup
              v-if="!filter.isMultiSelect"
              :title="filter.title"
              :isrequired="filter.isRequired || false"
              :checkBoxes="filter.options"
              :reset="state.reset"
            />
            <FilterMultiGroup
              v-if="filter.isMultiSelect && filter.key == 'date_types'"
              :title="filter.title"
              :isrequired="filter.isRequired || false"
              :checkBoxes="filter.options"
              :reset="state.reset"
            />
            <MultiSelect
              v-if="filter.key === 'statuses'"
              v-model="usersStore.orderFilters.statuses"
              :options="filter.options"
              optionLabel="label"
              placeholder="* Select Status"
              style="width: 15em"
            />
            <MultiSelect
              v-if="filter.key === 'regions'"
              filter
              v-model="usersStore.orderFilters.regions"
              :options="filter.options"
              optionLabel="label"
              placeholder="Regions"
              style="width: 15em"
            />
            <MultiSelect
              v-if="filter.key === 'pickup_regions'"
              filter
              v-model="usersStore.orderFilters.pickup_regions"
              :options="filter.options"
              optionLabel="label"
              placeholder="Pickup Regions"
              style="width: 15em"
            />
            <MultiSelect
              v-if="filter.key === 'users'"
              @click="checkUsers"
              filter
              v-model="usersStore.orderFilters.searched_user_ids"
              :options="mappedUsers"
              optionLabel="label"
              placeholder="Select Agent"
              style="width: 15em"
              :loading="usersStore.users.length === 0"
            />
            <MultiSelect
              v-if="filter.key === 'order_types'"
              v-model="usersStore.orderFilters.order_types"
              :options="filter.options"
              optionLabel="label"
              placeholder="Select Order Type"
              style="width: 15em"
            />
            <MultiSelect
              v-if="filter.key === 'container_sizes'"
              v-model="usersStore.orderFilters.container_sizes"
              :options="filter.options"
              optionLabel="label"
              placeholder="Select Container Size"
              style="width: 15em"
            />
            <MultiSelect
              v-if="filter.key === 'container_types'"
              v-model="usersStore.orderFilters.container_types"
              :options="filter.options"
              optionLabel="label"
              optionValue="value"
              placeholder="Select Container Type"
              style="width: 15em"
            />
            <MultiSelect
              v-if="filter.key === 'location'"
              v-model="usersStore.orderFilters.location"
              :options="mappedCities"
              optionLabel="label"
              optionValue="value"
              placeholder="Select City"
              style="width: 15em"
            />
            <MultiSelect
              v-if="filter.key === 'good_to_go'"
              v-model="usersStore.orderFilters.good_to_go"
              :options="filter.options"
              optionLabel="label"
              optionValue="value"
              placeholder="Good to Go"
              style="width: 15em"
            />
            <MultiSelect
              v-if="filter.key === 'welcome_call'"
              v-model="usersStore.orderFilters.welcome_call"
              :options="filter.options"
              optionLabel="label"
              optionValue="value"
              placeholder="Welcome Call"
              style="width: 15em"
            />
          </div>
        </div>
        <div class="col-span-12 field xs:col-10 md:col-span-4 xl:col-span-4">
          <label for="range">* Select date range</label>
          <DatePicker
            class="ml-4"
            inputId="range"
            v-model="usersStore.orderFilters.dateRange"
            selectionMode="range"
            :manualInput="false"
          />
        </div>
      </AccordionContent>
    </AccordionPanel>
  </Accordion>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, ref, watch } from "vue"

  import CustomerService from "@/service/Customers"
  import CustomerApi from "@/api/customers"

  import LineItemsService from "@/service/LineItem"
  import UsersService from "@/service/User"
  import UserApi from "@/api/user"
  import { FilterMatchMode } from "@primevue/core/api"

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useDrivers } from "@/store/modules/drivers"
  import { useUsers } from "@/store/modules/users"
  import { useContainerPrices } from "@/store/modules/pricing"

  import FilterGroup from "./FilterGroup.vue"
  import FilterMultiGroup from "./FilterMultiGroup.vue"

  import { filterValues, searchFilters } from "@/utils/constants"
  import { useAuth0 } from "@auth0/auth0-vue"
  import cloneDeep from "lodash.clonedeep"
  import { useToast } from "primevue/usetoast"
  import {
    originalOrderFilters,
    selectedSearchCriteriaOriginal
  } from "../../utils/constants"

  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import { useCustomerOrderFull } from "@/store/modules/customerOrderFull"

  const breakpoints = useBreakpoints(breakpointsTailwind)

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")

  const toast = useToast()
  const driverStore = useDrivers()
  const pricingStore = useContainerPrices()
  const usersStore = useUsers()
  const usersService = new UsersService()
  const userApi = new UserApi()
  const customersStore = useCustomerOrder()
  const customerService = new CustomerService()
  const customerApi = new CustomerApi()
  const customerStoreMergedOrders = useCustomerOrderFull()
  const $ability = inject("$ability")

  const { user } = useAuth0()
  const authUser = user

  const $DateTime = inject("$DateTime")
  const hasErrors = ref(false)
  const allErrors = ref([])
  const mappedUsers = computed(() => {
    return usersStore.users
      .filter((u) => {
        if (usersStore.currentUser.permissions.includes("read:all_orders")) {
          return true
        } else {
          return (
            usersStore.currentUser.team_lead
              .map((u) => u.team_member.id)
              .includes(u.id) ||
            usersStore.currentUser.manager
              .map((u) => u.assistant.id)
              .includes(u.id)
          )
        }
      })
      .map((user) => {
        return {
          label: user.full_name,
          value: user.id
        }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const driversList = computed(() => {
    return driverStore.drivers.map((d) => {
      return { label: d.company_name, value: d.id }
    })
  })

  const mappedCities = computed(() => {
    return pricingStore.locations
      .map((d) => {
        return { label: d.city, value: d.city }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const resetSearch = () => {
    state.mainSearch = ""
    usersStore.setOrderFilters(cloneDeep(originalOrderFilters))
    usersStore.setSelectedSearchCriteria(
      cloneDeep(selectedSearchCriteriaOriginal)
    )
    // force prop change
    state.reset = true
    setTimeout(() => {
      state.reset = false
    }, 100)
    state.reset = true
  }
  const onlyPaidStatusSelected = (filter) => {
    return filter.statuses.length == 1 && filter.statuses[0] == "Paid"
  }
  const canRunSearch = computed(() => {
    return true
    if (quickFiltersSelected.value) {
      return state.mainSearch.length > 0
    }
    return otherFiltersSelected.value ? true : false
  })

  const validateFilters = (filter) => {
    let errors = []
    if (filter.statuses.length == 0) {
      hasErrors.value = true
      errors.push(
        "Consider selecting an order status as larger searches will sometimes not return data."
      )
    }
    if (!onlyPaidStatusSelected(filter)) {
      if (!filter.start_date || !filter.end_date) {
        hasErrors.value = true
        errors.push(
          "Consider refining your searches to two week periods as larger searches will sometimes not return data."
        )
      } else {
        if (filter.created_at || filter.paid_at) {
          // date range can be a month
          const date1 = $DateTime.fromJSDate(filter.dateRange[0])
          const date2 = $DateTime.fromJSDate(filter.dateRange[1])
          if (date2.diff(date1, ["month"]).values.months > 1) {
            hasErrors.value = true
            errors.push(
              "Consider refining your searches to one month periods as larger searches will sometimes not return data."
            )
          }
        } else if (filter.delivered_at || filter.completed_at) {
          // date range has to be less than 2 weeks
          const date1 = $DateTime.fromJSDate(filter.dateRange[0])
          const date2 = $DateTime.fromJSDate(filter.dateRange[1])
          if (date2.diff(date1, ["days"]).values.days > 14) {
            hasErrors.value = true
            errors.push(
              "Consider refining your searches to two week periods as larger searches will sometimes not return data."
            )
          }
        }
      }
    }

    allErrors.value = errors
  }

  const quickFiltersSelected = computed(() => {
    return usersStore.selectedSearchCriteria.display_order_id ||
      usersStore.selectedSearchCriteria.customer_phone ||
      usersStore.selectedSearchCriteria.customer_email ||
      usersStore.selectedSearchCriteria.customer_name ||
      usersStore.selectedSearchCriteria.container_number ||
      usersStore.selectedSearchCriteria.container_release_number
      ? true
      : false
  })
  const returnFilterValues = (filter) => {
    return filter.map((s) => s.value)
  }
  const otherFiltersSelected = computed(() => {
    let filters = currentFilters.value
    return returnFilterValues(filters.statuses).length > 0 ||
      returnFilterValues(filters.order_types).length > 0 ||
      returnFilterValues(filters.container_sizes).length > 0 ||
      returnFilterValues(filters.searched_user_ids).length > 0 ||
      returnFilterValues(filters.regions).length > 0
      ? true
      : false || returnFilterValues(filters.pickup_regions).length > 0
      ? true
      : false
  })
  const canRunValidation = computed(() => {
    return usersStore.currentUser.account_id == 1 && !quickFiltersSelected.value
  })
  const currentFilters = computed(() => {
    return cloneDeep(usersStore.orderFilters)
  })

  const constructSearchUrl = () => {
    let filters = currentFilters.value
    const statuses = filters.statuses.map((s) => s?.value || "")
    const order_types = filters.order_types.map((s) => s?.value || "")
    const container_sizes = filters.container_sizes.map((s) => s?.value || "")
    const userIds = filters.searched_user_ids.map((s) => s?.value || "")
    const regions = filters.regions.map((s) => s?.value || "")
    const pickup_regions = filters.pickup_regions.map((s) => s?.value || "")
    if (statuses.length > 0) {
      filters.statuses = statuses
    }
    if (order_types.length > 0) {
      filters.order_types = order_types
    }
    if (container_sizes.length > 0) {
      filters.container_sizes = container_sizes
    }
    filters.container_condition = null
    if (filters.used) {
      filters.container_condition = "Used"
    }
    if (filters.one_trip) {
      filters.container_condition = "One-Trip"
    }

    if (userIds.length > 0) {
      filters.searched_user_ids = userIds
    }
    if (regions.length > 0) {
      filters.regions = regions
    }

    if (pickup_regions.length > 0) {
      filters.pickup_regions = pickup_regions
    }

    if (state.mainSearch) {
      if (usersStore.selectedSearchCriteria.display_order_id) {
        filters.display_order_id = state.mainSearch
      }
      if (usersStore.selectedSearchCriteria.customer_phone) {
        filters.customer_phone = state.mainSearch
      }
      if (usersStore.selectedSearchCriteria.customer_email) {
        filters.customer_email = state.mainSearch
      }
      if (usersStore.selectedSearchCriteria.customer_name) {
        filters.customer_name = state.mainSearch
      }
      if (usersStore.selectedSearchCriteria.container_number) {
        filters.container_number = state.mainSearch
      }
      if (usersStore.selectedSearchCriteria.container_release_number) {
        filters.container_release_number = state.mainSearch
      }

      if (usersStore.selectedSearchCriteria.tracking_number) {
        filters.tracking_number = state.mainSearch
      }

      if (usersStore.selectedSearchCriteria.customer_company_name) {
        filters.customer_company_name = state.mainSearch
      }
    }
    if (filters.dateRange) {
      filters.start_date = $DateTime
        .fromJSDate(filters.dateRange[0])
        .toFormat("M/d/yy")
      filters.end_date = $DateTime
        .fromJSDate(filters.dateRange[1])
        .toFormat("M/d/yy")
    }
    filters.product_type = state.productType
    // validateFilters(filters);
    const filteredNulls = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v != null)
    )
    const searchParams = new URLSearchParams(Object.entries(filteredNulls))
    return searchParams.toString()
  }

  const search = async () => {
    hasErrors.value = false
    allErrors.value = []

    state.loading = true
    const searchUrl = constructSearchUrl()
    if (!hasErrors.value) {
      const { data, error } = await customerApi.searchCustomers(
        searchUrl,
        usersStore.isEmulating ? usersStore.currentUser.id : null
      )
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
      customersStore.setSearchedOrders([])
      customerStoreMergedOrders.mergeOrders(data.value)
      customerStoreMergedOrders.setDisplayOrderIds(
        data.value.map((o) => {
          return o.display_order_id
        })
      )
      const searchedOrders = data.value
      customersStore.setSearchedOrders(searchedOrders)
    }
    state.loading = false
  }

  const checkUsers = async () => {
    if (usersStore.users.length === 0) {
      const { data } = await userApi.getUsers()
      usersStore.setUsers(data.value.map((u) => usersService.dtoUser(u)))
    }
  }

  const state = reactive({
    mainSearch: "",
    filterValues: cloneDeep(filterValues),
    customers: [],
    loading: false,
    filters: {},
    productType: "ALL",
    productTypes: [
      { label: "All", value: "ALL" },
      { label: "Container Sales", value: "SHIPPING_CONTAINER" }
    ]
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }
  initFilters()

  const dt = ref()

  // const loadDriversList = async (currentCol) => {
  //   if (driverStore.drivers.value.length === 0 && currentCol.includes("driver")) {
  //     const { data } = await driversService.getDrivers();
  //     driverStore.setDrivers(data.value);
  //   }
  // };

  onMounted(async () => {
    await checkUsers()
    if ($ability.can("view", "accessories"))
      state.productTypes.push({
        label: "Accessory Sales",
        value: "CONTAINER_ACCESSORY"
      })

    if (usersStore.cms?.feature_flags?.rto_enabled == false) {
      filterValues.forEach((element) => {
        if (element.key == "order_types") {
          element.options = element.options.filter(
            (option) => option.value !== "RENT_TO_OWN"
          )
          console.log(element.options)
        }
      })
    }
  })
  watch(
    () => state.productType,
    async (newVal, oldVal) => {
      if (state.productType == "" || state.productType == null)
        state.productType = "ALL"
    }
  )
</script>

<style lang="scss" scoped></style>
