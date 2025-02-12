<template>
  <div class="container">
    <!-- <h3 class="text-center">New Coupon Detail</h3> -->
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <InputText v-model="state.name" class="w-4/5" size="large" />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Enter a name that describes the coupon, making it easy to identify and manage.'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0">Coupon Title</label>
        </FloatLabel>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <Select
              class="p-component p-inputtext-fluid w-4/5"
              v-model="state.category_selected"
              optionLabel="name"
              :options="state.category_options"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Select the category this coupon belongs to, such as Containers only, Accessories only, or Both.'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0"
            >Coupon Category
          </label>
        </FloatLabel>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <InputNumber
              class="p-component p-inputtext-fluid w-4/5"
              inputId="currency-us"
              mode="currency"
              currency="USD"
              locale="en-US"
              v-model="state.minimum_discount_threshold"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Set the minimum purchase amount required to use this coupon.'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0"
            >Coupon Minimum Threshold</label
          >
        </FloatLabel>
      </div>
    </div>
    <div class="row" v-if="!state.priceLocked">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <InputNumber
              class="p-component p-inputtext-fluid w-4/5"
              inputId="currency-us"
              mode="currency"
              currency="USD"
              locale="en-US"
              v-model="state.amount"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Enter the discount value or benefit provided by this coupon. This is a fixed amount'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0">Coupon Value</label>
        </FloatLabel>
      </div>
    </div>
    <div class="row" v-if="state.priceLocked">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <InputNumber
              class="p-component p-inputtext-fluid w-4/5"
              locale="en-US"
              v-model="state.percentage"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Enter the discount value or benefit provided by this coupon. This a percentage'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0"
            >Coupon Percentage</label
          >
        </FloatLabel>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <InputText
              class="p-component p-inputtext-fluid w-4/5"
              v-model="state.code"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Provide a unique code for this coupon that users will enter to redeem the offer'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0">Coupon Code</label>
        </FloatLabel>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <DatePicker
              class="p-component p-inputtext-fluid w-4/5"
              inputId="range"
              v-model="state.schedule_range"
              selectionMode="range"
              :manualInput="false"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Define the date range during which this coupon is valid. Leave blank for no time restriction.'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0"
            >Coupon Schedule</label
          >
        </FloatLabel>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <MultiSelect
              v-model="state.city"
              optionLabel="name"
              :options="state.cities"
              class="p-component p-inputtext-fluid w-4/5"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Specify the cities where this coupon can be redeemed, if applicable.'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0">Coupon City</label>
        </FloatLabel>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <MultiSelect
              v-model="state.size"
              optionLabel="name"
              :options="state.sizes"
              class="p-component p-inputtext-fluid w-4/5"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Choose the sizes of containers which can activate this offer.'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0">Coupon Size</label>
        </FloatLabel>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0 mr-2"
          >Coupon permanent</label
        >
        <Checkbox v-model="state.is_permanent" binary="true"></Checkbox>
        <InputIcon
          class="pi pi-info-circle ml-2"
          v-tooltip="
            'Check this box if the coupon does not have an expiration date and will remain valid indefinitely.'
          "
          style="font-size: 1.2rem"
        />
      </div>
    </div>
    <div class="mb-4 field col-sm-6 col-md-4">
      <FloatLabel variant="in">
        <IconField>
          <Select
            v-model="state.type"
            optionLabel="name"
            :options="state.types"
            class="p-component p-inputtext-fluid w-4/5"
          />
          <InputIcon
            class="pi pi-info-circle ml-2"
            v-tooltip="
              'Specify the type of coupon: internal (for internal use) or external (available for public use) or both'
            "
            style="font-size: 1.5rem"
          />
        </IconField>
        <label class="font-medium text-900 dark:text-0">Type</label>
      </FloatLabel>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <MultiSelect
              v-model="state.role"
              optionLabel="name"
              :options="state.roleOptions"
              class="p-component p-inputtext-fluid w-4/5"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Assign roles or user groups eligible to use this coupon, such as admin, customer, or guest.'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0">Roles</label>
        </FloatLabel>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0 mr-2">Add Rules? </label>
        <Checkbox v-model="state.isAddRules" binary="true"></Checkbox>
        <InputIcon
          class="pi pi-info-circle ml-2"
          v-tooltip="'Enable additional rules for the coupon'"
          style="font-size: 1.2rem"
        />
        <div v-if="state.isAddRules" v-for="key in Object.keys(state.rules)">
          <div v-if="Number.isInteger(state.rules[key])">
            <label class="pr-4 font-medium text-900 dark:text-0">{{
              key
            }}</label>
            <InputNumber
              v-model="state.rules[key]"
              class="p-component p-inputtext-fluid"
            ></InputNumber>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <FloatLabel variant="in">
          <IconField>
            <MultiSelect
              v-model="state.attributes"
              optionLabel="name"
              :options="state.attributesOptions"
              class="p-component p-inputtext-fluid w-4/5"
            />
            <InputIcon
              class="pi pi-info-circle ml-2"
              v-tooltip="
                'Select attributes that define the applicability of this coupon, such as pre paid orders'
              "
              style="font-size: 1.5rem"
            />
          </IconField>
          <label class="font-medium text-900 dark:text-0"
            >Coupon Attribute(s)
          </label>
        </FloatLabel>
      </div>
    </div>
    <div>
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0 mr-2"
          >Cannot combine with other discounts/coupons?
        </label>
        <Checkbox v-model="state.cannot_combine" binary="true"></Checkbox>
        <InputIcon
          class="pi pi-info-circle ml-2"
          v-tooltip="
            'Check this box to restrict users from combining this coupon with other offers or discounts'
          "
          style="font-size: 1.2rem"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-6 field col-sm-6 col-md-3">
        <Button
          class="p-button-rounded p-button-successsave"
          label="Save Coupon"
          :loading="loading"
          :disabled="!isValidateForm || loading"
          @click="save"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
  import { ref, reactive, computed, onMounted, watch } from "vue"
  import CouponApi from "@/api/coupon"
  import { useCoupons } from "@/store/modules/coupons"
  import PricingApi from "../../../api/pricing.js"
  import { useToast } from "primevue/usetoast"
  import QuoteGenerationService from "@/service/QuoteGeneration"
  import RoleApi from "@/api/roles"
  import RolesService from "../../../service/Roles"

  const quoteGenerationService = new QuoteGenerationService()

  const roleApi = new RoleApi()

  const toast = useToast()

  const couponApi = new CouponApi()
  const couponStore = useCoupons()
  const pricingApi = new PricingApi()

  const isValidateForm = computed(() => {
    if (state.amount < 0) return false
    if (state.name == "" || state.name == " ") return false
    if (state.code.length < 2) return false
    if (state.code.schedule_range == 0) return false
    return true
  })

  const save = async () => {
    loading.value = true
    const dataToSave = { ...state }
    delete dataToSave.cities
    delete dataToSave.sizes
    delete dataToSave.types
    delete dataToSave.roles
    delete dataToSave.isAddRules
    delete dataToSave.category_options

    dataToSave.is_stackable = !dataToSave.cannot_combine
    delete dataToSave.cannot_combine

    if (state.category_selected) {
      dataToSave.category = state.category_selected.code
    }
    delete state.category_selected

    if (!state.isAddRules) {
      delete dataToSave.rules
    }

    dataToSave.type = dataToSave.type != null ? dataToSave.type.code : null
    dataToSave.account_id = 1

    const cityMap = {}
    if (state.city != []) {
      state.city.forEach((element) => {
        cityMap[element.name] = true
      })
    }
    dataToSave.city = cityMap

    const sizeMap = {}
    if (state.size != []) {
      state.size.forEach((element) => {
        sizeMap[element.name] = true
      })
    }
    dataToSave.size = sizeMap

    const roleMap = {}
    if (state.role != []) {
      state.role.forEach((element) => {
        roleMap[element.name] = true
      })
    }
    const attributeMap = {}
    if (state.attributes != []) {
      state.attributes.forEach((element) => {
        attributeMap[element.code] = true
      })
    }

    dataToSave.attributes = attributeMap
    dataToSave.role = roleMap

    dataToSave.start_date = dataToSave.schedule_range[0]
    dataToSave.end_date = dataToSave.schedule_range[1]
    delete dataToSave.schedule_range

    const { data, error } = await couponApi.createCoupon(dataToSave)
    const res = await couponApi.getAllCoupons()
    couponStore.setCoupons(res.data.value)

    state.amount = 0
    state.minimum_discount_threshold = 1000
    state.name = ""
    state.code = ""
    state.start_date = ""
    state.end_date = ""
    state.schedule_range = []
    state.size = 0
    state.city = ""
    state.category = null
    loading.value = false

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Coupon Code Saved",
        detail: "Successfully created coupon code",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error creating coupon code",
        group: "br",
        life: 5000
      })
    }
  }

  const state = reactive({
    amount: 0,
    minimum_discount_threshold: 1000,
    name: "",
    code: "",
    start_date: "",
    end_date: "",
    schedule_range: [],
    city: [],
    size: [],
    cities: [],
    sizes: [],
    is_permanent: false,
    priceLocked: false,
    types: [
      { name: "internal", code: "internal" },
      { name: "external", code: "external" },
      { name: "both", code: "both" }
    ],
    type: { name: "internal", code: "internal" },
    roleOptions: [],
    attributesOptions: [],
    role: [],
    attributes: [],
    rules: {
      line_item_minimum: 0
    },
    isAddRules: false,
    category_selected: null,
    category_options: [
      { name: "Containers Only", code: "containers_only" },
      { name: "Accessories Only", code: "accessories_only" },
      { name: "Both", code: "both" }
    ]
  })

  const resetData = async () => {
    const locations = await pricingApi.getLocations()
    state.cities = locations.data.value.map((obj) => {
      return { name: obj.city, code: obj.city }
    })
    // state.cities.push({ name: "All", code: "All" });

    state.sizes = quoteGenerationService.orderedTitles.map((title) => {
      return {
        name: title,
        code: title
      }
    })

    const response = await roleApi.getRoles()
    state.roleOptions = response.data.value.map((el) => {
      return {
        name: el.name,
        code: el.id
      }
    })
    state.attributesOptions = [
      {
        name: "Pre Pay",
        code: "is_pre_paid"
      }
    ]
  }
  watch(
    () => state.category_selected,
    (newVal, oldVal) => {
      console.log(state.category_selected.code)
      if (state.category_selected.code == "accessories_only") {
        state.priceLocked = true
      } else {
        state.priceLocked = false
      }
    }
  )
  onMounted(async () => {
    resetData()
    // [
    //   {name: "20", code: "20"},
    //   {name: "40", code: "40"},
    //   {name: "All", code: "All"}
    // ]
  })
  const loading = ref(false)
</script>
