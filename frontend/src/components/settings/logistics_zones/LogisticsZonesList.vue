<template>
  <div class="container">
    <ConfirmPopup></ConfirmPopup>

    <h3 class="text-center">Logistics Zones List</h3>

    <Button
      label="Add Logistics Zone"
      icon="pi pi-plus"
      class="p-button-success ml-4"
      @click="addLogisticZones()"
    />
    <div class="row">
      <div class="field mb-12 col-sm-12 col-md-12">
        <DataTable
          :value="
            state.logistics_zones.map((lz) => {
              return {
                zone_id: lz.id,
                zone_name: lz.zone_name,
                coordinator_name: lz.coordinator_name,
                email: lz.email,
                support_number: lz.support_number,
                direct_number: lz.direct_number,
                color: lz.color
              }
            })
          "
          responsiveLayout="scroll"
        >
          <Column field="zone_name" header="Zone Name"></Column>
          <Column field="coordinator_name" header="Coordinator Name"></Column>
          <Column field="email" header="Email"></Column>
          <Column field="support_number" header="Support Number"></Column>
          <Column field="direct_number" header="Direct Number"></Column>
          <Column field="color" header="Color"></Column>
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

    <Dialog
      v-model:visible="state.lzDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="
        state.selectedLZ.zone_id == null
          ? 'Create Logistics Zone'
          : 'Edit Logistics Zone'
      "
      :modal="true"
      class="p-fluid"
    >
      <EditLogisticsZone
        @hide="state.lzDialog = false"
        @lzEdited="editLogisticsZone()"
        :lzProp="state.selectedLZ"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted } from "vue"
  import { useConfirm } from "primevue/useconfirm"
  import LogisticsZonesApi from "@/api/logistics_zones"
  import { useToast } from "primevue/usetoast"
  import EditLogisticsZone from "./EditLogisticsZone.vue"

  const toast = useToast()

  const logisticsZonesApi = new LogisticsZonesApi()

  const state = reactive({
    logistics_zones: [],
    lzDialog: false,
    selectedLZ: {},
    loading: false
  })
  onMounted(async () => {
    const { data } = await logisticsZonesApi.getAllLogisticsZones()
    state.logistics_zones = data.value
  })
  const addLogisticZones = async () => {
    state.selectedLZ = {}
    state.lzDialog = true
  }

  const editLogisticsZone = async () => {
    state.lzDialog = false
    refresh()
  }
  const refresh = async () => {
    const { data } = await logisticsZonesApi.getAllLogisticsZones()
    state.logistics_zones = data.value
  }

  const openLZ = async (data) => {
    state.selectedLZ = data
    state.lzDialog = true
  }

  const deleteLZ = async (dataToDelete) => {
    state.loading = true
    const { data, error } = await logisticsZonesApi.delete(dataToDelete.zone_id)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error deleting logistics zone.",
        group: "br",
        life: 5000
      })
    }

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Logistics zone successfully deleted.",
        group: "br",
        life: 5000
      })
      refresh()
    }
    state.loading = false
  }
</script>
