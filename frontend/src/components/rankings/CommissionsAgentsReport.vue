<template>
  <div class="card">
    <div>
      <ul
        class="flex p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900"
      >
        <template :key="idx" v-for="(name, idx) in tabs">
          <li class="pr-4">
            <a
              v-ripple
              class="flex items-center px-6 py-4 transition-colors duration-150 cursor-pointer hover:bg-100 dark:hover:bg-700 rounded-border p-ripple"
              :class="{
                'border-blue-600 text-blue-600 hover:border-blue-600':
                  state.activeTab === name.value,
                'text-700 dark:text-100': state.activeTab !== name.value
              }"
              @click="state.activeTab = name.value"
            >
              <span class="text-2xl font-medium">{{ name.name }}</span>
            </a>
          </li>
          <li class="flex items-center">
            <div style="width: 1px; height: 50%" class="border border-r"></div>
          </li>
        </template>
      </ul>
    </div>
    <div class="flex flex-wrap justify-center m-4">
      <label
        for="display_toggle"
        class="block m-1 mr-2 text-xl text-900 dark:text-0"
      >
        Closed commission
      </label>
      <toggleSwitch
        class="m-1 text-sm"
        v-model="state.closedCommission"
        id="display_toggle"
        :disabled="true"
        @change="toggleClosedCommissionOnly"
      />
      <label
        v-if="state.closed_date"
        for="display_toggle"
        class="block m-1 mr-2 text-xl text-900 dark:text-0"
      >
        Closed on {{ dfc(state.closed_date) }}
      </label>
      <label
        v-else
        for="display_toggle"
        class="block m-1 mr-2 text-xl text-900 dark:text-0"
      >
        Not closed.
      </label>
    </div>
    <div class="flex flex-wrap justify-center mt-2">
      <Select
        v-if="$ability.can('read', 'can_change_individual_commission_users')"
        class="w-3/12"
        v-model="state.selectedUser"
        :options="mappedUsers"
        placeholder="Select a User"
        optionLabel="label"
        optionValue="value"
        @change="handleMultiSelectChange()"
      />
    </div>
    <div class="flex flex-wrap justify-center">
      <DateRangeSelection
        :isBiWeeklyPicker="true"
        :isMonthPicker="false"
        @selectedDates="setDates"
      />
    </div>
    <DataTable
      v-if="!state.isLoading && state.activeTab == 'containers'"
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

    <DataTable
      v-if="
        state.activeTab == 'containers' &&
        !state.isManagersOnly &&
        !state.isLoading
      "
      :value="state.result"
      id="general_export"
    >
      <Column :frozen="true" field="agent_name" header="Agent" :sortable="true">
        <template #body="slotProps">
          <p>{{ slotProps.data.agent_name }}</p>
        </template>
      </Column>
      <Column field="sum_agent_commission" header="Agent commission"></Column>

      <ColumnGroup type="footer">
        <Row>
          <Column footer="Totals" :colspan="1" footerStyle="text-align:right" />
          <Column :footer="state.total_sum_agent_commission" />
        </Row>
      </ColumnGroup>
    </DataTable>
    <LoadingTable
      v-if="state.isLoading && !state.isManagersOnly"
      :columns="agentCommissionsColumns"
    />

    <DataTable
      v-if="!state.isLoading && state.activeTab == 'accessories'"
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
      <Column field="commission" header="Total Commission" sortable>
        <template #body="slotProps">
          {{ $fc(slotProps.data.commission) }}
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
      <Column field="subtotal_amount" header="Subtotal" sortable>
        <template #body="slotProps">
          {{ $fc(slotProps.data.subtotal_amount) }}
        </template>
      </Column>

      <ColumnGroup type="footer">
        <Row>
          <Column footer="Totals" :colspan="3" footerStyle="text-align:right" />
          <Column :footer="state.sum_total_commission" />
          <Column footer="Totals" :colspan="2" footerStyle="text-align:right" />
          <Column :footer="state.sum_subtotal_amount" />
        </Row>
      </ColumnGroup>
    </DataTable>
    <LoadingTable v-if="state.isLoading" :columns="managerCommissionsColumns" />
    <ColumnGroup type="footer">
      <Row>
        <Column footer="Totals" :colspan="1" footerStyle="text-align:right" />
        <Column :footer="state.total_sum_agent_commission" />
      </Row>
    </ColumnGroup>
    <LoadingTable
      v-if="state.isLoading && !state.isManagersOnly"
      :columns="agentCommissionsColumns"
    />
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
  import { reactive, ref, inject, onMounted, computed, watch } from "vue"
  import DateRangeSelection from "./DateRangeSelection.vue"
  import ReportsApi from "@/api/reports"
  import IntervalManager from "@/service/IntervalManager.js"
  import { loadingStateStore } from "@/store/modules/loadingState.js"
  import { useUsers } from "@/store/modules/users"
  import { df, dfc } from "@/service/DateFormat.js"
  import { exportHtmlToPdf } from "@/utils/htmlToPdf.js"
  import { data } from "autoprefixer"
  import CommissionsIndividualReport from "./CommissionsIndividualReport.vue"
  import LoadingTable from "@/components/loadingTable/LoadingTable.vue"
  import CommissionApi from "@/api/commission.js"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import CustomerApi from "@/api/customers"
  import CustomerOrderDetail from "@/components/invoicing/CustomerOrderDetail.vue"

  const commissionApi = new CommissionApi()
  const customersStore = useCustomerOrder()
  const customerApi = new CustomerApi()

  const $fc = inject("$formatCurrency")
  const $ability = inject("$ability")

  const usersStore = useUsers()
  const useLoadingStateStore = loadingStateStore()
  const intervalManager = new IntervalManager()

  const reportsApi = new ReportsApi()

  const dates = ref()

  const agentCommissionsColumns = [
    { field: "agent_name", header: "Agent" },
    { field: "total_sum_agent_commission", header: "Agent Commission" }
  ]

  const managerCommissionsColumns = [
    { field: "manager_name", header: "Manager" },
    { field: "sum_total_amount", header: "Total Completed Amount" },
    { field: "sum_total_commission", header: "Commission" }
  ]

  const state = reactive({
    startDateTimestamp: null,
    endDateTimestamp: null,
    selectedConditions: [],
    selectedProductTypes: [],
    customerOrder: {},
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
    dates: {},
    selectedUser: null,
    isManagersOnly: true,
    isManagersOnlyLabel: "Managers Only",
    total_sum_total_amount: 0,
    total_sum_total_commission: 0,
    total_sum_agent_commission: 0,
    closedCommission: false,
    closed_date: null,
    activeTab: "containers"
  })

  onMounted(async () => {})

  const mappedUsers = computed(() => {
    return usersStore.users
      .filter((u) => u.is_active)
      .map((u) => {
        return {
          label: u?.full_name ? u?.full_name : "",
          value: u
        }
      })
      .sort((a, b) => a?.label?.localeCompare(b.label))
  })

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

  const setDates = async (dataStart, dataEnd) => {
    state.dates = { start_date: dataStart, end_date: dataEnd }
    state.isLoading = true
    state.startDateTimestamp = dataStart
    state.endDateTimestamp = dataEnd

    while (true) {
      const { data, error } = await commissionApi.closed_commissions_date({
        start_date: dataStart,
        end_date: dataEnd
      })
      state.closed_date = data.value
      if (error.value == null) {
        break
      }
      await sleep(1000)
    }

    if (state.closed_date != null) {
      state.closedCommission = true
    } else {
      state.closedCommission = false
    }

    handleMultiSelectChange()
  }

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

  const handleMultiSelectChange = async (event) => {
    state.isLoading = true
    if (state.activeTab == "containers") {
      if (!state.closedCommission) {
        const dataObj = {
          begin_date: state.startDateTimestamp,
          end_date: state.endDateTimestamp,
          account_id: 1,
          run_by: usersStore.currentUser.full_name,
          can_read_all:
            usersStore.currentUser.permissions.includes("read:all-rankings"),
          user_id:
            state.selectedUser != null
              ? state.selectedUser.id
              : usersStore.currentUser.id
        }

        await reportsApi.runByName(
          "commissions_agents_individual_report",
          dataObj
        )
        intervalManager.runFunctionInInterval(
          runFunctionInInterval(
            "commissions_agents_individual_report",
            dataObj,
            function (result) {
              state.result = result
              state.result = state.result.filter((item, index, self) => {
                return (
                  index ===
                  self.findIndex(
                    (t) => t.display_order_id === item.display_order_id
                  )
                )
              })

              state.sum_profit = $fc(
                state.result.reduce((accumulator, currentValue) => {
                  return accumulator + currentValue.profit
                }, 0)
              )

              state.sum_total_commission = $fc(
                state.result.reduce((accumulator, currentValue) => {
                  return accumulator + currentValue.total_commission
                }, 0)
              )

              state.sum_manager_commission = $fc(
                state.result.reduce((accumulator, currentValue) => {
                  return accumulator + currentValue.manager_commission
                }, 0)
              )

              state.sum_agent_commission = $fc(
                state.result.reduce((accumulator, currentValue) => {
                  return accumulator + currentValue.agent_commission
                }, 0)
              )

              state.sum_subtotal_amount = $fc(
                state.result.reduce((accumulator, currentValue) => {
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
          begin_date: state.startDateTimestamp,
          end_date: state.endDateTimestamp,
          account_id: 1,
          run_by: usersStore.currentUser.full_name,
          can_read_all:
            usersStore.currentUser.permissions.includes("read:all-rankings"),
          user_id:
            state.selectedUser != null
              ? state.selectedUser.id
              : usersStore.currentUser.id
        }

        await reportsApi.runByName(
          "commissions_closed_agents_individual_report",
          dataObj
        )
        intervalManager.runFunctionInInterval(
          runFunctionInInterval(
            "commissions_closed_agents_individual_report",
            dataObj,
            function (result) {
              state.result = result
              state.result = state.result.filter((item, index, self) => {
                return (
                  index ===
                  self.findIndex(
                    (t) => t.display_order_id === item.display_order_id
                  )
                )
              })
              state.sum_profit = $fc(
                state.result.reduce((accumulator, currentValue) => {
                  return accumulator + currentValue.profit
                }, 0)
              )

              state.sum_total_commission = $fc(
                state.result.reduce((accumulator, currentValue) => {
                  return accumulator + currentValue.total_commission
                }, 0)
              )

              state.sum_manager_commission = $fc(
                state.result.reduce((accumulator, currentValue) => {
                  return accumulator + currentValue.manager_commission
                }, 0)
              )

              state.sum_agent_commission = $fc(
                state.result.reduce((accumulator, currentValue) => {
                  return accumulator + currentValue.agent_commission
                }, 0)
              )

              state.sum_subtotal_amount = $fc(
                state.result.reduce((accumulator, currentValue) => {
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
    } else if (state.activeTab == "accessories") {
      const dataObj = {
        begin_date: state.startDateTimestamp,
        end_date: state.endDateTimestamp,
        account_id: 1,
        run_by: usersStore.currentUser.full_name,
        can_read_all:
          usersStore.currentUser.permissions.includes("read:all-rankings"),
        user_id:
          state.selectedUser != null
            ? state.selectedUser.id
            : usersStore.currentUser.id
      }

      await reportsApi.runByName(
        "commissions_individual_accessories_report",
        dataObj
      )
      intervalManager.runFunctionInInterval(
        runFunctionInInterval(
          "commissions_individual_accessories_report",
          dataObj,
          function (result) {
            state.result = result
            state.result = state.result.filter((item, index, self) => {
              return (
                index ===
                self.findIndex(
                  (t) => t.display_order_id === item.display_order_id
                )
              )
            })
            state.sum_total_commission = $fc(
              state.result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.commission
              }, 0)
            )

            state.sum_subtotal_amount = $fc(
              state.result.reduce((accumulator, currentValue) => {
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

  const tabs = computed(() => {
    let tabs = [
      { name: "Containers", value: "containers" },
      { name: "Accessories", value: "accessories" }
    ]
    return tabs
  })

  const toggleClosedCommissionOnly = () => {
    setDates(state.dates.start_date, state.dates.end_date)
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
  watch(
    () => state.activeTab,
    async (newVal, oldVal) => {
      if (newVal) {
        handleMultiSelectChange()
      }
    }
  )
</script>
