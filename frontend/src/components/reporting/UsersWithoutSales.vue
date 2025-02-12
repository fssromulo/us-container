<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displaySelectAcount="true"
      :displayPurchaseType="false"
      :displayCondition="false"
      :displayProductType="false"
      :report_name="state.name"
      @exportData="exportData"
      :exportTypes="[
        { name: 'Export All', value: 'all', id: 'all_sales_tax_report' }
      ]"
    />
    <DataTable
      :value="state.users"
      tableStyle="min-width: 50rem; max-width:98%"
    >
      <Column
        style="max-width: 16%"
        field="first_name"
        header="First Name"
      ></Column>
      <Column
        style="max-width: 16%"
        field="last_name"
        header="Last Name"
      ></Column>
      <Column
        style="max-width: 16%"
        field="formatted_created_at"
        header="Created At"
      ></Column>
      <Column style="max-width: 16%" field="email" header="Email"></Column>
      <Column
        style="max-width: 16%"
        field="days_as_use"
        header="Days As User"
      ></Column>
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
  import { dfl, dfc, dfa } from "@/service/DateFormat.js"
  import Lock from "@/service/Lock.js"

  const usersStore = useUsers()

  const $fc = inject("$formatCurrency")

  const lock = new Lock()

  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()

  const reportsApi = new ReportsApi()

  const dates = ref()

  const state = reactive({
    startDateTimestamp: null,
    endDateTimestamp: null,
    users: [{ column1: "test" }],
    selectedAccount: 1,
    isLoading: false,
    name: "Users Without Sales"
  })

  const runReport = (filters) => {
    state.selectedAccount = filters["account_id"]
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

  const handleMultiSelectChange = async (event) => {
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      run_by: usersStore.currentUser.full_name,
      account_id: state.selectedAccount
    }

    await reportsApi.runByName("users_without_sales", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("users_without_sales", dataObj, function (result) {
        state.users = result
        state.users.sort((a, b) => {
          return a.first_name.localCompare(b.first_name)
        })
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }

  const exportPdf = async (id, file_name) => {
    state.scrollableHeight = "100%"
    await exportHtmlToPdf(
      id,
      file_name,
      "Users without sales in the last N days"
    )
      .then((r) => {
        state.scrollableHeight = "500px"
      })
      .catch((e) => {
        console.log(e)
      })
    return
  }
  const exportData = async (type) => {
    type.title = type.title.replace(
      "[INSERT_REPORT_TITLE]",
      "Users without sales in the last N days"
    )
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
    } else {
      let data_summary = state.users
      if (!data_summary) {
        return
      }

      const headers_summary = Object.keys(data_summary[0])

      const csvContent =
        "data:text/csv;charset=utf-8," +
        [
          headers_summary.join(","),
          ...data_summary.map((obj) =>
            headers_summary
              .map((key) => {
                if (obj[key] == undefined) {
                  return ""
                } else {
                  return obj[key].toString().replace(/,/g, "")
                }
              })
              .join(",")
          )
        ].join("\n")

      const encodedUri = encodeURI(csvContent)
      const link = document.createElement("a")
      link.setAttribute("href", encodedUri)
      link.setAttribute("download", type.title)
      document.body.appendChild(link)
      link.click()
      return
    }
  }
</script>
