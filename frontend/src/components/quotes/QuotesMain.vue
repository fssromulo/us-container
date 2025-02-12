<template>
  <div>
    <div v-if="!$isPublic">
      <ul
        class="flex w-full p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900 md:w-"

      >
        <li class="pr-4">
          <a
            v-ripple
            class="flex items-center px-6 py-4 transition-colors duration-150 cursor-pointer rounded-border p-ripple"
            :class="{
              'p-button p-component p-button-secondary':
                state.visibleQuoteOption === 'Container',
              'text-700 dark:text-100': state.visibleQuoteOption !== 'Container'
            }"
            @click="state.visibleQuoteOption = 'Container'"
          >
            <span class="text-2xl font-medium">Containers</span>
          </a>
        </li>

        <li class="flex items-center">
          <div style="width: 1px; height: 50%" class="border border-r"></div>
        </li>
        <li
          class="pr-4"
          v-if="buyType === 'PURCHASE' && $ability.can('quote', 'accessories')"
        >
          <a
            v-ripple
            class="flex items-center px-6 py-4 transition-colors duration-150 cursor-pointer rounded-border p-ripple"
            :class="{
              'p-button p-component p-button-secondary':
                state.visibleQuoteOption === 'Accessories',
              'text-700 dark:text-100':
                state.visibleQuoteOption !== 'Accessories'
            }"
            @click="state.visibleQuoteOption = 'Accessories'"
          >
            <span class="text-2xl font-medium">Accessories</span>
          </a>
        </li>
      </ul>
    </div>

    <div v-if="pageSize" class="grid grid-cols-12 gap-4 formgrid p-fluid">
      <ul
        class="flex p-0 m-0 list-none select-none bg-0 dark:bg-900"
        v-if="!isRental"
      >
        <li class="" v-for="(q, i) in state.pageItems" :key="i">
          <a
            v-ripple
            class="flex items-center px-4 py-4 text-2xl transition-colors border-b-2 cursor-pointer hover:border-500 dark:hover:border-300 transition-duration-1 p-ripple"
            :class="{
              'border-blue-500 text-blue-500 hover:border-blue-500':
                state.selectedLocation === i,
              'text-700 dark:text-100 border-transparent':
                state.selectedLocation !== i
            }"
            @click="selectLocation(i)"
          >
            <span class="font-medium">{{ tabTitle(q, i) }}</span>
          </a>
        </li>
        <li
          class=""
          v-if="
            buyType === 'PURCHASE' &&
            visibleQuoteOption === 'Accessories' &&
            $ability.can('quote', 'accessories')
          "
        >
          <a
            v-ripple
            class="flex items-center px-4 py-4 text-2xl transition-colors border-b-2 cursor-pointer hover:border-500 dark:hover:border-300 transition-duration-1 p-ripple"
            :class="{
              'border-blue-500 text-blue-500 hover:border-blue-500':
                state.selectedLocation === state.pageItems.length,
              'text-700 dark:text-100 border-transparent':
                state.selectedLocation !== state.pageItems.length
            }"
            @click="selectLocation(state.pageItems.length)"
          >
            <span class="font-medium">Accessories</span>
          </a>
        </li>
      </ul>
    </div>

    <AccessoriesQuote
      :buyType="buyType"
      v-if="
        state.selectedLocation === state.pageItems.length &&
        $ability.can('quote', 'accessories')
      "
    ></AccessoriesQuote>
    <div v-else class="grid grid-cols-12 gap-4 mt-2 formgrid p-fluid">
      <div class="col-span-12" v-if="userStore?.cms?.quotes_filter?.is_active">
        <div class="flex flex-col items-center">
          <div class="grid grid-cols-12 gap-2 w-2/3">
            <div
              v-for="filterOptions in quotesFilterOptions"
              :key="JSON.stringify(filterOptions)"
              class="col-span-4"
            >
              <MultiSelect
                v-if="
                  filterOptions.type === 'dropdown' &&
                  filterOptions.is_multple_select
                "
                v-model="state.containerOptions[filterOptions.default_name]"
                class="w-full mt-1"
                :options="filterOptions.options"
                :placeholder="filterOptions.name"
                optionLabel="label"
                optionValue="value"
              />
              <Select
                v-if="
                  filterOptions.type === 'dropdown' &&
                  !filterOptions.is_multple_select
                "
                v-model="state.containerOptions[filterOptions.default_name]"
                class="w-full mt-1"
                :options="filterOptions.options"
                :placeholder="filterOptions.name"
                optionLabel="label"
                optionValue="value"
              />
              <Button
                v-if="filterOptions.type === 'button'"
                :severity="
                  state.containerOptions[filterOptions.default_name]
                    ? 'primary'
                    : 'primary'
                "
                raised
                :label="filterOptions.name"
                @click="toggleContainerOption(filterOptions.default_name)"
              />
            </div>
          </div>
        </div>
      </div>
      <div class="col-span-11 md:col-span-11 xl:col-span-11">
        <p class="text-xl">
          {{ title }}
        </p>
      </div>
      <br />
      <div class="col-span-11">
        <label class="text-xl" v-if="state.singles_mode == true">Singles</label>
        <label class="text-xl" v-if="state.singles_mode == false"
          >(2) 20's</label
        >
        <ToggleSwitch
          style="margin-left: 30px"
          v-model="state.singles_mode"
          :disabled="isRental"
          type="text"
        />
      </div>

      <div class="cols-span-1" style="margin-right: 8rem">
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
    <div
      v-if="
        state.selectedLocation === state.pageItems.length &&
        $ability.can('quote', 'accessories')
      "
      class="grid grid-cols-12 gap-4 formgrid p-fluid"
      style="min-height: 50vh"
    >
      <AccessoriesBox
        class="z-50"
        @click="openButtonMenu(i)"
        :openButtonMenu="state.selectedButtonMenu === i"
        v-for="(quote, i) in pricingStore.filteredAccessoriesPrices"
        :key="quote.id"
        :quote="quote"
        :category="quote?.product_category || {}"
      />
    </div>
    <div
      class="grid formgrid p-fluid"
      :class="{
        'grid-cols-12  gap-4': quotesListComped.length > 1 || hasFilters,
        'grid-cols-4': quotesListComped.length == 1 && !hasFilters
      }"
      v-else
    >
      <QuoteBox
        v-if="pageSize > 0"
        class="z-50"
        @click="openButtonMenu(i)"
        :openButtonMenu="state.selectedButtonMenu === i"
        v-for="(quote, i) in quotesListComped"
        :key="quote?.containerId"
        :payOnDeliveryContract="payOnDeliveryContract"
        :quote="quote"
        :duplicationMode="duplicationMode"
        :line_items="line_items"
      />
      <QuoteBox
        v-if="pageSize === 0"
        class="z-50"
        @click="openButtonMenu(i)"
        :openButtonMenu="true"
        v-for="(quote, i) in quotesListComped"
        :key="quote.containerId"
        :payOnDeliveryContract="payOnDeliveryContract"
        :quote="quote"
      />
      <div
        class="flex justify-center col-span-10 col-start-2"
        v-if="
          pageSize === 0 &&
          customerOrderStore.cart.containers.length +
            customerOrderStore.cart.accessories.length >
            0
        "
      >
        <Button
          class="flex justify-center p-button-rounded p-button-secondary"
          label="View Cart"
          @click="customerOrderStore.setCreateOrderStatus('IN_PROGRESS')"
        />
        <Button
          class="flex justify-center ml-4 mr-16 p-button-rounded p-button-primary"
          label="Continue shopping"
          @click="emit('hide')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import {
    defineProps,
    reactive,
    computed,
    onMounted,
    watch,
    inject,
    ref
  } from "vue"

  import QuoteBox from "./QuoteBox.vue"
  import AccessoriesBox from "./AccessoriesBox.vue"
  import CartMini from "@/components/cart/CartMini.vue"
  import AccessoriesQuote from "./AccessoriesQuote.vue"
  import { useContainerPrices } from "@/store/modules/pricing"
  import { useUsers } from "@/store/modules/users"
  import { useRoute } from "vue-router"

  const useRouteVar = useRoute()

  const $isPublic = inject("$isPublic") || useRouteVar.path.includes("/quoting")

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const pricingStore = useContainerPrices()

  const customerOrderStore = useCustomerOrder()
  const $ability = inject("$ability")

  const userStore = useUsers()

  const emit = defineEmits(["hide"])

  const {
    quotesList,
    pageSize,
    isPickup,
    isRental,
    buyType,
    visibleQuoteOption,
    payOnDeliveryContract,
    duplicationMode,
    line_items
  } = defineProps({
    quotesList: {
      type: Object,
      default: () => ({})
    },
    payOnDeliveryContract: {
      type: Object,
      default: () => ({})
    },
    isPickup: {
      type: Boolean,
      default: () => false
    },
    pageSize: {
      type: Number,
      default: () => 20
    },
    isRental: {
      type: Boolean,
      default: () => false
    },
    visibleQuoteOption: {
      type: String,
      default: "Container"
    },
    buyType: {
      type: String,
      default: ""
    },
    duplicationMode: {
      type: Boolean,
      default: ""
    },
    line_items: {
      type: Array,
      default: []
    }
  })

  const mappedQuotes = computed(() => {
    return quotesList.map((quote) => quote[0])
  })

  const toggleContainerOption = (option) => {
    initContainerOptions(quotesFilterOptions.value)
    state.containerOptions[option] = !state.containerOptions[option]
  }

  const initContainerOptions = (options) => {
    options.forEach((filterOptions) => {
      state.containerOptions[filterOptions.default_name] =
        filterOptions.default_value
    })
  }

  const quotesFilterOptions = computed(() => {
    const options = userStore?.cms?.quotes_filter?.is_active
      ? userStore?.cms?.quotes_filter?.filter_fields.filter((e) => e.is_enabled)
      : []
    initContainerOptions(options)
    return options
  })

  const rentalList = computed(() => {
    if (userStore?.cms?.rental_filter_title_suffix) {
      return quotesList[state.selectedLocation]?.filter(
        (quote, index, self) => {
          return quote.title.includes(
            userStore?.cms?.rental_filter_title_suffix
          )
        }
      )
    }
    return quotesList[state.selectedLocation]
  })
  const hasFilters = computed(() => {
    if (
      userStore?.cms?.quotes_filter?.is_active &&
      (state.containerOptions?.size.length > 0 ||
        state.containerOptions?.quality.length)
    )
      return true
    return false
  })
  const quotesListComped = computed(() => {
    if (isRental) {
      rentalList.value.sort((a, b) => a.shipping_revenue - b.shipping_revenue)
    }
    let quotesListResult = isRental
      ? rentalList.value.slice(0, 3).filter((quote, index, self) => {
          return (
            index ===
            self.findIndex((q) => q?.containerId === quote?.containerId)
          )
        })
      : quotesList[state.selectedLocation]?.filter((quote, index, self) => {
          return (
            index ===
            self.findIndex((q) => q?.containerId === quote?.containerId)
          )
        })

    if (Object.keys(state.containerOptions).length > 0) {
      const { show_all, size = [], quality = [] } = state.containerOptions
      quotesListResult = quotesListResult.filter((quote) => {
        if (show_all) return true

        const isSizeMatch = (containerSize) =>
          size.includes(containerSize) ||
          (containerSize === "40" &&
            quote.title.includes("High Cube") &&
            size.includes("40_HC"))

        const isQualityMatch = () =>
          quality.some((val) => {
            const splitValues = val.split("|")
            return splitValues.some((splitVal) => {
              const trimmedValue = splitVal.trim()
              if (trimmedValue.includes(" ")) {
                return quote.title.endsWith(trimmedValue)
              }
              return quote.title.includes(trimmedValue)
            })
          })

        if (size.length > 0 && quality.length > 0) {
          return isSizeMatch(quote.container_size) && isQualityMatch()
        }

        if (size.length > 0) {
          return isSizeMatch(quote.container_size)
        }

        if (quality.length > 0) {
          return isQualityMatch()
        }

        return false
      })
    }

    let new_containers = []
    quotesListResult.forEach((el) => {
      if (el.container_size == "20") {
        const new_container = Object.assign({}, el)
        new_container.price = new_container.price * 2
        new_container.shipping_revenue =
          new_container.shipping_revenue +
          (userStore?.cms?.ship_two_twenties_added_fee == undefined
            ? 100
            : userStore?.cms?.ship_two_twenties_added_fee)
        new_container.tax = 2 * new_container.tax
        new_container.is_single = false
        new_containers.push(new_container)
      }
    })

    if (state.singles_mode == true) {
    } else {
      quotesListResult = new_containers
    }

    if (isRental) {
      const uniqueValues = new Set()
      const result = []

      for (const obj of quotesListResult) {
        const value = obj["container_size"]

        if (!uniqueValues.has(value)) {
          uniqueValues.add(value)
          result.push(obj)
        }
      }
      return result
    }
    return quotesListResult
  })

  const mappedAccessories = computed(() => {
    return accessoryList.map((quote) => quote[0])
  })

  const tabTitle = (q, idx) => {
    if (!$isPublic) {
      if (idx === 0 && isPickup) {
        return q.location_name
      }
      if (idx === 0 && !isPickup) {
        return "Cheapest"
      }
    } else {
      if (idx === 0) {
        return "Cheapest"
      }
    }

    return q.location_name
  }
  const title = computed(() => {
    let title = isPickup ? "Customer location:" : "Shipping to:"
    const addr = customerOrderStore.address
    title += ` ${addr.city} ${addr.state} ${addr.zip}`
    return title
  })

  const state = reactive({
    selectedLocation: 0,
    page: 1,
    containerOptions: {},
    pageItems:
      visibleQuoteOption === "Accessories"
        ? []
        : quotesList.map((quote) => quote[0]).slice(0, pageSize),
    selectedQuotes: quotesList.slice(0, pageSize),
    selectedButtonMenu: null,
    viewCart: false,
    visibleQuoteOption: visibleQuoteOption,
    singles_mode: true
  })

  const selectLocation = (index) => {
    console.log(index)
    state.selectedLocation = index
  }

  onMounted(async () => {
    if (mappedQuotes.value.length > 0) {
      if (pageSize > 0) {
        paginate(mappedQuotes.value, pageSize, 0)
      }
    }
  })
  const cartMini = ref()
  const toggle = (event) => {
    cartMini.value.toggle(event)
  }
  const openButtonMenu = (i) => {
    state.selectedButtonMenu = i
  }

  const viewCart = () => {
    state.viewCart = true
    //   emit("hide");
  }

  const paginate = (arr, pageSize, pageNumber) => {
    if (pageNumber < 1 || pageNumber > arr.length / pageSize) return
    state.page = pageNumber
    state.pageItems = arr.slice(
      (state.page - 1) * pageSize,
      state.page * pageSize
    )
    state.selectedQuotes = quotesList.slice(
      (state.page - 1) * pageSize,
      state.page * pageSize
    )
  }
  watch(
    () => state.visibleQuoteOption,
    async (newVal) => {
      if (newVal === "Container") {
        state.pageItems = quotesList.map((quote) => quote[0]).slice(0, pageSize)
      }
      if (newVal === "Accessories") {
        state.pageItems = []
      }
    }
  )
  watch(
    () => quotesFilterOptions,
    (newVal) => {
      if (newVal.length > 0) {
        initContainerOptions(newVal)
      }
    }
  )
  watch(
    () => state.containerOptions,
    (newVal) => {
      if (Object.keys(state.containerOptions).length > 0) {
        if (newVal.size.length > 0 || newVal.quality.length > 0) {
          state.containerOptions.show_all = false
        } else {
          state.containerOptions.show_all = true
        }
      }
    },
    { deep: true }
  )
</script>
