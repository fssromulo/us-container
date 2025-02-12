<template>
  <div class="container">
    <div class="row">
      <div class="mb-3 field col-sm-6 col-md-4">
        <label class="font-medium text-900">Delivery Time Frame</label>
        <div class="grid">
          <div class="mb-4 field col-6">
            <DatePicker
              :disabled="!$ability.can('update', 'order_column-potential_date')"
              v-model="state.potentialStartDate"
              placeholder="Start Time"
              id="potential_date"
              class="text-md"
              dateFormat="mm/dd/y"
            />
          </div>

          <div class="mb-4 field col-6">
            <DatePicker
              :disabled="!$ability.can('update', 'order_column-potential_date')"
              v-model="state.potentialEndDate"
              placeholder="End Time"
              id="potential_date"
              class="text-md"
              dateFormat="mm/dd/y"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-12 gap-4">
      <div class="col-span-6 mb-6 field">
        <Button
          @click="sendTimeFrameDate"
          class="p-button-rounded p-button-raised"
          :loading="state.isLoading"
          :disabled="
            state.isLoading ||
            !state.potentialStartDate ||
            !state.potentialEndDate
          "
          label="Save"
        >
        </Button>
      </div>

      <div class="col-span-6 mb-6 field">
        <Button
          @click="emit('hide')"
          class="p-button-raised p-button-rounded p-button-secondary"
          :disabled="state.isLoading"
          label="Cancel"
        >
        </Button>
      </div>
    </div>
  </div>
</template>
<script setup>
  import { reactive, inject, defineEmits } from "vue"
  import NotificationsApi from "@/api/notifications"
  import { useToast } from "primevue/usetoast"
  const emit = defineEmits(["hide"])

  const notificationsApi = new NotificationsApi()
  const toast = useToast()
  const $ability = inject("$ability")

  const { orderId, lineItem } = defineProps({
    orderId: {
      type: String,
      required: true
    },
    lineItem: {
      type: Object,
      required: true
    }
  })
  const state = reactive({
    isLoading: false,
    potentialStartDate: "",
    potentialEndDate: ""
  })

  const sendTimeFrameDate = async () => {
    state.isLoading = true
    const startDateObj = new Date(state.potentialStartDate)

    const startYear = startDateObj.getFullYear()
    const startMonth = String(startDateObj.getMonth() + 1).padStart(2, "0")
    const startDay = String(startDateObj.getDate()).padStart(2, "0")

    const endDateObj = new Date(state.potentialEndDate)

    const endYear = endDateObj.getFullYear()
    const endMonth = String(endDateObj.getMonth() + 1).padStart(2, "0")
    const endDay = String(endDateObj.getDate()).padStart(2, "0")

    let { data, error } = await notificationsApi.sendTimeFrameEmail(
      lineItem?.id,
      orderId,
      {
        start_date: `${startYear}-${startMonth}-${startDay}`,
        end_date: `${endYear}-${endMonth}-${endDay}`
      }
    )
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Delivery Time frame sent",
        detail: "Successfully sent delivery time frame email",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "There was an error sending time frame email",
        group: "br",
        life: 5000
      })
    }
    state.isLoading = false
    emit("hide")
  }
</script>
