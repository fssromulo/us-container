<template>
  <div>
    <ConfirmPopup></ConfirmPopup>

    <p class="mx-6 mt-4 text-3xl table-header">Accessories Pricing</p>
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6">
        <template #start>
          <!-- <SelectButton
              v-model="state.selectedCategory"
              :options="state.categorys"
              optionLabel="name"
              placeholder="Select a category"
            /> -->
          <Button
            label="Add Accessory Price"
            :disabled="!$ability.can('create', 'product')"
            icon="pi pi-plus"
            class="ml-4 p-button-success"
            @click="openAccessoryPrice"
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
        :value="filteredAccesoryPricess"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        :rows="25"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Accessories Pricess"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col table-header md:flex-row md:justify-start">
            <h5 class="mb-2 md:m-0 p-as-md-center">Accessories Pricess</h5>
            <IconField>
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="state.filters['global'].value"
                placeholder="Search..."
              />
            </IconField>
          </div>
        </template>
        <Column field="id" header="SKU" style="width: 160px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              :disabled="!$ability.can('edit', 'accessories')"
              @click="openAccessoryPrice(slotProps.data)"
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
        <Column field="image" header="Product Image" style="width: 160px">
          <template #body="slotProps">
            <p v-if="slotProps.data.file_upload.length > 0">{{
              slotProps.data.file_upload[0].filename
            }}</p>
          </template>
        </Column>

        <Column field="id" header="Delete" style="width: 160px">
          <template #body="slotProps">
            <Button
              type="button"
              :disabled="!$ability.can('edit', 'accessories')"
              icon="pi pi-trash text-sm"
              @click="deleteAccessory(slotProps.data, $event)"
              class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
            ></Button>
          </template>
        </Column>
      </DataTable>
      <LoadingTable v-if="state.loading" :columns="columnOrder" />
    </div>

    <Dialog
      v-model:visible="state.accessoryPriceDialog"
      maximizable
      :dismissableMask="false"
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="state.containerPrice?.id ? 'Edit Accessory' : 'Add Accessory'"
      :modal="true"
      class="p-fluid"
    >
      <create-accessory-price
        @hide="state.accessoryPriceDialog = false"
        :accessoryPriceProp="state.accessoryPrice"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import PriceService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import CreateAccessoryPrice from "./CreateAccessoryPrice.vue"

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import { useContainerPrices } from "@/store/modules/pricing"

  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { useConfirm } from "primevue/useconfirm"

  const confirm = useConfirm()
  import { useAuth0 } from "@auth0/auth0-vue"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  const breakpoints = useBreakpoints(breakpointsTailwind)
  const toast = useToast()
  const usersStore = useUsers()
  const pricingStore = useContainerPrices()

  const customerStore = useCustomerOrder()
  const priceService = new PriceService()
  const pricingApi = new PricingApi()

  const { user } = useAuth0()
  const authUser = user
  const $ability = inject("$ability")

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg

  const columnOrder = priceService.columnAccessoryOrdering
  const deleteAccessory = async (accessoryPrice, event) => {
    confirm.require({
      target: event.target,
      message: "Do you want to remove this accesory?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        if (accessoryPrice.id) {
          state.loading = true
          const { data, error } = await pricingApi.deleteProduct(
            accessoryPrice.id
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
              detail: "Accessory deleted",
              group: "br",
              life: 5000
            })

            pricingStore.setAccessoryPrices(
              pricingStore.accessoryPrices.filter(
                (c) => c.id !== accessoryPrice.id
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

  const state = reactive({
    accessoryPrice: {},
    accessoryPrices: [],
    accessoryPriceDialog: false,
    loading: false,
    noteDialog: false,
    filters: {},
    selectedCategory: { name: "Sales", code: "PURCHASE" },
    categorys: [
      { name: "Sales", code: "PURCHASE" },
      { name: "Accessory Sales", code: "PURCHASE_ACCESSORY" },
      { name: "Rent to Own", code: "RENT_TO_OWN" },
      { name: "Rentals", code: "RENT" }
    ]
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

  const filteredAccesoryPricess = computed(() => {
    return pricingStore.accessoryPrices
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
    if (pricingStore.productCategories.length === 0) {
      const { data } = await pricingApi.getProductCategory()
      const prices = data.value
      pricingStore.setProductCategories(prices)
    }

    if (pricingStore.accessoryPrices.length === 0) {
      const { data } = await pricingApi.getProduct()
      const prices = data.value.map((p) => priceService.dtoProductPricing(p))
      pricingStore.setAccessoryPrices(prices)
    }
  })

  const exportCSV = () => dt.value.exportCSV()

  const getProductPrices = async () => {
    if (pricingStore.productPrices.length > 0) {
      return
    }

    state.loading = true
    const { data, isLoading, error } = await pricingApi.getProduct()

    if (error.value) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading pricing",
        group: "br",
        life: 5000
      })
      return
    }

    if (!isLoading) {
      state.loading = false
    }

    if (data) {
      state.loading = false
      pricingStore.setProductPrices(
        data.value.map((p) => {
          return priceService.dtoProductPricing(p)
        })
      )
    }
  }

  const openAccessoryPrice = async (accessoryPrice) => {
    if (accessoryPrice.id) {
      state.accessoryPrice = await getProductById(accessoryPrice.id)
      state.accessoryPrice.product_category_id =
        state.accessoryPrice?.product_category?.id
    } else {
      state.accessoryPrice = {}
    }
    state.accessoryPriceDialog = true
  }

  const getProductById = async (id) => {
    state.singleOrderLoading = true
    const { data, error } = await pricingApi.getProductById(id)

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
      return priceService.dtoProductPricing(data.value)
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
