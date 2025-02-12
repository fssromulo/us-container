<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayProductType="false"
      :report_name="state.name"
      @exportData="exportData"
    />
    <div id="general_export">
      <div>
        <h4>Average profit per container by state</h4>

        <Chart type="bar" :data="chartData" :options="chartOptions" />
      </div>

      <div>
        <h4>Average profit per container by city / state</h4>
        <div class="chart-container">
          <Chart
            type="bar"
            height="5000px"
            :data="locationItemChartData"
            :options="chartOptions"
            :style="{ height: chartHeight }"
          />
        </div>
      </div>

      <div>
        <h4>Average profit per container by state map</h4>
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

  const data_states = ref()
  const data_chart = ref()
  let chart

  const toExportData = ref()

  const toExportDataCityLoc = ref()

  const usersStore = useUsers()
  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()
  const reportsApi = new ReportsApi()

  onMounted(() => {
    Promise.all([
      fetch("https://unpkg.com/us-atlas/states-10m.json").then((r) => r.json()),
      fetch(
        "https://gist.githubusercontent.com/mbostock/9535021/raw/928a5f81f170b767162f8f52dbad05985eae9cac/us-state-capitals.csv"
      )
        .then((r) => r.text())
        .then((d) => Papa.parse(d, { dynamicTyping: true, header: true }).data)
    ]).then(([us, data]) => {
      const states = ChartGeo.topojson.feature(us, us.objects.states).features
      data_chart.value = data
      data_states.value = data_chart.value.map((d) =>
        Object.assign(d, { value: 0 })
      )

      chart = new ChartJS(canvas.value.getContext("2d"), {
        type: "bubbleMap",
        data: {
          labels: data.map((d) => d.name),
          datasets: [
            {
              label: "Average profit",
              outline: states,
              showOutline: true,
              backgroundColor: "steelblue",
              data: data_states.value
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
              size: [1, 200]
            }
          }
        }
      })
    })
  })

  const findUsed = (stateFullName, result) => {
    const stateAbrev = stateService.getStateAbbreviation(stateFullName)
    for (var i = 0; i < result.length; i++) {
      if (result[i].state == stateAbrev) {
        return result[i].profit
      }
    }
  }

  const state = reactive({
    startDateTimestamp: null,
    endDateTimestamp: null,
    selectedAccount: 1,
    isLoading: false,
    name: "average profit per container"
  })

  const chartHeight = ref("200px")

  const chartData = ref({
    labels: [],
    datasets: [
      {
        label: "Average Profit",
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)", // Adjust color as needed
        borderColor: "rgba(255, 99, 132, 1)", // Adjust color as needed
        borderWidth: 1
      }
    ]
  })

  const locationItemChartData = ref({
    labels: [],
    datasets: [
      {
        label: "Average Profit",
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)", // Adjust color as needed
        borderColor: "rgba(255, 99, 132, 1)", // Adjust color as needed
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
    handleMultiSelectChange()
  }

  const handleMultiSelectChange = async (event) => {
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name
    }

    await reportsApi.runByName("average_profit_per_container", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "average_profit_per_container",
        dataObj,
        function (result) {
          result.sort((a, b) => -a.profit + b.profit)

          toExportData.value = result

          chartData.value.labels = result.map((el) => {
            return el.state
          })

          chartData.value.datasets[0].data = result.map((el) => {
            return el.profit
          })

          chart.data.datasets[0].data = data_chart.value.map((d) =>
            Object.assign(d, { value: findUsed(d.name, result) })
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

    await reportsApi.runByName(
      "average_profit_per_container_city_location",
      dataObj
    )
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "average_profit_per_container_city_location",
        dataObj,
        function (result) {
          result.sort((a, b) => -a.profit + b.profit)

          toExportDataCityLoc.value = result

          locationItemChartData.value.labels = result.map((el) => {
            return el.state
          })

          locationItemChartData.value.datasets[0].data = result.map((el) => {
            return el.profit
          })

          chartHeight.value =
            15 * locationItemChartData.value.labels.length + "px"
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
    },
    responsive: true
  })
  const exportPdf = async (id) => {
    await exportHtmlToPdf(
      id,
      `${df()}_data.pdf`,
      "Average Profit Per Container"
    )
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
      let headers = Object.keys(toExportData.value[0])

      // Convert list of objects to CSV string
      let csvContent =
        "data:text/csv;charset=utf-8," +
        [
          headers.join(","),
          ...toExportData.value.map((obj) =>
            headers.map((key) => obj[key]).join(",")
          )
        ].join("\n")

      // Create a hidden link and trigger the download
      let encodedUri = encodeURI(csvContent)
      let link = document.createElement("a")
      link.setAttribute("href", encodedUri)
      link.setAttribute("download", "data.csv")
      document.body.appendChild(link) // Required for Firefox
      link.click()

      // Extract headers from the first object
      headers = Object.keys(toExportDataCityLoc.value[0])

      // Convert list of objects to CSV string
      csvContent =
        "data:text/csv;charset=utf-8," +
        [
          headers.join(","),
          ...toExportDataCityLoc.value.map((obj) =>
            headers.map((key) => obj[key]).join(",")
          )
        ].join("\n")

      // Create a hidden link and trigger the download
      encodedUri = encodeURI(csvContent)
      link = document.createElement("a")
      link.setAttribute("href", encodedUri)
      link.setAttribute("download", `${df()}_data.csv`)
      document.body.appendChild(link) // Required for Firefox
      link.click()
    }
  }
</script>

<style scoped>
  .chart-container {
    width: 80%;
    overflow-y: auto;
    max-height: 400px; /* Set a maximum height for vertical scrolling */
  }
</style>
