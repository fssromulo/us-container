<template>
  <div class="flex flex-col w-full">
    <div>
      <CreateAccessory
        v-if="$ability.can('edit', 'accessories')"
        isAttaching
        @containerAttached="setAttachedContainer"
        :lineItem="props.lineItem"
        :displayOrderId="props.displayOrderId"
      />
    </div>
    <div class="border border-t col-span-12 mt-2"></div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, inject, computed, watch } from "vue"
  import InventoryService from "@/service/Inventory"

  import InventoryApi from "@/api/inventory"
  import LineItemApi from "@/api/lineItem"
  import DepotApi from "@/api/depot"
  import DepotService from "@/service/Depot"
  import { useDepots } from "@/store/modules/depots"
  import CreateAccessory from "./CreateAccessory.vue"
  import AttachContainer from "../inventory/AttachContainer.vue"
  import InventoryDataTable from "./InventoryDataTable.vue"
  import { useUsers } from "@/store/modules/users"
  import InventorySearchMenu from "./InventorySearchMenu.vue"
  import { useInventory } from "@/store/modules/inventory"

  import { useToast } from "primevue/usetoast"
  const $ability = inject("$ability")

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const customerStore = useCustomerOrder()

  const toast = useToast()

  const inventoryService = new InventoryService()
  const inventoryApi = new InventoryApi()

  const depotApi = new DepotApi()
  const depotService = new DepotService()
  const depotStore = useDepots()
  const userStore = useUsers()
  const inventoryStore = useInventory()

  const lineItemApi = new LineItemApi()

  const emit = defineEmits(["onUpdate"])

  const props = defineProps({
    displayOrderId: {
      type: String,
      default: ""
    },
    lineItem: {
      type: Object,
      default: () => ({})
    },
    close: {
      type: Function,
      default: () => {}
    },
    updatedLineItem: {
      type: Function,
      default: () => {}
    },
    returnContainerId: {
      type: Boolean,
      default: false
    },
    selectedContainers: {
      type: Array,
      default: []
    }
  })

  onMounted(async () => {
    if (depotStore.depots?.length === 0) {
      state.isLoading = true
      const { data } = await depotApi.getDepots()
      const depots = data.value.map((depot) => depotService.dtoDepot(depot))
      depotStore.setDepots(depots)
      state.isLoading = false
    }
  })

  const state = reactive({
    selectedDepot: null,
    selectedCity: null,
    selectedContainer: null,
    availableInventory: [],
    addNew: false,
    isLoading: false,
    detachLoading: false,
    filters: {
      global: {
        value: ""
      }
    }
  })

  const mappedDepotCities = computed(() => {
    return depotStore.depots
      .map((depot) => {
        return {
          label: depot?.city || "No City",
          value: depot?.city || "No City"
        }
      })
      .filter((depot, index, self) => {
        return self.findIndex((t) => t.value === depot.value) === index
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const mappedDepots = computed(() => {
    return depotStore.depots
      .filter((d) => d.city === state.selectedCity)
      .map((depot) => {
        return {
          label: depot.name,
          value: depot.id
        }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const filteredInventory = computed(() => {
    if (!state.filters.global.value) {
      return state.availableInventory
    }
    return state.availableInventory.filter((item) => {
      const searchQuery = state.filters.global.value.toLowerCase()
      const fieldsToSearch = Object.keys(item).filter(
        (key) => typeof item[key] === "string"
      )
      return fieldsToSearch.some((key) =>
        item[key].toLowerCase().includes(searchQuery)
      )
    })
  })

  const mappedContainers = computed(() => {
    return filteredInventory.value
      .filter((container) => !props.selectedContainers.includes(container.id))
      .sort((a, b) =>
        a.container_release_number.localeCompare(b.container_release_number)
      )
  })

  const setSelectedContainer = (container) => {
    state.selectedContainer = container
  }

  const setAttachedContainer = async (container) => {
    await attachContainer(container)
  }

  const attachContainer = async (newContainer) => {
    if (props.returnContainerId) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Container details attached",
        group: "br",
        life: 2000
      })
      emit("onUpdate", {
        inventory_id: state.selectedContainer?.id || newContainer?.id,
        inventory_title: state.selectedContainer
          ? state.selectedContainer?.container_release_number +
            " | " +
            state.selectedContainer?.container_number
          : newContainer?.container_release_number +
            " | " +
            newContainer?.container_number
      })
      state.isLoading = false
      state.addNew = false
    } else {
      state.isLoading = true

      let updateData = [
        {
          id: props.lineItem.id,
          inventory_id: state.selectedContainer?.id || newContainer?.id,
          product_cost:
            state.selectedContainer?.total_cost || newContainer?.total_cost
        }
      ]
      const { data, error } = await lineItemApi.updateLineItem(updateData)
      if (data.value) {
        await inventoryApi.updateInventory(data.value[0].inventory.id, {
          status: "Attached"
        })

        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Order updated",
          group: "br",
          life: 2000
        })
        emit("onUpdate")
        state.isLoading = false
        state.addNew = false
        return
      }

      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating order",
          group: "br",
          life: 2000
        })
        state.isLoading = false
        return
      }
    }
  }

  watch(
    () => inventoryStore.allInventory,
    async (newVal, oldVal) => {
      state.availableInventory = newVal
        .map((inventory) => inventoryService.dtoInventory(inventory))
        .filter(function (container) {
          return container.status === "Available"
        })
    }
  )

  watch(
    () => state.selectedDepot,
    async (newVal, oldVal) => {
      state.isLoading = true
      const { data, error } = await inventoryApi.getInventoryByDepot(newVal)
      if (error.value && !data.value) {
        toast.add({
          severity: "info",
          summary: "Not found",
          detail: "No containers available at this depot",
          group: "br",
          life: 2000
        })
        state.availableInventory = []
        return
      } else {
        state.availableInventory = data.value
          .filter((container) => {
            return container.status === "Available"
          })
          .map((inventory) => inventoryService.dtoInventory(inventory))
      }
      state.isLoading = false
    }
  )
</script>

<style scoped>
  .p-datepicker-current-day {
    background-color: blue !important;
  }
</style>
