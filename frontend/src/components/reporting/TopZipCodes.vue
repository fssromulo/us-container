<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayProductType="false"
      :displayOrderStatus="true"
      :report_name="state.name"
      @exportData="exportData"
    />
    <div id="general_export">
      <h4>Top {{ postalZipText }}, containers, orders</h4>
      <DataTable :value="state.top_zip_codes" tableStyle="min-width: 50rem">
        <Column field="zip_code" :header="postalZipText"></Column>
        <Column field="count" header="Total Units"></Column>
        <Column field="count_orders" header="Total Orders"></Column>
      </DataTable>
    </div>
    <div>
      <Chart type="bar" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
  import { reactive, ref, computed } from "vue"
  import ReportingFilterOptions from "./ReportingFilterOptions.vue"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import { df } from "@/service/DateFormat.js"
  import { exportHtmlToPdf } from "@/utils/htmlToPdf.js"

  const toExportData = ref()

  const usersStore = useUsers()
  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()
  const postalZipText = computed(() => {
    return usersStore.cms?.account_country &&
      usersStore.cms?.account_country == "Canada"
      ? "Postal Code"
      : "Zip Code"
  })

  const chartData = ref({
    labels: [],
    datasets: [
      {
        label: `Top ${postalZipText.value}`,
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)", // Adjust color as needed
        borderColor: "rgba(255, 99, 132, 1)", // Adjust color as needed
        borderWidth: 1
      }
    ]
  })

  const reportsApi = new ReportsApi()
  const dates = ref()

  const state = reactive({
    startDateTimestamp: null,
    endDateTimestamp: null,
    selectedStatuses: [],
    selectedAccount: 1,
    isLoading: false,
    name: "top zip codes",
    top_zip_codes: []
  })

  const runReport = (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    state.selectedStatuses = filters["statuses"]
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
      statuses: state.selectedStatuses,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name
    }

    await reportsApi.runByName("top_zip_codes", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("top_zip_codes", dataObj, function (result) {
        let elements = result.slice(0, 50)
        elements = elements.filter((el) => {
          return el.zip_code != null
        })
        toExportData.value = elements

        chartData.value.labels = elements.map((el) => {
          return el.zip_code
        })

        chartData.value.datasets[0].data = elements.map((el) => {
          return el.count
        })
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )

    await reportsApi.runByName("top_zip_codes_table", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("top_zip_codes_table", dataObj, function (result) {
        state.top_zip_codes = result.map((el) => {
          return {
            zip_code: el.zip_code,
            count: el.count,
            count_orders: el.count_orders
          }
        })
        state.top_zip_codes.sort((a, b) => -a.count + b.count)
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }

  const chartOptions = ref({
    indexAxis: "y",
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
    await exportHtmlToPdf(id, file_name, `Top ${postalZipText.value}`)
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    type.title = type.title.replace(
      "[INSERT_REPORT_TITLE]",
      `Top ${postalZipText.value}`
    )
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
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
      link.setAttribute("download", type.title)
      document.body.appendChild(link) // Required for Firefox
      link.click()
    }
  }
</script>
