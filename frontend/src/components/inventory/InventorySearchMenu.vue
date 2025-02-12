<template>
  <div
    class="grid col-span-12 md:grid-cols-12 sm:grid-cols-2"
    style="max-width: 85vw"
  >
    <div class="grid grid-cols-12 col-span-12 gap-1">
      <SelectButton
        v-if="
          categorys.length > 0 && requiredFilterFields.includes('categories')
        "
        class="col-span-12 mt-4 md:col-span-3"
        v-model="state.selectedCategory"
        :options="categorys"
        optionLabel="name"
        placeholder="Select a category"
      />
      <Button
        label="Add Container"
        icon="pi pi-plus"
        class="col-span-12 mt-4 md:col-span-2 p-button-success"
        v-if="requiredFilterFields.includes('addContainer')"
        @click="openContainer"
      />
      <div class="grid grid-cols-6 col-span-12 mt-6 md:col-span-3">
        <div
          class="col-span-3"
          v-if="requiredFilterFields.includes('container')"
        >
          <RadioButton
            v-model="state.searchType"
            inputId="containerNumber"
            name="currentSearchType"
            class="p-component p-inputtext-fluid"
            value="CONTAINER_NUMBER"
          />
          <label for="containerNumber" class="ml-2">Container #</label>
        </div>
        <div class="col-span-3" v-if="requiredFilterFields.includes('release')">
          <RadioButton
            v-model="state.searchType"
            inputId="searchType"
            name="currentSearchType"
            class="p-component p-inputtext-fluid"
            value="CONTAINER_RELEASE"
          />
          <label for="searchType" class="ml-2">Release</label>
        </div>
        <div class="col-span-3" v-if="requiredFilterFields.includes('orderId')">
          <RadioButton
            v-model="state.searchType"
            inputId="orderId"
            name="currentSearchType"
            class="p-component p-inputtext-fluid"
            value="ORDER_ID"
          />
          <label for="orderId" class="ml-2">Order Id</label>
        </div>
      </div>

      <InputText
        style="min-width: 10em"
        v-model="state.search"
        v-on:blur="setReleaseNumber"
        v-if="requiredFilterFields.includes('searchContainer')"
        class="col-span-6 mt-4 md:col-span-2 p-component p-inputtext-fluid"
        placeholder="Search containers"
      />
      <div class="col-span-6 mt-4 md:col-span-1">
        <Button
          class="ml-1"
          icon="pi pi-search"
          slot="right-icon"
          :loading="state.quickSearchLoading || state.loading"
          @click="searchInventory()"
        />
        <Button
          class="ml-1 p-button-secondary"
          icon="pi pi-refresh"
          slot="right-icon"
          :loading="state.loading"
          @click="resetSearch"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
  import { reactive, computed, watch, ref } from "vue"
  import InventoryService from "@/service/Inventory"
  import InventoryApi from "@/api/inventory"
  import { useToast } from "primevue/usetoast"

  // import { useDrivers } from "@/store/modules/drivers";
  import { useUsers } from "@/store/modules/users"
  import { useInventory } from "@/store/modules/inventory"
  import { isRentalsVisible } from "../../utils/allowedVisibilityForFeatures"

  import { useAuth0 } from "@auth0/auth0-vue"
  import cloneDeep from "lodash.clonedeep"
  const emit = defineEmits(["openContainer", "setReleaseNumber"])
  const usersStore = useUsers()
  const inventoryStore = useInventory()
  const inventoryService = new InventoryService()
  const inventoryApi = new InventoryApi()
  const toast = useToast()

  const { user } = useAuth0()
  const authUser = user

  const categorys = computed(() => {
    let isProd = import.meta.env.PROD
    let accountId = usersStore?.cms?.account_id
    let isCMSRentalsEnabled = usersStore.cms?.feature_flags?.rentals_enabled
    let userEmail = usersStore?.currentUser.email
    let isRentalsFeatureVisible = isRentalsVisible(
      isProd,
      accountId,
      isCMSRentalsEnabled,
      userEmail
    )

    return isRentalsFeatureVisible
      ? [
          { name: "All", code: "ALL" },
          { name: "Sales", code: "PURCHASE" },
          { name: "Accessory Sales", code: "PURCHASE_ACCESSORY" },
          { name: "Rent to Own", code: "RENT_TO_OWN" },
          { name: "Rentals", code: "RENT" }
        ]
      : []
  })

  const container_default_search_type = computed(() => {
    return usersStore.cms?.default_container_search == "number"
      ? "CONTAINER_NUMBER"
      : "CONTAINER_RELEASE"
  })

  const { requiredFilterFields, containerStatus, resetFunc, changeCategory } =
    defineProps({
      containerStatus: {
        type: String,
        default: "All"
      },
      requiredFilterFields: {
        type: Array,
        default: () => []
      },
      resetFunc: {
        type: Function,
        default: () => {}
      },
      changeCategory: {
        type: Function,
        default: () => {}
      }
    })

  const openContainer = async (container) => {
    emit("openContainer", container)
  }
  const getContainerById = async (id) => {
    state.singleOrderLoading = true
    const { data, isLoading, error } = await inventoryApi.getInventoryById(id)

    if (error.value) {
      state.containerLoading = false
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
      state.containerLoading = false
      return inventoryService.dtoInventory(data.value)
    }
  }
  const resetSearch = async () => {
    state.search = ""
    state.quickSearchLoading = false
    state.searchType = container_default_search_type.value
    state.containers = []
    await resetFunc()
    toast.add({
      severity: "info",
      summary: "Reset Search",
      detail: "Search reset",
      group: "br",
      life: 5000
    })
  }

  const appendLineItemsToRentalHistory = (data) => {
    for (var i = 0; i < data.length; i++) {
      for (var j = 0; j < data[i].line_items.length; j++) {
        let rental_history = data[i].line_items[j].inventory.rental_history
        for (var x = 0; x < rental_history.length; x++) {
          rental_history[x].line_item = data[i].line_items[j]
          rental_history[x].line_item.order = data[i]
        }
      }
    }
    return data
  }

  const searchInventory = async () => {
    state.quickSearchLoading = true
    state.containers = []
    state.search = state.search.trim()
    let urlStr = `searchBy=${state.searchType}&searchValue=${state.search}&searchStatus=${containerStatus}`
    if (state.search) {
      urlStr = `searchBy=${state.searchType}&searchValue=${state.search}`
    }
    const { error, data } = await inventoryApi.searchInventory(urlStr)
    if (error.value) {
      data.value = []
    }
    state.containers = appendLineItemsToRentalHistory(
      inventoryService.removeOtherInventory(
        state.searchType,
        state.search,
        data.value
      )
    )
      .map((i) => inventoryService.orderToInventory(i))
      .flat(1)
      .filter((v, i, a) => a.findIndex((t) => t.id === v.id) === i)

    inventoryStore.setAvailableInventory([...state.containers])
    inventoryStore.setAllInventory([...state.containers])
    inventoryStore.setDeliveredInventory([...state.containers])
    inventoryStore.setAttachedInventory([...state.containers])
    inventoryStore.setDelinquentInventory([...state.containers])

    state.quickSearchLoading = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Search complete",
      group: "br",
      life: 5000
    })
  }
  const currentStatus = computed(() => {
    return statusOptions.value[state.selectedStatusIndex]
  })

  const getInventory = async (skip = 0) => {
    if (skip === 0) {
      state.inventory = []
    }
    state.loading = true

    if (currentStatus.value === "Attached") {
      const mappedInventory = await getOrderInventory("Attached")
      inventoryStore.setAttachedInventory(mappedInventory)
      state.inventoryRawLength += mappedInventory.length
    } else if (currentStatus.value === "Delivered") {
      const mappedInventory = await getOrderInventory("Delivered")
      inventoryStore.setDeliveredInventory(mappedInventory)
      state.inventoryRawLength += mappedInventory.length
    }

    if (currentStatus.value === "Available" || currentStatus.value === "All") {
      const { data, error } = await inventoryApi.getInventoryByStatus(
        currentStatus.value,
        state.selectedCategory.code,
        skip
      )

      if (error.value) {
        state.loading = false
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error loading inventory",
          group: "br",
          life: 5000
        })
        return
      }

      if (currentStatus.value === "All") {
        const allInventory = [
          ...cloneDeep(inventoryStore.allInventory),
          ...inventoryService.inventoryListToDtos(data.value)
        ]
        inventoryStore.setAllInventory(allInventory)
      } else {
        const availableInventory = [
          ...cloneDeep(inventoryStore.availableInventory),
          ...inventoryService.inventoryListToDtos(data.value)
        ]
        inventoryStore.setAvailableInventory(availableInventory)
      }
    }
    state.loading = false
  }
  const statusOptions = computed(() => {
    return usersStore.cms?.inventory_status_options || []
  })

  const state = reactive({
    searchType: container_default_search_type.value,
    refreshKey: 0,
    ordersWithContainer: [],
    deleteLoading: false,
    search: "",
    quickSearchLoading: false,
    container: {},
    containers: [],
    containerDialog: false,
    containerDetailDialog: false,
    selectedAddButton: null,
    selectedStatusIndex: 0,
    loading: false,
    inventoryRawLength: 0,
    noteDialog: false,
    filters: {},
    selectedCategory: { name: "All", code: "ALL" }
  })
  const setReleaseNumber = () => {
    if (state.searchType == "CONTAINER_RELEASE")
      emit("setReleaseNumber", state.search)
  }
  watch(
    () => state.selectedCategory,
    async () => {
      //await changeCategory(state.selectedCategory);
    }
  )

  watch(
    () => state.searchType,
    async () => {
      setReleaseNumber()
    }
  )
</script>
