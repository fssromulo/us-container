<template>
  <div class="grid grid-cols-12 gap-4">
    <div
      v-for="component in components"
      :key="component.name"
      class="col-span-6"
    >
      <div
        class="card bg-white rounded-xl shadow-xl overflow-hidden transform transition duration-500 hover:scale-105"
      >
        <component :is="component" />
      </div>
    </div>
  </div>
</template>

<script setup>
  import TextMessages from "./TextMessages.vue"
  import Links from "./Links.vue"
  import Auth from "./Auth.vue"
  import Commissions from "./Commissions.vue"
  import AdditionalSettings from "./AdditionalSettings.vue"
  import CountrySettings from "./CountrySettings.vue"

  import ZipCodeSearchCard from "./ZipCodeSearchCard.vue"
  import FeeType from "./FeeType.vue"
  import ClearCache from "./ClearCache.vue"
  import TermsAndConditionsList from "./TermsAndConditionsList.vue"
  import PayOnDeliverySettings from "./PayOnDeliverySettings.vue"

  import PaymentMethodsSettings from "./PaymentMethodsSettings.vue"
  import { reactive, watch, onMounted } from "vue"
  import { useUsers } from "@/store/modules/users"
  Auth
  const userStore = useUsers()

  const components = [
    TextMessages,
    Links,
    Auth,
    TermsAndConditionsList,
    AdditionalSettings,
    PayOnDeliverySettings,
    Commissions,
    ZipCodeSearchCard,
    FeeType,
    CountrySettings,
    ClearCache,
    PaymentMethodsSettings
  ]
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
