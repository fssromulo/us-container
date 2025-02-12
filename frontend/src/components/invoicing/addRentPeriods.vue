<template>
  <div class="grid grid-cols-12 gap-4">
    <div class="col-span-12 grid grid-cols-12 gap-4">
      <div class="field mb-4 col-span-12 md:col-span-12">
        <label
          for="new_rental_period"
          class="font-medium text-900 dark:text-0"
          style="margin: 10px"
          >Enter Number Of Period(s)</label
        >
        <InputNumber
          placeholder="Number Of Periods"
          :disabled="state.loading"
          v-model="state.addedPeriods"
          type="text"
          class="flex-1"
          :min="1"
          :max="24"
        >
        </InputNumber>
      </div>

      <div class="field mb-4 col-span-6 md:col-span-6">
        <Button
          @click="addPeriods()"
          :disabled="state.addedPeriods < 1"
          label="Add Period(s)"
          class="p-button-accent p-button-lg m-1"
          :loading="state.loading"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
  import { reactive, watch } from "vue"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"

  const toast = useToast()
  const customerApi = new CustomerApi()

  const emit = defineEmits(["reloadRentalPeriod"])
  const { editingData } = defineProps({
    editingData: {
      type: Object,
      required: true
    }
  })
  const state = reactive({
    addedPeriods: 0,
    loading: false,
    date_to_change: ""
  })
  const addPeriods = async () => {
    state.loading = true
    const { error, data } = await customerApi.addRentPeriods({
      order_id: editingData.order_id,
      number_of_period: state.addedPeriods
    })

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Rent periods added",
        group: "br",
        life: 5000
      })
      emit("reloadRentalPeriod", {})
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to update rent periods",
        group: "br",
        life: 5000
      })
    }
    state.loading = false
  }
</script>
