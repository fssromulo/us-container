<template>
  <div class="container">
    <h3 class="text-center">Extra Invoice Settings</h3>
    <div class="row">
      <div
        class="mb-4 field col-sm-12 col-md-12"
        v-for="(field, index) in filteredFields"
        :key="index"
      >
        <div v-if="typeof state.cms[field] === 'object'">
          <h4 :for="field" class="font-medium text-900 dark:text-0">
            {{ convertFromSnakeCase(field) }}
          </h4>
          <hr />
          <div
            class="mb-4 field col-sm-6 col-md-4"
            v-for="(innerField, innerIndex) in Object.keys(state.cms[field])"
            :key="innerIndex"
          >
            <div v-if="typeof state.cms[field][innerField] === 'boolean'">
              <div class="grid grid-cols-12 gap-4">
                <div class="col-sm-6 col-md-4">
                  <label
                    :for="field"
                    class="mr-8 font-medium text-900 dark:text-0"
                    >{{ convertFromSnakeCase(innerField) }}
                  </label></div
                >
                <div class="col-sm-6 col-md-4">
                  <toggleSwitch v-model="state.cms[field][innerField]"
                /></div>
              </div>
            </div>
            <div v-else-if="typeof state.cms[field][innerField] === 'object'">
              <h5 :for="field" class="mt-2 font-medium text-900 dark:text-0">
                {{ convertFromSnakeCase(innerField) }}
              </h5>
              <div
                class="mb-4 field col-sm-6 col-md-4"
                v-for="(innerField_, innerIndex_) in Object.keys(
                  state.cms[field][innerField]
                )"
                :key="innerIndex_"
              >
                <label :for="field" class="font-medium text-900 dark:text-0"
                  >{{ convertFromSnakeCase(innerField_) }}
                </label>
                <toggleSwitch
                  v-model="state.cms[field][innerField][innerField_]"
                />
              </div>
            </div>

            <div v-else>
              <label
                :for="field"
                class="font-medium text-900 dark:text-0"
                v-if="innerField != '0'"
                >{{ convertFromSnakeCase(innerField) }}
              </label>

              <InputText
                class="w-full"
                v-model="state.cms[field][innerField]"
              />
            </div>
          </div>
          <hr />
        </div>
        <div v-else-if="Array.isArray(state.cms[field])">
          <div
            class="mb-4 field col-sm-6 col-md-4"
            v-for="(innerField, innerIndex) in state.cms[field]"
            :key="innerIndex"
          >
            <div class="grid grid-cols-12 gap-4">
              <div class="col-sm-6 col-md-4">
                <label :for="field" class="font-medium text-900 dark:text-0"
                  >{{ convertFromSnakeCase(innerField) }}
                </label>
              </div>
              <div class="col-sm-6 col-md-4">
                <div v-if="typeof state.cms[field][innerField] === 'boolean'">
                  <toggleSwitch v-model="state.cms[field][innerField]" />
                </div>
                <div v-else>
                  <InputText
                    class="w-full"
                    v-model="state.cms[field][innerField]"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="typeof state.cms[field] === 'boolean'">
          <div class="grid grid-cols-12 gap-4">
            <div class="col-sm-6 col-md-4">
              <label :for="field" class="font-medium text-900 dark:text-0"
                >{{ convertFromSnakeCase(field) }}
              </label>
            </div>
            <div class="col-sm-6 col-md-4">
              <toggleSwitch v-model="state.cms[field]" />
            </div>
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

  const fieldsToShow = [
    "paid_message",
    "rto_paid_message",
    "quote_contact_email",
    "quote_contact_phone",
    "sales_quotes_message",
    "quote_expired_message",
    "quote_cancelled_message",
    "allow_deliveries_marked_on_15th_and_last_day_of_month",
    "invoice_message",
    "gurantees_present_on_status"
  ]
  const filteredFields = computed(() => {
    if (state.cms) {
      let filtered = fieldsToShow.filter((field) => field in state.cms)
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
