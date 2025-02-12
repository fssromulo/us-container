<template>
  <div class="grid grid-cols-12 gap-4 mt-6 ml-6 h-full">
    <div
      class="col-span-12"
      v-for="(field, index) in filteredFields"
      :key="index"
    >
      <div class="grid grid-cols-12 gap-4" v-if="field.length">
        <div
          class="col-span-12 md:col-span-6 lg:col-span-6"
          v-for="(sub_field, index_) in Object.keys(state.cms[field])"
          :key="index_"
        >
          <label :for="field" class="font-medium text-900 dark:text-0">{{
            convertFromSnakeCase(sub_field)
          }}</label>
          <InputText class="w-full" v-model="state.cms[field][sub_field]" />
        </div>
      </div>
      <div v-else>
        <label :for="field" class="font-medium text-900 dark:text-0">{{
          convertFromSnakeCase(field)
        }}</label>
        <InputText class="w-full" v-model="state.cms[field]" />
      </div>
    </div>
  </div>

  <div class="field mb-6 col-span-3">
    <Button
      class="p-button-rounded p-button-successsave p-button-lg"
      label="Save"
      :loading="state.loading"
      @click="save"
    />
  </div>
</template>

<script setup>
  import { reactive, computed, watch, onMounted } from "vue"
  import UsersService from "@/service/User"
  import AccountApi from "@/api/account"

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
        detail: "CMS updated",
        life: 3000,
        group: "br"
      })
      const attributes = data.value.cms_attributes
      attributes.id = data.value.id
      userStore.setCms(attributes)
      userStore.setIntegrations(data.value.integrations)
    }
    state.loading = false
  }

  const fieldsToShow = ["emails"]

  const filteredFields = computed(() => {
    if (state.cms) {
      let filtered = fieldsToShow.filter((field) => field in state.cms)
      return filtered
    }
    return []
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
