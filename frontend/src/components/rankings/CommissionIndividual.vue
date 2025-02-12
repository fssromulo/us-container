<template>
  <div class="flex flex-wrap justify-center mt-2" v-if="!props.selectedUser">
    <DateRangeSelection
      :isBiWeeklyPicker="!props.teamCommission"
      :isMonthPicker="props.teamCommission"
      @selectedDates="setDates"
    />
  </div>

  <div class="flex flex-wrap justify-center mt-2">
    <Select
      v-if="
        $ability.can('read', 'can_change_individual_commission_users') &&
        !props.selectedUser
      "
      class="w-3/12"
      v-model="state.selectedUser"
      :loading="state.usersLoading"
      :options="mappedUsers"
      placeholder="Select a User"
      optionLabel="label"
      optionValue="value"
    />
  </div>
  <div
    class="flex flex-wrap justify-center mt-2"
    v-if="
      $ability.can('read', 'can_change_individual_commission_users') &&
      !props.selectedUser
    "
  >
    <Button
      label="Reset"
      icon="pi pi-refresh"
      :loading="state.loading"
      class="mb-2 p-button-help"
      @click="reset"
    />
  </div>

  <div
    class="flex flex-wrap justify-center mt-2"
    v-if="!state.isQualified && props.teamCommission"
  >
    <p class="text-lg">
      Your sales have not qualified you to recieve team commissions.
    </p>
    <p class="text">
      You are at {{ $fc(state.amountSold) }} in sales and you need $20,000
    </p>
  </div>
  <ProgressBar
    v-if="!state.isQualified && props.teamCommission"
    :value="state.percentageQualified"
  ></ProgressBar>
  <DataTable
    v-if="!state.loading && state.isQualified"
    scrollHeight="70vh"
    :scrollable="true"
    scrollDirection="both"
    ref="dt"
    :filters="state.filters"
    :value="state.commissions"
    class="p-datatable-sm"
    sortField="commission_owed"
    :sortOrder="-1"
    :style="`width: ${tableWidth}`"
  >
    <template #header>
      <div class="grid grid-cols-12 gap-4" :class="{ 'mt-2': smAndSmaller }">
        <div
          class="md:col-span-2 sm:col-span-4"
          :class="{ 'ml-2': smAndSmaller }"
        >
          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText
              style="max-width: 20em"
              v-model="state.filters['global'].value"
              :placeholder="`Search`"
            />
          </IconField>
        </div>
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
          class="md:col-span-2 sm:col-span-12"
          :class="{ 'mt-2 ml-5': smAndSmaller }"
        >
          <p class="text-lg">Closed on: {{ state.generatedFromClosedDate }}</p>
        </div>
      </div>
    </template>
    <Column field="agent" :sortable="true" header="Manager"></Column>
    <Column field="assistant" :sortable="true" header="Agent"></Column>
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
    <Column
      v-if="totals.calculated_profit != 0"
      field="display_profit"
      sortField="calculated_profit"
      :sortable="true"
      header="Profit"
    ></Column>
    <Column
      v-if="$ability.can('read', 'commissions-owed')"
      field="display_commission_owed"
      sortField="commission_owed"
      :sortable="true"
      header="Total Commission"
    ></Column>
    <Column
      v-if="$ability.can('read', 'commissions-owed') && !props.teamCommission"
      field="display_manager_commission_owed"
      sortField="manager_commission_owed"
      :sortable="true"
      header="Manager Commission"
    ></Column>
    <Column
      field="display_agent_commission_owed"
      sortField="agent_commission_owed"
      :sortable="true"
      header="Agent Commission"
      v-if="!props.teamCommission"
    ></Column>
    <Column
      field="delivered_at"
      :sortable="true"
      header="Order delivered"
    ></Column>
    <Column field="paid_at" :sortable="true" header="Order Paid"></Column>
    <Column
      v-if="$ability.can('read', 'commissions-owed')"
      field="display_sub_total_price"
      sortField="sub_total_price"
      :sortable="true"
      header="Sub Total"
    ></Column>
    <ColumnGroup
      v-if="
        !$ability.can('read', 'commissions-owed') &&
        totals.agent_commission_owed === 'N/A'
      "
      type="footer"
    >
      <Row>
        <Column :colspan="3" footer="Totals:" footerStyle="text-align:right" />
        <Column :footer="totals.calculated_profit" />
        <Column
          v-if="$ability.can('read', 'commissions-owed')"
          :footer="totals.commission_owed"
        />
        <Column :colspan="3" />
      </Row>
    </ColumnGroup>
    <ColumnGroup v-if="$ability.can('read', 'commissions-owed')" type="footer">
      <Row>
        <Column :colspan="3" footer="Totals:" footerStyle="text-align:right" />
        <Column
          v-if="totals.calculated_profit != 0"
          :footer="totals.calculated_profit"
        />
        <Column :footer="totals.commission_owed" />
        <Column
          :footer="totals.manager_commission_owed"
          v-if="!props.teamCommission"
        />
        <Column
          :footer="totals.agent_commission_owed"
          v-if="!props.teamCommission"
        />
        <Column :colspan="3" />
      </Row>
    </ColumnGroup>
    <ColumnGroup type="footer">
      <Row v-if="totals.calculated_profit == 0">
        <Column :colspan="3" footer="Totals:" footerStyle="text-align:right" />
        <Column :footer="totals.agent_commission_owed" />
        <Column :colspan="3" />
      </Row>
      <Row v-else>
        <Column :colspan="3" footer="Totals:" footerStyle="text-align:right" />
        <Column :footer="totals.calculated_profit" />
        <Column :footer="totals.agent_commission_owed" />
        <Column :colspan="3" />
      </Row>
    </ColumnGroup>
  </DataTable>
  <LoadingTable v-if="state.loading" :columns="commissionColumns" />
  <div class="flex flex-wrap justify-center mt-2">
    <p class="text-lg">{{ state.commissions.length }} Order(s)</p>
  </div>
  <DataTable
    v-if="props.teamCommission"
    :scrollable="true"
    scrollDirection="vertical"
    ref="dt"
    :value="teamLead"
    class="w-4/12 mt-8 ml-4 p-datatable-sm"
  >
    <Column
      field="team_member.full_name"
      :sortable="true"
      header="Team Members"
    ></Column>
  </DataTable>
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
  import {
    reactive,
    computed,
    watch,
    onMounted,
    onBeforeMount,
    ref,
    inject
  } from "vue"
  import CommissionService from "@/service/Commission.js"
  import CustomerService from "@/service/Customers"
  import CustomerApi from "@/api/customers"

  import { useAuth0 } from "@auth0/auth0-vue"
  import DateRangeSelection from "./DateRangeSelection.vue"
  import { FilterMatchMode } from "@primevue/core/api"
  import LoadingTable from "@/components/loadingTable/LoadingTable.vue"
  import CustomerOrderDetail from "@/components/invoicing/CustomerOrderDetail.vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { breakpointsTailwind, set, useBreakpoints } from "@vueuse/core"
  import { changeCountry } from "@/utils/formatCurrency.js"
  import cloneDeep from "lodash.clonedeep"

  import { useUsers } from "@/store/modules/users"
  import UsersService from "@/service/User"
  import { useToast } from "primevue/usetoast"
  import { dfl } from "../../service/DateFormat"
  import ProgressBar from "primevue/progressbar"

  import Lock from "../../service/Lock.js"
  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")

  const lock = new Lock()
  const userStore = useUsers()

  const toast = useToast()

  const $ability = inject("$ability")
  const $fc = inject("$formatCurrency")
  const $DateTime = inject("$DateTime")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const usersStore = useUsers()
  const usersService = new UsersService()

  const { user } = useAuth0()
  const authUser = user
  const commissionService = new CommissionService()
  const customerService = new CustomerService()
  const customersStore = useCustomerOrder()

  const customerApi = new CustomerApi()

  const props = defineProps({
    teamCommission: {
      type: Boolean,
      default: false
    },
    selectedUser: {
      type: Object,
      default: null
    },
    dates: {
      type: Object,
      default: null
    }
  })
  const largerThanSm = breakpoints.greater("sm")
  const lgAndSmaller = breakpoints.smallerOrEqual("lg")
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg")

  onBeforeMount(() => {
    //  let account_country = userStore.cms.account_country;
    //  changeCountry(account_country)
  })

  const tableWidth = computed(() => {
    if (greaterOrEqualLarge.value) {
      return "92vw"
    } else if (lgAndSmaller.value) {
      return "100vw"
    } else if (largerThanSm.value) {
      return "90vw"
    }
  })

  const commissionColumns = [
    { field: "agent", display: "Manager" },
    { field: "units", display: "Agent" },
    { field: "display_sub_total_price", display: "Order #" },
    { field: "display_sub_total_price", display: "Profit" },
    { field: "display_sub_total_price", display: "Total Commission" },
    { field: "display_sub_total_price", display: "Manager Commission" },
    { field: "display_sub_total_price", display: "Agent Commission" },
    { field: "display_sub_total_price", display: "Order delivered" },
    { field: "display_sub_total_price", display: "Order Paid" },
    { field: "display_sub_total_price", display: "Sub Total" }
  ]

  const mappedUsers = computed(() => {
    if (state.usersLoading) {
      return []
    }
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

  const teamLead = computed(() => {
    return usersStore.users.find((u) => u.id === usersStore.currentUser.id)
      ?.team_lead
  })

  const reset = () => {
    state.selectedUser = null
    state.refreshKey++
  }

  onMounted(async () => {
    state.loading = true
    let account_country = userStore?.cms?.account_country
    changeCountry(account_country)

    // await lock.acquire()
    await commissionService.refreshUsers()
    // await lock.release()

    state.selectedUser = cloneDeep(props.selectedUser)
    if ($isObjectPopulated(props.dates)) {
      const { start_date, end_date } = props.dates
      await setDates(start_date, end_date)
    }
    state.loading = false
  })
  const dt = ref()

  const totals = computed(() => {
    state.refreshKey
    if (state.commissions.length === 0) {
      return {
        calculated_profit: 0,
        commission_owed: 0,
        manager_commission_owed: 0,
        agent_commission_owed: 0
      }
    }
    let result = state.commissions.reduce(
      (acc, curr) => {
        return {
          calculated_profit: acc.calculated_profit + curr.calculated_profit,
          commission_owed: acc.commission_owed + curr.commission_owed,
          manager_commission_owed:
            acc.manager_commission_owed + curr.manager_commission_owed,
          agent_commission_owed:
            acc.agent_commission_owed + curr.agent_commission_owed
        }
      },
      {
        calculated_profit: 0,
        commission_owed: 0,
        manager_commission_owed: 0,
        agent_commission_owed: 0
      }
    )
    result = {
      calculated_profit: $fc(result.calculated_profit),
      commission_owed: $fc(result.commission_owed),
      manager_commission_owed: $fc(result.manager_commission_owed),
      agent_commission_owed: $fc(result.agent_commission_owed)
    }
    return result
  })

  const state = reactive({
    commissions: [],
    isQualified: false,
    percentageQualified: 0,
    amountSold: 0,
    individualOrderLoading: null,
    updateOrderDialog: false,
    customerOrder: {},
    loading: false,
    usersLoading: false,
    filters: {},
    selectedUser: null,
    refreshKey: 0,
    generatedFromClosedDate: null
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  const exportCSV = () => dt.value.exportCSV()

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

  const setDates = async (start_date, end_date) => {
    // adding some reset code so that individual commissions can work properly when switching from periods that
    // have commissions to those that do not
    // await lock.acquire()

    state.commissions = []
    state.generatedFromClosedDate = "Not Closed"
    if (start_date === "Invalid DateTime" || end_date === "Invalid DateTime") {
      return
    }
    if (start_date && end_date) {
      console.log("setting dates")
      console.log(start_date, end_date)
      state.start_date = start_date
      state.end_date = end_date
    }

    state.loading = true
    state.selectedUser = state.selectedUser || usersStore.currentUser

    let commissionResponse
    if (props.teamCommission) {
      commissionResponse = await commissionService.getTeamCommission(
        state.start_date,
        state.end_date,
        state.selectedUser
      )
    } else {
      commissionResponse = await commissionService.getIndividualCommission(
        state.start_date,
        state.end_date,
        state.selectedUser
      )
    }

    if (commissionResponse?.commissions?.length > 0) {
      state.commissions = commissionService.formatIndividualCommission(
        commissionResponse.commissions
      )
      state.generatedFromClosedDate = commissionResponse.closed_date
        ? dfl(commissionResponse.closed_date)
        : "Not closed"
      toast.add({
        severity: "success",
        summary: "Success",
        detail: commissionResponse.from_closed
          ? "Commission From closed period"
          : "Commission Generated",
        life: 2000,
        group: "br"
      })
    }

    if (!props.teamCommission) {
      state.isQualified = true
    }

    if (props.teamCommission) {
      // take m/d/y and convert to luxon date
      start_date = $DateTime.fromFormat(state.start_date, "M/d/yy")
      end_date = $DateTime.fromFormat(state.end_date, "M/d/yy")
      const rankings = await commissionService.getRankings(start_date, end_date)
      if (!rankings) {
        state.loading = false
        return
      }
      let sub_total_price_acc = 0

      sub_total_price_acc = rankings.reduce((acc, curr) => {
        return acc + curr.sub_total_price
      }, 0)
      console.log("sub_total_price", sub_total_price_acc)
      state.isQualified = sub_total_price_acc >= 20000
      state.amountSold = sub_total_price_acc
      state.percentageQualified = ((sub_total_price_acc / 20000) * 100).toFixed(
        2
      )
    }

    state.refreshKey++
    state.loading = false
    // await lock.release()
  }

  watch(
    () => state.selectedUser,
    async (newVal, oldVal) => {
      // if (newVal === oldVal) {
      //   return;
      // }
      if (newVal) {
        await setDates()
      }
    },
    { immediate: true, deep: true }
  )

  watch(
    () => usersStore.currentUser,
    async (newVal, oldVal) => {
      if (newVal === oldVal) {
        return
      }
      if (newVal && !$isObjectPopulated(props.dates)) {
        await setDates()
      }
    },
    { immediate: true, deep: true }
  )
</script>
