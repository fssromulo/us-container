<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayProductType="false"
      :report_name="state.name"
      :clear_report_names="['vendor_inventory']"
      @exportData="exportData"
      :displayPurchaseType="false"
      :displaySelectVendor="true"
      :exportTypes="[{ name: 'Export All', value: 'all', id: 'vendor_report' }]"
    />

    <div id="taxable">
      <DataTable
        :value="state.inventory_report"
        tableStyle="min-width: 50rem; max-width:98%;height:1200px"
        :scrollable="true"
        :scrollHeight="state.scrollableHeight"
        id="vendor_report"
        scrollWidth="600px"
      >
        <Column
          field="name"
          header="Vendor name"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="container_release_number"
          header="Container Release Number"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="container_number"
          header="Container Number"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="created_at"
          header="Created At Date"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="invoice_number"
          header="Invoice Number"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="total_cost"
          header="Total Cost"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="container_size"
          header="Container Size"
          style="max-width: 10%"
          sticky
        ></Column>
      </DataTable>
    </div>
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
  import { DateTime } from "luxon"
  import { useToast } from "primevue/usetoast"

  const toast = useToast()

  const usersStore = useUsers()

  const $fc = inject("$formatCurrency")
  const saleTaxReportFormatCurrency = (value) => {
    if (value) {
      return (Math.round(value * 10000) / 10000).toLocaleString("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 3
      })
    }
    return 0
  }
  const lock = new Lock()

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
    name: "sales tax report",
    selectedVendors: [],
    calculated_order_fees_paid: 0,
    scrollableHeight: "1200px",
    inventory_report: []
  })

  const runReport = (filters) => {
    state.selectedAccount = filters["account_id"]
    state.startDateTimestamp = filters["begin_date"]
    state.endDateTimestamp = filters["end_date"]
    state.selectedVendors = filters["vendors"]
    handleMultiSelectChange()
  }

  const runFunctionInInterval = (name, dataObj, fun) => {
    return async function () {
      const result = await reportsApi.retrieveByName(name, dataObj)
      console.log(result.data.value)
      if (result.data.value != null) {
        useLoadingStateStore.setIsLoading(false)
        if (result.data.value.result.length == 0) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "No results for report, try again.",
            group: "br",
            life: 5000
          })
        } else {
          fun(result.data.value.result)
        }
      }
      return result.data.value
    }
  }

  const handleMultiSelectChange = async (event) => {
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: state.selectedAccount,
      run_by: usersStore.currentUser.full_name,
      vendors: state.selectedVendors
    }

    await reportsApi.runByName("vendor_inventory", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval("vendor_inventory", dataObj, function (result) {
        state.inventory_report = result
        state.inventory_report.map((el) => {
          el.created_at = dfc(el.created_at)
        })
      }),
      function () {
        useLoadingStateStore.setIsLoading(false)
      },
      3000,
      12000
    )
  }

  const compare_dates_string = (a, b) => {
    let transactionDate1 = DateTime.fromFormat(a.created, "M/d/yy")
    let transactionDate2 = DateTime.fromFormat(b.created, "M/d/yy")

    return transactionDate1 > transactionDate2 ? 1 : -1
  }

  const exportPdf = async (id, file_name) => {
    state.scrollableHeight = "100%"
    await exportHtmlToPdf(id, file_name, "Vendor Report")
      .then((r) => {
        state.scrollableHeight = "500px"
      })
      .catch((e) => {
        console.log(e)
      })
    return
  }
  const exportData = async (type) => {
    type.title = type.title.replace("[INSERT_REPORT_TITLE]", "Vendor Report")
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
    } else {
      let data_summary = state.inventory_report
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
