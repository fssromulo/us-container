<template>
  <div v-if="state.isLoading">
    <div class="flex justify-center p-2">
      <ProgressSpinner />
    </div>
  </div>
  <div v-else class="card">
    <div class="grid grid-cols-2 gap-4">
      <div>
        <b>Customer Name:</b> {{ state.order?.customer?.first_name }}
        {{ state.order?.customer?.last_name }} <br />
        <b>Company Name:</b> {{ state.order?.customer?.company_name }} <br />
        <b>Address: </b> {{ state.order?.address?.street_address }} <br />
        <b>City, State, Zip:</b> {{ state.order?.address?.city }}
        {{ state.order?.address?.state }} {{ state.order?.address?.zip }}<br />
        <b>Container Locations:</b> {{ state.receipt.delivery_address }}
      </div>

      <div>
        <b>Customer Orders:</b> {{ state.receipt.customer_orders }} <br />
        <b>Current Balance:</b> {{ state.receipt.current_balance }} <br />
        <b>Payment Date: </b
        >{{
          state.transactions.length > 0
            ? dfc_without_zone(state.transactions[0].transaction_effective_date)
            : ""
        }}
      </div>

      <DataTable
        class="col-span-2"
        :value="state.transaction_report"
        style="min-width: 50rem; max-width: 98%"
        :scrollable="true"
        :scrollHeight="state.scrollableHeight"
        scrollWidth="600px"
      >
        <!-- <Column field="created_at" header="Charge Date" style="max-width: 10%;" sticky></Column> -->
        <Column
          field="order"
          header="Order"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="description"
          header="Description"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="unit"
          header="Unit"
          style="max-width: 10%"
          sticky
        ></Column>
        <Column
          field="subtotal"
          header="Subtotal"
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
      </DataTable>

      <div class="col-span-1"></div>

      <table class="col-span-1 table-auto">
        <tr v-for="(value, key) in state.distribution_details" :key="key">
          <th class="text-left">{{ key }}</th>
          <td class="text-right">{{ value }}</td>
        </tr>
      </table>

      <DataTable
        v-if="state.mergedOrders"
        class="col-span-2"
        :value="state.mergedOrders"
        :paginator="true"
        :rows="10"
        responsiveLayout="scroll"
      >
        <Column field="display_order_id" header="Order Id" sortable></Column>
        <Column field="balance" header="Balance" sortable>
          <template #body="slotProps">
            {{ receiptFormatCurrency(slotProps.data.calculated_rent_balance) }}
          </template>
        </Column>
        <Column field="paidThru" header="Paid Thru" sortable>
          <template #body="slotProps">
            {{ slotProps.data.calculated_paid_thru }}
          </template>
        </Column>
      </DataTable>

      <div class="col-span-2 mt-4"
        >Notes: {{ generateNotes(state.transactions) }}
      </div>
    </div>

    <div class="mt-4 flex space-x-4">
      <Button
        label="Print Receipt"
        class="bg-blue-500 text-white p-2 rounded"
        @click="printReceiptPdf()"
        :loading="state.loadingPrintReceipt"
      />
      <Button
        label="Email Receipt"
        class="bg-blue-500 text-white p-2 rounded"
        @click="state.emailDialog = true"
        :loading="state.loadingEmailReceipt"
      />
    </div>
    <Dialog
      v-model:visible="state.emailDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Email Address"
      :modal="true"
      class="p-fluid"
    >
      <Textarea
        v-model="state.emails"
        :autoResize="true"
        rows="4"
        placeholder="Email Address"
        label="Email Address"
        cols="10"
      />
      <Button
        class="p-button-rounded"
        @click="emailReceipt()"
        :loading="state.loadingSendEmailReceipt"
      >
        Send Receipt
      </Button>
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, watch, onMounted, computed, ref, inject } from "vue"
  import { useRoute } from "vue-router"
  import CustomerApi from "@/api/customers"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import {
    dfs,
    dfc,
    dfa,
    dfc_without_zone,
    convertDateForPost
  } from "@/service/DateFormat"
  import { DateTime } from "luxon"
  import { useCustomerOrder } from "@/store/modules/customerOrder"

  import { useToast } from "primevue/usetoast"
  const toast = useToast()
  const customerStore = useCustomerOrder()
  const $fc = inject("$formatCurrency")

  const intervalManager = new IntervalManager()
  const reportsApi = new ReportsApi()
  const useLoadingStateStore = loadingStateStore()
  const route = useRoute()
  const customerApi = new CustomerApi()

  const receiptFormatCurrency = (value) => {
    return (value || 0).toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }

  const props = defineProps({
    transaction_id: {
      type: String,
      default: null
    }
  })

  const generateNotes = (transactions) => {
    let notes = ""
    const uniqueTransactions = transactions.reduce((unique, transaction) => {
      if (!unique.some((item) => item.group_id === transaction.group_id)) {
        unique.push(transaction)
      }
      return unique
    }, [])

    transactions = uniqueTransactions

    transactions.forEach((item) => {
      const name = item?.user?.first_name
        ? item.user.first_name + " " + item.user.last_name
        : "No User Recoreded"

      notes += item.notes == null ? "" : item.notes
      notes += "\nProcessed by " + name
      try {
        notes += "\nProcessed on " + dfa(convertDateForPost(item.created_at))
      } catch (error) {}
      if (item.credit_card_object != null) {
        notes +=
          "\n Authorization: " +
          item.credit_card_object?.response_from_gateway?.transactionResponse
            ?.authCode
        notes +=
          "\n Reference: " +
          item.credit_card_object?.response_from_gateway?.transactionResponse
            ?.transId
      }
    })
    return notes
  }

  const state = reactive({
    transactions: [],
    subtotal_paid_taxed: 0,
    subtotal_paid_tax_exempt: 0,
    tax_paid: 0,
    total_paid: 0,
    distribution_details: {},
    order: null,
    mergedOrders: [],
    transaction_report: [],
    loadingEmailReceipt: false,
    loadingSendEmailReceipt: false,
    loadingPrintReceipt: false,
    emailDialog: false,
    receipt: {
      customer_name: null,
      company_name: null,
      address: null,
      city_state_zip: null,
      customer_orders: null,
      current_balance: null,
      payment_date: null,
      main_table: null,
      vertical_table: null,
      bottom_table: null,
      notes: "",
      delivery_address: "",
      payment_type: "",
      show_bottom_table: false
    },
    isLoading: true,
    emails: customerStore?.order?.customer?.email,
    delivery_address: ""
  })

  const runFunctionInInterval = (name, dataObj, fun) => {
    return async function () {
      const result = await reportsApi.retrieveByName(name, dataObj)
      useLoadingStateStore.setIsLoading(false)
      if (result.data.value != null) {
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

  const printReceiptPdf = async () => {
    state.loadingPrintReceipt = true
    state.receipt.notes = generateNotes(state.transactions)
    console.log("Before printing receipt, state is: ", state.receipt)
    const { data, error } = await customerApi.downloadRentReceipt(
      state.order.id,
      state.receipt
    )
    console.log(data.value)
    if (data.value.pdf_url) {
      window.open(data.value.pdf_url, "_blank")
      state.loadingPrintReceipt = false
      return
    }

    toast.add({
      severity: "success",
      summary: "Success",
      group: "br",
      detail: "Receipt Downloaded!",
      life: 3000
    })
    state.loadingPrintReceipt = false
  }

  const emailReceipt = async () => {
    state.loadingEmailReceipt = true
    state.loadingSendEmailReceipt = true
    const emailsEncoded = encodeURIComponent(state.emails)
    console.log("Before sending email receipt, state is: ", state.receipt)
    const { data, error } = await customerApi.emailRentalReceipt(
      state.order.id,
      emailsEncoded,
      state.receipt
    )
    console.log(data.value)
    toast.add({
      severity: "success",
      summary: "Success",
      group: "br",
      detail: "Receipt Emailed!",
      life: 3000
    })
    state.emailDialog = false
    state.loadingSendEmailReceipt = false
    state.loadingEmailReceipt = false
  }

  function transformTransactionList(transactions) {
    let lateFees = []
    let result = []

    transactions.forEach((transaction) => {
      if (transaction.description === "Late fee") {
        lateFees.push(transaction)
      } else {
        result.push(transaction)
      }
    })

    if (lateFees.length > 0) {
      const totalLateFee = lateFees.reduce((sum, fee) => sum + fee.amount, 0)
      const earliestDate = new Date(
        Math.min(...lateFees.map((fee) => new Date(fee.created_at)))
      )
      const latestDate = new Date(
        Math.max(...lateFees.map((fee) => new Date(fee.created_at)))
      )

      result.push({
        ...lateFees[0],
        amount: totalLateFee,
        created_at: earliestDate.toISOString(),
        description: `Late fee ${dfc(earliestDate.toISOString())} - ${dfc(
          latestDate.toISOString()
        )}`
      })
    }

    return result
  }

  const runReceiptItemsReport = async (
    begin_date,
    end_date,
    account_id,
    purchase_type
  ) => {
    const dataObj = {
      begin_date: begin_date,
      end_date: end_date,
      account_id: account_id,
      purchase_type: purchase_type,
      run_by: "user"
    }

    let { data, error } = await customerApi.get_receipt_items_report(dataObj)
    let result = data.value
    let transaction_ids = state.transactions.map((el) => el.id)
    result = result.filter((transaction) =>
      transaction_ids.includes(transaction.transaction_id)
    )
    result = transformTransactionList(result)
    console.log(result)

    state.transaction_report = result.map((el) => {
      return {
        created_at: dfc_without_zone(el.created_at),
        order: el.order,
        unit: el.unit,
        description: el.description,
        subtotal: receiptFormatCurrency(el.amount),
        total_tax_paid: receiptFormatCurrency(el.tax),
        total_paid: receiptFormatCurrency(el.amount + el.tax),
        payment_type: el.payment_type
      }
    })

    state.receipt.main_table = result.map((el) => {
      return {
        date: dfc_without_zone(el.created_at),
        display_order_id: el.order,
        description: el.description,
        unit: el.unit,
        subtotal: receiptFormatCurrency(el.amount),
        total_tax_paid: receiptFormatCurrency(el.tax),
        total_paid: receiptFormatCurrency(el.amount + el.tax),
        payment_type: el.payment_type
      }
    })
    let usedPaymentTypes = []
    state.receipt.main_table.forEach((el) => {
      if (!usedPaymentTypes.includes(el.payment_type)) {
        usedPaymentTypes.push(el.payment_type)
        if (usedPaymentTypes.length > 1) {
          state.receipt.payment_type += ", "
        }
        state.receipt.payment_type += el.payment_type
      }
    })
    console.log(
      "After running report, the state looks like the following: ",
      state.receipt
    )
    state.isLoading = false
  }

  const runReport = async (begin_date, end_date, account_id, purchase_type) => {
    const dataObj = {
      begin_date: begin_date,
      end_date: end_date,
      account_id: account_id,
      purchase_type: purchase_type,
      run_by: "user"
    }

    await reportsApi.runByName("financial_report_rentals", dataObj)
    intervalManager.runFunctionInInterval(
      runFunctionInInterval(
        "financial_report_rentals",
        dataObj,
        function (result) {
          let transaction_ids = state.transactions.map((el) => el.id)
          result = result.filter((transaction) => {
            return transaction_ids.includes(transaction.transaction_id)
          })

          state.subtotal_paid_taxed = result.reduce(
            (accumulator, currentValue) => {
              if (currentValue.taxed_subtotal_paid != "N/A") {
                return accumulator + currentValue.taxed_subtotal_paid
              } else {
                return accumulator
              }
            },
            0
          )

          state.total_paid = result.reduce((accumulator, currentValue) => {
            if (currentValue.total_paid != "N/A") {
              return accumulator + currentValue.total_paid
            } else {
              return accumulator
            }
          }, 0)

          state.tax_paid = result.reduce((accumulator, currentValue) => {
            if (currentValue.total_tax_paid != "N/A") {
              return accumulator + currentValue.total_tax_paid
            } else {
              return accumulator
            }
          }, 0)

          state.subtotal_paid_tax_exempt = result.reduce(
            (accumulator, currentValue) => {
              if (currentValue.tax_exempt_subtotal_paid != "N/A") {
                return accumulator + currentValue.tax_exempt_subtotal_paid
              } else {
                return accumulator
              }
            },
            0
          )
          state.distribution_details = {
            "Taxed Subtotal": receiptFormatCurrency(state.subtotal_paid_taxed),
            "Tax Exempt Subtotal": receiptFormatCurrency(
              state.subtotal_paid_tax_exempt
            ),
            "Tax Paid": receiptFormatCurrency(state.tax_paid),
            "Total Paid": receiptFormatCurrency(state.total_paid)
          }

          state.receipt.vertical_table = {
            taxed_subtotal: state.distribution_details["Taxed Subtotal"],
            tax_exempt_subtotal:
              state.distribution_details["Tax Exempt Subtotal"],
            tax_paid: state.distribution_details["Tax Paid"],
            total_paid: state.distribution_details["Total Paid"]
          }
        }
      ),
      function () {},
      3000,
      50000
    )
  }

  function subtractOneDay(date) {
    return new Date(date.getTime() - 2 * 86400000)
  }

  function addOneDay(date) {
    return new Date(date.getTime() + 2 * 86400000)
  }

  onMounted(async () => {
    let id
    if (props.transaction_id == null) {
      id = route.params.id
    } else {
      id = props.transaction_id
    }

    const { data, error } = await customerApi.getGroupedTransactions(id)

    if (data.value) {
      state.transactions = data.value
      let begin_date = subtractOneDay(
        new Date(state.transactions[0].transaction_effective_date)
      )
      let end_date = addOneDay(
        new Date(
          state.transactions[
            state.transactions.length - 1
          ].transaction_effective_date
        )
      )
      let account_id = state.transactions[0].account_id

      await runReport(begin_date, end_date, account_id, "RENT")

      await runReceiptItemsReport(begin_date, end_date, account_id, "RENT")

      let order = await customerApi.getOrderByRentPeriodId(
        state.transactions[0].rent_period.id
      )
      state.order = order.data.value

      state.delivery_address = ""
      state.transactions.forEach(async (el) => {
        let order = await customerApi.getOrderByRentPeriodId(el.rent_period.id)
        order = order.data.value
        order.line_items.forEach((li) => {
          state.delivery_address +=
            li.inventory_address[0]?.full_address_computed + " | "
        })
      })

      if (state.delivery_address == "" && customerStore.order.single_customer) {
        const customer_address =
          customerStore.order.single_customer.customer_contacts[0]
            .customer_address
        state.delivery_address =
          customer_address.state + " " + customer_address.street_address
      }

      //if(state.delivery_address  == ''){
      //  state.delivery_address = state.order.customer.state + " " + state.order.customer.city + " " + state.order.customer.street_address
      //}

      if (customerStore.order.single_customer) {
        const singleCustomerOrders =
          await customerApi.customerSearchSingleCustomerId(
            customerStore.order.single_customer.id
          )
        state.mergedOrders = []
        if (singleCustomerOrders?.data?.value) {
          singleCustomerOrders?.data.value.forEach((order) => {
            if (!order.is_archived && order.type === "RENT") {
              state.mergedOrders.push(order)
            }
          })
          state.mergedOrders = state.mergedOrders.filter((i) => i != null)

          state.receipt.bottom_table = state.mergedOrders.map((el) => {
            return {
              display_order_id: el.display_order_id,
              type: el.type,
              balance: el.calculated_rent_balance,
              paid_thru: el.calculated_paid_thru
            }
          })
          state.receipt.show_bottom_table =
            state.receipt.bottom_table.length > 1 ? true : false
        }
      }

      let company_name = ""
      if (account_id == 1) {
        company_name = "USAC"
      } else if (account_id == 2) {
        company_name = "A Mobile Box"
      }

      state.receipt.customer_name = state.order?.customer?.full_name
      state.receipt.company_name = company_name
      state.receipt.address = state.order?.address?.street_address
      state.receipt.city_state_zip =
        state.order?.address?.city +
        " " +
        state.order?.address?.state +
        " " +
        state.order?.address?.zip
      state.receipt.customer_orders =
        state.mergedOrders.map((el) => el.display_order_id).join(", ") ||
        state.order?.display_order_id
      state.receipt.current_balance =
        $fc(
          state.mergedOrders.reduce(
            (acc, curr) => acc + curr.calculated_rent_balance,
            0
          )
        ) || $fc(state.order?.calculated_rent_balance)
      state.receipt.payment_date =
        state.transactions.length > 0
          ? dfc_without_zone(state.transactions[0].transaction_effective_date)
          : ""
      state.receipt.delivery_address = state.delivery_address

      state.receipt.notes = generateNotes(state.transactions)
    }
  })
</script>

<style scoped>
  .loading-screen {
    position: fixed;
    top: -300px;
    left: 0;
    width: 100%;
    height: 700px;
    background-color: rgba(255, 255, 255, 1);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: #3498db;
  }

  .spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
