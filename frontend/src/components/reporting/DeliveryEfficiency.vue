<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayOrderStatus="false"
      :displayStates="false"
      :displayProductType="false"
      :report_name="state.name"
      :exportButton="false"
    />
    <div>
      <table class="w-full">
        <tbody>
          <tr>
            <td>
              <h4> Top 10 states</h4>
              <h5>
                This shows the days difference from paid to delivered. (less is
                better)</h5
              >
              <Chart
                style="width: 600px"
                type="bar"
                :data="top10StatesChartData"
                :options="chartOptions"
              />
            </td>
            <td>
              <h4> Top 10 Warehouses</h4>
              <h5>
                This shows the days difference from paid to delivered. (less is
                better)</h5
              >
              <Chart
                style="width: 600px"
                type="bar"
                :data="top10WarehousesChartData"
                :options="chartOptions"
              />
            </td>
          </tr>
          <tr>
            <td>
              <h4> Bottom 10 States</h4>
              <h5>
                This shows the days difference from paid to delivered. (less is
                better)</h5
              >
              <Chart
                style="width: 600px"
                type="bar"
                :data="bottom10StatesChartData"
                :options="chartOptions"
              />
            </td>
            <td>
              <h4>Bottom 10 Warehouses</h4>
              <h5
                >This shows the days difference from paid to delivered. (less is
                better)</h5
              >
              <Chart
                style="width: 600px"
                type="bar"
                :data="bottom10WarehousesChartData"
                :options="chartOptions"
              />
            </td>
          </tr>
        </tbody>
      </table>
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

  const usersStore = useUsers()
  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()
  const top10StatesChartData = ref({
    labels: [],
    datasets: [
      {
        label: "Days",
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)", // Adjust color as needed
        borderColor: "rgba(255, 99, 132, 1)", // Adjust color as needed
        borderWidth: 1
      }
    ]
  })

  const top10WarehousesChartData = ref({
    labels: [],
    datasets: [
      {
        label: "Days",
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)", // Adjust color as needed
        borderColor: "rgba(255, 99, 132, 1)", // Adjust color as needed
        borderWidth: 1
      }
    ]
  })

  const bottom10StatesChartData = ref({
    labels: [],
    datasets: [
      {
        label: "Days",
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)", // Adjust color as needed
        borderColor: "rgba(255, 99, 132, 1)", // Adjust color as needed
        borderWidth: 1
      }
    ]
  })

  const bottom10WarehousesChartData = ref({
    labels: [],
    datasets: [
      {
        label: "Days",
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
    selectedProductTypes: [],
    productTypes: [],
    selectedStatuses: [],
    selectedStates: [],
    selectedAccount: 1,
    isLoading: false,
    name: "delivery efficiency"
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
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name
    }

    await reportsApi.runByName("top_10_states_delivery_efficiency", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "top_10_states_delivery_efficiency",
        dataObj,
        function (result) {
          top10StatesChartData.value.labels = result.map((el) => {
            return el.state
          })

          top10StatesChartData.value.datasets[0].data = result.map((el) => {
            return el.days
          })
        }
      ),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )

    await reportsApi.runByName("top_10_warehouses_delivery_efficiency", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "top_10_warehouses_delivery_efficiency",
        dataObj,
        function (result) {
          top10WarehousesChartData.value.labels = result.map((el) => {
            return el.city_loc
          })

          top10WarehousesChartData.value.datasets[0].data = result.map((el) => {
            return el.days
          })
        }
      ),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )

    await reportsApi.runByName("bottom_10_states_delivery_efficiency", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "bottom_10_states_delivery_efficiency",
        dataObj,
        function (result) {
          bottom10StatesChartData.value.labels = result.map((el) => {
            return el.state
          })

          bottom10StatesChartData.value.datasets[0].data = result.map((el) => {
            return el.days
          })
        }
      ),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )

    await reportsApi.runByName(
      "bottom_10_warehouses_delivery_efficiency",
      dataObj
    )
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "bottom_10_warehouses_delivery_efficiency",
        dataObj,
        function (result) {
          bottom10WarehousesChartData.value.labels = result.map((el) => {
            return el.city_loc
          })

          bottom10WarehousesChartData.value.datasets[0].data = result.map(
            (el) => {
              return el.days
            }
          )
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
        stacked: true
      },
      y: {
        stacked: true
      }
    }
  })
</script>
