<template>
  <div class="grid grid-cols-12 gap-4">
    <div class="col-span-12">
      <div class="card">
        <PaymentMethodsList />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, watch, onMounted } from "vue"
  import { useUsers } from "@/store/modules/users"
  import PaymentMethodsList from "./PaymentMethodsList.vue"

  const userStore = useUsers()

  const state = reactive({
    cms: null,
    loading: false,
    cmsId: null
  })

  onMounted(async () => {
    console.log(userStore.cms)
    state.id = userStore.cms.id
    state.cms = userStore.cms
  })

  watch(
    () => userStore.cms,
    (newVal, oldVal) => {
      state.cms = newVal
    }
  )
</script>

<style></style>
