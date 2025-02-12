<template>
  <div>
    <ul
      class="flex p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900"
    >
      <template :key="idx" v-for="(name, idx) in state.componentList">
        <li class="pr-4">
          <a
            v-ripple
            class="flex items-center px-6 py-4 p-button p-component"
            :class="{
              'p-button-primary': state.active === idx,
              'p-button-secondary': state.active !== idx
            }"
            @click="state.active = idx"
          >
            <span
              class="text-2xl font-medium p-button-label"
              style="color: #f5f9ff"
              >{{ name }}</span
            >
          </a>
        </li>
        <li class="flex items-center">
          <div style="width: 1px; height: 50%" class="border border-r"></div>
        </li>
      </template>
    </ul>
    <inventory-table v-if="state.active === 0" class="mt-2"></inventory-table>
    <vendors-table
      v-if="state.active === 1 && $ability.can('read', 'inventory-vendors')"
      class="mt-2"
    ></vendors-table>
    <depots-table v-if="state.active === 2" class="mt-2"></depots-table>
  </div>
</template>

<script setup>
  // && $ability.can('read', 'inventory-depots')
  import { reactive, inject } from "vue"
  import InventoryTable from "@/components/inventory/InventoryTable.vue"
  import VendorsTable from "@/components/vendors/VendorsTable.vue"
  import DepotsTable from "@/components/depots/DepotsTable.vue"
  const $ability = inject("$ability")

  const state = reactive({
    active: 0,
    componentList: ["Inventory", "Vendors", "Depots"]
  })
</script>

<style></style>
