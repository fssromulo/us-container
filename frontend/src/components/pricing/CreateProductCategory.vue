<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="field mb-4 col-span-12 md:col-span-6">
          <label for="description" class="font-medium text-900 dark:text-0"
            >Category Name</label
          >
          <InputText
            placeholder="Category Name"
            v-model="state.category.name"
            id="category_name"
            type="text"
          />
        </div>
      </div>
    </div>
    <Button
      :label="
        $isObjectPopulated(categoryProp) ? 'Update Category' : 'Create Category'
      "
      @click="createUpdateCategory"
      :loading="state.loading"
      icon="pi pi-file"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, defineEmits } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"

  import PricingApi from "@/api/pricing"
  import InventoryService from "@/service/Inventory"

  import { useToast } from "primevue/usetoast"
  import { useContainerPrices } from "@/store/modules/pricing"
  import { reset } from "@formkit/vue"

  const toast = useToast()

  const pricingApi = new PricingApi()
  const pricingStore = useContainerPrices()
  const inventoryService = new InventoryService()

  const stateService = new StateService()

  const { categoryProp } = defineProps({
    categoryProp: {
      type: Object,
      default: () => ({})
    }
  })

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const swapOldCategory = (updatedCategory) => {
    const index = cloneDeep(pricingStore.productCategories)
      .map((u) => u.id)
      .indexOf(updatedCategory.id)
    let clonedCategories = cloneDeep(pricingStore.productCategories)
    clonedCategories[index] = updatedCategory
    pricingStore.setProductCategories(clonedCategories)
  }

  onMounted(async () => {
    state.statesList = stateService.getStates()
    resetCategory()
  })

  const emptyCategory = {
    name: ""
  }

  const state = reactive({
    loading: false,
    category: cloneDeep(emptyCategory),
    originalCategory: null,
    isRental: false
  })

  const rules = computed(() => ({
    category: {
      name: { required, $lazy: true }
    }
  }))

  const v$ = useVuelidate(rules, state)

  const resetCategory = () => {
    let category = null
    if ($isObjectPopulated(categoryProp)) {
      category = cloneDeep(categoryProp)
    } else {
      category = emptyCategory
    }
    state.originalCategory = cloneDeep(category)
    state.category = cloneDeep(category)
    v$.value.$reset()
  }

  const createUpdateCategory = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    state.loading = true

    if (state.category.id) {
      let requestData = $removeUnusedProps(
        cloneDeep(state.category),
        cloneDeep(state.originalCategory)
      )

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "Category Unchanged",
          detail: "Category Unchanged",
          group: "br",
          life: 5000
        })
        return
      }

      const { data, error } = await pricingApi.updateProductCategory(
        state.category.id,
        requestData
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Category Updated",
          detail: "Successfully updated product category",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating product category",
          group: "br",
          life: 5000
        })
      }
      swapOldCategory(data.value)
      state.loading = false
    } else {
      await pricingApi.createProductCategory(state.category)
      const { data } = await pricingApi.getProductCategory()

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Product Category Saved",
          detail: "Successfully saved product category",
          group: "br",
          life: 5000
        })
      }
      const prices = data.value
      pricingStore.setProductCategories(prices)
      resetCategory()
      state.loading = false
    }
    emit("hide")
  }
</script>

<style></style>
