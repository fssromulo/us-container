<template>
  <div>
    <p class="mx-6 mt-4 text-3xl table-header">Drivers</p>
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6">
        <template #start>
          <Button
            label="Add Driver"
            icon="pi pi-plus"
            class="ml-4 p-button-success"
            @click="openDriver"
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
        :value="filteredDrivers"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        :rows="25"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Drivers"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col items-start">
            <h5 class="mb-2">Drivers</h5>
            <div class="flex items-center space-x-2">
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="state.filters['global'].value"
                placeholder="Search..."
              />
            </div>
          </div>
        </template>
        <Column field="id" header="Driver Id" style="width: 160px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              @click="openDriver(slotProps.data)"
              >{{ slotProps.data.id.substring(0, 4) }}</Button
            >
          </template>
        </Column>
        <Column
          v-for="(col, i) in driversService.columnOrdering"
          :key="col.order_id + col.line_item_id + i.toString()"
          :field="col.field"
          :header="col.display"
          :sortable="col.sortable"
          :style="col.style"
        ></Column>
        <Column field="id" header="Delete driver" style="width: 80px">
          <template #body="slotProps">
            <Button
              type="button"
              icon="pi pi-trash text-sm"
              :loading="state.deleteLoading"
              @click="deleteDriver(slotProps.data, $event)"
              class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
            ></Button>
          </template>
        </Column>
      </DataTable>
      <LoadingTable
        v-if="state.loading"
        :columns="driversService.columnOrdering"
      />
    </div>

    <Dialog
      v-model:visible="state.driverDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="state.driver?.id ? 'Update Driver' : 'Create Driver'"
      :modal="true"
      class="p-fluid"
    >
      <create-driver
        @hide="state.driverDialog = false"
        :driverProp="state.driver"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import DriversService from "@/service/Drivers"
  import DriverApi from "@/api/drivers"
  import CreateDriver from "./CreateDriver.vue"
  import { useUsers } from "@/store/modules/users"
  import { useDrivers } from "@/store/modules/drivers"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { useAuth0 } from "@auth0/auth0-vue"
  import { useConfirm } from "primevue/useconfirm"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  const breakpoints = useBreakpoints(breakpointsTailwind)
  const toast = useToast()
  const usersStore = useUsers()
  const driverStore = useDrivers()
  const confirm = useConfirm()

  const driversService = new DriversService()
  const driverApi = new DriverApi()

  const { user } = useAuth0()
  const authUser = user

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg

  const state = reactive({
    driver: {},
    drivers: [],
    driverDialog: false,
    loading: false,
    noteDialog: false,
    filters: {},
    deleteLoading: false
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

  const filteredDrivers = computed(() => {
    return driverStore.drivers
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  onMounted(async () => {
    if (driverStore.drivers.length === 0) {
      const { data } = await driverApi.getDrivers()
      const drivers = data.value.map((l) => driversService.dtoDriver(l))
      driverStore.setDrivers(drivers)
    }
  })

  const exportCSV = () => dt.value.exportCSV()

  const openDriver = async (driver) => {
    if (driver.id) {
      state.driver = await getDriverById(driver.id)
    } else {
      state.driver = {}
    }
    state.driverDialog = true
  }

  const getDriverById = async (id) => {
    state.singleOrderLoading = true
    const { data, error } = await driverApi.getDriverById(id)

    if (error.value) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading driver",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.loading = false
      return driversService.dtoDriver(data.value)
    }
  }

  const deleteDriver = async (driverData, event) => {
    state.deleteLoading = true
    const { data, error } = await driverApi.deleteDriver(driverData.id)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error deleting driver",
        group: "br",
        life: 5000
      })
      state.deleteLoading = false

      return
    }
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Driver deleted",
      group: "br",
      life: 5000
    })
    const driverDataRes = await driverApi.getDrivers()
    const drivers = driverDataRes.data.value.map((l) =>
      driversService.dtoDriver(l)
    )
    driverStore.setDrivers(drivers)

    state.deleteLoading = false
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

  .product-image {
    width: 50px;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
  }

  .p-dialog .product-image {
    width: 50px;
    margin: 0 auto 2rem auto;
    display: block;
  }

  .confirmation-content {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  @media screen and (max-width: 960px) {
    ::v-deep(.p-toolbar) {
      flex-wrap: wrap;

      .p-button {
        margin-bottom: 0.25rem;
      }
    }
  }
</style>
