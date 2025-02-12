<template>
  <section class="flex flex-col w-full">
    <p class="mt-0 mt-1 mb-2 ml-2 text-xl font-semibold text-900 dark:text-0">
      Pricing and Cost
    </p>
    <div class="grid grid-cols-3 grid-cols-12 gap-2 gap-4 ml-1">
      <div>
        <table class="p-datatable-sm">
          <tbody>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100">Cost</td>
            </tr>
            <tr>
              <!-- !ability.can('update', 'order_column-accessory_cost') -->
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  disabled
                  mode="currency"
                  :placeholder="state.selectedLineItem.product_cost"
                  id="inventory_total_cost"
                  currency="USD"
                  type="text"
                  class="flex-1"
                >
                </InputNumber>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div>
        <table class="p-datatable-sm">
          <tbody>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100">
                Shipping Cost
              </td>
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  :disabled="
                    !ability.can('update', 'order_column-shipping_cost')
                  "
                  mode="currency"
                  currency="USD"
                  v-model="state.selectedLineItem.shipping_cost"
                  id="shipping_cost"
                  placeholder="0.00"
                  type="text"
                  class="flex-1"
                ></InputNumber>
              </td>
            </tr>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100">
                Shipping Price
              </td>
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  mode="currency"
                  currency="USD"
                  v-model="state.selectedLineItem.shipping_revenue"
                  id="shipping_revenue"
                  type="text"
                  class="flex-1"
                >
                </InputNumber>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div>
        <table class="p-datatable-sm">
          <tbody>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100">
                Accessory price
              </td>
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  mode="currency"
                  currency="USD"
                  v-model="state.selectedLineItem.revenue"
                  id="line_item_line_item_revenue"
                  type="text"
                  class="flex-1"
                >
                </InputNumber>
              </td>
            </tr>

            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100">
                Delivery Date
              </td>
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <DatePicker
                  :disabled="!ability.can('update', 'accessory-potential_date')"
                  v-model="state.selectedLineItem.delivery_date"
                  id="delivery_date"
                  class="text-md"
                  dateFormat="mm/dd/y"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="col-span-12 mt-2 border-t border"></div>

    <div class="grid grid-cols-12 gap-4 mt-4 ml-1 grid-nogutter p-fluid">
      <div
        class="col-span-4 mt-4 text-base text-xl text-900 dark:text-0 md:col-span-2 xl:col-span-2"
        >Tracking Number</div
      >
      <div class="col-span-8 mt-4 text-xl">
        {{ state.selectedLineItem?.other_inventory?.tracking_number }}
      </div>
      <div
        v-if="ability.can('read', 'order_column-accessory_release')"
        class="col-span-4 md:col-span-3 xl:col-span-3"
      >
        <Button
          @click="state.attachAccessoryDialog = true"
          :disabled="!ability.can('attach', 'accessory')"
          class="p-button-raised"
          :label="state.selectedLineItem?.other_inventory ? 'Update' : 'Attach'"
        />
      </div>
      <div
        v-if="
          ability.can('read', 'order_column-accessory_release') &&
          state.selectedLineItem.other_inventory != null
        "
        class="col-span-4 md:col-span-3 xl:col-span-3"
      >
        <Button
          :disabled="!ability.can('attach', 'accessory')"
          @click="detachAccessory"
          :loading="state.detachAccessoryLoading"
          class="ml-2 p-button-raised"
          label="Detach"
        />
      </div>
      <div
        v-if="ability.can('read', 'order_column-accessory_release')"
        class="col-span-3 ml-2"
      >
        <Button
          v-if="state.selectedLineItem?.other_inventory?.tracking_number"
          :disabled="
            !ability.can('attach', 'accessory') ||
            !state.selectedLineItem?.other_inventory
          "
          @click="sendPickupEmail"
          :loading="state.pickupEmailLoading"
          class="ml-2 mr-8 p-button-raised p-button-secondary"
          :label="
            state.selectedLineItem?.pickup_email_sent
              ? 'Send pickup email again'
              : 'Send pickup email'
          "
        />
      </div>
    </div>
    <Divider></Divider>
    <div class="mt-4 text-center">
      <Button
        @click="toggleEdit"
        class="p-button-raised p-button-secondary"
        label="Cancel"
      >
      </Button>
      <Button
        @click="saveLineItem"
        class="ml-4 mr-8 p-button-raised"
        :loading="state.isLoading"
        label="Save"
      >
      </Button>
    </div>
  </section>
</template>

<script setup>
  import { useDrivers } from "../../store/modules/drivers"
  import DriversService from "../../service/Drivers"
  import DriverApi from "../../api/drivers"
  import { onMounted, computed } from "vue"

  const driverStore = useDrivers()
  const driversService = new DriversService()
  const driverApi = new DriverApi()

  const driversList = computed(() => {
    return driverStore.drivers
      .map((d) => {
        return { label: d.company_name, value: d.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const accessoryReleaseAndNumber = computed(() => {
    return state.selectedLineItem?.other_inventory.tracking_number
  })

  onMounted(async () => {
    const { data } = await driverApi.getDrivers()
    const drivers = data.value.map((l) => driversService.dtoDriver(l))
    driverStore.setDrivers(drivers)
  })

  const {
    toggleEdit,
    saveLineItem,
    detachDriver,
    detachAccessory,
    sendPickupEmail,
    state,
    ability,
    customerStore,
    customerOrder,
    inventoryService,
    isNotInvoiced
  } = defineProps({
    toggleEdit: {
      type: Function,
      default: () => ({})
    },
    saveLineItem: {
      type: Function,
      default: () => ({})
    },
    detachDriver: {
      type: Function,
      default: () => ({})
    },
    detachAccessory: {
      type: Function,
      default: () => ({})
    },
    sendPickupEmail: {
      type: Function,
      default: () => ({})
    },
    state: {
      type: Object,
      default: {
        lineItems: {},
        isDeleting: false,
        attachAccessoryDialog: false,
        attachDriverDialog: false,
        originalLineItems: {},
        isLoading: false,
        selectedLineItem: {},
        selectedTypes: null,
        pickupEmailLoading: false,
        detachDriverLoading: false,
        detachAccessoryLoading: false
      }
    },
    ability: {
      type: Object
    },
    customerStore: {
      type: Object
    },
    customerOrder: {
      type: Object
    },
    inventoryService: {
      type: Object
    },
    isNotInvoiced: {
      type: Boolean,
      default: false
    }
  })
</script>
