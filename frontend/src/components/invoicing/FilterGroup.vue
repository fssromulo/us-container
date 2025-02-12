<template>
  <div class="grid grid-cols-12 gap-4">
    <div class="col-span-12">
      <strong v-if="isrequired">* {{ title }}</strong>
      <strong v-else> {{ title }}</strong>
    </div>
    <div
      class="col-span-12 gap-4"
      :class="`grid-cols-${props.checkBoxes.length}`"
    >
      <div
        v-for="(v, index) in props.checkBoxes"
        class="inline-flex px-4 py-2 text-lg transition-colors duration-150 border cursor-pointer text-900 dark:text-0 rounded-border"
        @click="setCurrent(index)"
        :style="[state.current === index ? { color: 'white !important' } : '']"
        :class="{
          'bg-0 dark:bg-900 border hover:bg-emphasis ': state.current !== index,
          'p-button p-component p-button-secondary transition-colors':
            state.current === index
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
    current: 0
  })
  const setCurrent = (index) => {
    if (state.current == index) {
      state.current = null
    } else {
      state.current = index
    }
  }
  onMounted(() => {
    state.current = null
    if (props.defaultSelected >= 0) {
      state.current = props.defaultSelected
    }
    if (props.reset) {
      state.current = null
    }
  })

  watch(
    () => state.current,
    (index) => {
      console.log(index)
      let copiedSearchCriteria = cloneDeep(usersStore.selectedSearchCriteria)
      let copiedOrderFilters = cloneDeep(usersStore.orderFilters)
      console.log(props.checkBoxes[index]?.value)
      if (copiedOrderFilters.hasOwnProperty(props.checkBoxes[index]?.value)) {
        props.checkBoxes.forEach((v, i) => {
          if (i !== index) {
            copiedOrderFilters[props.checkBoxes[i].value] = null
          }
        })
        copiedOrderFilters[props.checkBoxes[index].value] =
          !copiedOrderFilters[props.checkBoxes[index].value]
        usersStore.setOrderFilters(copiedOrderFilters)
      }
      if (copiedSearchCriteria.hasOwnProperty(props.checkBoxes[index]?.value)) {
        props.checkBoxes.forEach((v, i) => {
          if (i !== index) {
            copiedSearchCriteria[props.checkBoxes[i].value] = null
          }
        })
        copiedSearchCriteria[props.checkBoxes[index]?.value] = true
        usersStore.setSelectedSearchCriteria(copiedSearchCriteria)
      }
      if (index === null) {
        props.checkBoxes.forEach((v, i) => {
          copiedSearchCriteria[props.checkBoxes[i].value] = null
        })
        usersStore.setSelectedSearchCriteria(copiedSearchCriteria)
      }
    }
  )

  watch(
    () => props.reset,
    (index) => {
      state.current = null
    }
  )

  watch(
    () => props.defaultSelected,
    (index) => {
      state.current = index
    }
  )
</script>
