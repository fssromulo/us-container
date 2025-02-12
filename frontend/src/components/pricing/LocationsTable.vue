<template>
  <div>
    <p class="mx-6 mt-4 text-3xl table-header">Locations</p>
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6">
        <template #start>
          <Button
            label="Add Location"
            :disabled="!$ability.can('create', 'warehouse')"
            icon="pi pi-plus"
            class="ml-4 p-button-success"
            @click="openLocation"
          />
          <div class="ml-8">
            <label :for="field" class="mr-2 font-medium text-900 dark:text-0"
              >Max Allowed POD Miles</label
            >
            <InputText v-model="state.pod.max_allowed_miles" />
            <Button
              label="Save"
              class="ml-4 p-button"
              @click="saveMaxAllowedMiles"
              :loading="state.loading"
            />
          </div>
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
            <IconField>
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="state.filters['global'].value"
                placeholder="Search..."
              />
            </IconField>
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
          v-for="(col, i) in replace_price_per(
            priceService.locationColumnOrdering
          )"
          :key="col.order_id + col.line_item_id + i.toString()"
          :field="col.field"
          :header="col.display"
          :sortable="col.sortable"
          :style="col.style"
        >
        </Column>
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
  import { reactive, computed, onMounted, inject, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import PriceService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import CreateLocation from "./CreateLocation.vue"
  import { useUsers } from "@/store/modules/users"
  import { useContainerPrices } from "@/store/modules/pricing"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { useAuth0 } from "@auth0/auth0-vue"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import AccountApi from "@/api/account"

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const toast = useToast()
  const usersStore = useUsers()
  const pricingStore = useContainerPrices()
  const $ability = inject("$ability")

  const priceService = new PriceService()
  const pricingApi = new PricingApi()

  const { user } = useAuth0()
  const authUser = user

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg
  const accountApi = new AccountApi()

  const state = reactive({
    location: {},
    locations: [],
    locationDialog: false,
    loading: false,
    noteDialog: false,
    filters: {},
    pod: {}
  })

  const dt = ref()

  const saveMaxAllowedMiles = async () => {
    state.loading = true
    const { data, error } = await accountApi.updateAccountAttribute({
      cms_attributes: Object.fromEntries(
        Object.entries(usersStore.cms).filter(([key, value]) => state.pod)
      ),
      type: "cms_attributes"
    })
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error saving CMS",
        detail: error.message,
        life: 3000,
        group: "br"
      })
    } else {
      state.cities = []
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Request Saved",
        life: 3000,
        group: "br"
      })
      const cms_attributes = data.value.cms_attributes
      cms_attributes.id = data.value.id
      usersStore.setCms(cms_attributes)
      state.pod = usersStore.cms.pay_on_delivery_contract
    }
    state.loading = false
  }

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

  const replace_price_per = (lst) => {
    let account_country = usersStore.cms.account_country
    if (account_country == "Canada") {
      lst.forEach((el) => {
        if (el.display == "Price per mile") {
          el.display = "Price per km"
        }
      })
    }
    return lst
  }

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
    state.pod = usersStore.cms.pay_on_delivery_contract
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
