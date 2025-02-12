<template>
  <div class="card">
    <ReportingFilterOptions
      @runReport="runReport"
      :displayCondition="false"
      :displayProductType="false"
      :report_name="state.name"
      :clear_report_names="[
        'financial_report_taxable',
        'financial_report_rentals'
      ]"
      @exportData="exportData"
      :displayPurchaseType="true"
      :exportTypes="[
        { name: 'Export All', value: 'all', id: 'all_sales_tax_report' }
      ]"
    />
    <div id="all_sales_tax_report">
      <div id="taxable">
        <DataTable
          :value="state.reports_taxable_all"
          tableStyle="min-width: 50rem; max-width:98%;max-height:1200px"
          :scrollable="true"
          :scrollHeight="state.scrollableHeight"
          scrollWidth="600px"
        >
          <Column
            field="order_id"
            header="Order id"
            style="max-width: 10%"
            sticky
          ></Column>
          <Column
            field="created"
            header="Transaction Date"
            style="max-width: 10%"
            sticky
          ></Column>
          <Column
            field="name"
            header="Name"
            style="max-width: 10%"
            sticky
          ></Column>
          <Column
            field="container_number"
            header="Container number"
            style="max-width: 10%"
            sticky
          ></Column>
          <Column
            field="taxed_subtotal_paid"
            header="Taxed Subtotal"
            style="max-width: 10%"
            sticky
          ></Column>
          <Column
            field="tax_exempt_subtotal_paid"
            header="Tax Exempt Subtotal"
            style="max-width: 10%"
            sticky
          ></Column>
          <Column
            field="total_tax_paid"
            header="Total Tax Paid"
            style="max-width: 10%"
            sticky
          ></Column>
          <Column
            field="total_paid"
            header="Total Paid"
            style="max-width: 10%"
            sticky
          ></Column>
          <Column
            field="payment_type"
            header="Payment Type"
            style="max-width: 10%"
            sticky
          ></Column>

          <ColumnGroup type="footer">
            <Row>
              <Column
                footer="Totals"
                :colspan="4"
                footerStyle="text-align:right"
              />
              <Column
                :footer="
                  saleTaxReportFormatCurrency(state.taxed_subtotal_paid_tax)
                "
              />
              <Column
                :footer="
                  saleTaxReportFormatCurrency(
                    state.calculated_tax_exempt_subtotal_paid
                  )
                "
              />
              <Column
                :footer="saleTaxReportFormatCurrency(state.total_tax_paid_tax)"
              />
              <Column
                :footer="saleTaxReportFormatCurrency(state.total_paid_tax)"
              />
              <Column :colspan="2" />
            </Row>
          </ColumnGroup>
        </DataTable>
      </div>
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
    reports_tax_exempt: [],
    reports_tax_exempt_all: [],
    reports_taxable: [],
    reports_taxable_all: [],
    purchaseType: null,
    total_paid_tax: 0,
    calculated_total_price_tax: 0,
    calculated_sub_total_price_tax: 0,
    calculated_shipping_revenue_total_tax: 0,
    calculated_order_tax_tax: 0,
    calculated_remaining_order_balance_tax: 0,
    total_paid_no_tax: 0,
    calculated_total_price_no_tax: 0,
    calculated_sub_total_price_no_tax: 0,
    calculated_shipping_revenue_total_no_tax: 0,
    calculated_order_tax_no_tax: 0,
    calculated_remaining_order_balance_no_tax: 0,
    subtotal_paid_tax: 0,
    calculated_order_fees_paid: 0,
    scrollableHeight: "1200px"
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
      purchase_type: state.purchaseType
    }

    state.reports_tax_exempt_all = []
    state.reports_taxable_all = []
    let reports_ran = {}

    if (
      dataObj.purchase_type == "PURCHASE" ||
      dataObj.purchase_type == "PURCHASE_ACCESSORY"
    ) {
      await reportsApi.runByName("financial_report_taxable", dataObj)
      intervalManager.runFunctionInInterval(
        runFunctionInInterval(
          "financial_report_taxable",
          dataObj,
          function (result) {
            if (!("financial_report_taxable" in reports_ran)) {
              reports_ran["financial_report_taxable"] = true
            } else {
              return
            }
            state.reports_taxable = result

            const sumsById = {}

            state.reports_taxable.forEach((element) => {
              if (element.order_id in sumsById) {
                sumsById[element.order_id] += element.total_tax_paid
              } else {
                sumsById[element.order_id] = element.total_tax_paid
              }
            })
            const totalSum = Object.values(sumsById).reduce(
              (acc, curr) => acc + curr,
              0
            )

            //state.container_sales[0].total_tax = saleTaxReportFormatCurrency(totalSum);

            for (const obj of state.reports_taxable) {
              obj.created = dfc(new Date(obj.created).toISOString())
            }

            state.taxed_subtotal_paid_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.taxed_subtotal_paid != "N/A") {
                  return accumulator + currentValue.taxed_subtotal_paid
                } else {
                  return accumulator
                }
              },
              0
            )

            state.total_paid_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.total_paid != "N/A") {
                  return accumulator + currentValue.total_paid
                } else {
                  return accumulator
                }
              },
              0
            )

            state.total_tax_paid_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.total_tax_paid != "N/A") {
                  return accumulator + currentValue.total_tax_paid
                } else {
                  return accumulator
                }
              },
              0
            )

            state.calculated_shipping_revenue_total_tax =
              state.reports_taxable.reduce((accumulator, currentValue) => {
                if (currentValue.calculated_shipping_revenue_total != "N/A") {
                  return (
                    accumulator + currentValue.calculated_shipping_revenue_total
                  )
                } else {
                  return accumulator
                }
              }, 0)

            state.calculated_order_tax_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.calculated_order_tax != "N/A") {
                  return accumulator + currentValue.calculated_order_tax
                } else {
                  return accumulator
                }
              },
              0
            )

            state.calculated_order_tax_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.calculated_order_tax != "N/A") {
                  return accumulator + currentValue.calculated_order_tax
                } else {
                  return accumulator
                }
              },
              0
            )

            state.calculated_tax_exempt_subtotal_paid =
              state.reports_taxable.reduce((accumulator, currentValue) => {
                if (currentValue.tax_exempt_subtotal_paid != "N/A") {
                  return accumulator + currentValue.tax_exempt_subtotal_paid
                } else {
                  return accumulator
                }
              }, 0)

            state.reports_taxable.forEach((el) => {
              el.calculated_remaining_order_balance =
                el.calculated_remaining_order_balance != "N/A"
                  ? saleTaxReportFormatCurrency(
                      el.calculated_remaining_order_balance
                    )
                  : "N/A"
              el.calculated_order_tax =
                el.calculated_order_tax != "N/A"
                  ? saleTaxReportFormatCurrency(el.calculated_order_tax)
                  : "N/A"
              el.calculated_shipping_revenue_total =
                el.calculated_shipping_revenue_total != "N/A"
                  ? saleTaxReportFormatCurrency(
                      el.calculated_shipping_revenue_total
                    )
                  : "N/A"
              if (el.total_paid != "N/A")
                el.total_paid = saleTaxReportFormatCurrency(el.total_paid)
              el.total_tax_paid =
                el.total_tax_paid != "N/A"
                  ? saleTaxReportFormatCurrency(el.total_tax_paid)
                  : "N/A"
              el.taxed_subtotal_paid =
                el.taxed_subtotal_paid != "N/A"
                  ? saleTaxReportFormatCurrency(el.taxed_subtotal_paid)
                  : "N/A"
              el.tax_exempt_subtotal_paid =
                el.tax_exempt_subtotal_paid != "N/A"
                  ? saleTaxReportFormatCurrency(el.tax_exempt_subtotal_paid)
                  : "N/A"
            })

            state.reports_taxable_all = [
              ...state.reports_taxable_all,
              ...state.reports_taxable
            ]
          }
        ),
        function () {
          useLoadingStateStore.setIsLoading(false)
        },
        3000,
        12000
      )
    } else {
      await reportsApi.runByName("financial_report_rentals", dataObj)
      intervalManager.runFunctionInInterval(
        runFunctionInInterval(
          "financial_report_rentals",
          dataObj,
          function (result) {
            if (!("financial_report_rentals" in reports_ran)) {
              reports_ran["financial_report_rentals"] = true
            } else {
              return
            }

            state.reports_taxable = result

            const sumsById = {}

            state.reports_taxable.forEach((element) => {
              if (element.order_id in sumsById) {
                sumsById[element.order_id] += element.total_tax_paid
              } else {
                sumsById[element.order_id] = element.total_tax_paid
              }
            })
            const totalSum = Object.values(sumsById).reduce(
              (acc, curr) => acc + curr,
              0
            )

            //state.container_sales[0].total_tax = saleTaxReportFormatCurrency(totalSum);

            for (const obj of state.reports_taxable) {
              obj.created = dfc(new Date(obj.created).toISOString())
            }

            state.taxed_subtotal_paid_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.taxed_subtotal_paid != "N/A") {
                  return accumulator + currentValue.taxed_subtotal_paid
                } else {
                  return accumulator
                }
              },
              0
            )

            state.total_paid_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.total_paid != "N/A") {
                  return accumulator + currentValue.total_paid
                } else {
                  return accumulator
                }
              },
              0
            )

            state.total_tax_paid_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.total_tax_paid != "N/A") {
                  return accumulator + currentValue.total_tax_paid
                } else {
                  return accumulator
                }
              },
              0
            )

            state.calculated_shipping_revenue_total_tax =
              state.reports_taxable.reduce((accumulator, currentValue) => {
                if (currentValue.calculated_shipping_revenue_total != "N/A") {
                  return (
                    accumulator + currentValue.calculated_shipping_revenue_total
                  )
                } else {
                  return accumulator
                }
              }, 0)

            state.calculated_order_tax_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.calculated_order_tax != "N/A") {
                  return accumulator + currentValue.calculated_order_tax
                } else {
                  return accumulator
                }
              },
              0
            )

            state.calculated_order_tax_tax = state.reports_taxable.reduce(
              (accumulator, currentValue) => {
                if (currentValue.calculated_order_tax != "N/A") {
                  return accumulator + currentValue.calculated_order_tax
                } else {
                  return accumulator
                }
              },
              0
            )

            state.calculated_tax_exempt_subtotal_paid =
              state.reports_taxable.reduce((accumulator, currentValue) => {
                if (currentValue.tax_exempt_subtotal_paid != "N/A") {
                  return accumulator + currentValue.tax_exempt_subtotal_paid
                } else {
                  return accumulator
                }
              }, 0)

            state.reports_taxable.forEach((el) => {
              el.calculated_remaining_order_balance =
                el.calculated_remaining_order_balance != "N/A"
                  ? saleTaxReportFormatCurrency(
                      el.calculated_remaining_order_balance
                    )
                  : "N/A"
              el.calculated_order_tax =
                el.calculated_order_tax != "N/A"
                  ? saleTaxReportFormatCurrency(el.calculated_order_tax)
                  : "N/A"
              el.calculated_shipping_revenue_total =
                el.calculated_shipping_revenue_total != "N/A"
                  ? saleTaxReportFormatCurrency(
                      el.calculated_shipping_revenue_total
                    )
                  : "N/A"
              if (el.total_paid != "N/A")
                el.total_paid = saleTaxReportFormatCurrency(el.total_paid)
              el.total_tax_paid =
                el.total_tax_paid != "N/A"
                  ? saleTaxReportFormatCurrency(el.total_tax_paid)
                  : "N/A"
              el.taxed_subtotal_paid =
                el.taxed_subtotal_paid != "N/A"
                  ? saleTaxReportFormatCurrency(el.taxed_subtotal_paid)
                  : "N/A"
              el.tax_exempt_subtotal_paid =
                el.tax_exempt_subtotal_paid != "N/A"
                  ? saleTaxReportFormatCurrency(el.tax_exempt_subtotal_paid)
                  : "N/A"
            })

            state.reports_taxable_all = [
              ...state.reports_taxable_all,
              ...state.reports_taxable
            ]
          }
        ),
        function () {
          useLoadingStateStore.setIsLoading(false)
        },
        3000,
        12000
      )
    }
  }

  const compare_dates_string = (a, b) => {
    let transactionDate1 = DateTime.fromFormat(a.created, "M/d/yy")
    let transactionDate2 = DateTime.fromFormat(b.created, "M/d/yy")

    return transactionDate1 > transactionDate2 ? 1 : -1
  }

  const exportPdf = async (id, file_name) => {
    state.scrollableHeight = "100%"
    await exportHtmlToPdf(id, file_name, "Sales Tax Report")
      .then((r) => {
        state.scrollableHeight = "500px"
      })
      .catch((e) => {
        console.log(e)
      })
    return
  }
  const exportData = async (type) => {
    type.title = type.title.replace("[INSERT_REPORT_TITLE]", "Sales Tax Report")
    if (type.option != null && type.option == "PDF") {
      await exportPdf(type.id, type.title)
    } else {
      if (type.type == "all") {
        let data_summary = state.reports_taxable_all
        if (!data_summary) {
          return
        }

        const headers = [
          "Order Id",
          "Transaction Date",
          "Name",
          "Container Number",
          "Taxed Subtotal",
          "Tax Exempt Subtotal",
          "Total Tax Paid",
          "Total Paid",
          "Payment Type"
        ]

        const csvContent =
          "data:text/csv;charset=utf-8," +
          [
            headers.join(","),
            ...data_summary.map((obj) =>
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

        const encodedUri = encodeURI(csvContent)
        const link = document.createElement("a")
        link.setAttribute("href", encodedUri)
        link.setAttribute("download", type.title)
        document.body.appendChild(link)
        link.click()
        return
      }
    }
  }
</script>
