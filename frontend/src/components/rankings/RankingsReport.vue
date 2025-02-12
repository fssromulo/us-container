<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayProductType="false"
      :displayManagers="true"
      :report_name="state.name"
      :displayExportButton="true"
      :displayPurchaseTypeFull="true"
      @exportData="exportData"
    />
    <DataTable :value="state.result" id="general_export">
      <Column field="name" header="Agent"></Column>
      <Column field="num_units" header="Units"></Column>
      <Column field="subtotal_price" header="Total Order Amount"></Column>

      <ColumnGroup type="footer">
        <Row>
          <Column footer="Totals" :colspan="1" footerStyle="text-align:right" />
          <Column :footer="state.totalUnits" />
          <Column :footer="state.totalSubtotalPrice" />
        </Row>
      </ColumnGroup>
    </DataTable>
  </div>
</template>

<script setup>
  import { reactive, ref, inject } from "vue"
  import ReportingFilterOptions from "@/components/reporting/ReportingFilterOptions.vue"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import { df } from "@/service/DateFormat.js"
  import { exportHtmlToPdf } from "@/utils/htmlToPdf.js"

  const $fc = inject("$formatCurrency")

  const usersStore = useUsers()
  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()

  const reportsApi = new ReportsApi()

  const dates = ref()

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
    name: "rankings",
    result: [],
    manager: false,
    selectedPurchaseType: null,
    totalUnits: 0,
    totalSubtotalPrice: 0
  })

  const runReport = (filters) => {
    state.isLoading = true
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    state.manager = filters["manager"]
    state.selectedPurchaseTypes = filters["selectedOrderTypeFilter"]
    handleMultiSelectChange()
    state.isLoading = false
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
    console.log(state.selectedPurchaseType)
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name,
      manager: state.manager,
      purchase_types: state.selectedPurchaseTypes,
      can_read_all:
        usersStore.currentUser.permissions.includes("read:all-rankings"),
      user_id: usersStore.currentUser.id
    }

    if (state.selectedAccount == 1) {
      await reportsApi.runByName("rankings", dataObj)
      intervalManager.runFunctionInInterval(
        runFunctionInInterval("rankings", dataObj, function (result) {
          state.result = result
          state.result = state.result.map((el) => {
            return {
              subtotal_price: $fc(el.subtotal_price),
              name: el.name,
              num_units: el.num_units
            }
          })

          state.totalUnits = result.reduce((accumulator, currentValue) => {
            return accumulator + currentValue.num_units
          }, 0)

          state.totalSubtotalPrice = result.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue.subtotal_price
            },
            0
          )
          state.totalSubtotalPrice = $fc(state.totalSubtotalPrice)
        }),
        function () {
          useLoadingStateStore.setIsLoading(false)
        },
        3000,
        12000
      )
    }
  }

  const exportPdf = async (id, file_name) => {
    await exportHtmlToPdf(id, file_name, "Rankings Report")
      .then((r) => {})
      .catch((e) => {
        console.log(e)
      })
    return
  }

  const exportData = async (type) => {
    type.title = type.title.replace("[INSERT_REPORT_TITLE]", "Rankings Report")
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
    } else {
      const headers = ["Agent", "Units", "Total Order Amount"]

      // Prepare data for CSV
      const csvData = state.result.map((item) => ({
        Agent: item.name,
        Units: item.num_units,
        "Total Paid Amount": item.subtotal_price.replace(/[^0-9.-]+/g, "")
      }))

      // Add total row
      csvData.push({
        Agent: "Totals",
        Units: state.totalUnits,
        "Total Paid Amount": state.totalSubtotalPrice.replace(/[^0-9.-]+/g, "")
      })

      // Convert to CSV string
      let csvContent = headers.join(",") + "\n"
      csvContent += csvData
        .map((row) =>
          headers
            .map((header) =>
              row[header] === undefined ? "" : `"${row[header]}"`
            )
            .join(",")
        )
        .join("\n")

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const url = URL.createObjectURL(blob)

      // Create a link and trigger download
      const link = document.createElement("a")
      link.setAttribute("href", url)
      link.setAttribute("download", `${type.title}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }
</script>
