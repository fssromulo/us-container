<template>
  <div class="flex flex-col w-full">
    <div class="col-span-12 mt-2 border-t border"></div>
    <div class="grid grid-cols-12 gap-4">
      <div class="md:col-span-4 md:col-start-2">
        <Select
          class="w-full"
          placeholder="Select Driver"
          v-model="state.selectedDriver"
          optionLabel="label"
          optionValue="value"
          :options="mappedDrivers"
        />
      </div>
      <div class="md:col-span-3">
        <DatePicker
          class="w-full"
          inputId="basic"
          dateFormat="m/d/y"
          placeholder="Set Date"
          v-model="state.scheduled_date"
        />
      </div>
      <div class="md:col-span-3">
        <InputNumber
          class="w-full"
          mode="currency"
          currency="USD"
          placeholder="Shipping cost"
          v-model="state.shipping_cost"
        />
      </div>
    </div>
    <div class="col-span-12 mt-2 border-t border"></div>
    <div class="text-right">
      <Button
        @click="props.close"
        label="Cancel"
        class="p-button-raised p-button-secondary"
      >
        Cancel
      </Button>
      <Button
        @click="attachDriver"
        :loading="state.isLoading"
        class="ml-4 mr-8 p-button-raised"
        label="Save"
      >
      </Button>
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, computed } from "vue"
  import InventoryService from "@/service/Inventory"
  import LineItemApi from "@/api/lineItem"
  import DriverService from "@/service/Drivers"
  import DriverApi from "@/api/drivers"
  import { useDrivers } from "@/store/modules/drivers"
  import { useInventory } from "@/store/modules/inventory"

  import { useToast } from "primevue/usetoast"
  const toast = useToast()

  const inventoryStore = useInventory()
  const inventoryService = new InventoryService()

  const driverService = new DriverService()
  const driverApi = new DriverApi()
  const driverStore = useDrivers()

  const lineItemApi = new LineItemApi()

  const props = defineProps({
    lineItem: {
      type: Object,
      default: () => ({})
    },
    close: {
      type: Function,
      default: () => {}
    },
    updatedLineItem: {
      type: Function,
      default: () => {}
    }
  })

  onMounted(async () => {
    if (driverStore.drivers?.length === 0) {
      state.isLoading = true
      const { data } = await driverApi.getDrivers()
      const drivers = data.value.map((driver) =>
        driverService.dtoDriver(driver)
      )
      driverStore.setDrivers(drivers)
      state.isLoading = false
    }
  })

  const mappedDrivers = computed(() => {
    return driverStore.drivers
      .map((driver) => {
        return {
          label: driver.company_name,
          value: driver
        }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const emit = defineEmits(["onUpdate"])

  const resetOrder = (updatedOrder = null) => {}

  const attachDriver = async () => {
    state.isLoading = true

    // let cost =
    //   state.selectedDriver.cost_per_mile * props.lineItem.potential_miles;
    // if (cost < Number(props.lineItem.minimum_shipping_cost)) {
    //   toast.add({
    //     severity: "error",
    //     summary: "Error",
    //     detail: `You need to charge more than the minimum shipping cost ${props.lineItem.minimum_shipping_cost}`,
    //     group: "br",
    //     life: 2000,
    //   });
    //   state.isLoading = false;
    //   return;
    // }
    let updateData = [
      {
        id: props.lineItem.id,
        driver_id: state.selectedDriver.id,
        shipping_cost: state.shipping_cost,
        scheduled_date: state.scheduled_date
      }
    ]
    const { data, error } = await lineItemApi.updateLineItem(updateData)

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error updating order",
        group: "br",
        life: 2000
      })
      state.isLoading = false
      return
    }
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Driver attached successfully",
      group: "br",
      life: 2000
    })
    emit("onUpdate", data)
    state.isLoading = false
  }

  const state = reactive({
    selectedDriver: null,
    selectedCity: null,
    shipping_cost: null,
    isLoading: false,
    detachLoading: false
  })
</script>

<style scoped>
  .p-datepicker-current-day {
    background-color: blue !important;
  }
</style>
