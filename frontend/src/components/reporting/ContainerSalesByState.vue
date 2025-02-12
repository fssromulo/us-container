<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      @exportData="exportData"
      :report_name="state.name"
    />
    <div>
      <h4>Data table of total containers per state</h4>
      <DataTable
        :value="state.container_sales"
        tableStyle="min-width: 50rem"
        id="general_export"
      >
        <Column field="state" header="State"></Column>
        <Column field="total_units" header="Total Units"></Column>
        <Column field="total_orders" header="Total Orders"></Column>
        <Column
          field="percent_total_units"
          header="Percent Total Units"
        ></Column>
      </DataTable>
    </div>

    <div>
      <h4>Map of total containers for each state</h4>
      <canvas ref="canvas" id="canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, ref, inject } from "vue"
  import ReportingFilterOptions from "./ReportingFilterOptions.vue"
  import ReportsApi from "@/api/reports"
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

  const usersStore = useUsers()

  const $fc = inject("$formatCurrency")

  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()

  const reportsApi = new ReportsApi()

  const dates = ref()

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
              label: "Sales",
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
        return result[i].total_units
      }
    }
  }

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
    name: "container_sales"
  })

  const runReport = (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    state.selectedConditions = filters["conditions"]
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
      conditions: state.selectedConditions,
      productTypes: state.selectedProductTypes,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name
    }
    await reportsApi.runByName("container_sales", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("container_sales", dataObj, function (result) {
        state.container_sales = result.map((el) => {
          return {
            state: el.state,
            total_units: el.total_units,
            total_orders: el.total_orders,
            percent_total_units: el.percent_total_units.toFixed(2)
          }
        })
        state.container_sales.sort((a, b) => -a.total_units + b.total_units)

        chart.data.datasets[0].data = data_chart.value.map((d) =>
          Object.assign(d, { value: findUsed(d.name, result) })
        )
        chart.update()
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }
  const exportPdf = async (id, file_name) => {
    await exportHtmlToPdf(id, file_name, "Container Sales By State")
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }
  const exportData = async (type) => {
    type.title = type.title.replace(
      "[INSERT_REPORT_TITLE]",
      "Container Sales By State"
    )
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
