<template>
  <div>
    <ConfirmPopup></ConfirmPopup>

    <div class="mt-4">
      <Toolbar class="mb-6">
        <template #start>
          <InventorySearchMenu
            @openContainer="openContainer"
            :resetFunc="reset"
            :changeCategory="changeCategory"
            :requiredFilterFields="[
              'categories',
              'addContainer',
              'container',
              'release',
              'searchContainer',
              'orderId'
            ]"
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

      <ul
        class="flex p-0 m-0 overflow-x-scroll list-none select-none bg-0 dark:bg-900"
        style="max-width: 95vw"
      >
        <li v-for="(status, i) in statusOptions" :key="i">
          <a
            v-ripple
            class="flex items-center px-6 py-4 text-2xl transition-colors duration-150 border-b-2 cursor-pointer hover:border-500 dark:hover:border-300 p-ripple"
            :class="{
              'border-blue-500 text-blue-500 hover:border-blue-500':
                state.selectedStatusIndex === i,
              'text-700 dark:text-100 border-transparent':
                state.selectedStatusIndex !== i
            }"
            @click="selectStatus(i)"
          >
            <span class="font-medium">{{ status }}</span>
          </a>
        </li>
      </ul>
      <DataTable
        v-if="!state.loading"
        ref="dt"
        :value="filteredContainers"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        @page="onPage"
        :rows="100"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[25, 50, 100]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} containers"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col items-start">
            <h5 class="mb-2">Containers</h5>
            <div class="flex items-center space-x-2">
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="state.filters['global'].value"
                placeholder="Search..."
              />
            </div>
          </div>
        </template>
        <Column field="detail" header="Container Id" style="width: 160px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              @click="openContainerDetail(slotProps.data)"
              >{{
                slotProps.data.id ? slotProps.data.id.substring(0, 4) : ""
              }}</Button
            >
          </template>
        </Column>

        <Column field="id" header="Edit" style="width: 160px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              @click="openContainer(slotProps.data)"
              >Edit</Button
            >
          </template>
        </Column>

        <Column field="notes" header="Notes" style="width: 160px">
          <template #body="slotProps">
            <Button
              @click="openButton(slotProps.data)"
              :label="slotProps.data.note?.length > 0 ? 'Notes' : 'Add Note'"
            />
          </template>
        </Column>
        <Column
          field="appended_order_id"
          header="Order Id"
          style="width: 160px"
        >
          <template #body="slotProps">
            <div v-if="slotProps.data.rental_history?.length > 0">
              <Button
                class="p-button-rounded"
                v-if="slotProps.data.rental_history?.length === 1"
                @click="
                  openOrder(
                    slotProps.data.rental_history[0]?.line_item.order
                      ?.display_order_id
                  )
                "
                >{{
                  slotProps.data.rental_history[0]?.line_item?.order
                    ?.display_order_id
                }}</Button
              >
              <Tag
                v-else
                value="Has Orders"
                @click="openContainerDetail(slotProps.data)"
              />
            </div>
            <Button
              class="p-button-rounded"
              v-else-if="
                slotProps.data.display_order_id &&
                slotProps.data.display_order_id.length > 0
              "
              @click="openOrder(slotProps.data.display_order_id)"
              >{{ slotProps.data.display_order_id }}</Button
            >
            <p v-else></p>
          </template>
        </Column>

        <Column
          v-for="(col, i) in filteredColumnOrder"
          :key="col.order_id + col.line_item_id + i.toString()"
          :field="col.field"
          :header="col.display"
          :sortable="col.sortable"
          :style="col.style"
        ></Column>
        <Column field="id" header="Delete Container" style="width: 80px">
          <template #body="slotProps">
            <Button
              type="button"
              icon="pi pi-trash text-sm"
              :loading="state.deleteLoading === slotProps.data.id"
              @click="deleteInventory(slotProps.data, $event)"
              class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
            ></Button>
          </template>
        </Column>
      </DataTable>
      <LoadingTable v-if="state.loading" :columns="columnOrder" />
    </div>
    <Dialog
      v-model:visible="state.containerDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="
        state.container.id
          ? state.container.status == 'Attached'
            ? 'Edit Container Container Associated ( ' +
              state.container.order_display_id +
              ' )'
            : 'Edit Container'
          : 'Add Container'
      "
      :modal="true"
      class="p-fluid"
    >
      <create-container
        :disabled="!$ability.can('create', 'inventory-containers')"
        @hide="state.containerDialog = false"
        :containerProp="state.container"
        :status="currentStatus"
        :resetFunction="reset"
        :shouldSwap="true"
      />
    </Dialog>

    <Dialog
      v-model:visible="state.containerDetailDialog"
      maximizable
      dismissableMask
      closeOnEscape
      header="Container Detail"
      :modal="true"
      class="p-fluid"
    >
      <ContainerHistory
        :container="state.container"
        @hide="state.containerDetailDialog = false"
      />
    </Dialog>

    <Dialog
      v-model:visible="state.orderDetailDialog"
      :style="{ height: '100vh' }"
      :breakpoints="{
        '2000px': '45vw',
        '1400px': '55vw',
        '1200px': '65vw',
        '992px': '75vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
      closeOnEscape
      :dismissableMask="true"
      keepInViewPort
      modal=""
      :draggable="false"
    >
      <template #header>
        <div class="flex align-items">
          <div class="flex">
            <p :class="smAndSmaller ? 'text-xl' : 'text-3xl'">
              Invoice - {{ state.customerOrder.display_order_id }}
            </p>
          </div>
        </div>
      </template>
      <CustomerOrderDetail :customerOrderProp="state.customerOrder" />
    </Dialog>

    <Dialog
      v-model:visible="state.noteDialog"
      dismissableMask
      closeOnEscape
      :breakpoints="{
        '2000px': '45vw',
        '1400px': '55vw',
        '1200px': '65vw',
        '992px': '75vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
      :modal="true"
    >
      <NoteDetail
        :inventory="state.crtInventory"
        @noteSubmitted="onNoteSubmitted"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, watch, onMounted, inject, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import InventoryService from "@/service/Inventory"
  import CreateContainer from "./CreateContainer.vue"
  import ContainerHistory from "./ContainerHistory.vue"
  import InventorySearchMenu from "./InventorySearchMenu.vue"
  import { useConfirm } from "primevue/useconfirm"
  // import { useDrivers } from "@/store/modules/drivers";
  import { useUsers } from "@/store/modules/users"
  import { useInventory } from "@/store/modules/inventory"

  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import NoteDetail from "../notes/NoteDetail.vue"

  import { useAuth0 } from "@auth0/auth0-vue"
  import cloneDeep from "lodash.clonedeep"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import Lock from "../../service/Lock.js"
  import { useRoute } from "vue-router"
  import { useRouter } from "vue-router"
  import CustomerApi from "@/api/customers"
  import CustomerOrderDetail from "@/components/invoicing/CustomerOrderDetail.vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { isRentalsVisible } from "../../utils/allowedVisibilityForFeatures"
  import { dfl, dfc, dfa, dfc_without_zone } from "@/service/DateFormat.js"
  import InventoryApi from "@/api/inventory"

  const inventoryApi = new InventoryApi()

  const lock = new Lock()
  const customersStore = useCustomerOrder()

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const usersStore = useUsers()
  const inventoryStore = useInventory()
  const customerApi = new CustomerApi()

  const inventoryService = new InventoryService()
  const confirm = useConfirm()
  const toast = useToast()

  const { user } = useAuth0()
  const authUser = user
  const $ability = inject("$ability")

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg

  const columnOrder = inventoryService.columnOrdering

  const router = useRouter()
  const $route = inject("$route")

  const vueRoute = useRoute()
  const route = inject("$route")

  const filteredColumnOrder = computed(() => {
    return columnOrder.filter(
      (col) =>
        col?.status.find((i) => i === currentStatus.value) ||
        col?.status[0] === "All"
    )
  })

  const disabledStatus = computed(() => {
    const statuseKeys = Object.keys(usersStore.cms?.inventory_status_list)
    return statuseKeys.filter((e) => {
      return usersStore.cms?.inventory_status_list[e] === false ? true : false
    })
  })
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
          { name: "Sales", code: "PURCHASE" },
          { name: "Acessory Sales", code: "PURCHASE_ACCESSORY" },
          { name: "Rent to Own", code: "RENT_TO_OWN" },
          { name: "Rentals", code: "RENT" },
          { name: "All", code: "ALL" }
        ]
      : []
  })

  const state = reactive({
    searchType: "CONTAINER_RELEASE",
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
    selectedCategory: { name: "All", code: "ALL" },
    loaded_once_with_param: true,
    customerOrder: {},
    orderDetailDialog: false,
    crtInventory: {}
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

  const filteredContainers = computed(() => {
    state.refreshKey
    if (state.search) {
      return appendOrderId(state.containers)
    }

    switch (currentStatus.value) {
      case "All":
        return appendOrderId(inventoryStore.allInventory)
      case "Available":
        return appendOrderId(inventoryStore.availableInventory)
      case "Attached":
        return appendOrderId(inventoryStore.attachedInventory)
      case "Delivered":
        return appendOrderId(inventoryStore.deliveredInventory)
      case "Delinquent":
        return appendOrderId(inventoryStore.delinquentInventory)
      case "Ready":
        return appendOrderId(inventoryStore.readyInventory)
      case "UNKNOWN":
        return appendOrderId(inventoryStore.unknownInventory)
      default:
        break
    }
  })

  const appendOrderId = (inventory) => {
    return inventory.map((item) => {
      let orderId = ""
      if (item.rental_history?.length > 0) {
        if (item.rental_history?.length === 1) {
          orderId = item.rental_history[0]?.line_item?.order?.display_order_id
        } else {
          orderId = "Has Orders"
        }
      } else {
        if (item.display_order_id && item.display_order_id.length > 0) {
          orderId = item.display_order_id
        }
      }
      item.appended_order_id = orderId

      item.display_created_at = dfc_without_zone(item.created_at)
      item.display_invoiced_at = dfc_without_zone(item.invoiced_at)
      return item
    })
  }

  const openButton = async (data) => {
    state.crtInventory = data
    state.noteDialog = true
  }

  const statusOptions = computed(() => {
    const rentalStatus = usersStore.cms?.inventory_status_options || []
    return rentalStatus.filter((e) => !disabledStatus.value.includes(e))
  })

  const deleteInventory = (container, event) => {
    confirm.require({
      target: event.currentTarget,
      message: "Do you want to remove this inventory item ?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        state.deleteLoading = container.id
        const { data, error } = await inventoryApi.deleteInventory(container.id)
        if (error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Error deleting container",
            group: "br",
            life: 5000
          })
          return
        }
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Container deleted",
          group: "br",
          life: 5000
        })
        inventoryStore.removeFromInventory(container)
        state.refreshKey += 1

        state.isDeleting = false
        state.deleteLoading = null
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Canceled",
          detail: "Inventory removal canceled",
          group: "br",
          life: 2000
        })
        state.deleteLoading = null
      }
    })
  }

  const resetSearch = async () => {
    state.search = ""
    state.quickSearchLoading = false
    state.searchType = "CONTAINER_RELEASE"
    state.containers = []
    toast.add({
      severity: "info",
      summary: "Reset Search",
      detail: "Search reset",
      group: "br",
      life: 5000
    })
  }

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  const getOrderInventory = async (status) => {
    const { data, error } = await inventoryApi.getOrdersWithInventory(
      status,
      state.selectedCategory.code
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
    const flatInventoryOrders = data.value
      .map((i) => inventoryService.orderToInventory(i))
      .flat(1)
    // remove dups from flatInventoryOrders
    return flatInventoryOrders.filter(
      (v, i, a) => a.findIndex((t) => t.id === v.id) === i
    )
  }

  const getInventory = async (skip = 0, limit = 1) => {
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
    } else if (
      currentStatus.value === "Unknown" ||
      currentStatus.value === "UNKNOWN"
    ) {
      const { data, error } = await inventoryApi.getInventoryByStatus(
        currentStatus.value.toUpperCase(),
        state.selectedCategory.code,
        skip,
        limit
      )

      const unknownInventory = [
        ...cloneDeep(inventoryStore.unknownInventory),
        ...inventoryService.inventoryListToDtos(data.value)
      ]
      inventoryStore.setUnknownInventory(unknownInventory)
    } else if (currentStatus.value === "Ready") {
      const { data, error } = await inventoryApi.getInventoryByStatus(
        currentStatus.value,
        state.selectedCategory.code,
        skip,
        limit
      )

      const readyInventory = [
        ...cloneDeep(inventoryStore.readyInventory),
        ...inventoryService.inventoryListToDtos(data.value)
      ]
      inventoryStore.setReadyInventory(readyInventory)
    }

    if (currentStatus.value === "Available" || currentStatus.value === "All") {
      const { data, error } = await inventoryApi.getInventoryByStatus(
        currentStatus.value,
        state.selectedCategory.code,
        skip,
        limit
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

  const currentStatus = computed(() => {
    return statusOptions.value[state.selectedStatusIndex]
  })

  const openContainer = async (container) => {
    if (container.id) {
      state.container = await getContainerById(container.id)
    } else {
      state.container = {}
    }

    const res = await inventoryApi.GetOrderForContainer(state.container.id)
    if (Object.keys(state.container).length != 0) {
      if (res.data.value.length == 0) {
        state.container.order_display_id = "UNKNOWN ORDER"
      } else {
        state.container.order_display_id =
          "Order " + res.data.value[0]["display_order_id"]
      }
    }
    state.containerDialog = true
  }

  const openContainerDetail = async (container) => {
    if (container.id) {
      state.container = container
      state.containerLoading = true
      const { data, error } = await inventoryApi.getInventoryById(container.id)
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
      state.ordersWithContainer = data.value
      state.container = data.value
    } else {
      state.container = {}
    }
    state.containerDetailDialog = true
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

  const onNoteSubmitted = async (inventory_id) => {
    await reset()
    state.noteDialog = false
  }

  const reset = async () => {
    const prevPage = dt.value.d_first
    state.loading = true
    await lock.acquire()
    inventoryStore.$reset()
    await getInventory(0, prevPage + 50)
    await lock.release()
    state.loading = false
    dt.value.d_first = prevPage
  }

  onMounted(async () => {
    if (Object.keys(route.currentRoute.value.params).length != 0) {
      state.containerLoading = true
      let { data, isLoading, error } =
        await inventoryApi.getInventoryByIdPrefix(
          route.currentRoute.value.params["id"]
        )
      if (error.value) {
        state.containerLoading = false
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error loading inventory",
          group: "br",
          life: 5000
        })
        return
      }

      state.container = data.value
      state.containerLoading = true
      state.ordersWithContainer = data.value
      state.containerDetailDialog = true
      state.containerLoading = false
      state.loaded_once_with_param = true
    } else {
      if ($route.currentRoute.value.query.hasOwnProperty("status")) {
        for (var i = 0; i < statusOptions.value.length; i++) {
          if (
            statusOptions.value[i].toLowerCase() ==
            $route.currentRoute.value.query["status"].toLowerCase()
          ) {
            state.selectedStatusIndex = i
            break
          }
        }
      }
      await lock.acquire()
      inventoryStore.$reset()
      let skip = 0
      await getInventory(skip)
      await lock.release()
    }
  })

  watch(
    () => vueRoute.params,
    async (newParams, oldParams) => {
      if (Object.keys(route.currentRoute.value.params).length != 0) {
        state.containerLoading = true
        let { data, isLoading, error } =
          await inventoryApi.getInventoryByIdPrefix(
            route.currentRoute.value.params["id"]
          )
        if (error.value) {
          state.containerLoading = false
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Error loading inventory",
            group: "br",
            life: 5000
          })
          return
        }
        state.container = data.value
        state.ordersWithContainer = data.value
        state.containerDetailDialog = true
        state.containerLoading = false
      }
    }
  )

  const selectStatus = async (index) => {
    state.selectedStatusIndex = index
    state.inventoryRawLength = 0
  }

  const onPage = async (props) => {
    if (props.page === props.pageCount - 1) {
      let skip = 0
      switch (currentStatus.value) {
        case "All":
          skip = inventoryStore.allInventory.length
          break
        case "Available":
          skip = inventoryStore.availableInventory.length
          break
        case "Attached":
          skip = inventoryStore.attachedInventory.length
          break
        case "Delivered":
          skip = inventoryStore.deliveredInventory.length
          break
        case "Delinquent":
          skip = inventoryStore.delinquentInventory.length
          break
        case "UNKNOWN":
          skip = inventoryStore.unknownInventory.length
          break
        default:
          break
      }

      await lock.acquire()
      await getInventory(skip)
      await lock.release()

      dt.value.d_first = 100 * (props.pageCount - 1)
    }
  }

  const searchInventory = async () => {
    state.quickSearchLoading = true
    state.containers = []
    const { data } = await inventoryApi.searchInventory(
      `searchBy=${state.searchType}&searchValue=${state.search}`
    )
    state.containers = inventoryService
      .removeOtherInventory(state.searchType, state.search, data.value)
      .map((i) => inventoryService.orderToInventory(i))
      .flat(1)
      .filter((v, i, a) => a.findIndex((t) => t.id === v.id) === i)
    state.quickSearchLoading = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Search complete",
      group: "br",
      life: 5000
    })
  }

  const changeCategory = async (category) => {
    await lock.acquire()
    state.selectedCategory = category
    await getInventory(0)
    await lock.release()
  }

  const exportCSV = () => dt.value.exportCSV()
  const openOrder = async (orderId) => {
    state.individualOrderLoading = orderId
    await getOrderByDisplayId(orderId)
    state.individualOrderLoading = null
    state.orderDetailDialog = true
  }
  const getOrderByDisplayId = async (id) => {
    const { data, isLoading, error } = await customerApi.getOrderByDisplayId(id)

    if (error.value) {
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
      state.customerOrder = data.value
      customersStore.setOrder(data.value)
    }
  }

  watch(
    () => currentStatus.value,
    async () => {
      await lock.acquire()
      inventoryStore.$reset()
      let skip = 0
      await getInventory(skip)
      await lock.release()

      router.push({
        name: "inventory",
        query: { status: currentStatus.value.toLowerCase() }
      })
    }
  )

  watch(
    () => $route.currentRoute.value.query.status,
    async (newVal, oldVal) => {
      for (var i = 0; i < statusOptions.value.length; i++) {
        if (
          statusOptions.value[i].toLowerCase() ==
          $route.currentRoute.value.query["status"]?.toLowerCase()
        ) {
          state.selectedStatusIndex = i
          break
        }
      }
    }
  )

  watch(
    () => state.containerDetailDialog,
    async (oldValue, newValue) => {
      if (oldValue == false && newValue == true) {
        if (state.loaded_once_with_param == true) {
          state.loaded_once_with_param = false
          reset()
        }
      }
    }
  )

  watch(
    () => state.selectedCategory,
    async () => {
      await lock.acquire()
      inventoryStore.$reset()
      let skip = 0
      await getInventory(skip)
      await lock.release()
    }
  )
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
