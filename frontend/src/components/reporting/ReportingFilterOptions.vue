<template>
  <ConfirmPopup group="download_options">
    <template #message="slotProps">
      <div
        class="flex flex-col items-center w-full gap-4 p-4 pb-0 mb-4 border border-b"
      >
        <i
          :class="slotProps.message.icon"
          class="text-6xl text-primary-500"
        ></i>
        <p>Please select an option</p>
      </div>
    </template>
  </ConfirmPopup>
  <div class="col-span-12 field xs:col-10 md:col-span-12 xl:col-span-12">
    <label
      class="col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      for="conditions"
      v-if="
        $ability.can('view', 'account_switcher') && props.displaySelectAcount
      "
    >
      Select account
    </label>
    <Select
      v-model="state.selectedAccount"
      placeholder="Select account"
      :options="state.accounts"
      :disabled="true"
      optionLabel="name"
      optionValue="code"
      class="col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      v-if="props.displaySelectAcount"
    />
    <label class="add-margin" for="range"> Select date range</label>
    <DatePicker class="add-margin" v-model="dates" selectionMode="range" />

    <label
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      for="conditions"
      v-if="props.displayCondition"
    >
      Select condition</label
    >
    <MultiSelect
      v-if="props.displayCondition"
      @change="handleChangeConditions"
      v-model="state.selectedConditions"
      :options="state.conditionOptions"
      optionLabel="name"
      placeholder="Select Condition"
      class="w-full md:w-80 add-margin"
    />

    <label
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      for="product_type"
      v-if="props.displayProductType"
    >
      Select product type</label
    >
    <MultiSelect
      @change="handleChangeProductType"
      v-if="props.displayProductType"
      v-model="state.selectedProductTypes"
      :options="state.productTypes"
      optionLabel="name"
      placeholder="Select Product Type"
      class="w-full md:w-80 add-margin"
    />

    <label
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      for="product_type"
      v-if="props.displayOrderStatus"
    >
      Select status</label
    >
    <MultiSelect
      @change="handleChangeStatus"
      v-if="props.displayOrderStatus"
      v-model="state.selectedStatuses"
      :options="state.statusesOptions"
      optionLabel="name"
      placeholder="Select Status"
      class="w-full md:w-80 add-margin"
    />

    <label
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      for="product_type"
      v-if="props.displaySelectVendor"
    >
      Select vendor</label
    >
    <MultiSelect
      @change="handleChangeVendor"
      v-if="props.displaySelectVendor"
      v-model="state.selectedVendors"
      :options="state.vendorOptions"
      optionLabel="name"
      placeholder="Select Vendor"
      class="w-full md:w-80 add-margin"
    />

    <label
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      for="product_type"
      v-if="props.displayStates"
    >
      Select state</label
    >
    <MultiSelect
      @change="handleChangeState"
      v-if="props.displayStates"
      v-model="state.selectedStates"
      :options="state.statesOptions"
      optionLabel="name"
      placeholder="Select State"
      class="w-full md:w-80 add-margin"
    />

    <label
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      for="purchase_type"
      v-if="props.displayPurchaseType"
    >
      Select purchase type</label
    >

    <Select
      v-model="state.selectedPurchaseType"
      placeholder="Select purchase type"
      :options="state.purchaseTypes"
      optionLabel="name"
      optionValue="code"
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      v-if="props.displayPurchaseType"
    />

    <MultiSelect
      v-model="state.selectedOrderTypeFilter"
      placeholder="Select purchase type"
      :options="state.secondaryOrderTypeFilterOptions"
      optionLabel="name"
      optionValue="code"
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      v-if="props.displayPurchaseTypeFull"
    />

    <Select
      v-model="state.managers"
      placeholder="Select mode"
      :options="state.managers_options"
      optionLabel="name"
      optionValue="code"
      class="add-margin col-6 sm:col-6 md:col-2 lg:col-2 xl:col-2"
      v-if="props.displayManagers"
    />
    <div class="flex flex-wrap gap-2 mt-3 col-12 justify-content-start">
      <Button
        @click="runReport"
        :loading="state.isLoading"
        :disabled="disableButton"
        class="ml-4 mr-8 p-button-raised"
        label="Get Report"
      >
      </Button>

      <Button
        v-if="
          props.displayExportButton &&
          props.exportButton &&
          props.exportTypes.length == 0 &&
          !smAndSmaller
        "
        @click="exportData($event, '', 'general_export')"
        class="ml-4 mr-8 p-button-raised"
        label="Export"
      >
      </Button>

      <Button
        @click="clearReports"
        :loading="state.isLoading"
        class="ml-4 mr-8 p-button-raised"
        label="Clear cache"
      >
      </Button>

      <Button
        v-for="(exportType, index) in props.exportTypes"
        :key="index"
        @click="exportData($event, exportType.value, exportType.id)"
        class="p-button-raised"
        :label="exportType.name"
        v-if="props.displayExportButton"
      >
      </Button>
    </div>
    <br />
    <br />
    <p v-if="state.created_at">
      Ran on: {{ state.created_at }}, for
      {{ dfc_without_zone(state.startDate) }} -
      {{ dfc_without_zone(state.endDate) }} by {{ state.ran_by }}, params
      entered
      {{ filtersList }}
    </p>
  </div>
</template>

<script setup>
  import { reactive, watch, onMounted, computed, ref, inject } from "vue"
  import ReportsApi from "@/api/reports"
  import StateService from "@/service/StateService.js"
  import { ABILITY_TOKEN } from "@casl/vue"
  import { useToast } from "primevue/usetoast"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import {
    dfl,
    dfc,
    dfa,
    dfc_without_zone,
    convertDateForPostRealDate
  } from "@/service/DateFormat.js"
  import { useConfirm } from "primevue/useconfirm"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"

  const usersStore = useUsers()

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")
  const useLoadingStateStore = loadingStateStore()
  const confirm = useConfirm()
  const toast = useToast()
  const stateService = new StateService()
  const reportsApi = new ReportsApi()
  const emit = defineEmits(["changedFilters", "exportData"])
  const props = defineProps({
    exportTypes: {
      type: Array,
      default: []
    },
    displayCondition: {
      type: Boolean,
      default: true
    },
    notesReport: {
      type: Boolean,
      default: false
    },
    displayProductType: {
      type: Boolean,
      default: true
    },
    displayOrderStatus: {
      type: Boolean,
      default: false
    },
    displayStates: {
      type: Boolean,
      default: false
    },
    displaySelectVendor: {
      type: Boolean,
      default: false
    },
    report_name: {
      type: String,
      default: ""
    },
    clear_report_names: {
      type: Array,
      default: []
    },
    displaySelectAcount: {
      type: Boolean,
      default: true
    },
    exportButton: {
      type: Boolean,
      default: true
    },
    displayPurchaseType: {
      type: Boolean,
      default: false
    },
    onlyDates: {
      type: Boolean,
      default: false
    },
    displayManagers: {
      type: Boolean,
      default: false
    },
    displayExportButton: {
      type: Boolean,
      default: true
    },
    displayPurchaseTypeFull: {
      type: Boolean,
      default: false
    }
  })

  const dates = ref()

  const $ability = inject(ABILITY_TOKEN)

  const disableButton = computed(() => {
    if (props.notesReport) {
      return false
    }

    if (props.displayStates && state.selectedStates == false) {
      return true
    }

    if (props.displayOrderStatus && state.selectedStatuses == false) {
      return true
    }

    if (props.displayProductType && state.selectedProductTypes == false) {
      return true
    }

    if (props.displayCondition && state.selectedConditions == false) {
      return true
    }

    if (props.displaySelectVendor && state.selectedVendors == false) {
      return true
    }

    if (state.startDate == null || state.endDate == null) {
      return true
    }

    if (
      state.selectedAccount == null &&
      $ability.can("view", "account_switcher")
    ) {
      return true
    }

    if (
      props.displayPurchaseType &&
      state.selectedPurchaseType.code == "Purchase"
    ) {
      return true
    }

    if (props.onlyDates) {
      return false
    }

    return false
  })

  const filtersList = computed((el) => {
    const filters_list = []
    if (props.displayStates) {
      filters_list.push("states")
    }

    if (props.displayOrderStatus) {
      filters_list.push("statuses")
    }

    if (props.displayProductType) {
      filters_list.push("product types")
    }

    if (props.displayCondition && state.selectedConditions == false) {
      filters_list.push("conditions")
    }

    filters_list.push("begin_date")
    filters_list.push("end_date")

    if ($ability.can("view", "account_switcher")) {
      filters_list.push("account_id")
    }

    if (props.displayPurchaseType) {
      filters_list.push("purchase_type")
    }

    return filters_list.join(", ")
  })

  const state = reactive({
    startDate: null,
    endDate: null,
    selectedConditions: [],
    selectedProductTypes: [],
    conditionOptions: [
      { name: "One trip", code: "One-Trip" },
      { name: "Used", code: "Used" }
    ],
    productTypes: [],
    container_sales: [],
    selectedStatuses: [],
    statusesWithoutALl: [
      { name: "Invoiced", code: "Invoiced" },
      { name: "Paid", code: "Paid" },
      { name: "Partially Paid", code: "Partially Paid" },
      { name: "Delayed", code: "Delayed" },
      { name: "Delivered", code: "Delivered" },
      { name: "Expired", code: "Expired" },
      { name: "Cancelled", code: "Cancelled" },
      { name: "Completed", code: "Completed" },
      { name: "Driver Paid", code: "Driver Paid" }
    ],
    statusesOptions: [
      { name: "All", code: "All" },
      { name: "Invoiced", code: "Invoiced" },
      { name: "Paid", code: "Paid" },
      { name: "Partially Paid", code: "Partially Paid" },
      { name: "Delayed", code: "Delayed" },
      { name: "Delivered", code: "Delivered" },
      { name: "Expired", code: "Expired" },
      { name: "Cancelled", code: "Cancelled" },
      { name: "Completed", code: "Completed" },
      { name: "Driver Paid", code: "Driver Paid" }
    ],
    accounts: [
      { name: "USA Containers", code: 1 },
      { name: "A Mobile Box", code: 2 },
      { name: "Container America", code: 4 }
    ],
    purchaseTypes: [
      { name: "Purchase", code: "PURCHASE" },
      { name: "Rent", code: "RENT" }
    ],
    secondaryOrderTypeFilterOptions: [
      { name: "Purchase", code: "PURCHASE" },
      { name: "Rent", code: "RENT" },
      { name: "Rent to own", code: "RENT_TO_OWN" },
      { name: "All", code: "ALL" },
      { name: "Accessories", code: "ACCESSORIES" }
    ],
    selectedAccount: { name: "USA Containers", code: 1 },
    selectedPurchaseType: { name: "Purchase", code: "Purchase" },
    selectedOrderTypeFilter: ["PURCHASE", "RENT", "RENT_TO_OWN"],
    selectedStates: [],
    selectedVendors: [],
    statesOptions: [],
    isLoading: false,
    created_at: null,
    ran_by: null,
    managers: "Everyone",
    managers_options: [
      { name: "Managers", code: "Managers" },
      { name: "Everyone", code: "Everyone" }
    ]
  })

  const exportData = async (event, type = "", id = "") => {
    if (id == "" || id == null) {
      let title =
        "[INSERT_REPORT_TITLE] - Run by " +
        state.ran_by +
        " for " +
        dfc(state.startDate) +
        " - " +
        dfc(state.endDate) +
        " on " +
        dfc(new Date(state.created_at).toISOString()) +
        ".csv"
      emit("exportData", { type: type, title: title, option: "CSV", id: id })
    } else {
      confirm.require({
        target: event.currentTarget,
        group: "download_options",
        message: "Please select an option.",
        icon: "pi pi-exclamation-circle",
        acceptIcon: "pi pi-check",
        rejectIcon: "pi pi-times",
        acceptLabel: "Download CSV",
        rejectLabel: "Download PDF",
        rejectClass: "p-button-outlined p-button-sm",
        acceptClass: "p-button-sm",
        accept: () => {
          let title =
            "[INSERT_REPORT_TITLE] - Run by " +
            state.ran_by +
            " for " +
            dfc(state.startDate) +
            " - " +
            dfc(state.endDate) +
            " on " +
            dfc(new Date(state.created_at).toISOString()) +
            ".csv"
          emit("exportData", {
            type: type,
            title: title,
            option: "CSV",
            id: id
          })
        },
        reject: () => {
          let title =
            "[INSERT_REPORT_TITLE] - Run by " +
            state.ran_by +
            " for " +
            dfc(state.startDate) +
            " - " +
            dfc(state.endDate) +
            " on " +
            dfc(new Date(state.created_at).toISOString()) +
            ".pdf"
          emit("exportData", {
            type: type,
            title: title,
            option: "PDF",
            id: id
          })
        }
      })
    }
  }

  const clearReports = async () => {
    state.isLoading = true
    props.clear_report_names.forEach(async (el) => {
      const { data, error } = await reportsApi.clearReports(
        el,
        state.selectedAccount
      )

      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error clearing cahce",
          group: "br",
          life: 5000
        })
      } else {
        toast.add({
          severity: "success",
          summary: "Cache cleared",
          detail: "Successfully cleared cache",
          group: "br",
          life: 5000
        })
      }
    })
    state.isLoading = false
  }

  const runReport = async () => {
    state.isLoading = true
    useLoadingStateStore.setIsLoading(true)

    let states = []
    if (state.selectedStates.some((obj) => obj.code === "All")) {
      states = ["All"]
    } else {
      states = state.selectedStates.map((el) => {
        return el.code
      })
    }

    let productTypes = []
    if (state.selectedProductTypes.some((obj) => obj.code === "All")) {
      productTypes = ["All"]
    } else {
      productTypes = state.selectedProductTypes.map((el) => {
        return el.code
      })
    }

    let statuses = []
    if (state.selectedStatuses.some((obj) => obj.code === "All")) {
      statuses = state.statusesWithoutALl.map((el) => {
        return el.code
      })
    } else {
      statuses = state.selectedStatuses.map((el) => {
        return el.code
      })
    }

    emit("runReport", {
      account_id: state.selectedAccount || 1,
      begin_date: state.startDate,
      end_date: state.endDate,
      states: states,
      statuses: statuses,
      productTypes: productTypes,
      purchaseType: state.selectedPurchaseType,
      selectedOrderTypeFilter: state.selectedOrderTypeFilter,
      conditions: state.selectedConditions.map((el) => {
        return el.code
      }),
      vendors: state.selectedVendors.map((el) => {
        return el.code
      }),
      manager: state.managers == "Everyone" ? false : true
    })

    toast.add({
      severity: "success",
      summary: "Success",
      detail: `Started running ${props.report_name}`,
      life: 3000,
      group: "br"
    })

    const currentTimeInMillis = Date.now()
    const currentDate = new Date(currentTimeInMillis).toISOString()
    state.created_at = dfl(currentDate)

    state.ran_by = usersStore.currentUser.full_name
  }

  onMounted(async () => {
    const result = await reportsApi.getProductTypes({})
    state.productTypesWithoutAll = result.data.value.map((el) => {
      return { name: el["Result"], code: el["Result"] }
    })
    state.productTypes = [
      ...[{ name: "All", code: "All" }],
      ...state.productTypesWithoutAll
    ]

    state.statesOptionsWithoutAll = stateService.getStates().map((el) => {
      return {
        name: el,
        code: el
      }
    })
    state.statesOptions = [
      ...[{ name: "All", code: "All" }],
      ...state.statesOptionsWithoutAll
    ]

    let account_id = usersStore?.cms?.account_id
    state.selectedAccount = account_id

    if (state.selectedAccount) {
      const resultVendors = await reportsApi.getVendors(state.selectedAccount)
      let vendors = resultVendors.data.value.map((el) => {
        return { name: el, code: el }
      })

      state.vendorOptions = [...[{ name: "All", code: "All" }], ...vendors]
    }
  })

  watch(
    () => dates.value,
    async (newValue, oldValue) => {
      if (newValue[1] === null) {
        return
      }
      let a = convertDateForPostRealDate(newValue[0])
      let b = convertDateForPostRealDate(newValue[1])
      state.startDate = a.toISOString()
      state.endDate = b.toISOString()
    }
  )

  watch(
    () => useLoadingStateStore.isLoading,
    async (newValue) => {
      state.isLoading = newValue
    }
  )

  const handleChangeState = () => {
    if (
      state.selectedStates.length != 0 &&
      state.selectedStates.some((obj) => obj.code === "All")
    ) {
      state.selectedStates = [{ name: "All", code: "All" }]
    }
  }

  const handleChangeProductType = () => {
    if (
      state.selectedProductTypes.length != 0 &&
      state.selectedProductTypes.some((obj) => obj.code === "All")
    ) {
      state.selectedProductTypes = [{ name: "All", code: "All" }]
    }
  }

  const handleChangeVendor = () => {
    if (
      state.selectedVendors.length != 0 &&
      state.selectedVendors.some((obj) => obj.code === "All")
    ) {
      state.selectedVendors = [{ name: "All", code: "All" }]
    }
  }

  const handleChangeStatus = () => {
    if (
      state.selectedStatuses.length != 0 &&
      state.selectedStatuses.some((obj) => obj.code === "All")
    ) {
      state.selectedStatuses = [{ name: "All", code: "All" }]
    }
  }
</script>

<style scoped>
  .add-margin {
    margin-right: 20px;
  }
</style>
