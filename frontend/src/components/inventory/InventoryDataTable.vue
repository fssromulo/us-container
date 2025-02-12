<template>
  <div>
    <div class="mx-6 mt-4">
      <DataTable
        ref="dt"
        selectionMode="single"
        :value="props.containers"
        v-model:selection="state.selectedInventory"
        dataKey="id"
      >
        <Column selectionMode="single" headerStyle="width: 3rem"></Column>
        <Column field="id" header="Container Id" style="width: 160px">
          <template #body="slotProps">
            <p>{{ slotProps.data.id.substring(0, 4) }}</p>
          </template>
        </Column>
        <Column field="created_at" header="Created on" style="width: 160px">
          <template #body="slotProps">
            <p>{{ dfc_without_zone(slotProps.data.created_at) }} </p>
          </template>
        </Column>
        <Column field="invoiced_at" header="Invoiced date" style="width: 160px">
          <template #body="slotProps">
            <p>{{ dfc_without_zone(slotProps.data.invoiced_at) }} </p>
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
      </DataTable>
      <LoadingTable v-if="state.loading" :columns="filteredColumnOrder" />
    </div>
  </div>
</template>

<script setup>
  import { reactive, computed, watch, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import InventoryService from "@/service/Inventory"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { dfs, dfc_without_zone } from "@/service/DateFormat"
  const inventoryService = new InventoryService()

  const props = defineProps(["containers"])
  const emit = defineEmits(["attachContainer"])

  const columnOrder = inventoryService.columnOrdering
  const filteredColumnOrder = computed(() => {
    let data = columnOrder.filter(
      (col) =>
        col?.status.find((i) => i === "AttachingContainer") &&
        col.field != "display_invoiced_at" &&
        col.field != "display_created_at"
    )
    return data
  })

  const state = reactive({
    selectedInventory: null
  })

  const dt = ref()

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  const attachContainer = () => {}

  initFilters()

  watch(
    () => state.selectedInventory,
    (newVal) => {
      if (newVal) {
        emit("attachContainer", state.selectedInventory)
      }
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
