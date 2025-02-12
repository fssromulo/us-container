<template>
  <div class="container">
    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Zone Name</label>
        <InputText
          class="w-full"
          v-model="state.zone_name"
          placeholder="Zone Name"
        />
      </div>
    </div>

    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Coordinator Name</label>
        <InputText
          class="w-full"
          v-model="state.coordinator_name"
          placeholder="Coordinator Name"
        />
      </div>
    </div>

    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Email</label>
        <InputText class="w-full" v-model="state.email" placeholder="Email" />
      </div>
    </div>

    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Direct Number</label>
        <InputText
          class="w-full"
          v-model="state.direct_number"
          placeholder="Direct NUmber"
        />
      </div>
    </div>

    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Support Number</label>
        <InputText
          class="w-full"
          v-model="state.support_number"
          placeholder="Support Number"
        />
      </div>
    </div>

    <div class="row">
      <div class="field mb-4 col-sm-6 col-md-4">
        <label class="font-medium text-900 dark:text-0">Color</label>
        <InputText class="w-full" v-model="state.color" placeholder="Color" />
      </div>
    </div>

    <div class="row">
      <div class="field mb-6 col-sm-6 col-md-3">
        <Button
          class="p-button-rounded p-button-successsave"
          :label="
            state.id == null ? 'Create Logistics Zone' : 'Update Logistics Zone'
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
  import LogisticsZonesApi from "@/api/logistics_zones"
  const logisticsZonesApi = new LogisticsZonesApi()

  const { lzProp } = defineProps({
    lzProp: {
      type: Object,
      default: () => ({})
    }
  })
  const emit = defineEmits(["lzEdited"])

  const toast = useToast()

  const state = reactive({
    zone_name: lzProp.zone_name || "",
    coordinator_name: lzProp.coordinator_name || "",
    email: lzProp.email || "",
    support_number: lzProp.support_number || "",
    direct_number: lzProp.direct_number || "",
    id: lzProp.zone_id,
    loading: false,
    color: lzProp.color
  })

  const update = async () => {
    console.log(state.id)
    if (state.id == null) {
      state.loading = true
      const dataRequest = {
        zone_name: state.zone_name,
        coordinator_name: state.coordinator_name,
        email: state.email,
        support_number: state.support_number,
        direct_number: state.direct_number,
        color: state.color
      }

      const { data, error } = await logisticsZonesApi.create(
        dataRequest,
        state.id
      )
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error creating logistics zone.",
          group: "br",
          life: 5000
        })
      }

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Logistics zone successfully created.",
          group: "br",
          life: 5000
        })
        emit("lzEdited")
      }
      state.loading = false
    } else {
      state.loading = true
      const dataRequest = {
        zone_name: state.zone_name,
        coordinator_name: state.coordinator_name,
        email: state.email,
        support_number: state.support_number,
        direct_number: state.direct_number,
        color: state.color
      }

      const { data, error } = await logisticsZonesApi.update(
        dataRequest,
        state.id
      )
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating logistics zone.",
          group: "br",
          life: 5000
        })
      }

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Logistics zone successfully updated.",
          group: "br",
          life: 5000
        })
        emit("lzEdited")
      }
      state.loading = false
    }
  }
</script>
