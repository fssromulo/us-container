<template>
  <div class="container">
    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"> Name</label>
        <InputText class="w-full" v-model="state.name" placeholder="Name" />
      </div>
    </div>

    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Display Name</label>
        <InputText
          class="w-full"
          v-model="state.display_name"
          placeholder="Display Name"
        />
      </div>
    </div>

    <div class="row">
      <div class="field mb-6 col-sm-6 col-md-3">
        <Button
          class="p-button-rounded p-button-successsave"
          :label="
            state.id == null ? 'Create Payment Method' : 'Update Payment Method'
          "
          :loading="loading"
          :disabled="loading"
          @click="update"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, ref, computed, defineEmits, onMounted } from "vue"

  import { useToast } from "primevue/usetoast"
  import PaymentMethodsApi from "@/api/payment_methods"
  const paymentMethodsApi = new PaymentMethodsApi()

  const { lzProp } = defineProps({
    lzProp: {
      type: Object,
      default: () => ({})
    }
  })
  const emit = defineEmits(["lzEdited"])

  const toast = useToast()

  const state = reactive({
    name: lzProp.name || "",
    display_name: lzProp.display_name || "",
    id: lzProp.id,
    loading: false
  })

  const update = async () => {
    console.log(state.id)
    if (state.id == null) {
      state.loading = true
      const dataRequest = {
        name: state.name,
        display_name: state.display_name
      }

      const { data, error } = await paymentMethodsApi.create(
        dataRequest,
        state.id
      )
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error creating payment method.",
          group: "br",
          life: 5000
        })
      }

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Payment method successfully created.",
          group: "br",
          life: 5000
        })
        emit("lzEdited")
      }
      state.loading = false
    } else {
      state.loading = true
      const dataRequest = {
        name: state.name,
        display_name: state.display_name
      }

      const { data, error } = await paymentMethodsApi.update(
        dataRequest,
        state.id
      )
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating payment method.",
          group: "br",
          life: 5000
        })
      }

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Payment method successfully updated.",
          group: "br",
          life: 5000
        })
        emit("lzEdited")
      }
      state.loading = false
    }
  }
</script>
