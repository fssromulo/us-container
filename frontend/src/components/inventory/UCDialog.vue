<template>
  <Dialog
    v-model:visible="showDialog"
    dismissableMask
    closeOnEscape
    :breakpoints="breakpointsDialog"
    :modal="modalDialog"
  >
    <template #header>
      <slot name="header"></slot>
    </template>
    <slot name="content"></slot>
  </Dialog>
</template>

<script setup>
  import { computed, onMounted } from "vue"
  const showDialog = computed(() => {
    return props.isVisible ?? false
  })

  const props = defineProps({
    breakpointsDialog: {
      type: Object,
      default: () => {
        return {
          "2000px": "45vw",
          "1400px": "55vw",
          "1200px": "65vw",
          "992px": "75vw",
          "600px": "100vw",
          "480px": "100vw",
          "320px": "100vw"
        }
      },
      required: false
    },
    modalDialog: {
      type: Boolean,
      default: true,
      required: false
    },
    isVisible: {
      type: Boolean,
      default: true
    }
  })

  onMounted(async () => {})
</script>
