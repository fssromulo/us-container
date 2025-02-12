<template>
  <div v-if="state.cms" class="container">
    <h3 class="text-center">Terms and Conditions</h3>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"
          >Terms and conditions</label
        >
        <InputText class="w-full" v-model="state.cms.terms_and_conditions" />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"
          >Terms and conditions paid</label
        >
        <InputText
          class="w-full"
          v-model="state.cms.terms_and_conditions_paid"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-6 field col-sm-6 col-md-3">
        <Button
          class="p-button-rounded p-button-successsave"
          label="Save"
          :loading="state.loading"
          @click="save"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, watch, onMounted, computed } from "vue"
  import AccountApi from "@/api/account"
  import { useUsers } from "@/store/modules/users"
  import { useToast } from "primevue/usetoast"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const customerOrderStore = useCustomerOrder()

  const accountApi = new AccountApi()

  const userStore = useUsers()
  const toast = useToast()

  const state = reactive({
    cms: null,
    loading: false,
    cmsId: null
  })

  const save = async () => {
    state.loading = true
    const { data, error } = await accountApi.updateAccountAttribute({
      cms_attributes: Object.fromEntries(
        Object.entries(state.cms).filter(([key, value]) =>
          filteredFields.value.includes(key)
        )
      ),
      type: "cms_attributes"
    })
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error saving CMS",
        detail: error.message,
        life: 3000,
        group: "br"
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Terms and Conditions Saved",
        life: 3000,
        group: "br"
      })
      const cms_attributes = data.value.cms_attributes
      cms_attributes.id = data.value.id
      userStore.setCms(cms_attributes)
      userStore.setIntegrations(data.value.integrations)
    }
    state.loading = false
  }

  const fieldsToShow = ["terms_and_conditions_paid", "terms_and_conditions"]

  const filteredFields = computed(() => {
    if (state.cms) {
      return fieldsToShow.filter((field) => field in state.cms)
    }
    return []
  })

  onMounted(async () => {
    console.log("mounted")
    console.log(userStore.cms)
    state.cms = userStore.cms
  })

  watch(
    () => userStore.cms,
    (newVal, oldVal) => {
      state.cms = newVal
      state.cms.terms_and_conditions_paid = state.cms.terms_and_conditions_paid
      state.cms.terms_and_conditions = state.cms.terms_and_conditions
    }
  )
</script>
