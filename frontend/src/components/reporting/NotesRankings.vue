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
      :notesReport="true"
      @exportData="exportData"
    />
    <DataTable
      :value="state.notes_rankings"
      tableStyle="min-width: 50rem"
      id="general_export"
    >
      <Column field="name" header="Name"></Column>
      <Column field="quantity" header="Number Of Notes"></Column>
    </DataTable>
  </div>
</template>

<script setup>
  import { reactive, ref, inject } from "vue"
  import ReportingFilterOptions from "./ReportingFilterOptions.vue"
  import ReportsApi from "@/api/reports"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import { exportHtmlToPdf } from "@/utils/htmlToPdf.js"
  import IntervalManager from "@/service/IntervalManager.js"

  const usersStore = useUsers()
  const intervalManager = new IntervalManager()

  const useLoadingStateStore = loadingStateStore()
  const reportsApi = new ReportsApi()

  const dates = ref()

  const state = reactive({
    startDateTimestamp: null,
    endDateTimestamp: null,
    selectedConditions: [],
    selectedProductTypes: [],
    productTypes: [],
    notes_rankings: [],
    selectedAccount: 1,
    isLoading: false,
    name: "notes rankings"
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
      run_by: usersStore.currentUser.full_name
    }
    await reportsApi.runByName("notes_rankings", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("notes_rankings", dataObj, function (result) {
        const items = result.map((el) => {
          return {
            name: el.name,
            quantity: el.quantity
          }
        })
        state.notes_rankings = items
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }

  const exportPdf = async (id, file_name) => {
    await exportHtmlToPdf(id, file_name, "Notes Ranking")
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    type.title = type.title.replace("[INSERT_REPORT_TITLE]", "Notes Ranking")

    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
    } else {
      // Extract headers from the first object
      const headers = Object.keys(state.notes_rankings[0])

      // Convert list of objects to CSV string
      const csvContent =
        "data:text/csv;charset=utf-8," +
        [
          headers.join(","),
          ...state.notes_rankings.map((obj) =>
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
