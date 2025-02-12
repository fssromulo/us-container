<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayProductType="false"
      :displayOrderStatus="false"
      :displayStates="false"
      :report_name="state.name"
      :displaySelectAcount="false"
      @exportData="exportData"
    />
    <DataTable
      :value="state.agent_ranking"
      tableStyle="min-width: 50rem"
      id="general_export"
    >
      <Column field="name" header="name"></Column>
      <Column
        field="max_units_sold_year_month"
        header="Highest selling month (units)"
      ></Column>
      <Column field="max_units_sold" header="Most sold units"></Column>

      <Column
        field="highest_sales_year_month"
        header="Highest selling month"
      ></Column>
      <Column field="highest_sales" header="Highest Sales"></Column>

      <Column field="current_sales" header="Current Sales"></Column>
      <Column field="current_units" header="Current Units"></Column>
    </DataTable>
  </div>
</template>

<script setup>
  import { reactive, ref, inject } from "vue"
  import ReportingFilterOptions from "./ReportingFilterOptions.vue"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import { df } from "@/service/DateFormat.js"
  import { exportHtmlToPdf } from "@/utils/htmlToPdf.js"

  const usersStore = useUsers()

  const $fc = inject("$formatCurrency")

  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()
  const reportsApi = new ReportsApi()

  const dates = ref()

  const state = reactive({
    startDateTimestamp: null,
    endDateTimestamp: null,
    selectedConditions: [],
    selectedProductTypes: [],
    conditionOptions: [
      { name: "One trip", code: "One-Trip" },
      { name: "Used", code: "Used" }
    ],
    productTypes: [],
    agent_ranking: [],
    selectedAccount: 1,
    isLoading: false,
    name: "manager ranking"
  })

  const runReport = (filters) => {
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    handleMultiSelectChange()
  }

  const runFunctionInInterval = (name, dataObj, fun) => {
    return async function () {
      const result = await reportsApi.retrieveByName(name, dataObj)
      console.log(result.data.value)
      if (result.data.value != null) {
        useLoadingStateStore.setIsLoading(false)
        fun(result.data.value.result)
      }
      return result.data.value
    }
  }

  const handleMultiSelectChange = async () => {
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: state.selectedAccount,
      role_id: "manager",
      run_by: usersStore.currentUser.full_name
    }
    await reportsApi.runByName("top_managers", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("top_managers", dataObj, function (result) {
        const items = result.map((el) => {
          return {
            name: el.name,
            max_units_sold_year_month:
              el.max_units_sold_year + " " + el.max_units_sold_month,
            max_units_sold: el.max_units_sold,

            highest_sales_year_month:
              el.highest_sales_year + " " + el.highest_sales_month,
            highest_sales: $fc(el.highest_sales),

            current_sales: $fc(el.current_sales),
            current_units: el.current_units
          }
        })
        state.agent_ranking = items
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }

  const exportPdf = async (id, file_name) => {
    await exportHtmlToPdf(id, file_name, "Manager Ranking")
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    type.title = type.title.replace("[INSERT_REPORT_TITLE]", "Manager Ranking")
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
    } else {
      // Extract headers from the first object
      const headers = Object.keys(state.agent_ranking[0])

      // Convert list of objects to CSV string
      const csvContent =
        "data:text/csv;charset=utf-8," +
        [
          headers.join(","),
          ...state.agent_ranking.map((obj) =>
            headers.map((key) => obj[key]).join(",")
          )
        ].join("\n")

      // Create a hidden link and trigger the download
      const encodedUri = encodeURI(csvContent)
      const link = document.createElement("a")
      link.setAttribute("href", encodedUri)
      link.setAttribute("download", type.title)
      document.body.appendChild(link) // Required for Firefox
      link.click()
    }
  }
</script>
