<template>
  <div class="container">
    <h3 class="text-center">Additional Settings</h3>
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
            v-for="(innerField, innerIndex) in Object.keys(
              state.cms[field] || {}
            )"
            :key="innerIndex"
          >
            <div v-if="typeof state.cms[field][innerField] === 'boolean'">
              <label :for="field" class="font-medium text-900 dark:text-0"
                >{{ convertFromSnakeCase(innerField) }}
              </label>
              <toggleSwitch v-model="state.cms[field][innerField]" />
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
                <div
                  v-if="
                    typeof state.cms[field][innerField][innerField_] == 'string'
                  "
                >
                  <label
                    :for="field"
                    class="font-medium text-900 dark:text-0"
                    v-if="innerField != '0'"
                    >{{ convertFromSnakeCase(innerField_) }}
                  </label>

                  <InputText
                    class="w-full"
                    v-model="state.cms[field][innerField][innerField_]"
                  />
                </div>
                <div v-else>
                  <label :for="field" class="font-medium text-900 dark:text-0"
                    >{{ convertFromSnakeCase(innerField_) }}
                  </label>
                  <toggleSwitch
                    v-model="state.cms[field][innerField][innerField_]"
                  />
                </div>
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
            <label :for="field" class="font-medium text-900 dark:text-0"
              >{{ convertFromSnakeCase(innerField) }}
            </label>

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
        <div v-else-if="typeof state.cms[field] === 'boolean'">
          <label :for="field" class="font-medium text-900 dark:text-0"
            >{{ convertFromSnakeCase(field) }}
          </label>
          <toggleSwitch v-model="state.cms[field]" />
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

  // const fieldsToShow = [Object.keys(state.cms).filter((e) =>{
  //   e.includes('link')
  // })];
  // 'sales_internal_link1_desc', 'sales_internal_link2_desc'
  const fieldsToShow = [
    "default_public_agent",
    "late_fee",
    "applications",
    "grace_period",
    "rent_options",
    "feature_flags",
    "nav_item_name",
    "bank_fee_message",
    "credit_card_fees",
    "payment_warranties",
    "afterPaymentMessage",
    "convenience_fee_rate",
    "test_account_identity",
    "default_selling_states",
    "sendInternalAgentEmails",
    "internal_payment_enabled",
    "default_external_payments",
    "contract_title_with_rent_autopay_info",
    "company_mailing_address",
    "send_public_notification",
    "inventory_status_list",
    "links",
    "mailer_send_template_defaults",
    "mailer_send_defaults",
    "stripe",
    "order_expire_days",
    "pod_contract"
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
