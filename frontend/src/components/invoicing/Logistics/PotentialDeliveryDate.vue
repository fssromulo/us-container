<template>
  <div class="container">
    <div class="row">
      <div class="mb-4 field col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0"
          >Potential Delivery Date</label
        >
        <DatePicker
          :disabled="!$ability.can('update', 'order_column-potential_date')"
          v-model="state.potentialDate"
          id="potential_date"
          class="text-md"
          dateFormat="mm/dd/y"
        />
      </div>
    </div>
    <div class="grid grid-cols-12 gap-4">
      <div class="col-span-6 mb-6 field">
        <Button
          @click="sendPotentialDeliveryDate"
          class="p-button-rounded p-button-raised"
          :loading="state.isLoading"
          :disabled="state.isLoading || !state.potentialDate"
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
    potentialDate: lineItem?.potential_date
      ? new Date(lineItem?.potential_date)
      : null
  })

  const sendPotentialDeliveryDate = async () => {
    state.isLoading = true
    const dateObj = new Date(state.potentialDate)

    const year = dateObj.getFullYear()
    const month = String(dateObj.getMonth() + 1).padStart(2, "0")
    const day = String(dateObj.getDate()).padStart(2, "0")
    let { data, error } = await notificationsApi.sendPotentialDeliveryEmail(
      lineItem.id,
      orderId,
      {
        potential_date: `${year}-${month}-${day}`
      }
    )
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Email sent",
        detail: "Successfully sent potential delivery email",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "There was an error sending email",
        group: "br",
        life: 5000
      })
    }
    state.isLoading = false
    emit("hide")
  }
</script>
