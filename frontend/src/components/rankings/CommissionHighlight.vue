<template>
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
      :isBiWeeklyPicker="!props.isTeamCommission"
      :isMonthPicker="props.isTeamCommission"
      @selectedDates="setDates"
    />
  </div>
  <DataTable
    v-if="!state.loading"
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
      <div class="grid grid-cols-12 gap-4 mt-2">
        <div
          class="md:col-span-2 sm:col-span-6"
          :class="{ 'ml-2': smAndSmaller }"
        >
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText
              style="max-width: 20em"
              v-model="state.filters['global'].value"
              :placeholder="`Search`"
            />
          </span>
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
          class="md:col-span-2 sm:col-span-10"
          :class="{ 'ml-5 mt-4 mb-2': smAndSmaller }"
        >
          <p class="text-lg">Closed on: {{ state.fromClosedDate }}</p>
        </div>

        <div
          class="md:col-span-2 sm:col-span-5"
          :class="{ 'ml-5 mt-2 mb-2': smAndSmaller }"
        >
          <Button
            v-if="isSuperUser"
            label="Close Commission Period"
            icon="pi pi-close"
            :loading="state.closeComissionLoading"
            class="p-button-success"
            @click="closeCommissions()"
          />
        </div>
        <div
          class="md:col-span-2 sm:col-span-5"
          :class="{ 'ml-5 mt-2 mb-2': smAndSmaller }"
        >
          <Button
            v-if="isSuperUser"
            label="Re-open Commission Period"
            icon="pi pi-close"
            :loading="state.openCommissionLoading"
            class="p-button-success"
            @click="openCommissionPeriod()"
          />
        </div>
      </div>
    </template>
    <template #empty> Select a commission range </template>

    <Column :frozen="true" field="agent" header="Agent" :sortable="true">
      <template #body="slotProps">
        <Button
          size="small"
          class="p-button-text p-button-success"
          @click="openIndividualCommissions(slotProps.data)"
          :label="slotProps.data.agent"
          v-if="state.isManagersOnly"
        />
        <p v-else>{{ slotProps.data.agent }}</p>
      </template>
    </Column>
    <Column
      field="display_sub_total_price"
      sortField="sub_total_price"
      :sortable="true"
      header="Total Completed Amount"
      v-if="state.isManagersOnly"
    ></Column>
    <Column
      field="display_commission_owed"
      :defaultSortOrder="-1"
      sortField="commission_owed"
      :sortable="true"
      header="Commission"
    ></Column>
    <ColumnGroup v-if="totals.sub_total_price" type="footer">
      <Row>
        <Column footer="Totals:" footerStyle="text-align:right" />
        <Column :footer="totals.sub_total_price" v-if="state.isManagersOnly" />
        <Column :footer="totals.commission_owed" />
      </Row>
    </ColumnGroup>
  </DataTable>
  <LoadingTable v-if="state.loading" :columns="highlightColumns" />

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
          <p class="text-3xl">{{ state.selectedUser?.full_name }}'s Orders</p>
        </div>
      </div>
    </template>
    <CommissionIndividual
      :team-commission="props.isTeamCommission"
      :dates="state.dates"
      :selectedUser="state.selectedUser"
    />
  </Dialog>
</template>

<script setup>
  import { reactive, computed, inject, onMounted, ref } from "vue"
  import CommissionService from "@/service/Commission.js"
  import { useAuth0 } from "@auth0/auth0-vue"
  import DateRangeSelection from "./DateRangeSelection.vue"
  import UsersService from "../../service/User"
  import UserApi from "../../api/user"
  import { useUsers } from "../../store/modules/users"
  import { FilterMatchMode } from "@primevue/core/api"
  import { useToast } from "primevue/usetoast"
  import CommissionIndividual from "./CommissionIndividual.vue"
  import LoadingTable from "@/components/loadingTable/LoadingTable.vue"
  import { dfl } from "@/service/DateFormat.js"
  import Lock from "../../service/Lock.js"
  import { breakpointsTailwind, set, useBreakpoints } from "@vueuse/core"

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")
  const largerThanSm = breakpoints.greater("sm")
  const lgAndSmaller = breakpoints.smallerOrEqual("lg")
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg")

  const tableWidth = computed(() => {
    if (greaterOrEqualLarge.value) {
      return "92vw"
    } else if (lgAndSmaller.value) {
      return "100vw"
    } else if (largerThanSm.value) {
      return "90vw"
    }
  })

  const lock = new Lock()
  const toast = useToast()

  const userStore = useUsers()
  const usersService = new UsersService()
  const userApi = new UserApi()
  const $fc = inject("$formatCurrency")

  const { user } = useAuth0()
  const currentUserId = computed(() => user.value.sub.replace("auth0|", ""))
  const commissionService = new CommissionService()

  const isSuperUser = () => {
    return (
      ["andrei@usacontainers.co", "tanner.cordovatech@gmail.com"].findIndex(
        user.value.email
      ) > -1
    )
  }

  const highlightColumns = [
    { field: "agent", header: "Agent" },
    { field: "display_sub_total_price", header: "Total Completed Amount" },
    { field: "display_commission_owed", header: "Total Commission" }
  ]

  onMounted(async () => {
    if (userStore.users.length === 0) {
      const { data } = await userApi.getUsers()
      userStore.setUsers(data.value.map((u) => usersService.dtoUser(u)))
    }
  })

  const props = defineProps({
    isTeamCommission: {
      type: Boolean,
      default: false
    }
  })

  const totals = computed(() => {
    if (state.commissions.length === 0) {
      return {
        sub_total_price: 0,
        commission_owed: 0
      }
    }
    let result = state.commissions.reduce(
      (acc, curr) => {
        return {
          commission_owed: acc.commission_owed + curr.commission_owed,
          sub_total_price: acc.sub_total_price + curr.sub_total_price
        }
      },
      { commission_owed: 0, sub_total_price: 0 }
    )
    result = {
      sub_total_price: $fc(result.sub_total_price),
      commission_owed: $fc(result.commission_owed)
    }
    return result
  })

  const dt = ref()

  const state = reactive({
    commissions: [],
    selectedUser: null,
    dates: {
      start_date: null,
      end_date: null
    },
    filters: {},
    loading: false,
    closeComissionLoading: false,
    openCommissionLoading: false,
    fromClosedDate: null,
    isManagersOnly: true,
    isManagersOnlyLabel: "Managers Only"
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  const openIndividualCommissions = (data) => {
    state.selectedUser = data?.user || data.team_lead
  }

  const closeCommissions = async () => {
    state.closeComissionLoading = true
    const commissionResponse = await commissionService.closeCommissions(
      state.dates.start_date,
      state.dates.end_date,
      props.isTeamCommission,
      state.isManagersOnly
    )
    state.commissions = commissionService.formatHighlightCommission(
      commissionResponse.commissions
    )
    state.fromClosedDate = dfl(commissionResponse.closed_date)
    state.closeComissionLoading = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Commission period closed",
      life: 3000,
      group: "br"
    })
  }

  const openCommissionPeriod = async () => {
    state.openCommissionLoading = true
    await commissionService.openCommissionPeriod(
      state.dates.start_date,
      state.dates.end_date,
      props.isTeamCommission
    )
    state.openCommissionLoading = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Commission period opened",
      life: 3000,
      group: "br"
    })
  }

  const exportCSV = () => dt.value.exportCSV()

  const setDates = async (start_date, end_date) => {
    await lock.acquire()
    if (start_date === "Invalid DateTime" || end_date === "Invalid DateTime") {
      return
    }
    state.loading = true
    state.dates.start_date = start_date
    state.dates.end_date = end_date

    const commissionResponse = await commissionService.getHighlightCommission(
      start_date,
      end_date,
      props.isTeamCommission,
      state.isManagersOnly
    )
    if (commissionResponse.from_closed) {
      state.fromClosedDate = dfl(commissionResponse.closed_date)
    } else {
      state.fromClosedDate = "Commissions not closed"
    }

    toast.add({
      severity: "success",
      summary: "Success",
      detail: commissionResponse.from_closed
        ? "Commission From Closed period"
        : "Commission Generated",
      life: 2000,
      group: "br"
    })

    state.commissions = commissionService.formatHighlightCommission(
      commissionResponse.commissions
    )

    state.loading = false
    await lock.release()
  }

  const toggleManagersOnly = () => {
    if (state.isManagersOnly) {
      state.isManagersOnlyLabel = "Managers Only"
    } else {
      state.isManagersOnlyLabel = "Everyone"
    }
    setDates(state.dates.start_date, state.dates.end_date)
  }
</script>
