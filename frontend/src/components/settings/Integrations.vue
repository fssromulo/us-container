<template>
  <div class="grid grid-cols-12 gap-4 h-full mt-6 ml-6 mr-6">
    <div
      class="mb-4 field col-span-12"
      v-for="(field, index) in filteredFields"
      :key="index"
    >
      <div v-if="typeof state.integrations[field] === 'object'">
        <h4 :for="field" class="font-medium text-center text-900 dark:text-0">
          {{ convertFromSnakeCase(field) }}
        </h4>
        <hr />
        <div
          class="mb-4 field col-sm-12 col-md-12"
          v-for="(innerField, innerIndex) in Object.keys(
            state.integrations[field] || {}
          )"
          :key="innerIndex"
        >
          <div
            v-if="typeof state.integrations[field][innerField] === 'boolean'"
          >
            <label :for="field" class="font-medium text-900 dark:text-0"
              >{{ convertFromSnakeCase(innerField) }}
            </label>
            <toggleSwitch v-model="state.integrations[field][innerField]" />
          </div>
          <div
            v-else-if="
              typeof state.integrations[field][innerField] === 'object'
            "
          >
            <h5 :for="field" class="mt-2 font-medium text-900 dark:text-0">
              {{ convertFromSnakeCase(innerField) }}
            </h5>
            <hr />
            <div
              class="mb-8 ml-8 mr-8 field col-sm-12 col-md-12"
              v-for="(innerField_, innerIndex_) in Object.keys(
                state.integrations[field][innerField]
              )"
              :key="innerIndex_"
            >
              <div
                v-if="
                  typeof state.integrations[field][innerField][innerField_] ==
                  'string'
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
                  v-model="state.integrations[field][innerField][innerField_]"
                />
              </div>
              <div v-else>
                <div
                  v-if="
                    (typeof state.integrations[field][innerField][
                      innerField_
                    ] ===
                      typeof state.integrations[field][innerField][
                        innerField_
                      ]) ===
                    'object'
                  "
                >
                  <div
                    class="mb-4 field col-sm-6 col-md-4"
                    v-for="(innerField_, innerIndex_) in Object.keys(
                      state.integrations[field][innerField][innerField_]
                    )"
                    :key="innerIndex_"
                  >
                    <label
                      :for="field"
                      class="font-medium text-900 dark:text-0"
                      v-if="typeof parseInt(innerField__) !== 'number'"
                      >{{ convertFromSnakeCase(innerField__) }}
                    </label>
                    {{}}
                    <InputText
                      class="w-full"
                      v-model="
                        state.integrations[field][innerField][innerField_][
                          innerField_
                        ]
                      "
                    />
                  </div>
                </div>

                <div v-else>
                  <div
                    class="mb-4 field col-sm-6 col-md-4"
                    v-for="(innerField__, innerIndex_) in state.integrations[
                      field
                    ][innerField][innerField_]"
                    :key="innerIndex_"
                  >
                    <label
                      :for="field"
                      class="font-medium text-900 dark:text-0"
                      v-if="typeof parseInt(innerField__) !== 'number'"
                      >{{ convertFromSnakeCase(innerField__) }}
                    </label>
                    {{
                      typeof state.integrations[field][innerField][innerField_]
                    }}
                    <InputText
                      class="w-full"
                      v-model="
                        state.integrations[field][innerField][innerField_]
                      "
                    />
                  </div>
                </div>
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
              v-model="state.integrations[field][innerField]"
            />
          </div>
        </div>
        <hr />
      </div>
      <div v-else-if="Array.isArray(state.integrations[field])">
        <div
          class="mb-4 field col-sm-12 col-md-12"
          v-for="(innerField, innerIndex) in state.integrations[field]"
          :key="innerIndex"
        >
          <label :for="field" class="font-medium text-900 dark:text-0"
            >{{ convertFromSnakeCase(innerField) }}
          </label>

          <div
            v-if="typeof state.integrations[field][innerField] === 'boolean'"
          >
            <toggleSwitch v-model="state.integrations[field][innerField]" />
          </div>
          <div v-else>
            <InputText
              class="w-full"
              v-model="state.integrations[field][innerField]"
            />
          </div>
        </div>
      </div>
      <div v-else-if="typeof state.integrations[field] === 'boolean'">
        <label :for="field" class="font-medium text-900 dark:text-0"
          >{{ convertFromSnakeCase(field) }}
        </label>
        <toggleSwitch v-model="state.integrations[field]" />
      </div>
      <div v-else>
        <label :for="field" class="font-medium text-900 dark:text-0">{{
          convertFromSnakeCase(field)
        }}</label>
        <InputText class="w-full" v-model="state.integrations[field]" />
      </div>
    </div>
  </div>
  <div class="mb-6 field col-span-3">
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

  const accountApi = new AccountApi()

  const userStore = useUsers()
  const toast = useToast()

  const state = reactive({
    loading: false,
    integrations: null
  })

  const convertFromSnakeCase = (k) => {
    if (typeof k == "string") {
      console.log(k)
      k = k.replace(/_/g, " ")
      k = k.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
      })
      return k
    }
    console.log(k)
    return k
  }

  const save = async () => {
    state.loading = true
    const { data, error } = await accountApi.updateAccountAttribute({
      integrations: state.integrations,
      type: "integrations"
    })
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error saving Integrations",
        detail: error.message,
        life: 3000,
        group: "br"
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Integrations updated",
        life: 3000,
        group: "br"
      })
      userStore.setIntegrations(data.value.integrations)
    }
    state.loading = false
  }

  const filteredFields = computed(() => {
    if (state.integrations) {
      return Object.keys(state.integrations).filter((e) => {
        return e
      })
    }
    return []
  })

  onMounted(async () => {
    state.integrations = userStore.integrations
  })

  watch(
    () => userStore.integrations,
    (newVal, oldVal) => {
      state.integrations = newVal
    }
  )
</script>
