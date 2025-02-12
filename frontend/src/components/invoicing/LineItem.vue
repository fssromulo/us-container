<template>
  <div class="flex items-center justify-between w-full"> </div>
  <div>
    <ul
      class="flex p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900"
    >
      <template v-for="(name, idx) in filteredLineList">
        <li class="pr-4">
          <a
            v-ripple
            class="p-button p-component"
            :class="{
              'p-button-primary': state.active === idx,
              'p-button-secondary': state.active !== idx
            }"
            :style="[state.active === idx ? { color: 'white' } : '']"
            @click="state.active = idx"
          >
            <span class="text-2xl font-medium">{{ name }}</span>
          </a>
        </li>
        <li class="flex items-center">
          <div style="width: 1px; height: 50%" class="border border-r"></div>
        </li>
      </template>
    </ul>
  </div>
  <div v-if="state.active === filteredLineList.indexOf('Containers')">
    <line-item-detail :swapCustomerOrder="props.swapCustomerOrder" />
  </div>
  <div
    v-if="
      state.active === filteredLineList.indexOf('Accessories') &&
      $ability.can('view', 'accessories')
    "
  >
    <accessory-item-detail />
  </div>
</template>

<script setup>
  import { reactive, inject, computed } from "vue"

  import LineItemDetail from "./LineItemDetail.vue"
  import AccessoryItemDetail from "./AccessoryItemDetail.vue"

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const customerStore = useCustomerOrder()
  const $ability = inject("$ability")

  const props = defineProps({
    swapCustomerOrder: {
      type: Function,
      required: false,
      default: () => {}
    }
  })

  const filteredLineList = computed(() => {
    let componentsList = []
    let accessories = customerStore.order.line_items.filter(
      (a) => a.product_type && a.product_type !== "CONTAINER"
    )
    let containers = customerStore.order.line_items.filter(
      (a) =>
        a.product_type === null ||
        a.product_type == undefined ||
        a.product_type === "CONTAINER"
    )

    if (containers.length > 0) componentsList.push("Containers")
    if (accessories.length > 0 && $ability.can("view", "accessories"))
      componentsList.push("Accessories")
    return componentsList
  })
  const state = reactive({
    active: 0
  })
</script>
