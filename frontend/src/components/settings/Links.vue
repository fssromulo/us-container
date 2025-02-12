<template>
  <div class="container">
    <h3 class="text-center">Links</h3>
    <div class="row">
      <div
        class="field mb-4 col-sm-6 col-md-4"
        v-for="(field, index) in filteredFields"
        :key="index"
      >
        <label :for="field" class="font-medium text-900 dark:text-0">{{
          convertFromSnakeCase(field)
        }}</label>
        <InputText class="w-full" v-model="state.cms[field]" />
      </div>
    </div>
    <div class="row">
      <div class="field mb-6 col-sm-6 col-md-3">
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
  import AccountApi from "@/api/account"
  import { reactive, computed, watch, onMounted, ref } from "vue"
  import UsersService from "@/service/User"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useDrivers } from "@/store/modules/drivers"
  import { useUsers } from "@/store/modules/users"
  import cloneDeep from "lodash.clonedeep"
  import { useToast } from "primevue/usetoast"
  const customerOrderStore = useCustomerOrder()

  const accountApi = new AccountApi()

  const userStore = useUsers()
  const toast = useToast()

  const state = reactive({
    cms: null,
    loading: false,
    cmsId: null
  })

  const zipcode = ref("")

  const convertFromSnakeCase = (k) => {
    k = k.replace(/_/g, " ")
    k = k.replace(/\w\S*/g, function (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    })
    return k
  }

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
        detail: "Links Saved",
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

  // const fieldsToShow = [Object.keys(state.cms).filter((e) =>{
  //   e.includes('link')
  // })];
  // 'sales_internal_link1_desc', 'sales_internal_link2_desc'
  const fieldsToShow = computed(() => {
    if (state.cms) {
      return Object.keys(state.cms).filter((e) => {
        return e.includes("link")
      })
    }
    return []
  })
  const filteredFields = computed(() => {
    if (state.cms) {
      let filtered = fieldsToShow.value.filter((field) => field in state.cms)
      return filtered
    }
    return []
  })

  onMounted(async () => {
    // const { data } = await cmsService.getCms();
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
