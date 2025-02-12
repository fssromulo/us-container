<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :report_name="state.name"
      @exportData="exportData"
    />
    <div id="general_export">
      <div>
        <h4>Bar graph of used vs one trip containers</h4>
        <Chart type="bar" :data="chartData" :options="chartOptions" />
      </div>

      <div>
        <h4>Map of used containers</h4>
        <canvas ref="canvas" id="canvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, ref } from "vue"
  import ReportsApi from "@/api/reports"
  import ReportingFilterOptions from "./ReportingFilterOptions.vue"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import { Chart as ChartJS } from "chart.js"
  import {
    ChoroplethController,
    GeoFeature,
    ColorScale,
    ProjectionScale,
    BubbleMapController,
    SizeScale
  } from "chartjs-chart-geo"
  import * as ChartGeo from "chartjs-chart-geo"
  import Papa from "papaparse"
  import StateService from "@/service/StateService"
  import { df } from "@/service/DateFormat.js"
  import { exportHtmlToPdf } from "@/utils/htmlToPdf.js"

  const stateService = new StateService()

  const canvas = ref()
  ChartJS.register(
    BubbleMapController,
    GeoFeature,
    ColorScale,
    ProjectionScale,
    SizeScale
  )

  const data_states_used = ref()
  const data_states_one_trip = ref()
  const data_chart_used = ref()
  const data_chart_one_trip = ref()
  let chart

  const usersStore = useUsers()
  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()
  const reportsApi = new ReportsApi()

  const toExportData = ref()

  onMounted(() => {
    Promise.all([
      fetch("https://unpkg.com/us-atlas/states-10m.json").then((r) => r.json()),
      fetch(
        "https://gist.githubusercontent.com/mbostock/9535021/raw/928a5f81f170b767162f8f52dbad05985eae9cac/us-state-capitals.csv"
      )
        .then((r) => r.text())
        .then((d) => Papa.parse(d, { dynamicTyping: true, header: true }).data)
    ]).then(([us, data]) => {
      console.log(data)
      const states = ChartGeo.topojson.feature(us, us.objects.states).features
      data_chart_used.value = data
      data_states_used.value = data_chart_used.value.map((d) =>
        Object.assign(d, { value: 0 })
      )

      const dataClone = JSON.parse(JSON.stringify(data))
      data_chart_one_trip.value = dataClone
      data_states_one_trip.value = data_chart_one_trip.value.map((d) =>
        Object.assign(d, { value: 0 })
      )

      chart = new ChartJS(canvas.value.getContext("2d"), {
        type: "bubbleMap",
        data: {
          labels: data.map((d) => d.name),
          datasets: [
            {
              label: "One trip",
              outline: states,
              showOutline: true,
              backgroundColor: "rgba(255, 99, 132, 0.2)",
              borderColor: "rgba(255, 99, 132, 1)",
              data: data_states_one_trip.value
            },
            {
              label: "Used",
              outline: states,
              showOutline: true,
              backgroundColor: "rgba(54, 162, 235, 0.2)",
              borderColor: "rgba(54, 162, 235, 1)",
              data: data_states_used.value
            }
          ]
        },
        options: {
          legend: {
            display: false
          },
          plugins: {
            datalabels: {
              align: "top",
              formatter: (v) => {
                return v.description
              }
            }
          },
          scale: {
            projection: "albersUsa"
          },
          geo: {
            radiusScale: {
              display: true,
              size: [1, 20]
            }
          }
        }
      })
    })
  })

  const state = reactive({
    startDateTimestamp: null,
    endDateTimestamp: null,
    selectedProductTypes: [],
    productTypes: [],
    container_sales: [],
    selectedAccount: 1,
    isLoading: false,
    name: "container_condition"
  })

  const chartData = ref({
    labels: [],
    datasets: [
      {
        label: "One-Trip",
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)", // Adjust color as needed
        borderColor: "rgba(255, 99, 132, 1)", // Adjust color as needed
        borderWidth: 1
      },
      {
        label: "Used",
        data: [],
        backgroundColor: "rgba(54, 162, 235, 0.2)", // Adjust color as needed
        borderColor: "rgba(54, 162, 235, 1)", // Adjust color as needed
        borderWidth: 1
      }
    ]
  })

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

  const runReport = (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    state.selectedProductTypes = filters["productTypes"]
    handleMultiSelectChange()
  }

  const findUsed = (stateFullName, result) => {
    const stateAbrev = stateService.getStateAbbreviation(stateFullName)
    for (var i = 0; i < result.length; i++) {
      if (result[i].state == stateAbrev) {
        return result[i].total_containers_used
      }
    }
  }

  const findOneTime = (stateFullName, result) => {
    const stateAbrev = stateService.getStateAbbreviation(stateFullName)
    for (var i = 0; i < result.length; i++) {
      if (result[i].state == stateAbrev) {
        return result[i].total_containers_one_trip
      }
    }
  }

  const handleMultiSelectChange = async (event) => {
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      productTypes: state.selectedProductTypes,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name
    }

    await reportsApi.runByName("container_sales_by_condition", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "container_sales_by_condition",
        dataObj,
        async function (result) {
          toExportData.value = result

          chartData.value.labels = result.map((el) => {
            return el.state
          })
          chartData.value.datasets[0].data = result.map((el) => {
            return el.total_containers_one_trip
          })
          chartData.value.datasets[1].data = result.map((el) => {
            return el.total_containers_used
          })

          chart.data.datasets[1].data = data_chart_used.value.map((d) =>
            Object.assign(d, { value: findUsed(d.name, result) })
          )
          chart.data.datasets[0].data = data_chart_one_trip.value.map((d) =>
            Object.assign(d, { value: findOneTime(d.name, result) })
          )

          chart.update()
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
    indexAxis: "y",
    scales: {
      x: {
        stacked: false
      },
      y: {
        stacked: false
      }
    }
  })
  const exportPdf = async (id) => {
    await exportHtmlToPdf(
      id,
      `${df()}_data.pdf`,
      "Container Condition By State"
    )
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id)
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
