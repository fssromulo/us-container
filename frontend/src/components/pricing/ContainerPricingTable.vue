<template>
  <div>
    <ConfirmPopup></ConfirmPopup>
    <p class="mx-6 mt-4 text-3xl table-header">Container Pricing</p>
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6 overflow-x-scroll" style="max-width: 95vw">
        <template #start>
          <!-- <SelectButton
            v-model="state.selectedCategory"
            :options="state.categorys"
            optionLabel="name"
            placeholder="Select a category"
          /> -->
          <Button
            label="Add Container Price"
            :disabled="!$ability.can('create', 'product')"
            icon="pi pi-plus"
            class="p-button-success"
            @click="openContainerPrice"
          />
          <div>
            <InputText
              style="margin-left: 10px"
              v-model="state.rental_price_20"
              placeholder="20' rental price"
            >
            </InputText>
            <Button
              label="Set 20 rental price"
              class="mt-2 ml-4 p-button"
              @click="setRentalPrice(20)"
              :loading="state.setRentalPrice20Loading"
            />
          </div>
          <div>
            <InputText
              style="margin-left: 10px"
              v-model="state.rental_price_40"
              placeholder="40' rental price"
            >
            </InputText>
            <Button
              label="Set 40 rental price"
              class="mt-2 ml-4 p-button"
              @click="setRentalPrice(40)"
              :loading="state.setRentalPrice40Loading"
            />
          </div>

          <div>
            <Button
              label="Set Global Pod"
              class="mt-2 ml-4 p-button"
              @click="state.dialogGlobalPod = true"
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
        :value="filteredContainerPricess"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        :rows="25"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Container Prices"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col items-start">
            <h5 class="mb-2">Container Prices</h5>
            <div class="flex items-center space-x-2">
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="state.filters['global'].value"
                placeholder="Search..."
              />
            </div>
          </div>
        </template>
        <Column field="id" header="Container Prices Id" style="width: 160px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              :disabled="!$ability.can('update', 'product')"
              @click="openContainerPrice(slotProps.data)"
              >{{ slotProps.data.id.substring(0, 4) }}</Button
            >
          </template>
        </Column>
        <Column
          v-for="(col, i) in columnOrder"
          :key="col.order_id + col.line_item_id + i.toString()"
          :field="col.field"
          :header="col.display"
          :sortable="col.sortable"
          :style="col.style"
        ></Column>
        <Column field="id" header="Delete" style="width: 160px">
          <template #body="slotProps">
            <Button
              type="button"
              :disabled="!$ability.can('update', 'product')"
              icon="pi pi-trash text-sm"
              @click="deleteContainer(slotProps.data, $event)"
              class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
            ></Button>
          </template>
        </Column>
      </DataTable>
      <LoadingTable v-if="state.loading" :columns="columnOrder" />
    </div>

    <Dialog
      v-model:visible="state.containerPriceDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="
        state.containerPrice?.id
          ? 'Edit Container Price'
          : 'Add Container Price'
      "
      :modal="true"
      class="p-fluid"
    >
      <create-container-price
        @hide="state.containerPriceDialog = false"
        :containerPriceProp="state.containerPrice"
      />
    </Dialog>

    <Dialog
      v-model:visible="state.dialogGlobalPod"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Set global pod"
      :modal="true"
      class="p-fluid"
    >
      <div class="col-span-12 mb-3 field md:col-span-4">
        <label for="type" class="font-medium text-900">Type</label>
        <MultiSelect
          icon="pi pi-plus"
          class="p-component p-inputtext-fluid"
          placeholder="Select type"
          :options="inventoryService.types"
          v-model="state.globalPodTypes"
          optionLabel="label"
          optionValue="value"
        />
      </div>
      <div class="col-span-12 mb-3 field md:col-span-4">
        <label for="condition" class="font-medium text-900">Condition</label>
        <Select
          placeholder="Select condition"
          :options="inventoryService.conditions"
          v-model="state.globalPodCondition"
          class="p-component p-inputtext-fluid"
          id="condition"
          type="text"
          optionLabel="label"
          optionValue="value"
        />
      </div>
      <div class="col-span-12 mb-3 field md:col-span-4">
        <Select
          placeholder="Payment on delivery"
          optionLabel="label"
          optionValue="value"
          :options="podsOptions"
          v-model="state.globalPodState"
          class="p-component p-inputtext-fluid"
          id="location_id"
          type="text"
        />
      </div>
      <div class="col-span-12 mb-3 field md:col-span-4">
        <MultiSelect
          placeholder="Select location"
          optionLabel="label"
          optionValue="value"
          :options="locationsList"
          v-model="state.globalPodLocations"
          class="p-component p-inputtext-fluid"
          @change="handleLocationChange"
          id="location_id"
          type="text"
        />
      </div>
      <Button
        label="Save"
        @click="setGlobalPod"
        :loading="globalPodButtonLoading"
        :disabled="globalPodButtonLoading"
        icon="pi pi-file"
        class="w-auto"
      ></Button>
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import PriceService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import CreateContainerPrice from "./CreateContainerPrice.vue"
  import { useContainerPrices } from "@/store/modules/pricing"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { useAuth0 } from "@auth0/auth0-vue"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import { useConfirm } from "primevue/useconfirm"
  import InventoryService from "@/service/Inventory"

  const confirm = useConfirm()
  const inventoryService = new InventoryService()

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const toast = useToast()
  const pricingStore = useContainerPrices()
  const priceService = new PriceService()
  const pricingApi = new PricingApi()

  const $ability = inject("$ability")

  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg

  const columnOrder = priceService.columnOrdering

  const state = reactive({
    containerPrice: {},
    containerPrices: [],
    containerPriceDialog: false,
    loading: false,
    noteDialog: false,
    filters: {},
    selectedCategory: { name: "Sales", code: "PURCHASE" },
    categorys: [
      { name: "Sales", code: "PURCHASE" },
      { name: "Accessory Sales", code: "PURCHASE_ACCESSORY" },
      { name: "Rent to Own", code: "RENT_TO_OWN" },
      { name: "Rentals", code: "RENT" }
    ],
    rental_price_20: null,
    rental_price_40: null,
    dialogGlobalPod: false,
    globalPodTypes: [],
    globalPodCondition: "",
    globalPodState: false,
    globalPodLocations: [],
    globalPodButtonLoading: false
  })

  const podsOptions = computed(() => {
    return [
      {
        label: "Enabled",
        value: true
      },
      {
        label: "Disabled",
        value: false
      }
    ]
  })

  const setGlobalPod = async () => {
    state.globalPodButtonLoading = true

    let dataRequest = {
      types: state.globalPodTypes,
      condition: state.globalPodCondition,
      state: state.globalPodState,
      locations: state.globalPodLocations
    }

    const { data, error } = await pricingApi.setGlobalPOD(dataRequest)

    state.globalPodButtonLoading = false

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error setting global pay on delivery.",
        group: "br",
        life: 5000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Global pay on delivery set up.",
        group: "br",
        life: 5000
      })

      state.dialogGlobalPod = false
    }
  }

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

  const locationsList = computed(() => {
    return pricingStore?.locations
      ?.map((v) => {
        return { label: v.city, value: v.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const filteredContainerPricess = computed(() => {
    return pricingStore.containerPrices
  })

  const setRentalPrice = async (containerSize) => {
    let rental_price = 0
    try {
      rental_price =
        containerSize == 20
          ? parseInt(state.rental_price_20, 10)
          : parseInt(state.rental_price_40, 10)
    } catch (error) {
      console.log(error)
      return
    }

    if (containerSize == 20) {
      state.setRentalPrice20Loading = true
    } else {
      state.setRentalPrice40Loading = true
    }

    const data = {
      container_size: containerSize,
      rental_price: rental_price
    }

    const { response, error } = await pricingApi.setRentalPrice(data)

    state.setRentalPrice40Loading = false
    state.setRentalPrice20Loading = false
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error updating price",
        group: "br",
        life: 5000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Rental price updated successfully",
        group: "br",
        life: 5000
      })
      await refreshTable(true)
    }
  }

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  const refreshTable = async (force = false) => {
    if (pricingStore.locations.length === 0 || force) {
      const { data } = await pricingApi.getLocations()
      const locations = data.value.map((l) => priceService.dtoLocation(l))
      pricingStore.setLocations(locations)
    }

    if (pricingStore.containerPrices.length === 0 || force) {
      const { data } = await pricingApi.getContainerPricing()
      const prices = data.value.map((p) => priceService.dtoContainerPricing(p))
      console.log("FORCE = true")
      pricingStore.setContainerPrices(prices)
    }
  }

  onMounted(async () => {
    state.loading = true
    await refreshTable()
    state.loading = false
  })

  const exportCSV = () => dt.value.exportCSV()

  const deleteContainer = async (containerPrice, event) => {
    confirm.require({
      target: event.target,
      message: "Do you want to remove this product?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        if (containerPrice.id) {
          state.loading = true
          const { data, error } = await pricingApi.deleteContainerPricing(
            containerPrice.id
          )
          if (error.value) {
            state.loading = false
            toast.add({
              severity: "error",
              summary: "Error",
              detail: "Error loading order",
              group: "br",
              life: 5000
            })
            return
          }
          if (data.value) {
            toast.add({
              severity: "success",
              summary: "Success",
              detail: "Container deleted",
              group: "br",
              life: 5000
            })

            pricingStore.setContainerPrices(
              pricingStore.containerPrices.filter(
                (c) => c.id !== containerPrice.id
              )
            )

            state.refreshKey = Math.random()
          }
          state.loading = false
        }
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Canceled",
          detail: "Product removal canceled",
          life: 2000
        })
      }
    })
  }

  const openContainerPrice = async (containerPrice) => {
    if (containerPrice.id) {
      state.containerPrice = await getContainerPriceById(containerPrice.id)
    } else {
      state.containerPrice = {}
    }
    state.containerPriceDialog = true
  }

  const getContainerPriceById = async (id) => {
    state.singleOrderLoading = true
    const { data, error } = await pricingApi.getContainerPriceById(id)

    if (error.value) {
      state.loading = false
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
      state.loading = false
      return priceService.dtoContainerPricing(data.value)
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
