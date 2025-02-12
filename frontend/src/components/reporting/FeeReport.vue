<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayProductType="false"
      :report_name="state.name"
      @exportData="exportData"
    />
    <DataTable
      :value="state.container_sales"
      tableStyle="min-width: 50rem"
      id="general_export"
    >
      <Column field="total" header="Total"></Column>
      <Column field="type" header="Type"></Column>
    </DataTable>
  </div>
</template>

<script setup>
  import { reactive, ref } from "vue"
  import ReportingFilterOptions from "./ReportingFilterOptions.vue"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import { df } from "@/service/DateFormat.js"
  import { exportHtmlToPdf } from "@/utils/htmlToPdf.js"

  const usersStore = useUsers()
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
    container_sales: [],
    selectedAccount: 1,
    isLoading: false,
    name: "fee report"
  })

  const runReport = (filters) => {
    state.isLoading = true
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    handleMultiSelectChange()
    state.isLoading = false
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

  const handleMultiSelectChange = async (event) => {
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name
    }

    await reportsApi.runByName("fee_report", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("fee_report", dataObj, function (result) {
        state.container_sales = result
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }

  const exportPdf = async (id, file_name) => {
    await exportHtmlToPdf(id, file_name, "Fee Report")
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    type.title = type.title.replace("[INSERT_REPORT_TITLE]", "Fee Report")
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
    } else {
      // Extract headers from the first object
      const headers = Object.keys(state.container_sales[0])

      // Convert list of objects to CSV string
      const csvContent =
        "data:text/csv;charset=utf-8," +
        [
          headers.join(","),
          ...state.container_sales.map((obj) =>
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
