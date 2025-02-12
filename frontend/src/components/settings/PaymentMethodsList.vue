<template>
  <div class="container">
    <ConfirmPopup></ConfirmPopup>

    <h3 class="text-center">Payment Methods List</h3>

    <Button
      label="Add Payment Method"
      icon="pi pi-plus"
      class="p-button-success ml-4"
      @click="addPaymentMethod()"
    />
    <div class="row">
      <div class="field mb-12 col-sm-12 col-md-12">
        <DataTable
          :value="
            state.payment_methods.map((lz) => {
              return {
                id: lz.id,
                name: lz.name,
                display_name: lz.display_name
              }
            })
          "
          responsiveLayout="scroll"
        >
          <Column field="name" header="Name"></Column>
          <Column field="display_name" header="Display Name"></Column>
          <Column field="id" header="Edit" style="width: 160px">
            <template #body="slotProps">
              <Button class="p-button-rounded" @click="openLZ(slotProps.data)"
                >Edit</Button
              >
            </template>
          </Column>
          <Column field="id" header="Delete" style="width: 160px">
            <template #body="slotProps">
              <Button
                class="p-button-rounded"
                :disabled="state.loading"
                @click="deleteLZ(slotProps.data)"
                >Delete</Button
              >
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </div>

  <Dialog
    v-model:visible="state.lzDialog"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ maxWidth: '1100px' }"
    :header="
      state.selectedLZ.id == null
        ? 'Create Payment Method'
        : 'Edit Payment Method'
    "
    :modal="true"
    class="p-fluid"
  >
    <EditPaymentMethod
      @hide="state.lzDialog = false"
      @lzEdited="refresh()"
      :lzProp="state.selectedLZ"
    />
  </Dialog>
</template>

<script setup>
  import { reactive, computed, onMounted } from "vue"
  import { useConfirm } from "primevue/useconfirm"
  import PaymentMethodsApi from "@/api/payment_methods"
  import { useToast } from "primevue/usetoast"
  import EditPaymentMethod from "./EditPaymentMethod.vue"

  const toast = useToast()

  const paymentMethodsApi = new PaymentMethodsApi()

  const state = reactive({
    payment_methods: [],
    lzDialog: false,
    selectedLZ: {},
    loading: false
  })
  const addPaymentMethod = () => {
    state.selectedLZ = {}
    state.lzDialog = true
  }
  onMounted(async () => {
    const { data } = await paymentMethodsApi.getAllPaymentMethods()
    console.log(data.value)
    state.payment_methods = data.value
  })

  const refresh = async () => {
    state.lzDialog = false
    const { data } = await paymentMethodsApi.getAllPaymentMethods()
    state.payment_methods = data.value
  }

  const openLZ = async (data) => {
    state.selectedLZ = data
    state.lzDialog = true
  }

  const deleteLZ = async (dataToDelete) => {
    state.loading = true
    const { data, error } = await paymentMethodsApi.delete(dataToDelete.id)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error deleting payment method.",
        group: "br",
        life: 5000
      })
    }

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Payment method successfully deleted.",
        group: "br",
        life: 5000
      })
      refresh()
    }
    state.loading = false
  }
</script>
