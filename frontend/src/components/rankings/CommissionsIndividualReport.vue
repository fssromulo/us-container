<template>
  <div class="card">
    <DataTable
      v-if="!state.isLoading"
      :value="state.result"
      id="general_export"
      responsiveLayout="scroll"
      stripedRows
    >
      <Column field="manager_name" header="Manager" sortable />
      <Column field="agent_name" header="Agent" sortable />
      <Column field="display_order_id" :sortable="true" header="Order #">
        <template #body="{ data, field }">
          <Button
            :loading="state.individualOrderLoading === data.display_order_id"
            class="p-button-rounded p-button-secondary"
            @click="openOrder(data, field)"
            >{{ data.display_order_id }}
          </Button>
        </template>
      </Column>
      <Column field="profit" header="Profit" sortable>
        <template #body="slotProps">
          {{ $fc(slotProps.data.profit) }}
        </template>
      </Column>
      <Column field="total_commission" header="Total Commission" sortable>
        <template #body="slotProps">
          {{ $fc(slotProps.data.total_commission) }}
        </template>
      </Column>
      <Column field="manager_commission" header="Manager Commission" sortable>
        <template #body="slotProps">
          {{ $fc(slotProps.data.manager_commission) }}
        </template>
      </Column>
      <Column field="agent_commission" header="Agent Commission" sortable>
        <template #body="slotProps">
          {{ $fc(slotProps.data.agent_commission) }}
        </template>
      </Column>
      <Column field="delivered_at" header="Order Delivered" sortable>
        <template #body="slotProps">
          {{ dfc(slotProps.data.delivered_at) }}
        </template>
      </Column>

      <Column field="paid_at" header="Order Paid" sortable>
        <template #body="slotProps">
          {{ dfc(slotProps.data.paid_at) }}
        </template>
      </Column>
      <Column field="total_amount" header="Subtotal" sortable>
        <template #body="slotProps">
          {{ $fc(slotProps.data.subtotal_amount) }}
        </template>
      </Column>

      <ColumnGroup type="footer">
        <Row>
          <Column footer="Totals" :colspan="3" footerStyle="text-align:right" />
          <Column :footer="state.sum_profit" />
          <Column :footer="state.sum_total_commission" />
          <Column :footer="state.sum_manager_commission" />
          <Column :footer="state.sum_agent_commission" />
          <Column footer="Totals" :colspan="2" footerStyle="text-align:right" />
          <Column :footer="state.sum_subtotal_amount" />
        </Row>
      </ColumnGroup>
    </DataTable>
    <LoadingTable v-if="state.isLoading" :columns="managerCommissionsColumns" />
    <div class="flex flex-wrap justify-center mt-2">
      <p class="text-lg">{{ state.result.length }} Order(s)</p>
    </div>
  </div>

  <Dialog
    v-model:visible="state.updateOrderDialog"
    :style="{ height: '100vh' }"
    :breakpoints="{
      '2000px': '45vw',
      '1400px': '55vw',
      '1200px': '65vw',
      '992px': '75vw',
      '600px': '100vw',
      '480px': '100vw',
      '320px': '100vw'
    }"
    closeOnEscape
    :dismissableMask="true"
    keepInViewPort
    modal=""
    :draggable="false"
  >
    <template #header>
      <div class="flex align-items">
        <div class="flex">
          <p :class="smAndSmaller ? 'text-xl' : 'text-3xl'">
            Invoice - {{ state.customerOrder.display_order_id }}
          </p>
        </div>
      </div>
    </template>
    <CustomerOrderDetail :customerOrderProp="state.customerOrder" />
  </Dialog>
</template>

<script setup>
  import { reactive, ref, inject, onMounted } from "vue"
  import DateRangeSelection from "./DateRangeSelection.vue"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import { df, dfc } from "@/service/DateFormat.js"
  import { exportHtmlToPdf } from "@/utils/htmlToPdf.js"
  import { data } from "autoprefixer"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import LoadingTable from "@/components/loadingTable/LoadingTable.vue"

  import CustomerOrderDetail from "@/components/invoicing/CustomerOrderDetail.vue"
  import CustomerApi from "@/api/customers"

  const $fc = inject("$formatCurrency")
  const customerApi = new CustomerApi()
  const customersStore = useCustomerOrder()

  const usersStore = useUsers()
  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()

  const reportsApi = new ReportsApi()

  const managerCommissionsColumns = [
    { field: "manager_name", header: "Manager" },
    { field: "agent_name", header: "Agent" },
    { field: "display_order_id", header: "Order #" },
    { field: "profit", header: "Profit" },
    { field: "total_commission", header: "Total Commission" },
    { field: "manager_commission", header: "Manager Commission" },
    { field: "agent_commission", header: "Agent Commission" },
    { field: "delivered_at", header: "Order Delivered" },
    { field: "paid_at", header: "Order Paid" },
    { field: "total_amount", header: "Subtotal" }
  ]

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
    totalSubtotalPrice: 0,
    individualOrderLoading: null,
    isManagersOnly: true,
    isManagersOnlyLabel: "Managers Only",
    sum_profit: 0,
    sum_total_commission: 0,
    sum_manager_commission: 0,
    sum_agent_commission: 0,
    sum_subtotal_amount: 0
  })

  const props = defineProps({
    dates: {
      type: Object,
      default: {}
    },
    selectedUser: {
      type: Object,
      default: {}
    },
    closed: {
      type: Boolean,
      default: false
    }
  })

  const openOrder = async (data = null, field = null) => {
    if (data && field) {
      state.individualOrderLoading = data["display_order_id"]
      await getOrderByDisplayId(data[field])
      state.individualOrderLoading = null
    } else {
      state.customerOrder = {}
    }
    state.updateOrderDialog = true
  }

  const getOrderByDisplayId = async (id) => {
    const { data, isLoading, error } = await customerApi.getOrderByDisplayId(id)

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading order",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.customerOrder = data.value
      customersStore.setOrder(data.value)
    }
  }

  onMounted(async () => {
    state.isLoading = true
    await handleMultiSelectChange()
  })

  const runFunctionInInterval = (name, dataObj, fun) => {
    return async function () {
      const result = await reportsApi.retrieveByName(name, dataObj)
      console.log(result.data.value)
      if (result.data.value != null) {
        useLoadingStateStore.setIsLoading(false)
        fun(result.data.value.result)
        state.isLoading = false
      }
      return result.data.value
    }
  }

  const handleMultiSelectChange = async () => {
    if (!props.closed) {
      const dataObj = {
        begin_date: props.dates["start_date"],
        end_date: props.dates["end_date"],
        account_id: 1,
        run_by: usersStore.currentUser.full_name,
        can_read_all:
          usersStore.currentUser.permissions.includes("read:all-rankings"),
        user_id: props.selectedUser
      }

      await reportsApi.runByName("commissions_individual_report", dataObj)
      intervalManager.runFunctionInInterval(
        runFunctionInInterval(
          "commissions_individual_report",
          dataObj,
          function (result) {
            state.result = result

            state.sum_profit = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.profit
              }, 0)
            )

            state.sum_total_commission = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.total_commission
              }, 0)
            )

            state.sum_manager_commission = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.manager_commission
              }, 0)
            )

            state.sum_agent_commission = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.agent_commission
              }, 0)
            )

            state.sum_subtotal_amount = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.subtotal_amount
              }, 0)
            )
          }
        ),
        function () {
          useLoadingStateStore.setIsLoading(false)
        },
        1000,
        12000
      )
    } else {
      const dataObj = {
        begin_date: props.dates["start_date"],
        end_date: props.dates["end_date"],
        account_id: 1,
        run_by: usersStore.currentUser.full_name,
        can_read_all:
          usersStore.currentUser.permissions.includes("read:all-rankings"),
        user_id: props.selectedUser
      }

      await reportsApi.runByName(
        "commissions_closed_individual_report",
        dataObj
      )
      intervalManager.runFunctionInInterval(
        runFunctionInInterval(
          "commissions_closed_individual_report",
          dataObj,
          function (result) {
            state.result = result

            state.sum_profit = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.profit
              }, 0)
            )

            state.sum_total_commission = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.total_commission
              }, 0)
            )

            state.sum_manager_commission = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.manager_commission
              }, 0)
            )

            state.sum_agent_commission = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.agent_commission
              }, 0)
            )

            state.sum_subtotal_amount = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.subtotal_amount
              }, 0)
            )
          }
        ),
        function () {
          useLoadingStateStore.setIsLoading(false)
        },
        1000,
        12000
      )
    }
  }
</script>
