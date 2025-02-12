<template>
  <div
    class="flex flex-wrap mb-4"
    :class="{
      'justify-center': !smAndSmaller,
      'justify-content-left': !smAndSmaller
    }"
  >
    <!-- <DateRangeSelection :isMonthPicker="true" @selectedDates="" /> -->
    <DatePicker
      inputId="range"
      v-model="state.dateRange"
      :class="{
        'ml-20 mt-4': smAndSmaller
      }"
      selectionMode="range"
      :placeholder="month"
      :manualInput="false"
    />
  </div>
  <DataTable
    v-if="!state.loading"
    scrollHeight="70vh"
    :scrollable="true"
    scrollDirection="both"
    ref="dt"
    :filters="state.filters"
    :value="state.rankings"
    class="p-datatable-sm"
    sortField="units"
    responsiveLayout="scroll"
    :sortOrder="-1"
    :tableStyle="{ 'max-width': maxWidth }"
  >
    <template #header>
      <div class="grid grid-cols-12 gap-4">
        <div class="col-span-8">
          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText
              style="min-width: 10em"
              v-model="state.filters['global'].value"
              :placeholder="`Search`"
            />
          </IconField>
        </div>
        <div class="col-span-3 ml-4">
          <Button
            label="Export"
            icon="pi pi-upload"
            class="mr-2 p-button-help"
            @click="exportCSV($event)"
          />
        </div>
      </div>
    </template>
    <Column field="agent" :sortable="true" header="Agent"> </Column>
    <Column
      field="units"
      :defaultSortOrder="-1"
      sortField="units"
      :sortable="true"
      header="Units"
    ></Column>
    <Column
      field="display_sub_total_price"
      sortField="sub_total_price"
      :sortable="true"
      header="Total Paid Amount"
    ></Column>
    <ColumnGroup type="footer">
      <Row>
        <Column footer="Totals:" />
        <Column :footer="totals.units" />
        <Column :footer="totals.sub_total_price" />
      </Row>
    </ColumnGroup>
  </DataTable>
  <LoadingTable v-if="state.loading" :columns="rankingColumns" />
</template>

<script setup>
  import { reactive, computed, watch, onMounted, ref, inject } from "vue"
  import CommissionService from "@/service/Commission.js"
  import DateRangeSelection from "./DateRangeSelection.vue"
  import UsersService from "../../service/User"
  import { useUsers } from "../../store/modules/users"
  import { FilterMatchMode } from "@primevue/core/api"
  import { useToast } from "primevue/usetoast"
  import LoadingTable from "@/components/loadingTable/LoadingTable.vue"
  import { $DateTime } from "../../main"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")

  const toast = useToast()
  const $fc = inject("$formatCurrency")

  const props = defineProps({
    showManagingAgentOnly: {
      type: Boolean,
      required: true,
      default: false
    }
  })

  const userStore = useUsers()
  const usersService = new UsersService()

  const commissionService = new CommissionService()

  const dt = ref()

  const rankingColumns = [
    { field: "agent", display: "Agent" },
    { field: "units", display: "Units" },
    { field: "display_sub_total_price", display: "Total Paid Amount" }
  ]

  const state = reactive({
    rankings: [],
    filters: {},
    loading: false,
    dateRange: null
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }
  const maxWidth = computed(() => {
    return smAndSmaller ? "100vw" : ""
  })

  const totals = computed(() => {
    let result = state.rankings.reduce(
      (acc, curr) => {
        return {
          units: acc.units + curr.units,
          sub_total_price: acc.sub_total_price + curr.sub_total_price
        }
      },
      { units: 0, sub_total_price: 0 }
    )
    result = {
      ...result,
      sub_total_price: $fc(result.sub_total_price)
    }
    return result
  })

  initFilters()
  // give me the month full name in Luxon
  const month = $DateTime.local().monthLong

  onMounted(async () => {
    state.loading = true
    await commissionService.refreshUsers()
    await setDates(
      $DateTime.local().startOf("month"),
      $DateTime.local().endOf("month")
    )
    state.loading = false
  })

  const exportCSV = () => dt.value.exportCSV()

  const setDates = async (start_date, end_date) => {
    if (
      start_date.toFormat("M/d/yy") === "Invalid DateTime" ||
      end_date.toFormat("M/d/yy") === "Invalid DateTime"
    ) {
      return
    }

    console.log(start_date.toFormat("M/d/yy"), end_date.toFormat("M/d/yy"))

    state.loading = true
    state.rankings = commissionService.formatRankings(
      await commissionService.getRankings(
        start_date,
        end_date,
        props.showManagingAgentOnly
      )
    )
    state.loading = false

    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Commission loaded",
      life: 3000,
      group: "br"
    })
  }

  watch(
    () => state.dateRange,
    async (newVal, oldVal) => {
      if (newVal) {
        let start = $DateTime.fromJSDate(newVal[0])
        let end = $DateTime.fromJSDate(newVal[1])

        await setDates(start, end)
      }
    }
  )
</script>
