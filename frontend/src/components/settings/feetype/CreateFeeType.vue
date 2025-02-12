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
          placeholder="Display Name"
          v-model="state.feeType.display_name"
          type="text"
        />
      </div>
      <div class="field mb-3 col-12 md:col-12">
        <label for="state" class="font-medium text-900">Is Taxable</label>
        <ToggleSwitch
          v-model="state.feeType.is_taxable"
          class="ml-8"
        ></ToggleSwitch>
      </div>
    </div>
    <Button
      :label="'Create Fee Type'"
      @click="createFeeType"
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

  const state = reactive({
    feeType: {
      name: "",
      display_name: "",
      is_archived: false,
      is_taxable: false,
      account_id: userStore.cms?.id
    },
    isLoading: false
  })
  const emit = defineEmits(["hide"])

  const createFeeType = async () => {
    state.isLoading = true
    await customerApi.addFeeType(state.feeType)
    let { data, error } = await customerApi.fetchFeeTypes()
    customerStore.setFeeTypes(data.value)

    state.feeType.name = ""
    state.feeType.is_taxable = false
    state.isLoading = false
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Fee Type Saved",
        detail: "Successfully created fee type",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error creating fee type",
        group: "br",
        life: 5000
      })
    }
    emit("hide", {})
  }
</script>

<style></style>
