<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayOrderStatus="false"
      :displayStates="true"
      :report_name="state.name"
      @exportData="exportData"
    />
    <div id="general_export">
      <Chart
        type="pie"
        :data="chartData"
        :options="chartOptions"
        class="w-full md:w-[30rem]"
      />
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
        label: "One-Trip",
        data: [],
        backgroundColor: [
          "red",
          "blue",
          "yellow",
          "green",
          "purple",
          "black",
          "orange",
          "azure",
          "gray"
        ]
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
    name: "order by payment types"
  })

  const runReport = (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    state.selectedStates = filters["states"]
    state.selectedProductTypes = filters["productTypes"]
    handleMultiSelectChange()
  }

  const runFunctionInInterval = (name, dataObj, fun) => {
    return async function () {
      const result = await reportsApi.retrieveByName(name, dataObj)
      console.log(result.data.value)
      if (result.data.value != null) {
        fun(result.data.value.result)
        useLoadingStateStore.setIsLoading(false)
      }
      return result.data.value
    }
  }

  const handleMultiSelectChange = async (event) => {
    console.log(state.selectedStates, "States")
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      productTypes: state.selectedProductTypes,
      states: state.selectedStates,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name
    }

    await reportsApi.runByName("orders_by_payment_type", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "orders_by_payment_type",
        dataObj,
        function (result) {
          toExportData.value = result

          chartData.value.labels = result.map((el) => {
            return el.payment_type
          })

          chartData.value.datasets[0].data = result.map((el) => {
            return el.count
          })
        }
      ),
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
  const exportPdf = async (id) => {
    await exportHtmlToPdf(id, `${df()}_data.pdf`, "Order By Payment Type")
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    // Extract headers from the first object
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id)
    } else {
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
