<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayProductType="false"
      :report_name="state.name"
      @exportData="exportData"
      :displayPurchaseType="true"
      :exportTypes="[
        { name: 'Export Summary', value: 'summary', id: 'export_summary' },
        { name: 'Export Daily', value: 'daily', id: 'export_daily' }
      ]"
    />
    <div id="export_daily">
      <DataTable
        :value="state.deposit_by_day"
        tableStyle="min-width: 50rem"
        scrollable="vertical"
        :scrollHeight="state.scrollableHeight"
        style="height: 700px"
      >
        <Column field="day" header="Date"></Column>
        <Column field="cash" header="Cash"></Column>
        <Column field="check" header="Check"></Column>
        <Column field="cc" header="CC"></Column>
        <Column field="echeck" header="Echeck"></Column>
        <Column field="wire" header="Wire"></Column>
        <Column field="rto" header="Rto"></Column>
        <Column field="zelle" header="Zelle"></Column>
      </DataTable>
    </div>
    <div id="export_summary">
      <DataTable :value="sortedContainerSales" tableStyle="min-width: 50rem">
        <Column field="payment_type" header="Payment Type"></Column>
        <Column field="sum_transactions" header="Sum Transactions"></Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
  import { reactive, computed, ref, inject } from "vue"
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
    scrollableHeight: "500px",
    conditionOptions: [
      { name: "One trip", code: "One-Trip" },
      { name: "Used", code: "Used" }
    ],
    productTypes: [],
    container_sales: [],
    selectedAccount: 1,
    isLoading: false,
    name: "deposit report",
    purchaseType: null,
    deposit_by_day: []
  })

  const runReport = (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    state.purchaseType = filters["purchaseType"]
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
  const sortedContainerSales = computed(() => {
    let payment_type_order = [
      "Cash",
      "Check",
      "CC",
      "Echeck",
      "Wire",
      "Financed",
      "Zelle",
      "RTO",
      "Lease",
      "Leased"
    ]
    let ret = state.container_sales.sort((a, b) => {
      return (
        payment_type_order.indexOf(a.payment_type) -
        payment_type_order.indexOf(b.payment_type)
      )
    })
    console.log(ret)
    return ret
  })

  const handleMultiSelectChange = async (event) => {
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name,
      purchase_type: state.purchaseType
    }

    await reportsApi.runByName("deposit_report", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("deposit_report", dataObj, function (result) {
        state.container_sales = result.map((el) => {
          return {
            payment_type: el.payment_type,
            sum_transactions: $fc(el.sum_transactions)
          }
        })
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )

    await reportsApi.runByName("deposit_report_by_day", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "deposit_report_by_day",
        dataObj,
        function (result) {
          state.deposit_by_day = result
          const options = {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
          }

          for (const obj of state.deposit_by_day) {
            obj.day = new Date(obj.day).toLocaleString("en-US", options)
            for (let key in obj) {
              if (key != "day") {
                obj[key] = $fc(obj[key])
              }
            }
          }
        }
      ),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }

  const exportPdf = async (id, file_name) => {
    state.scrollableHeight = "100%"

    await exportHtmlToPdf(id, file_name, "Deposit Report")
      .then((r) => {
        state.scrollableHeight = "500px"
      })
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    // Extract headers from the first object
    type.title = type.title.replace("[INSERT_REPORT_TITLE]", "Deposit Report")
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
    } else {
      if (type.type == "daily") {
        // Convert list of objects to CSV string
        const headers = [
          "day",
          "cash",
          "check",
          "cc",
          "echeck",
          "wire",
          "rto",
          "zelle"
        ]
        const csvContent =
          "data:text/csv;charset=utf-8," +
          [
            headers.join(","),
            ...state.deposit_by_day.map((obj) => {
              let opt = headers.map((key) => {
                if (obj[key] == undefined) {
                  return ""
                } else {
                  return obj[key].toString().replace(/,/g, "")
                }
              })
              return opt
            })
          ].join("\n")

        // Create a hidden link and trigger the download
        const encodedUri = encodeURI(csvContent)
        const link = document.createElement("a")
        link.setAttribute("href", encodedUri)
        link.setAttribute("download", type.title)
        document.body.appendChild(link) // Required for Firefox
        link.click()
      } else {
        const headers = Object.keys(state.container_sales[0])

        // Convert list of objects to CSV string
        const csvContent =
          "data:text/csv;charset=utf-8," +
          [
            headers.join(","),
            ...state.container_sales.map((obj) =>
              headers
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

        // Create a hidden link and trigger the download
        const encodedUri = encodeURI(csvContent)
        const link = document.createElement("a")
        link.setAttribute("href", encodedUri)
        link.setAttribute("download", type.title)
        document.body.appendChild(link) // Required for Firefox
        link.click()
      }
    }
  }
</script>
