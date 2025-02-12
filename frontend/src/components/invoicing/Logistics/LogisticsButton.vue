<template>
  <div class="text-right grid grid-cols-12 gap-4">
    <div class="col-span-6">
      <Button
        label="Delivery Questionnaire"
        :loading="state.sendingDeliveryQuestionnaire"
        :disabled="state.sendingDeliveryQuestionnaire"
        @click="sendDeliveryQuestionnaire"
        class="p-button-raised"
      />
    </div>
    <div class="col-span-6">
      <Button
        class="p-button-raised"
        :loading="state.sendingTimeFrame"
        @click="sendTimeFrame"
        label="Time Frame"
      />
    </div>
    <div class="col-span-6">
      <Button
        class="p-button-raised"
        :loading="state.sendingPotentialDeliveryDate"
        label="Potential Delivery Date"
        @click="editPotentialDeliveryDate"
        :disabled="!$ability.can('update', 'order_column-potential_date')"
      />
    </div>
    <div class="col-span-6">
      <Button
        class="p-button-raised"
        :loading="state.sendingConfirmPotentialDeliveryDate"
        label="Confirm Potential Delivery Date"
        :disabled="!$ability.can('update', 'order_column-potential_date')"
        @click="sendConfirmationDeliveryDate"
      />
    </div>
    <div class="col-span-6" v-if="$ability.can('send', 'accessory_emails')">
      <Button
        class="p-button-raised"
        label="Send email present tracking numbers"
        @click="sendEmailTrackingNumbers"
      />
    </div>

    <Dialog
      v-model:visible="state.editSendingPotentialDeliveryDate"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Potential Delivery Date"
      :modal="true"
      class="p-fluid"
    >
      <PotentialDeliveryDate
        @hide="state.editSendingPotentialDeliveryDate = false"
        :lineItem="lineItem"
        :orderId="orderId"
      >
      </PotentialDeliveryDate>
    </Dialog>
    <Dialog
      v-model:visible="state.editSendingTimeFrame"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Time Frame"
      :modal="true"
      class="p-fluid"
    >
      <TimeFrame
        @hide="state.editSendingTimeFrame = false"
        :lineItem="lineItem"
        :orderId="orderId"
      >
      </TimeFrame>
    </Dialog>
    <Dialog
      v-model:visible="state.editSendingConfirmPotentialDeliveryDate"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Confirma Potential Delivery Date"
      :modal="true"
      class="p-fluid"
    >
      <ConfirmationDeliveryDate
        @hide="state.editSendingConfirmPotentialDeliveryDate = false"
        :lineItem="lineItem"
        :orderId="orderId"
      >
      </ConfirmationDeliveryDate>
    </Dialog>
  </div>
</template>
<script setup>
  import { reactive, inject } from "vue"
  import NotificationsApi from "@/api/notifications"
  import { useToast } from "primevue/usetoast"
  import PotentialDeliveryDate from "@/components/invoicing/Logistics/PotentialDeliveryDate.vue"
  import TimeFrame from "@/components/invoicing/Logistics/TimeFrame.vue"
  import ConfirmationDeliveryDate from "@/components/invoicing/Logistics/ConfirmationDeliveryDate.vue"

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
  const editPotentialDeliveryDate = () => {
    state.editing = true
    state.editSendingPotentialDeliveryDate = true
  }
  const sendTimeFrame = () => {
    state.editing = true
    state.editSendingTimeFrame = true
  }
  const sendConfirmationDeliveryDate = () => {
    state.editing = true
    state.editSendingConfirmPotentialDeliveryDate = true
  }

  const state = reactive({
    sendingDeliveryQuestionnaire: false,
    sendingTimeFrame: false,
    editSendingTimeFrame: false,
    sendingPotentialDeliveryDate: false,
    editSendingPotentialDeliveryDate: false,
    sendingConfirmPotentialDeliveryDate: false,
    editSendingConfirmPotentialDeliveryDate: false,
    editing: false
  })

  const sendEmailTrackingNumbers = async () => {
    let { data, error } = await notificationsApi.sendEmailTrackingNumbers(
      orderId
    )
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Email sent",
        detail: "Successfully sent tracking numbers email.",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "There was an error sending tracking numbers mail",
        group: "br",
        life: 5000
      })
    }
  }

  const sendDeliveryQuestionnaire = async () => {
    state.sendingDeliveryQuestionnaire = true
    let { data, error } = await notificationsApi.sendPaidEmail(orderId)
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Delivery Questionnaire Sent",
        detail: "Successfully sent questionnaire email",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "There was an error sending questionnaire mail",
        group: "br",
        life: 5000
      })
    }
    state.sendingDeliveryQuestionnaire = false
  }
</script>
