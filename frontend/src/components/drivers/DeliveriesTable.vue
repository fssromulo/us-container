<template>
  <div>
    <p class="mx-6 mt-4 text-3xl table-header">Locations</p>
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6">
        <template #start>
          <Button
            label="Add Location"
            icon="pi pi-plus"
            class="ml-4 p-button-success"
            @click="openLocation"
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
        :value="filteredLocations"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        :rows="25"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Locations"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col table-header md:flex-row md:justify-start">
            <h5 class="mb-2 md:m-0 p-as-md-center">Locations</h5>
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
        <Column field="id" header="Location Id" style="width: 160px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              @click="openLocation(slotProps.data)"
              >{{ slotProps.data.id.substring(0, 4) }}</Button
            >
          </template>
        </Column>
        <Column
          v-for="(col, i) in priceService.locationColumnOrdering"
          :key="col.order_id + col.line_item_id + i.toString()"
          :field="col.field"
          :header="col.display"
          :sortable="col.sortable"
          :style="col.style"
        ></Column>
      </DataTable>
      <LoadingTable
        v-if="state.loading"
        :columns="priceService.locationColumnOrdering"
      />
    </div>

    <Dialog
      v-model:visible="state.locationDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="state.location?.id ? 'Update Location' : 'Create Location'"
      :modal="true"
      class="p-fluid"
    >
      <create-location
        @hide="state.locationDialog = false"
        :locationProp="state.location"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import PriceService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import CreateLocation from "./CreateDriver.vue"
  import { useUsers } from "@/store/modules/users"
  import { useContainerPrices } from "@/store/modules/pricing"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { useAuth0 } from "@auth0/auth0-vue"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  const breakpoints = useBreakpoints(breakpointsTailwind)
  const toast = useToast()
  const usersStore = useUsers()
  const pricingStore = useContainerPrices()

  const priceService = new PriceService()
  const pricingApi = new PricingApi()

  const { user } = useAuth0()
  const authUser = user

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg

  const state = reactive({
    location: {},
    locations: [],
    locationDialog: false,
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

  const filteredLocations = computed(() => {
    return pricingStore.locations
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  onMounted(async () => {
    if (pricingStore.locations.length === 0) {
      const { data } = await pricingApi.getLocations()
      const locations = data.value.map((l) => priceService.dtoLocation(l))
      pricingStore.setLocations(locations)
    }

    if (pricingStore.containerPrices.length === 0) {
      const { data } = await pricingApi.getContainerPricing()
      const prices = data.value.map((p) => priceService.dtoContainerPricing(p))
      pricingStore.setContainerPrices(prices)
    }
    if (pricingStore.accessoryPrices.length === 0) {
      const { data } = await pricingApi.getProduct()
      const prices = data.value.map((p) => priceService.dtoProductPricing(p))
      pricingStore.setAccessoryPrices(prices)
    }
  })

  const exportCSV = () => dt.value.exportCSV()

  const openLocation = async (location) => {
    if (location.id) {
      state.location = await getLocationById(location.id)
    } else {
      state.location = {}
    }
    state.locationDialog = true
  }

  const getLocationById = async (id) => {
    state.singleOrderLoading = true
    const { data, error } = await pricingApi.getLocationById(id)

    if (error.value) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading location",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.loading = false
      return priceService.dtoLocation(data.value)
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
