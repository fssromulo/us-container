<template>
  <div class="grid grid-cols-12 gap-4">
    <div
      v-for="component in components"
      :key="component.name"
      class="col-span-6"
    >
      <div
        class="overflow-hidden transition duration-500 transform bg-white shadow-xl card rounded-xl hover:scale-105"
      >
        <component :is="component" />
      </div>
    </div>
  </div>
</template>

<script setup>
  import Links from "./Links.vue"
  import Auth from "./Auth.vue"
  import Commissions from "./Commissions.vue"
  import AdditionalSettings from "./AdditionalSettings.vue"

  import ZipCodeSearchCard from "./ZipCodeSearchCard.vue"
  import FeeType from "./FeeType.vue"
  import ClearCache from "./ClearCache.vue"
  import TermsAndConditionsList from "./TermsAndConditionsList.vue"
  import extraInvoicePage from "./extraInvoicePage.vue"

  import { reactive, watch, onMounted } from "vue"
  import { useUsers } from "@/store/modules/users"
  Auth
  const userStore = useUsers()

  const components = [Links, extraInvoicePage, TermsAndConditionsList]
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
