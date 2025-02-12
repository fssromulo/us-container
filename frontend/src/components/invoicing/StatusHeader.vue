<template>
  <ul
    v-if="
      !state.searchAndFilter &&
      state.quickSearchOrder.length === 0 &&
      !smAndSmaller
    "
    class="flex p-0 m-0 overflow-x-scroll list-none select-none bg-0 dark:bg-900 status-list"
  >
    <li v-for="(status, i) in statusOptions" :key="i">
      <a
        v-ripple
        class="flex items-center px-4 py-4 transition-colors duration-150 cursor-pointer border-bottom-2 hover:border-500 dark:hover:border-300 p-ripple"
        :class="{
          'border-blue-600 text-blue-600 hover:border-blue-600':
            state.selectedStatusIndex === i,
          'text-700 dark:text-100 border-transparent':
            state.selectedStatusIndex !== i,
          'text-2xl': statusOptions.length <= 9,
          'text-xl': statusOptions.length > 9
        }"
        @click="selectStatus(i)"
      >
        <span class="font-medium">{{ status.label }}</span>
      </a>
    </li>
  </ul>
  <div class="flex flex-col items-center w-full mt-4 mb-4">
    <Select
      v-if="smAndSmaller"
      class="w-4/12 m-2"
      scrollHeight="330px"
      v-model="state.selectedStatus"
      :options="statusOptions"
      :placeholder="`Select a status`"
      optionLabel="label"
      optionValue="value"
      style="width: 70vw"
    />
  </div>
</template>

<script setup>
  import { useCustomerOrder } from "@/store/modules/customerOrder"

  import { computed, reactive, watch, inject, ref, onMounted } from "vue"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import { useUsers } from "@/store/modules/users"
  import { useRouter } from "vue-router"
  import AccountApi from "../../api/account"
  import currentRouteStatus from "../../utils/routes"
  import { isRentalsVisible } from "../../utils/allowedVisibilityForFeatures"
  import cloneDeep from "lodash.clonedeep"

  const scrollableTabs = ref(
    Array.from({ length: 50 }, (_, i) => ({
      title: `Tab ${i + 1}`,
      content: `Tab ${i + 1} Content`
    }))
  )
  const $route = inject("$route")

  const usersStore = useUsers()
  const customerStore = useCustomerOrder()

  const router = useRouter()
  const accountApi = new AccountApi()

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")

  const state = reactive({
    selectedStatus: smAndSmaller ? "Invoiced" : null,
    selectedStatusIndex: 0,
    quickSearchOrder: [],
    do_not_load_by_route: false
  })

  const isRentalsFeatureVisible = computed(() => {
    let isProd = import.meta.env.PROD
    let accountId = usersStore?.cms?.account_id
    let isCMSRentalsEnabled = usersStore.cms?.feature_flags?.rentals_enabled
    let userEmail = usersStore?.currentUser?.email
    let isRentalsFeatureVisible = isRentalsVisible(
      isProd,
      accountId,
      isCMSRentalsEnabled,
      userEmail
    )

    return isRentalsFeatureVisible
  })

  const filter_hidden = (lst) => {
    return lst.filter((el) => {
      if (el.is_hidden == undefined) {
        return true
      }

      if (el.is_hidden == true) {
        return false
      }

      return true
    })
  }

  const statusOptions = computed(() => {
    if (customerStore.selectedCategory.code === "ALL") {
      const allStatusOptions = cloneDeep(
        usersStore.cms?.order_status_options.allStatusOptions
      )
      if (allStatusOptions !== undefined && !isRentalsFeatureVisible.value) {
        // Find the index of the item with the value "To Deliver"
        const toDeliverIndex = allStatusOptions.findIndex(
          (option) => option.value === "To Deliver"
        )

        // Check if "To Deliver" was found
        // if (toDeliverIndex !== -1) {
        // Replace "To Deliver" with "Paid"
        // allStatusOptions[toDeliverIndex] = { label: "Paid", value: "Paid" };
        // }
      }
      // Proceed with your logic, if you have more to do here

      return allStatusOptions
    }
    if (customerStore.selectedCategory.code === "RENT") {
      return filter_hidden(
        usersStore.cms?.order_status_options.rentalStatusOptions
      )
    } else if (customerStore.selectedCategory.code === "RENT_TO_OWN") {
      return filter_hidden(
        usersStore.cms?.order_status_options.rentToOwnStatusOptions
      )
    } else if (
      customerStore.selectedCategory.code === "PURCHASE" ||
      customerStore.selectedCategory.code === "PURCHASE_ACCESSORY"
    ) {
      return filter_hidden(
        usersStore.cms?.order_status_options.salesStatusOptions
      )
    }
    return filter_hidden(usersStore.cms?.order_status_options.allStatusOptions)
  })

  const getRouteStatus = () => {
    let v = toCapitalizedWithSpaces($route.currentRoute.value.query["status"])
    return v
  }

  const setStatusFromQueryParam = () => {
    if ($route.currentRoute.value.query.hasOwnProperty("status")) {
      let routeStatus = currentRouteStatus($route)

      state.selectedStatus = routeStatus

      if (statusOptions.value?.length) {
        for (let i = 0; i < statusOptions.value.length; i++) {
          if (
            statusOptions.value[i].value.toLowerCase() ===
            state.selectedStatus.toLowerCase()
          ) {
            state.selectedStatusIndex = i
            break
          }
        }
      } else {
      }
    }
  }

  const fetchCms = async () => {
    const { data, error } = await accountApi.getAccount()

    const cms_attributes = data.value.cms_attributes
    cms_attributes.id = data.value.id
    usersStore.setCms(cms_attributes)
  }

  onMounted(async () => {
    // This is here because statusOptions oninitial load is undefined bc not set yet. we need it set for
    // on load to work for a call other than invoice
    await fetchCms()
    state.selectedStatus = currentRouteStatus($route)
    setStatusFromQueryParam()
  })

  const currentStatus = computed(() => {
    if (!statusOptions.value) return

    const selectedStatus = statusOptions.value.find(
      (s) => s.value === state.selectedStatus
    )

    return selectedStatus || statusOptions.value[state.selectedStatusIndex]
  })

  const selectStatus = (index) => {
    state.selectedStatusIndex = index
    for (let i = 0; i < statusOptions.value.length; i++) {
      if (i == index) {
        state.selectedStatus = statusOptions[i]
        break
      }
    }
    state.customerRawLength = 0
  }

  watch(
    () => currentStatus.value,
    async (newVal, oldVal) => {
      if (!newVal) return
      router.push({
        name: "invoices",
        query: { status: newVal.value.replace(/\s/g, "_").toLowerCase() }
      })
    }
  )

  watch(
    () => $route.currentRoute.value.query.status,
    async (newVal, oldVal) => {
      if (newVal) {
        setStatusFromQueryParam()
      }
    }
  )
</script>
<style lang="scss" scoped>
  @media screen and (max-width: 1350px) {
    .status-list {
      overflow-x: scroll;
      max-width: 90vw;
    }
  }
  @media screen and (max-width: 990px) {
    .status-list {
      overflow-x: scroll;
      max-width: 95vw;
    }
  }
</style>
