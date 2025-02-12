<template>
  <div>
    <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
      <div class="field mb-4 col-span-12 md:col-span-12">
        <label for="state" class="font-medium text-900 dark:text-0"
          >Fee Type</label
        >
        <InputText
          placeholder="Fee Type"
          v-model="state.feeType.name"
          type="text"
        />
      </div>
      <div class="field mb-3 col-12 md:col-12">
        <label for="state" class="font-medium text-900">Display Name</label>
        <InputText
          placeholder="Display name"
          v-model="state.feeType.display_name"
          type="text"
        />
      </div>
    </div>
    <Button
      :label="'Update Fee Type'"
      @click="editFeeType"
      :loading="state.isLoading"
      :disabled="state.feeType.name.length === 0"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, inject, defineEmits, provide } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"
  import { useUsers } from "@/store/modules/users"
  import { useCustomerOrder } from "@/store/modules/customerOrder"

  import cloneDeep from "lodash.clonedeep"

  import UsersService from "@/service/User"
  import InventoryService from "@/service/Inventory"
  import CustomerApi from "@/api/customers"

  const customerStore = useCustomerOrder()

  //addFeeType
  import { useToast } from "primevue/usetoast"
  import { ABILITY_TOKEN } from "@casl/vue"

  const $ability = inject(ABILITY_TOKEN)
  provide("$ability", $ability)
  const customerApi = new CustomerApi()

  const toast = useToast()
  const userStore = useUsers()

  const { feeName, display_name, feeId } = defineProps({
    feeName: {
      type: String,
      default: ""
    },
    display_name: {
      type: String,
      default: ""
    },
    feeId: {
      type: String,
      default: ""
    }
  })

  const state = reactive({
    feeType: {
      name: feeName,
      display_name: display_name
    },
    isLoading: false
  })
  const emit = defineEmits(["hide"])

  const editFeeType = async () => {
    state.isLoading = true
    await customerApi.updateFeeType(feeId, state.feeType)
    let { data, error } = await customerApi.fetchFeeTypes()
    customerStore.setFeeTypes(data.value)

    state.feeType.name = ""
    state.feeType.is_taxable = false
    state.isLoading = false
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Fee Type Saved",
        detail: "Successfully updated fee type",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error updating fee type",
        group: "br",
        life: 5000
      })
    }
    emit("hide", {})
  }
</script>

<style></style>
