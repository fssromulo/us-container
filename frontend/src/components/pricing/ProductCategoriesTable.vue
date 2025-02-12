<template>
  <div>
    <p class="mx-6 mt-4 text-3xl table-header">Product Categories</p>
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
            label="Add Product Category"
            :disabled="!$ability.can('create', 'product')"
            icon="pi pi-plus"
            class="ml-4 p-button-success"
            @click="openProductCategory"
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
        :value="filteredProductCategories"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        :rows="25"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Product Categories"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col table-header md:flex-row md:justify-start">
            <h5 class="mb-2 md:m-0 p-as-md-center">Product Categories</h5>
            <IconField>
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="state.filters['global'].value"
                placeholder="Search..."
              />
            </IconField>
          </div>
        </template>
        <Column field="id" header="Category Id" style="width: 160px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              :disabled="!$ability.can('update', 'product')"
              @click="openProductCategory(slotProps.data)"
              >{{ slotProps.data.id.substring(0, 4) }}</Button
            >
          </template>
        </Column>
        <Column field="name" header="Name" style="width: 160px"> </Column>

        <Column field="id" header="Delete" style="width: 160px">
          <template #body="slotProps">
            <Button
              v-if="slotProps.data?.other_product_news?.length === 0"
              type="button"
              :disabled="!$ability.can('update', 'product')"
              icon="pi pi-trash text-sm"
              @click="deleteProductCategory(slotProps.data)"
              class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
            ></Button>
            <p v-else>Has Acessories</p>
          </template>
        </Column>
      </DataTable>
      <LoadingTable v-if="state.loading" />
    </div>

    <Dialog
      v-model:visible="state.category"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="
        state.containerPrice?.id
          ? 'Edit Product Category'
          : 'Add Product Category'
      "
      :modal="true"
      class="p-fluid"
    >
      <create-product-category
        @hide="state.category = false"
        :categoryProp="state.category"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import PriceService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import CreateProductCategory from "./CreateProductCategory.vue"

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import { useContainerPrices } from "@/store/modules/pricing"

  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import NoteDetail from "../notes/NoteDetail.vue"

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

  const state = reactive({
    productCategory: {},
    productCategories: [],
    category: false,
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

  const filteredProductCategories = computed(() => {
    return pricingStore.productCategories
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
  })

  const exportCSV = () => dt.value.exportCSV()

  const deleteProductCategory = async (productCategory) => {
    if (productCategory.id) {
      state.loading = true
      const { data, error } = await pricingApi.deleteProductCategory(
        productCategory.id
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
          detail: "Category deleted",
          group: "br",
          life: 5000
        })

        pricingStore.setProductCategories(
          pricingStore.productCategories.filter(
            (c) => c.id !== productCategory.id
          )
        )

        state.refreshKey = Math.random()
      }
      state.loading = false
    }
  }

  const openProductCategory = async (category) => {
    if (category.id) {
      state.category = await getProductById(category.id)
    } else {
      state.category = {}
    }
    state.categoryDialog = true
  }

  const getProductById = async (id) => {
    state.singleOrderLoading = true
    const { data, error } = await pricingApi.getProductCategoryById(id)

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
      return data.value
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
