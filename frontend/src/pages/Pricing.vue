<template>
  <div>
    <ul
      class="flex p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900"
      style="max-width: 95vw"
    >
      <template :key="idx" v-for="(name, idx) in filteredComponentList">
        <li class="pr-4">
          <a
            v-ripple
            class="flex items-center px-6 py-4 cursor-pointer p-button p-component p-ripple"
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

    <container-pricing-table
      v-if="state.active === 0"
      :locations="locations"
      :containerPrices="containerPrices"
      :accessoriesPrices="accessoriesPrices"
      :productCategories="productCategories"
      class="mt-6"
    ></container-pricing-table>
    <accessories-pricing-table
      v-if="state.active === 1 && $ability.can('create', 'accessories')"
      :locations="locations"
      :containerPrices="containerPrices"
      :accessoriesPrices="accessoriesPrices"
      :productCategories="productCategories"
      class="mt-6"
    ></accessories-pricing-table>
    <product-categories-table
      v-if="state.active === 2 && $ability.can('create', 'accessories')"
      :locations="locations"
      :containerPrices="containerPrices"
      :accessoriesPrices="accessoriesPrices"
      :productCategories="productCategories"
      class="mt-6"
    ></product-categories-table>
    <locations-table
      v-if="state.active === 3 && $ability.can('create', 'accessories')"
      :locations="locations"
      :containerPrices="containerPrices"
      :accessoriesPrices="accessoriesPrices"
      :productCategories="productCategories"
      class="mt-6"
    ></locations-table>
  </div>
</template>

<script setup>
  import LocationsTable from "@/components/pricing/LocationsTable.vue"
  import ContainerPricingTable from "@/components/pricing/ContainerPricingTable.vue"
  import AccessoriesPricingTable from "@/components/pricing/AccessoriesPricingTable.vue"
  import ProductCategoriesTable from "@/components/pricing/ProductCategoriesTable.vue"

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const customerStore = useCustomerOrder()

  import { computed, inject, reactive } from "vue"

  const $ability = inject("$ability")
  const state = reactive({
    active: 0,
    componentList: []
  })

  const filteredComponentList = computed(() => {
    state.componentList = []
    state.componentList.push("Container")
    if ($ability.can("create", "accessories")) {
      state.componentList.push("Accessories")
      state.componentList.push("Categories")
    }
    state.componentList.push("Locations")

    return state.componentList.filter((name) => {
      if (name === "Locations") {
        return $ability.can("read", "navigation-warehouses")
      }
      return true
    })
  })
</script>

<style></style>
