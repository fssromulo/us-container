<template>
  <div class="container">
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coupon Title</label>
        <InputText
          class="w-full"
          v-model="state.name"
          placeholder="Coupon Title"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coupon Category </label>
        <br />
        <Select
          v-model="state.category_selected"
          placeholder="categories"
          optionLabel="name"
          :options="state.category_options"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"
          >Coupon Minimum Threshold</label
        >
        <InputNumber
          class="w-full"
          inputId="currency-us"
          mode="currency"
          currency="USD"
          locale="en-US"
          v-model="state.minimum_discount_threshold"
        />
      </div>
    </div>
    <div class="row" v-if="!state.priceLocked">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coupon Value</label>
        <InputNumber
          class="w-full"
          inputId="currency-us"
          mode="currency"
          currency="USD"
          locale="en-US"
          v-model="state.amount"
        />
      </div>
    </div>
    <div class="row" v-if="state.priceLocked">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"
          >Coupon Percentage</label
        >
        <InputNumber class="w-full" locale="en-US" v-model="state.percentage" />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coupon Code</label>
        <InputText
          class="w-full"
          v-model="state.code"
          placeholder="Coupon Code"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coupon Schedule</label>
        <DatePicker
          class="w-full"
          inputId="range"
          v-model="state.schedule_range"
          selectionMode="range"
          placeholder="Coupon Schedule"
          :manualInput="false"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coupon City</label>
        <br />
        <MultiSelect
          class="p-component p-inputtext-fluid"
          v-model="state.city"
          placeholder="city"
          :options="state.cities"
          optionLabel="name"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coupon Size</label>
        <br />
        <MultiSelect
          class="p-component p-inputtext-fluid"
          v-model="state.size"
          placeholder="size"
          :options="state.sizes"
          optionLabel="name"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coupon permanent</label>
        <br />
        <Checkbox v-model="state.is_permanent" binary="true"></Checkbox>
      </div>
    </div>
    <div class="mb-4 field col-sm-6 col-md-4">
      <label class="font-medium text-900 dark:text-0">Type</label>
      <br />
      <Select
        class="p-component p-inputtext-fluid"
        v-model="state.type"
        placeholder="type"
        optionLabel="name"
        :options="state.types"
      />
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Roles </label>
        <br />
        <MultiSelect
          v-model="state.role"
          placeholder="roles"
          optionLabel="name"
          :options="state.roleOptions"
        />
      </div>
    </div>
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"
          >Coupon Attribute(s)
        </label>
        <br />
        <MultiSelect
          v-model="state.attributes"
          placeholder="Coupon Attributes"
          optionLabel="name"
          :options="state.attributesOptions"
        />
      </div>
    </div>

    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Add Rules? </label>
        <br />
        <Checkbox v-model="state.isAddRules" binary="true"></Checkbox>
        <div v-if="state.isAddRules" v-for="key in Object.keys(state.rules)">
          <div v-if="Number.isInteger(state.rules[key])">
            <label class="pr-4 font-medium text-900 dark:text-0">{{
              key
            }}</label>
            <InputNumber v-model="state.rules[key]"></InputNumber>
          </div>
        </div>
      </div>
    </div>
    <div>
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"
          >Cannot combine with other discounts/coupons?
        </label>
        <br />
        <Checkbox v-model="state.cannot_combine" binary="true"></Checkbox>
      </div>
    </div>
    <div class="row">
      <div class="mb-6 field col-sm-6 col-md-3">
        <Button
          class="p-button-rounded p-button-successsave"
          label="Update Coupon"
          :loading="loading"
          :disabled="!isValidateForm || loading"
          @click="update"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, ref, computed, defineEmits, onMounted, watch } from "vue"

  import { useToast } from "primevue/usetoast"
  import { useCoupons } from "@/store/modules/coupons"
  import CouponApi from "@/api/coupon"
  import PricingApi from "../../../api/pricing.js"
  import QuoteGenerationService from "@/service/QuoteGeneration"
  import RoleApi from "@/api/roles"
  import { useRefHistory } from "@vueuse/core"
  import { useUsers } from "@/store/modules/users"

  const userStore = useUsers()
  const roleApi = new RoleApi()

  const quoteGenerationService = new QuoteGenerationService()

  const pricingApi = new PricingApi()

  const toast = useToast()
  const couponStore = useCoupons()
  const isValidateForm = computed(() => {
    if (state.amount < 0) return false
    if (state.name == "" || state.name == " ") return false
    if (state.code?.length < 2) return false
    if (state.code?.schedule_range == 0) return false
    return true
  })
  const couponApi = new CouponApi()
  const emit = defineEmits(["couponEdited"])

  const { couponProp } = defineProps({
    couponProp: {
      type: Object,
      default: () => ({})
    }
  })

  const update = async () => {
    loading.value = true
    const dataToSave = { ...state }
    delete dataToSave.cities
    delete dataToSave.sizes
    delete dataToSave.types
    delete dataToSave.roleOptions
    delete dataToSave.attributesOptions
    delete dataToSave.isAddRules
    delete dataToSave.priceLocked
    delete dataToSave.category_options

    dataToSave.is_stackable = !dataToSave.cannot_combine
    delete dataToSave.cannot_combine

    if (state.category_selected) {
      dataToSave.category = state.category_selected.code
    }
    delete dataToSave.category_selected

    if (!state.isAddRules) {
      delete dataToSave.rules
    }

    console.log(state.role)

    dataToSave.type = dataToSave.type != null ? dataToSave.type.code : null
    dataToSave.account_id = userStore.cms.id
    const cityMap = {}
    state.city.forEach((element) => {
      cityMap[element.name] = true
    })
    dataToSave.city = cityMap

    const sizeMap = {}
    state.size.forEach((element) => {
      sizeMap[element.name] = true
    })
    dataToSave.size = sizeMap

    const roleMap = {}
    if (state.role != []) {
      state.role.forEach((element) => {
        roleMap[element.name] = true
      })
    }
    dataToSave.role = roleMap

    const attributeMap = {}
    if (state.attributes != []) {
      state.attributes.forEach((element) => {
        attributeMap[element.code] = true
      })
    }
    dataToSave.attributes = attributeMap

    dataToSave.start_date = dataToSave.schedule_range[0]
    dataToSave.end_date = dataToSave.schedule_range[1]
    delete dataToSave.schedule_range
    const { data, error } = await couponApi.updateCoupon(
      couponStore.selectedCoupon.id,
      dataToSave
    )
    const res = await couponApi.getAllCoupons()
    couponStore.setCoupons(res.data.value)

    loading.value = false
    emit("couponEdited")

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Coupon Code Updated",
        detail: "Successfully created coupon code",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error updating coupon code",
        group: "br",
        life: 5000
      })
    }
  }

  const state = reactive({
    amount: couponStore.selectedCoupon.amount,
    minimum_discount_threshold:
      couponStore.selectedCoupon.minimum_discount_threshold || 1000,
    name: couponStore.selectedCoupon.name,
    code: couponStore.selectedCoupon.code,
    start_date: couponStore.selectedCoupon.start_date,
    end_date: couponStore.selectedCoupon.end_date,
    schedule_range: [
      new Date(couponStore.selectedCoupon.start_date),
      new Date(couponStore.selectedCoupon.end_date)
    ],
    city: ref([]),
    size: ref([]),
    cities: [],
    sizes: [],
    is_permanent: couponStore.selectedCoupon.is_permanent,
    types: [
      { name: "internal", code: "internal" },
      { name: "external", code: "external" },
      { name: "both", code: "both" }
    ],
    type: {
      name: couponStore.selectedCoupon.type,
      code: couponStore.selectedCoupon.type
    },
    roleOptions: [],
    role: ref([]),
    attributesOptions: [],
    attributes: ref([]),
    rules: {
      line_item_minimum: 0
    },
    isAddRules: false,
    priceLocked: true,
    category_selected: null,
    category_options: [
      { name: "Containers Only", code: "containers_only" },
      { name: "Accessories Only", code: "accessories_only" },
      { name: "Both", code: "both" }
    ]
  })
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
    const locations = await pricingApi.getLocations()
    state.cities = locations.data.value.map((obj) => {
      return { name: obj.city, code: obj.city }
    })
    // state.cities.push({name: "All", code: "All"})

    state.sizes = quoteGenerationService.orderedTitles.map((title) => {
      return {
        name: title,
        code: title
      }
    })
    // state.sizes.push({name: "All", code: "All"})
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
    for (let key in couponStore.selectedCoupon.city) {
      state.city.push({ name: key, code: key })
    }

    for (let key in couponStore.selectedCoupon.size) {
      state.size.push({ name: key, code: key })
    }

    for (let key in couponStore.selectedCoupon.role) {
      state.role.push({
        name: key,
        code: state.roleOptions.find((el) => el.name == key).code
      })
    }
    for (let key in couponStore.selectedCoupon.attributes) {
      state.attributes.push({
        name: state.attributesOptions.find((el) => el.code == key).name,
        code: key
      })
    }

    if (
      couponStore.selectedCoupon.rules !== null &&
      couponStore.selectedCoupon.rules !== undefined
    ) {
      state.isAddRules = true
      state.rules.line_item_minimum =
        couponStore.selectedCoupon.rules.line_item_minimum
    }

    const coupon_orders = await couponApi.getACouponOrders(
      couponStore.selectedCoupon.id
    )
    if (coupon_orders.data.value.length == 0) {
      state.priceLocked = false
    }

    state.cannot_combine = !couponStore.selectedCoupon.is_stackable

    if (couponStore.selectedCoupon) {
      state.category_options.forEach((el) => {
        if (el.code == couponStore.selectedCoupon.category) {
          state.category_selected = { name: el.name, code: el.code }
        }
      })
    }

    state.percentage = couponStore.selectedCoupon.percentage
  })
  const loading = ref(false)
</script>
<style></style>
