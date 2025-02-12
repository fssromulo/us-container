<template>
  <div class="container">
    <h3 class="text-center">Text Messages</h3>
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

    <div
      class="col-span-12"
      v-for="(field, index) in otherFilteredFields"
      :key="index"
    >
      <div class="grid grid-cols-12 gap-4" v-if="field.length">
        <div
          class="col-span-12 md:col-span-12 lg:col-span-12"
          v-for="(sub_field, index_) in Object.keys(state.cms[field])"
          :key="index_"
        >
          <label :for="field" class="font-medium text-900 dark:text-0">{{
            convertFromSnakeCase(sub_field)
          }}</label>
          <InputText class="w-full" v-model="state.cms[field][sub_field]" />
        </div>
      </div>
    </div>
    <div class="row card-footer">
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
  import { reactive, computed, watch, onMounted, ref } from "vue"
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
        detail: "Text Messages Saved",
        life: 3000,
        group: "br"
      })
      const cms_attributes = data.value.cms_attributes
      userStore.setCms(cms_attributes)
      userStore.setIntegrations(data.value.integrations)
    }
    state.loading = false
  }

  const fieldsToShow = [
    "sms_refferal_text",
    "delivered_sms_text",
    "sms_follow_up_text"
  ]

  const filteredFields = computed(() => {
    if (state.cms) {
      return fieldsToShow.filter((field) => field in state.cms)
    }
    return []
  })

  const otherFieldsToShow = ["sms_text_messages"]

  const otherFilteredFields = computed(() => {
    if (state.cms) {
      return otherFieldsToShow.filter((field) => field in state.cms)
    }
    return []
  })

  onMounted(async () => {
    // const { data } = await cmsService.getCms();
    console.log("TEST")
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

<style>
  .card-footer {
    margin-top: 26%; /* Add some margin between the fields and the button */
    display: flex;
    justify-content: flex-end;
  }
</style>
