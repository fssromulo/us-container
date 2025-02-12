<template>
  <div class="grid grid-cols-12 gap-4">
    <div
      v-if="!state.addNew"
      :class="{
        'col-span-3': state.hasRelatedContainers,
        'col-span-0': !state.hasRelatedContainers
      }"
      v-show="state.hasRelatedContainers"
    >
      <RelatedReleaseContainers
        :releaseNumber="state.containerReleaseNumber"
        @hasRelatedContainers="hasRelatedContainers"
      >
      </RelatedReleaseContainers>
    </div>
    <div
      :class="{
        'col-span-9': state.hasRelatedContainers,
        'col-span-12': !state.hasRelatedContainers
      }"
    >
      <div class="grid grid-cols-12 gap-4">
        <div class="col-span-12 mt-2 border border-t"></div>
        <div
          class="grid grid-cols-12 col-span-12 gap-4 md:col-start-2"
          v-if="!state.addNew"
        >
          <label class="col-span-12 font-medium text-900 dark:text-0"
            >Search By Id</label
          >
          <InventorySearchMenu
            containerStatus="Available"
            @openContainer="openContainer"
            @setReleaseNumber="setReleaseNumber"
            :requiredFilterFields="['container', 'release', 'searchContainer']"
          />
        </div>
        <div
          v-if="!state.addNew"
          class="grid grid-cols-12 col-span-12 gap-4 md:col-start-2"
        >
          <!-- CHANGE THIS -->
          <label class="col-span-12 font-medium text-900 dark:text-0"
            >Search By Depot</label
          >
          <template v-if="true">
            <div class="md:col-span-3">
              <Select
                class="w-full"
                placeholder="Select City"
                v-model="state.selectedCity"
                optionLabel="label"
                optionValue="value"
                :options="mappedDepotCities"
              />
            </div>
            <div class="md:col-span-3">
              <Select
                class="w-full"
                placeholder="Select Depot"
                v-model="state.selectedDepot"
                optionLabel="label"
                optionValue="value"
                :options="mappedDepots"
              />
            </div>
            <div class="md:col-span-3">
              <InputText
                class="w-full"
                placeholder="Search..."
                v-model="state.filters.global.value"
              />
            </div>
          </template>
        </div>
        <div v-else class="grid grid-cols-12 col-span-12 gap-4">
          <CreateContainer
            isAttaching
            @containerAttached="setAttachedContainer"
          />
        </div>
        <div
          v-if="
            mappedContainers && state.availableInventory.length && !state.addNew
          "
          class="col-span-12"
        >
          <InventoryDataTable
            @attachContainer="setSelectedContainer"
            :containers="mappedContainers"
          />
        </div>
        <div class="col-span-12">
          <h3
            style="font-size: medium; border-radius: 5px; padding: 5px"
            class="mr-2"
          >
            Number of Containers ({{ filteredInventory.length }})
          </h3>
        </div>
        <div class="col-span-12 text-right">
          <Button
            v-if="!state.addNew"
            @click="props.close"
            label="Cancel"
            class="p-button-raised p-button-secondary"
          />
          <Button
            v-if="!state.addNew"
            @click="attachContainer"
            :loading="state.isLoading"
            class="ml-4 mr-8 p-button-raised"
            label="Save"
          />
          <ToggleButton
            v-if="!state.addNew"
            v-model="state.addNew"
            class="ml-4 mr-8"
            onLabel="Existing Container"
            offLabel="Add new container"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, computed, watch } from "vue"
  import InventoryService from "@/service/Inventory"
  import InventoryApi from "@/api/inventory"
  import LineItemApi from "@/api/lineItem"
  import DepotApi from "@/api/depot"
  import DepotService from "@/service/Depot"
  import { useDepots } from "@/store/modules/depots"
  import CreateContainer from "./CreateContainer.vue"
  import AttachContainer from "../inventory/AttachContainer.vue"
  import InventoryDataTable from "./InventoryDataTable.vue"
  import { useUsers } from "@/store/modules/users"
  import InventorySearchMenu from "./InventorySearchMenu.vue"
  import { useInventory } from "@/store/modules/inventory"
  import RelatedReleaseContainers from "@/components/inventory/RelatedReleaseContainers.vue"

  import { useToast } from "primevue/usetoast"
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
    containerReleaseNumber: "",
    availableInventory: [],
    hasRelatedContainers: false,
    addNew: false,
    isLoading: false,
    detachLoading: false,
    filters: {
      global: {
        value: ""
      }
    }
  })

  const hasRelatedContainers = (status) => {
    state.hasRelatedContainers = status
  }

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
        title:
          state.selectedContainer?.product?.title ||
          newContainer?.product?.title,
        attribute: state.selectedContainer?.type || newContainer?.type,
        container_size:
          state.selectedContainer?.container_size ||
          newContainer?.container_size,
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
      if (
        !(
          "standard" in props.lineItem.attributes &&
          props.lineItem.attributes["standard"] == true
        ) &&
        !(
          "double_door" in props.lineItem.attributes &&
          props.lineItem.attributes["double_door"] == true
        ) &&
        !(
          "high_cube" in props.lineItem.attributes &&
          props.lineItem.attributes["high_cube"] == true
        )
      ) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Cannot attach a box as the container type is invalid.",
          group: "br",
          life: 10000
        })
        state.isLoading = false
        return
      }

      if (props.lineItem.inventory_id) {
        let updateData = {
          lineItems: [
            {
              id: props.lineItem.id,
              inventory_id: null
            }
          ],
          inventoryIdsToMakeAvailable: [props.lineItem.inventory_id]
        }
        const { data, error } = await lineItemApi.updateLineItemExtra(
          updateData
        )

        if (error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Error detaching old container.",
            group: "br",
            life: 2000
          })
          state.isLoading = false
          return
        }
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Sucessfully detached old container",
          group: "br",
          life: 2000
        })
      }

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
        let error_message = "Internal Error"
        if (error.value.response !== undefined)
          error_message = error.value.response.data.detail

        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating order: " + error_message,
          group: "br",
          life: 2000
        })
        state.isLoading = false
        return
      }
    }
  }

  const setReleaseNumber = (number) => {
    state.containerReleaseNumber = number
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
