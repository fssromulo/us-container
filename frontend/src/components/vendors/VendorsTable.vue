<template>
  <div>
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6">
        <template #start>
          <Button
            label="Add Vendor"
            icon="pi pi-plus"
            class="ml-4 p-button-success"
            :disabled="!$ability.can('create', 'inventory-vendors')"
            @click="openVendor"
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
        :value="vendorStore.vendors"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        :rows="25"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Vendors"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col table-header md:flex-row md:justify-start">
            <h5 class="mb-2 md:m-0 p-as-md-center">Vendors</h5>
            <IconField>
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="state.filters['global'].value"
                placeholder="Search..."
              />
            </IconField>
          </div>
        </template>
        <Column field="id" header="Vendor Id" style="width: 120px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              @click="openVendor(slotProps.data)"
              >{{ slotProps.data.id.substring(0, 4) }}</Button
            >
          </template>
        </Column>
        <Column
          v-for="(col, i) in vendorService.columnOrdering"
          :key="col.order_id + col.line_item_id + i.toString()"
          :field="col.field"
          :header="col.display"
          :sortable="col.sortable"
          :style="col.style"
        ></Column>
      </DataTable>
      <LoadingTable
        v-if="state.loading"
        :columns="vendorService.columnOrdering"
      />
    </div>

    <Dialog
      v-model:visible="state.vendorDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="state.vendor?.id ? 'Update Vendor' : 'Create Vendor'"
      :modal="true"
      class="p-fluid"
    >
      <create-vendor
        @hide="state.vendorDialog = false"
        :vendorProp="state.vendor"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import VendorService from "@/service/Vendors"
  import VendorApi from "@/api/vendors"
  import CreateVendor from "./CreateVendor.vue"
  import { useUsers } from "@/store/modules/users"
  import { useVendors } from "@/store/modules/vendors"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { useAuth0 } from "@auth0/auth0-vue"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"

  const $ability = inject("$ability")

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const toast = useToast()
  const usersStore = useUsers()
  const vendorStore = useVendors()

  const vendorService = new VendorService()
  const vendorApi = new VendorApi()

  const { user } = useAuth0()
  const authUser = user

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg

  const state = reactive({
    vendor: {},
    vendors: [],
    vendorDialog: false,
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
    if (vendorStore.vendors.length === 0) {
      const { data } = await vendorApi.getVendors()
      const vendors = data.value.map((l) => vendorService.dtoVendor(l))
      vendorStore.setVendors(vendors)
    }
  })

  const exportCSV = () => dt.value.exportCSV()

  const openVendor = async (vendor) => {
    if (vendor.id) {
      state.vendor = await getVendorById(vendor.id)
    } else {
      state.vendor = {}
    }
    state.vendorDialog = true
  }

  const getVendorById = async (id) => {
    state.singleOrderLoading = true
    const { data, error } = await vendorApi.getVendorById(id)

    if (error.value) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading vendor",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.loading = false
      return vendorService.dtoVendor(data.value)
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
