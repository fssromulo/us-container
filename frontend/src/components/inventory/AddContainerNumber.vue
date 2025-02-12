<template>
  <div>
    <table class="p-datatable-sm">
      <tr v-for="(lineItem, i) in lineItems" style="height: 2rem">
        <td class="text-xl text-900 dark:text-0">
          {{ lineItem.title }}, Release
          {{ lineItem?.inventory?.container_release_number }}
        </td>
        <td class="text-xl text-900 dark:text-0">
          <div class="field mb-4 col-span-12">
            <label
              for="container_number"
              class="font-medium text-900 dark:text-0"
              >Container #</label
            >
            <InputText
              mode="decimal"
              :useGrouping="false"
              v-model="lineItem.inventory.container_number"
              id="container_number"
              type="text"
            />
          </div>
        </td>
      </tr>
    </table>

    <Button
      label="Add container #"
      @click="createUpdateContainer()"
      icon="pi pi-file"
      class="w-auto"
    ></Button>

    <Button
      v-if="$ability.can('update', 'can_admin_override')"
      label="Admin Override"
      @click="createUpdateContainerAdmin()"
      icon="pi pi-file"
      class="w-auto ml-8"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, defineEmits } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"
  import VendorsService from "@/service/Vendors"
  import DepotService from "@/service/Depot"

  import { useVendors } from "@/store/modules/vendors"
  import { useDepots } from "@/store/modules/depots"
  import InventoryService from "@/service/Inventory"
  import InventoryApi from "@/api/inventory"
  import { useToast } from "primevue/usetoast"
  import { useInventory } from "@/store/modules/inventory"
  import { useUsers } from "@/store/modules/users"
  const $ability = inject("$ability")

  const toast = useToast()
  const userStore = useUsers()

  const depotService = new DepotService()
  const inventoryService = new InventoryService()
  const inventoryApi = new InventoryApi()

  const vendorStore = useVendors()
  const depotStore = useDepots()
  const inventoryStore = useInventory()

  const stateService = new StateService()

  const { containerProp, lineItems } = defineProps({
    containerProp: {
      type: Object,
      default: () => ({})
    },
    lineItems: {
      type: Array,
      default: () => []
    }
  })

  const emit = defineEmits(["containerNumberAdded"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  onMounted(async () => {
    state.statesList = stateService.getStates()
    resetContainer()
  })

  const state = reactive({
    loading: false,
    selectedCity: null,
    originalContainer: null,
    selectedCategory: { name: "Rental", code: "rental" },
    categorys: [
      { name: "Rental", code: "rental" },
      { name: "Rent to Own", code: "rto" },
      { name: "Sale", code: "purchase" }
    ]
  })

  const rules = computed(() => ({
    container: {
      container_number: { required, $lazy: true }
    }
  }))

  const v$ = useVuelidate(rules, state)

  const resetContainer = () => {
    let container = null
    if (containerProp) {
      container = inventoryService.dtoInventory(containerProp)
    } else {
      container = emptyContainer
    }
    state.originalContainer = cloneDeep(container)
    state.container = cloneDeep(container)
    v$.value.$reset()
  }

  const createUpdateContainer = async () => {
    state.loading = true

    const containerPromises = lineItems.map(async (lineItem) => {
      if (!lineItem.inventory.container_number) {
        toast.add({
          severity: "error",
          summary: "Container Number Required",
          detail: "Please enter a container number",
          group: "br",
          life: 5000
        })
        return
      }
      await inventoryApi.updateInventory(lineItem.inventory.id, {
        container_number: lineItem.inventory.container_number
      })
    })

    await Promise.all(containerPromises)

    toast.add({
      severity: "success",
      summary: "Container Updated",
      detail: "Successfully updated container",
      group: "br",
      life: 5000
    })
    resetContainer()
    state.loading = false
    emit("containerNumberAdded")
  }

  const createUpdateContainerAdmin = async () => {
    resetContainer()
    state.loading = false
    emit("containerNumberAdded")
  }
</script>
<style></style>
