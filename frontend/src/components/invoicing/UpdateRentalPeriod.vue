<template>
  <div class="grid grid-cols-12 gap-4">
    <div class="col-span-12 grid grid-cols-12 gap-4">
      <div
        class="field mb-4 col-span-12 md:col-span-12"
        v-if="editingData.option === 'start_date'"
      >
        <label
          for="new_rental_period"
          class="font-medium text-900 dark:text-0"
          style="margin: 10px"
          >Start Date</label
        >
        <DatePicker
          v-model="state.startDate"
          :modelValue="new Date(state.startDate)"
          :minDate="editingData.min_date"
        />
      </div>

      <div class="field mb-4 col-span-6 md:col-span-6">
        <Button
          @click="change_rental_period_due_date"
          label="Update"
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
    updateType: "",
    selectedPeriod: "Update only this period",
    startDate: editingData.selected_period.start_date,
    endDate: editingData.selected_period.end_date,
    loading: false,
    rent_due_on_day: editingData.rent_due_on_day,
    date_to_change: ""
  })
  const change_rental_period_due_date = async () => {
    state.loading = true
    state.date_to_change =
      editingData.option === "start_date"
        ? new Date(state.startDate).toLocaleDateString("en-US")
        : new Date(state.endDate).toLocaleDateString("en-US")
    console.log(editingData)
    const { error, data } = await customerApi.updateRentPeriodDueDate(
      {
        date: state.date_to_change,
        id: editingData.selected_period.id,
        order_id: editingData.order_id,
        rent_due_on_day: state.rent_due_on_day
      },
      editingData.subsequent_periods.map((period) => period.id)
    )

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Updated rent period due date",
        group: "br",
        life: 5000
      })
      emit("reloadRentalPeriod", {})
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to update rent period due date",
        group: "br",
        life: 5000
      })
    }
    state.loading = false
  }

  watch(
    () => state.startDate,
    async (newVal) => {
      // console.log(newVal);
      // const parts = newVal.split("/");
      // const day = parseInt(parts[0], 10);
      // const month = parseInt(parts[1], 10) - 1; // Subtract 1 to get the correct month
      // const year = parseInt(parts[2], 10);
      // const dateObject = new Date(year, month, day);
      const datePart = newVal.getDate()
      state.rent_due_on_day = datePart
    }
  )
</script>
