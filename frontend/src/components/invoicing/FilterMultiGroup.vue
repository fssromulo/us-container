<template>
  <div class="flex flex-wrap gap-4">
    <div class="col-span-12">
      <strong v-if="isrequired">* {{ title }}</strong>
      <strong v-else> {{ title }}</strong>
    </div>
    <div class="flex flex-wrap items-center justify-center gap-4 mb-2">
      <div
        v-for="(v, index) in props.checkBoxes"
        :style="[
          state.current.includes(index) ? { color: 'white !important' } : ''
        ]"
        class="inline-flex items-center justify-center px-4 py-2 text-lg transition-colors duration-150 border cursor-pointer text-900 dark:text-0 rounded-border"
        @click="setCurrent(index)"
        :class="{
          'bg-0 dark:bg-900 border hover:bg-emphasis ':
            !state.current.includes(index),
          'p-button p-component p-button-secondary':
            state.current.includes(index)
        }"
      >
        {{ v.label }}
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, watch, onMounted } from "vue"
  import { useUsers } from "@/store/modules/users"
  import { cloneDeep } from "lodash"
  const usersStore = useUsers()

  const props = defineProps({
    checkBoxes: {
      type: Array,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    reset: {
      type: Boolean,
      required: false,
      default: false
    },
    defaultSelected: {
      type: Number,
      required: false
    },
    isrequired: {
      type: Boolean,
      required: false
    }
  })

  const state = reactive({
    current: []
  })
  const setCurrent = (index) => {
    if (state.current.includes(index)) {
      state.current = [...state.current.filter((e) => e !== index)]
    } else {
      state.current.push(index)
    }
  }
  onMounted(() => {
    state.current = []
    if (props.defaultSelected >= 0) {
      state.current = props.defaultSelected
    }
    if (props.reset) {
      state.current = []
    }
  })

  watch(
    () => state.current.length,
    (index) => {
      console.log(index)
      let copiedSearchCriteria = cloneDeep(usersStore.selectedSearchCriteria)
      let copiedOrderFilters = cloneDeep(usersStore.orderFilters)
      // reset everything
      props.checkBoxes.forEach((v, i) => {
        copiedOrderFilters[props.checkBoxes[i].value] = null
      })
      props.checkBoxes.forEach((v, i) => {
        copiedSearchCriteria[props.checkBoxes[i].value] = null
      })
      //Check and set filters

      state.current.forEach((e) => {
        console.log(e)
        if (copiedOrderFilters.hasOwnProperty(props.checkBoxes[e]?.value)) {
          copiedOrderFilters[props.checkBoxes[e].value] =
            !copiedOrderFilters[props.checkBoxes[e].value]
          usersStore.setOrderFilters(copiedOrderFilters)
        }
        if (copiedSearchCriteria.hasOwnProperty(props.checkBoxes[e]?.value)) {
          copiedSearchCriteria[props.checkBoxes[e]?.value] = true
          usersStore.setSelectedSearchCriteria(copiedSearchCriteria)
        }
      })
    }
  )

  watch(
    () => props.reset,
    (index) => {
      state.current = []
    }
  )
</script>
