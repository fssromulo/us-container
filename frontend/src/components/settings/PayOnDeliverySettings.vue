<template>
  <div class="container">
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
              <label :for="field" class="font-medium text-900 dark:text-0"
                >{{ convertFromSnakeCase(innerField) }}
              </label>
              <toggleSwitch v-model="state.cms[field][innerField]" />
            </div>
          </div>
          <hr />
        </div>
        <div v-else-if="typeof state.cms[field] !== 'boolean'">
          <label :for="field" class="font-medium text-900 dark:text-0"
            >{{ convertFromSnakeCase(field) }}
          </label>
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
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"
  import { useToast } from "primevue/usetoast"
  import PricingApi from "@/api/pricing.js"

  const pricingApi = new PricingApi()

  const accountApi = new AccountApi()

  const userStore = useUsers()
  const toast = useToast()

  const state = reactive({
    cms: null,
    loading: false,
    cmsId: null,
    cities: [],
    allCities: []
  })

  const zipcode = ref("")

  const convertFromSnakeCase = (k) => {
    k = k.replace(/_/g, " ")
    k = k.replace(/\w\S*/g, function (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    })
    return k
  }

  const addCity = async () => {
    state.loading = true
    state.cities.map((city) => {
      if (!state.cms.pay_on_delivery_contract.availability_cities[city.name])
        state.cms.pay_on_delivery_contract.availability_cities[city.name] = true
    })
    state.cities = []
    await save()
    state.loading = false
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
      state.cities = []
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Request Saved",
        life: 3000,
        group: "br"
      })
      const cms_attributes = data.value.cms_attributes
      cms_attributes.id = data.value.id
      userStore.setCms(cms_attributes)
      userStore.setIntegrations(data.value.integrations)
      await loadData()
    }
    state.loading = false
  }

  // const fieldsToShow = [Object.keys(state.cms).filter((e) =>{
  //   e.includes('link')
  // })];
  // 'sales_internal_link1_desc', 'sales_internal_link2_desc'
  const fieldsToShow = ["pay_on_delivery_contract"]
  const filteredFields = computed(() => {
    if (state.cms) {
      let filtered = fieldsToShow.filter((field) => field in state.cms)
      return filtered
    }
    return []
  })
  const loadData = async () => {
    console.log(userStore.cms)
    state.id = userStore.cms.id
    state.cms = userStore.cms
    const locations = await pricingApi.getLocations()
    let cities = Object.keys(
      state.cms?.pay_on_delivery_contract?.availability_cities
    )
    state.allCities = locations.data.value
      .filter((e) => {
        if (cities.includes(e.city)) return false
        return true
      })
      .map((obj) => {
        return { name: obj.city, code: obj.city }
      })
  }

  onMounted(async () => {
    // const { data } = await cmsService.getCms();
    await loadData()
  })

  watch(
    () => userStore.cms,
    (newVal, oldVal) => {
      state.cms = newVal
    }
  )
</script>
