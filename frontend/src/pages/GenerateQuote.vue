<template>
  <div class="flex flex-col items-center justify-center">
    <GenerateQuote class="mt-2" />
  </div>
  <div
    v-if="!$isPublic"
    class="flex flex-wrap justify-center mx-16 mt-6 text-xl"
    v-html="usersStore?.cms?.sales_quotes_message"
  >
  </div>
  <div class="flex flex-wrap justify-center">
    <PublicQuotes v-if="state.cms && $isPublic" :cms="state.cms" />
  </div>
</template>

<script setup>
  import AccountApi from "@/api/account"
  import GenerateQuote from "@/components/quotes/GenerateQuote.vue"
  import PublicQuotes from "@/components/quotes/PublicQuotes.vue"
  import { useUsers } from "@/store/modules/users"
  import { reactive, onMounted, inject } from "vue"
  import { accountMap } from "../utils/accountMap"

  const usersStore = useUsers()

  const $isPublic = inject("$isPublic")

  const accountApi = new AccountApi()

  onMounted(async () => {
    state.loading = true
    if ($isPublic) {
      // need to update this
      console.log(accountMap[window.location.host].account_id)
      const res = await accountApi.getPublicAccount(
        accountMap[window.location.host].account_id
      )
      state.cms = res.data.value.cms_attributes
      // load coupons
    }

    state.loading = false
  })

  const state = reactive({
    loading: false,
    cms: null
  })
</script>

<style></style>
