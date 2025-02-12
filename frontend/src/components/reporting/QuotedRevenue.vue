<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayOrderStatus="true"
      :displayStates="true"
      :report_name="state.name"
      @exportData="exportData"
    />
    <div id="general_export">
      <Chart type="bar" :data="chartData" :options="chartOptions" />
    </div>
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
  const chartData = ref({
    labels: [],
    datasets: [
      {
        label: "# Orders & Quote Revenue",
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)", // Adjust color as needed
        borderColor: "rgba(255, 99, 132, 1)", // Adjust color as needed
        borderWidth: 1
      }
    ]
  })

  const reportsApi = new ReportsApi()

  const dates = ref()

  const toExportData = ref()

  const state = reactive({
    startDateTimestamp: null,
    endDateTimestamp: null,
    selectedProductTypes: [],
    productTypes: [],
    selectedStatuses: [],
    selectedStates: [],
    selectedAccount: 1,
    isLoading: false,
    name: "quoted revenue"
  })

  const runReport = (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    state.selectedStates = filters["states"]
    state.selectedStatuses = filters["statuses"]
    state.selectedProductTypes = filters["productTypes"]
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
      productTypes: state.selectedProductTypes,
      statuses: state.selectedStatuses,
      states: state.selectedStates,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name
    }

    await reportsApi.runByName("num_orders_per_month", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("num_orders_per_month", dataObj, function (result) {
        toExportData.value = result

        chartData.value.labels = result.map((el) => {
          return el.year + " " + el.month
        })

        chartData.value.datasets[0].data = result.map((el) => {
          return el.count
        })
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }

  const chartOptions = ref({
    indexAxis: "x",
    scales: {
      x: {
        stacked: true
      },
      y: {
        stacked: true
      }
    }
  })
  const exportPdf = async (id, file_name) => {
    await exportHtmlToPdf(id, file_name, "Quoted Revenue")
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, `${df()}_data.pdf`)
    } else {
      // Extract headers from the first object
      const headers = Object.keys(toExportData.value[0])

      // Convert list of objects to CSV string
      const csvContent =
        "data:text/csv;charset=utf-8," +
        [
          headers.join(","),
          ...toExportData.value.map((obj) =>
            headers.map((key) => obj[key]).join(",")
          )
        ].join("\n")

      // Create a hidden link and trigger the download
      const encodedUri = encodeURI(csvContent)
      const link = document.createElement("a")
      link.setAttribute("href", encodedUri)
      link.setAttribute("download", `${df()}_data.csv`)
      document.body.appendChild(link) // Required for Firefox
      link.click()
    }
  }
</script>
