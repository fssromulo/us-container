<template>
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
  <div class="card">
    <div class="flex justify-center flex-wrap m-4">
      <label
        for="display_toggle"
        class="text-900 dark:text-0 text-xl block m-1 mr-2"
      >
        Closed commission
      </label>
      <toggleSwitch
        class="text-sm m-1"
        v-model="state.closedCommission"
        id="display_toggle"
        :disabled="true"
        @change="toggleClosedCommissionOnly"
      />
      <label
        v-if="state.closed_date"
        for="display_toggle"
        class="text-900 dark:text-0 text-xl block m-1 mr-2"
      >
        Closed on {{ dfc(state.closed_date) }}
      </label>
      <label
        v-else
        for="display_toggle"
        class="text-900 dark:text-0 text-xl block m-1 mr-2"
      >
        Not closed.
      </label>
    </div>
    <div class="flex justify-center flex-wrap m-4">
      <label
        for="display_toggle"
        class="text-900 dark:text-0 text-xl block m-1 mr-2"
        >{{ state.isManagersOnlyLabel }}</label
      >
      <toggleSwitch
        class="text-sm m-1"
        v-model="state.isManagersOnly"
        id="display_toggle"
        @change="toggleManagersOnly"
      />
    </div>
    <div class="flex justify-center flex-wrap">
      <DateRangeSelection
        :isBiWeeklyPicker="true"
        :isMonthPicker="false"
        @selectedDates="setDates"
      />
    </div>
    <DataTable
      ref="dt"
      v-if="
        state.isManagersOnly &&
        !state.isLoading &&
        state.activeTab == 'containers'
      "
      :value="state.result"
      id="general_export"
    >
      <template #header>
        <div class="grid grid-cols-12 gap-4 mt-2">
          <div
            class="md:col-span-2 sm:col-span-4"
            :class="{ 'ml-2': smAndSmaller }"
          >
            <Button
              label="Export"
              icon="pi pi-upload"
              class="p-button-help"
              @click="exportCSV($event)"
            />
          </div>
          <div
            class="md:col-span-2 sm:col-span-4"
            :class="{ 'ml-2': smAndSmaller }"
          >
            <Button
              label="Close commissions report"
              icon="pi pi-upload"
              class="p-button-help"
              :disabled="state.closedCommission || state.loadCloseCommissions"
              :loading="state.loadCloseCommissions"
              @click="closeCommissions($event)"
            />
          </div>
        </div>
      </template>
      <Column
        :frozen="true"
        field="manager_name"
        header="Agent"
        :sortable="true"
      >
        <template #body="slotProps">
          <Button
            size="small"
            class="p-button-text p-button-success"
            @click="openIndividualCommissions(slotProps.data)"
            :label="slotProps.data.manager_name"
            v-if="state.isManagersOnly"
          />
          <p v-else>{{ slotProps.data.manager_name }}</p>
        </template>
      </Column>
      <Column field="sum_total_amount" header="Total Completed Amount"></Column>

      <Column field="sum_total_commission" header="Commission"></Column>

      <ColumnGroup type="footer">
        <Row>
          <Column footer="Totals" :colspan="1" footerStyle="text-align:right" />
          <Column :footer="state.total_sum_total_amount" />
          <Column :footer="state.total_sum_total_commission" />
        </Row>
      </ColumnGroup>
    </DataTable>
    <LoadingTable
      v-if="state.isLoading && state.isManagersOnly"
      :columns="managerCommissionsColumns"
    />

    <DataTable
      ref="dtEveryone"
      v-if="
        !state.isManagersOnly &&
        !state.isLoading &&
        state.activeTab == 'containers'
      "
      :value="state.result"
      id="general_export"
    >
      <template #header>
        <div class="grid grid-cols-12 gap-4 mt-2">
          <div
            class="md:col-span-2 sm:col-span-4"
            :class="{ 'ml-2': smAndSmaller }"
          >
            <Button
              label="Export"
              icon="pi pi-upload"
              class="p-button-help"
              @click="exportCSVEveryone($event)"
            />
          </div>
        </div>
      </template>
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
    >
      <Column :frozen="true" field="name" header="Agent" :sortable="true">
        <template #body="slotProps">
          <p>{{ slotProps.data.name }}</p>
        </template>
      </Column>
      <Column field="total_commission" header="Total Commission"></Column>

      <ColumnGroup type="footer">
        <Row>
          <Column footer="Totals" :colspan="1" footerStyle="text-align:right" />
          <Column :footer="state.sum_total_commission" />
        </Row>
      </ColumnGroup>
    </DataTable>
    <LoadingTable
      v-if="state.isLoading && !state.isManagersOnly"
      :columns="agentCommissionsColumns"
    />

    <Dialog
      v-model:visible="state.selectedUser"
      dismissableMask
      closeOnEscape
      :breakpoints="{
        '2000px': '75vw',
        '1400px': '75vw',
        '1200px': '75vw',
        '992px': '85vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
      :modal="true"
    >
      <template #header>
        <div class="flex items-stretch">
          <div class="flex">
            <p class="text-3xl"> Orders</p>
          </div>
        </div>
      </template>
      <CommissionsIndividualReport
        :dates="state.dates"
        :selectedUser="state.selectedUser"
        :closed="state.closedCommission"
      />
    </Dialog>
  </div>
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
  import { useToast } from "primevue/usetoast"

  const commissionApi = new CommissionApi()

  const $fc = inject("$formatCurrency")

  const toast = useToast()

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
    interval1: null,
    interval2: null,
    interval3: null,
    interval4: null,
    activeTab: "containers",
    loadCloseCommissions: false
  })

  onMounted(async () => {})

  const dt = ref()
  const dtEveryone = ref()

  const tabs = computed(() => {
    let tabs = [
      { name: "Containers", value: "containers" },
      { name: "Accessories", value: "accessories" }
    ]
    return tabs
  })

  const setDates = async (dataStart, dataEnd) => {
    state.dates = { start_date: dataStart, end_date: dataEnd }
    state.isLoading = true
    state.startDateTimestamp = dataStart
    state.endDateTimestamp = dataEnd

    const { data, error } = await commissionApi.closed_commissions_date({
      start_date: dataStart,
      end_date: dataEnd
    })
    state.closed_date = data.value

    if (state.closed_date != null) {
      state.closedCommission = true
    } else {
      state.closedCommission = false
    }

    const intervals = [
      state.interval1,
      state.interval2,
      state.interval3,
      state.interval4
    ]
    intervals.forEach((el) => {
      if (el != null) clearInterval(el)
    })

    handleMultiSelectChange()
  }

  const closeCommissions = async () => {
    const dataObj = {
      begin_date: state.startDateTimestamp,
      end_date: state.endDateTimestamp,
      account_id: usersStore.currentUser.account_id,
      run_by: usersStore.currentUser.full_name
    }

    state.loadCloseCommissions = true

    const { data, error } = await reportsApi.closeCommissions(dataObj)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error closing commissions.",
        group: "br",
        life: 5000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Successfully closed commission.",
        group: "br",
        life: 5000
      })
      state.closedCommission = true
      const data_commission = await commissionApi.closed_commissions_date({
        start_date: state.startDateTimestamp,
        end_date: state.endDateTimestamp
      })
      state.closed_date = data_commission.data.value

      if (state.closed_date != null) {
        state.closedCommission = true
      } else {
        state.closedCommission = false
      }
    }
    state.loadCloseCommissions = false
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

  const openIndividualCommissions = (data) => {
    state.selectedUser = data?.manager_id
  }

  const handleMultiSelectChange = async (event) => {
    if (state.activeTab == "containers") {
      if (!state.closedCommission) {
        if (state.isManagersOnly) {
          state.result = []
          const dataObj = {
            begin_date: state.startDateTimestamp,
            end_date: state.endDateTimestamp,
            account_id: usersStore.currentUser.account_id,
            run_by: usersStore.currentUser.full_name,
            can_read_all:
              usersStore.currentUser.permissions.includes("read:all-rankings"),
            user_id: usersStore.currentUser.id
          }

          await reportsApi.runByName("commissions_report", dataObj)
          state.interval1 = intervalManager.runFunctionInInterval(
            runFunctionInInterval(
              "commissions_report",
              dataObj,
              function (result) {
                console.log(state.startDateTimestamp, state.endDateTimestamp)
                state.result = result
                state.result = state.result.map((el) => {
                  return {
                    manager_name: el.manager_name,
                    sum_total_commission: $fc(el.sum_total_commission),
                    sum_total_amount: $fc(el.sum_total_amount),
                    manager_id: el.manager_id
                  }
                })

                state.total_sum_total_amount = $fc(
                  result.reduce((accumulator, currentValue) => {
                    return accumulator + currentValue.sum_total_amount
                  }, 0)
                )

                state.total_sum_total_commission = $fc(
                  result.reduce((accumulator, currentValue) => {
                    return accumulator + currentValue.sum_total_commission
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
          state.result = []
          const dataObj = {
            begin_date: state.startDateTimestamp,
            end_date: state.endDateTimestamp,
            account_id: usersStore.currentUser.account_id,
            run_by: usersStore.currentUser.full_name,
            can_read_all:
              usersStore.currentUser.permissions.includes("read:all-rankings"),
            user_id: usersStore.currentUser.id
          }

          await reportsApi.runByName("commissions_agents_report", dataObj)
          state.interval2 = intervalManager.runFunctionInInterval(
            runFunctionInInterval(
              "commissions_agents_report",
              dataObj,
              function (result) {
                state.result = result
                state.result = state.result.map((el) => {
                  return {
                    agent_name: el.agent_name,
                    sum_agent_commission: $fc(el.sum_agent_commission)
                  }
                })

                state.total_sum_agent_commission = $fc(
                  result.reduce((accumulator, currentValue) => {
                    return accumulator + currentValue.sum_agent_commission
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
      } else {
        if (state.isManagersOnly) {
          state.result = []
          const dataObj = {
            begin_date: state.startDateTimestamp,
            end_date: state.endDateTimestamp,
            account_id: usersStore.currentUser.account_id,
            run_by: usersStore.currentUser.full_name,
            can_read_all:
              usersStore.currentUser.permissions.includes("read:all-rankings"),
            user_id: usersStore.currentUser.id
          }

          await reportsApi.runByName("commissions_closed_report", dataObj)
          state.interval3 = intervalManager.runFunctionInInterval(
            runFunctionInInterval(
              "commissions_closed_report",
              dataObj,
              function (result) {
                state.result = result
                state.result = state.result.map((el) => {
                  return {
                    manager_name: el.manager_name,
                    sum_total_commission: $fc(el.sum_total_commission),
                    sum_total_amount: $fc(el.sum_total_amount),
                    manager_id: el.manager_id
                  }
                })

                state.total_sum_total_amount = $fc(
                  result.reduce((accumulator, currentValue) => {
                    return accumulator + currentValue.sum_total_amount
                  }, 0)
                )

                state.total_sum_total_commission = $fc(
                  result.reduce((accumulator, currentValue) => {
                    return accumulator + currentValue.sum_total_commission
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
          state.result = []
          const dataObj = {
            begin_date: state.startDateTimestamp,
            end_date: state.endDateTimestamp,
            account_id: usersStore.currentUser.account_id,
            run_by: usersStore.currentUser.full_name,
            can_read_all:
              usersStore.currentUser.permissions.includes("read:all-rankings"),
            user_id: usersStore.currentUser.id
          }

          await reportsApi.runByName(
            "commissions_agents_closed_report",
            dataObj
          )
          state.interval4 = intervalManager.runFunctionInInterval(
            runFunctionInInterval(
              "commissions_agents_closed_report",
              dataObj,
              function (result) {
                state.result = result
                state.result = state.result.map((el) => {
                  return {
                    agent_name: el.agent_name,
                    sum_agent_commission: $fc(el.sum_agent_commission)
                  }
                })

                state.total_sum_agent_commission = $fc(
                  result.reduce((accumulator, currentValue) => {
                    return accumulator + currentValue.sum_agent_commission
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
    } else if (state.activeTab == "accessories") {
      state.result = []
      const dataObj = {
        begin_date: state.startDateTimestamp,
        end_date: state.endDateTimestamp,
        account_id: usersStore.currentUser.account_id,
        run_by: usersStore.currentUser.full_name,
        can_read_all:
          usersStore.currentUser.permissions.includes("read:all-rankings"),
        user_id: usersStore.currentUser.id
      }

      await reportsApi.runByName("commissions_accessories_report", dataObj)
      intervalManager.runFunctionInInterval(
        runFunctionInInterval(
          "commissions_accessories_report",
          dataObj,
          function (result) {
            state.result = result
            state.result = state.result.map((el) => {
              return {
                name: el.agent_name,
                total_commission: $fc(el.total_commission)
              }
            })

            state.sum_total_commission = $fc(
              result.reduce((accumulator, currentValue) => {
                return accumulator + currentValue.total_commission
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

  const toggleManagersOnly = () => {
    if (state.isManagersOnly) {
      state.isManagersOnlyLabel = "Managers Only"
    } else {
      state.isManagersOnlyLabel = "Everyone"
    }
    setDates(state.dates.start_date, state.dates.end_date)
  }

  const toggleClosedCommissionOnly = () => {
    setDates(state.dates.start_date, state.dates.end_date)
  }

  const exportCSV = () => dt.value.exportCSV()
  const exportCSVEveryone = () => dtEveryone.value.exportCSV()

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
