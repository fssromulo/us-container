<template>
  <div class="container">
    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <Toolbar class="mb-6">
          <template #start>
            <h3 class="text-center">Fee Types</h3>
          </template>
          <template #end>
            <Button
              label="Add Fee Type"
              icon="pi pi-plus"
              class="p-button-success ml-4"
              @click="openFeeType"
              :disabled="state.loading"
            />
          </template>
        </Toolbar>

        <DataTable :value="state.feeTypes">
          <Column field="name" header="Name"></Column>
          <Column field="is_taxable" header="Is Taxable">
            <template #body="slotProps">
              <toggleSwitch
                :modelValue="slotProps.data.is_taxable"
                :disabled="state.loading || !slotProps.data.is_editable"
                @change="
                  toggleTaxable(
                    slotProps.data.id,
                    slotProps.data.is_taxable,
                    slotProps.data.is_editable
                  )
                "
              ></toggleSwitch>
            </template>
          </Column>
          <Column field="is_archived" header="Is Archived">
            <template #body="slotProps">
              <toggleSwitch
                :modelValue="slotProps.data.is_archived"
                :disabled="state.loading || !slotProps.data.is_editable"
                @change="
                  toggleArchived(
                    slotProps.data.id,
                    slotProps.data.is_archived,
                    slotProps.data.is_editable
                  )
                "
              ></toggleSwitch>
            </template>
          </Column>
          <Column field="adjusts_profit" header="Adjusts Profit">
            <template #body="slotProps">
              <toggleSwitch
                :modelValue="slotProps.data.adjusts_profit"
                :disabled="state.loading || !slotProps.data.is_editable"
                @change="
                  toggleProfit(
                    slotProps.data.id,
                    slotProps.data.adjusts_profit,
                    slotProps.data.is_editable
                  )
                "
              ></toggleSwitch>
            </template>
          </Column>

          <Column header="Edit">
            <template #body="slotProps">
              <Button
                :disabled="state.loading"
                v-if="slotProps.data.is_editable"
                @click="
                  updateFeeType(
                    slotProps.data.name,
                    slotProps.data.display_name,
                    slotProps.data.id
                  )
                "
                >Edit</Button
              >
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
    <Dialog
      v-model:visible="state.feeTypeDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="'Add Fee Type'"
      :modal="true"
      class="p-fluid"
    >
      <CreateFeeType @hide="state.feeTypeDialog = false" />
    </Dialog>
    <Dialog
      v-model:visible="state.feeTypeUpdateDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="'Update Fee Type'"
      :modal="true"
      class="p-fluid"
    >
      <UpdateFeeType
        :feeName="state.selectedFee.name"
        :display_name="state.selectedFee.display_name"
        :feeId="state.selectedFee.id"
        @hide="state.feeTypeUpdateDialog = false"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import AccountApi from "@/api/account"
  import { reactive, watch, onMounted } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useDrivers } from "@/store/modules/drivers"
  import { useUsers } from "@/store/modules/users"
  import CreateFeeType from "./feetype/CreateFeeType"
  import UpdateFeeType from "./feetype/UpdateFeeType"

  import cloneDeep from "lodash.clonedeep"
  import { useToast } from "primevue/usetoast"
  import CustomerApi from "@/api/customers"

  const customerStore = useCustomerOrder()
  const customerOrderStore = useCustomerOrder()

  const accountApi = new AccountApi()
  const customerApi = new CustomerApi()

  const userStore = useUsers()
  const toast = useToast()

  const toggleArchived = async (id, is_archived, is_editable) => {
    if (!is_editable) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "This action is not allowed.",
        life: 4000,
        group: "br"
      })
      return
    }
    state.loading = true
    await customerApi.updateFeeType(id, { is_archived: !is_archived })
    let { data, error } = await customerApi.fetchFeeTypes()
    customerOrderStore.setFeeTypes(data.value)
    state.loading = false
  }
  const toggleTaxable = async (id, is_taxable, is_editable) => {
    if (!is_editable) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "This action is not allowed.",
        life: 4000,
        group: "br"
      })
      return
    }
    state.loading = true
    await customerApi.updateFeeType(id, { is_taxable: !is_taxable })
    let { data, error } = await customerApi.fetchFeeTypes()
    customerOrderStore.setFeeTypes(data.value)
    state.loading = false
  }

  const toggleProfit = async (id, adjusts_profit, is_editable) => {
    if (!is_editable) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "This action is not allowed.",
        life: 4000,
        group: "br"
      })
      return
    }
    state.loading = true
    await customerApi.updateFeeType(id, { adjusts_profit: !adjusts_profit })
    let { data, error } = await customerApi.fetchFeeTypes()
    customerOrderStore.setFeeTypes(data.value)
    state.loading = false
  }

  const updateFeeType = async (name, display_name, id) => {
    state.feeTypeUpdateDialog = true
    state.selectedFee.name = name
    state.selectedFee.id = id
    state.selectedFee.display_name = display_name
  }

  const state = reactive({
    loading: false,
    feeTypes: [],
    feeTypeDialog: false,
    feeTypeUpdateDialog: false,
    selectedFee: {
      name: "",
      id: ""
    }
  })
  const openFeeType = async () => {
    state.feeTypeDialog = true
  }
  onMounted(async () => {
    // const { data } = await cmsService.getCms();
    console.log(userStore.cms)
    state.id = userStore.cms.id
    state.cms = userStore.cms
    state.feeTypes = customerStore.feeTypes.sort((a, b) => {
      // First, sort by is_editable (putting true values first)
      if (a.is_editable === b.is_editable) {
        // If is_editable values are equal, sort alphabetically by name
        return a.name.localeCompare(b.name)
      }
      // Put items where is_editable is true before those where it's false
      return a.is_editable ? -1 : 1
    })
  })

  watch(
    () => customerStore.feeTypes,
    (newVal, oldVal) => {
      state.feeTypes = newVal
    }
  )
</script>
