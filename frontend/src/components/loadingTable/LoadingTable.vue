<template>
  <div>
    <DataTable
      :value="state.loadingData"
      responsiveLayout="scroll"
      scrollHeight="75vh"
    >
      <Column
        v-for="(col, i) in props.columns"
        :key="i"
        :field="col.field"
        :header="col.display"
        :style="col.style"
      >
        <template #body>
          <Skeleton></Skeleton>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
  import { reactive } from "vue"

  const props = defineProps({
    columns: Array
  })
  const state = reactive({
    loadingData: new Array(20)
  })
</script>

<style lang="scss" scoped></style>
