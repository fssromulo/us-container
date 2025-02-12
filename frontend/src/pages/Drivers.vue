<template>
  <div>
    <ul
      class="flex p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900"
    >
      <template :key="idx" v-for="(name, idx) in componentList">
        <li class="pr-4">
          <a
            v-ripple
            class="flex px-4 py-3 transition-colors cursor-pointer align-items-center hover:surface-100 border-round transition-duration-150 p-ripple"
            :class="{
              'p-button p-component p-button-secondary': active === idx,
              'text-700 dark:text-100': active !== idx
            }"
            @click="active = idx"
          >
            <span class="text-2xl font-medium">{{ name }}</span>
          </a>
        </li>
        <li class="flex items-center">
          <div style="width: 1px; height: 50%" class="border border-r"></div>
        </li>
      </template>
    </ul>

    <drivers-table v-if="active === 0" class="mt-2"></drivers-table>
    <!-- <deliveries-table
      v-if="active === 1"
      class="mt-2"
    ></deliveries-table> -->
  </div>
</template>

<script>
  import DriversTable from "@/components/drivers/DriversTable.vue"
  import DeliveriesTable from "@/components/drivers/DeliveriesTable.vue"

  export default {
    components: { DriversTable, DeliveriesTable },
    data() {
      return {
        active: 0,
        componentList: [
          "Drivers"
          // "Deliveries",
        ]
      }
    }
  }
</script>

<style></style>
