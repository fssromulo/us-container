<template>
  <div class="grid grid-cols-12 gap-4 mt-2 formgrid p-fluid">
    <div class="col-span-12 md:col-span-12 xl:col-span-12">
      <AutoComplete
        v-model="state.searchTerm"
        class="w-full p-component p-inputtext-fluid"
        @complete="search"
        placeholder="Search accessories"
        :suggestions="state.suggestions"
      />
    </div>
    <div class="col-span-11 mt-2 md:col-span-11 xl:col-span-11">
      <p class="text-xl">Most Popular:</p>
    </div>

    <div class="cols-span-1">
      <OverlayBadge
        :value="
          customerOrderStore.cart.containers.length +
          customerOrderStore.cart.accessories.length
        "
        severity="danger"
        v-if="
          customerOrderStore.cart.containers.length +
          customerOrderStore.cart.accessories.length
        "
        v-styleclass="{
          selector: '@next'
        }"
      >
        <i
          @click="toggle"
          class="pi pi-shopping-cart p-text-secondary"
          style="font-size: 2rem; float: right"
        />
      </OverlayBadge>
      <Popover ref="cartMini">
        <cart-mini class="z-5" />
      </Popover>
    </div>
  </div>
</template>
<script setup>
  import { reactive, inject, onMounted, watch, ref } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useContainerPrices } from "@/store/modules/pricing"

  import CartMini from "@/components/cart/CartMini.vue"
  const pricingStore = useContainerPrices()
  const { buyType, retrievedAccessories } = defineProps({
    buyType: {
      type: String,
      default: ""
    },
    retrievedAccessories: {
      type: Object,
      default: () => ({})
    }
  })
  const customerOrderStore = useCustomerOrder()
  const $fc = inject("$formatCurrency")

  const state = reactive({
    viewCart: false,
    searchTerm: null,
    suggestions: []
  })

  const viewCart = () => {
    state.viewCart = true
  }

  const search = (event) => {
    const mappedAccessories = pricingStore.accessoryPrices
      .filter((access) => {
        return access.title.toLowerCase().includes(event.query.toLowerCase())
      })
      .map((accessory) => {
        const location = accessory.location
        delete accessory.location
        return Object.assign(accessory, location, {
          accessoryId: accessory.id,
          type: buyType
        })
      })
      .sort((a, b) => a.title.localeCompare(b.title))

    state.suggestions = pricingStore.accessoryPrices
      .filter((access) => {
        return access.title.toLowerCase().includes(event.query.toLowerCase())
      })
      .map((el) => {
        return el.title
      })
    pricingStore.setFilteredAccessories(mappedAccessories)
  }
  const cartMini = ref()
  const toggle = (event) => {
    cartMini.value.toggle(event)
  }
  onMounted(() => {
    const mappedAccessories = pricingStore.accessoryPrices
      .map((accessory) => {
        const location = accessory.location
        delete accessory.location
        return Object.assign(accessory, location, {
          accessoryId: accessory.id,
          type: buyType
        })
      })
      .sort((a, b) => a.title.localeCompare(b.title))
    pricingStore.setFilteredAccessories(mappedAccessories)
  })
  watch(
    () => state.searchTerm,
    async (newVal, oldVal) => {
      if (newVal.length === 0) {
        const mappedAccessories = pricingStore.accessoryPrices
          .map((accessory) => {
            const location = accessory.location
            delete accessory.location
            return Object.assign(accessory, location, {
              accessoryId: accessory.id,
              type: buyType
            })
          })
          .sort((a, b) => a.title.localeCompare(b.title))
        pricingStore.setFilteredAccessories(mappedAccessories)
      }
    }
  )
</script>
