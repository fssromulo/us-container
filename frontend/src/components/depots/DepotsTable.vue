<template>
  <div>
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6">
        <template #start>
          <Button
            label="Add Depot"
            icon="pi pi-plus"
            class="ml-4 p-button-success"
            @click="openDepot"
          />
        </template>

        <template #end>
          <Button
            label="Export"
            icon="pi pi-upload"
            class="p-button-help"
            @click="exportCSV($event)"
          />
        </template>
      </Toolbar>
      <DataTable
        v-if="!state.loading"
        ref="dt"
        :value="depotStore.depots"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        :rows="25"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Depots"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col table-header md:flex-row md:justify-start">
            <h5 class="mb-2 md:m-0 p-as-md-center">Depots</h5>
            <span class="ml-4 p-input-icon-left">
              <IconField>
                <InputIcon class="pi pi-search" />
                <InputText
                  v-model="state.filters['global'].value"
                  placeholder="Search..."
                />
              </IconField>
            </span>
          </div>
        </template>
        <Column field="id" header="Depot Id" style="width: 120px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              @click="openDepot(slotProps.data)"
              >{{ slotProps.data.id.substring(0, 4) }}</Button
            >
          </template>
        </Column>
        <Column
          v-for="(col, i) in depotService.columnOrdering"
          :key="col.order_id + col.line_item_id + i.toString()"
          :field="col.field"
          :header="col.display"
          :sortable="col.sortable"
          :style="col.style"
        ></Column>
      </DataTable>
      <LoadingTable
        v-if="state.loading"
        :columns="depotService.columnOrdering"
      />
    </div>

    <Dialog
      v-model:visible="state.depotDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="state.depot?.id ? 'Update Depot' : 'Create Depot'"
      :modal="true"
      class="p-fluid"
    >
      <create-depot
        @hide="state.depotDialog = false"
        :depotProp="state.depot"
      />
    </Dialog>
  </div>
</template>

<script setup>
  // :disabled="!$ability.can('create','inventory-depots')"
  import { reactive, computed, onMounted, inject, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import DepotApi from "@/api/depot"
  import DepotService from "@/service/Depot"
  import CreateDepot from "./CreateDepot.vue"
  import { useUsers } from "@/store/modules/users"
  import { useDepots } from "@/store/modules/depots"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { useAuth0 } from "@auth0/auth0-vue"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  const breakpoints = useBreakpoints(breakpointsTailwind)
  const toast = useToast()
  const usersStore = useUsers()
  const depotStore = useDepots()
  const $ability = inject("$ability")

  const depotApi = new DepotApi()
  const depotService = new DepotService()

  const { user } = useAuth0()
  const authUser = user

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg

  const state = reactive({
    depot: {},
    depots: [],
    depotDialog: false,
    loading: false,
    noteDialog: false,
    filters: {}
  })

  const dt = ref()

  const tableWidth = computed(() => {
    if (greaterOrEqualLarge.value) {
      return "92vw"
    } else if (lgAndSmaller.value) {
      return "92vw"
    } else if (largerThanSm.value) {
      return "90vw"
    }
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  onMounted(async () => {
    if (depotStore.depots.length === 0) {
      const { data } = await depotApi.getDepots()
      const depots = data.value.map((l) => depotService.dtoDepot(l))
      depotStore.setDepots(depots)
    }
  })

  const exportCSV = () => dt.value.exportCSV()

  const openDepot = async (depot) => {
    if (depot.id) {
      state.depot = await getDepotById(depot.id)
    } else {
      state.depot = {}
    }
    state.depotDialog = true
  }

  const getDepotById = async (id) => {
    state.singleOrderLoading = true
    const { data, error } = await depotApi.getDepotById(id)

    if (error.value) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading depot",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.loading = false
      return depotService.dtoDepot(data.value)
    }
  }
</script>

<style lang="scss" scoped>
  .table-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    @media screen and (max-width: 960px) {
      align-items: start;
    }
  }
</style>
