<template>
  <div v-if="state.hasRelatedContainers">
    <h3>Containers In Release</h3>
    <DataTable v-if="!state.loading" :value="state.linkedContainers">
      <Column field="container_number" header="Container Number"> </Column>
      <template #empty> No containers found. </template>
    </DataTable>
    <LoadingTable
      v-if="state.loading"
      :columns="[{ field: 'container_number', display: 'Container Number' }]"
      :loading="state.loading"
    />
  </div>
</template>
<script setup>
  import { reactive, watch, onMounted, defineEmits } from "vue"
  import CustomerApi from "@/api/customers"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  const emit = defineEmits(["hasRelatedContainers"])

  const props = defineProps(["releaseNumber"])
  const customerApi = new CustomerApi()

  const state = reactive({
    linkedContainers: [],
    loading: false,
    hasRelatedContainers: false
  })

  const loadRelatedContainers = async () => {
    state.linkedContainers = []
    if (props.releaseNumber.length > 0) {
      state.loading = true
      const { data } = await customerApi.relatedContainers(props.releaseNumber)
      state.linkedContainers = data.value.filter((e) => {
        return e.container_number != null
      })
      state.loading = false
    }
  }

  onMounted(async () => {
    await loadRelatedContainers()
  })

  watch(
    () => props.releaseNumber,
    async (newVal) => {
      if (newVal) {
        await loadRelatedContainers()
      }
    }
  )
  watch(
    () => state.linkedContainers,
    async (newVal) => {
      if (newVal.length > 1) {
        state.hasRelatedContainers = true
      } else {
        state.hasRelatedContainers = false
      }
      emit("hasRelatedContainers", state.hasRelatedContainers)
    }
  )
</script>
