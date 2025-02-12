<template>
  <ConfirmPopup></ConfirmPopup>
  <section class="flex flex-col w-full">
    <p class="ml-2 text-xl font-semibold text-900 dark:text-0">Product</p>
    <div class="grid grid-cols-3 grid-cols-12 gap-2 gap-4 ml-1">
      <div>
        <table class="p-datatable-sm">
          <tbody>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100">Type</td>
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <MultiSelect
                  icon="pi pi-plus"
                  :disabled="!ability.can('update', 'order_column-productText')"
                  v-model="state.selectedLineItem.displayAttributes"
                  class="w-full mt-1"
                  :options="inventoryService.types"
                  optionLabel="label"
                  optionValue="value"
                />
              </td>
            </tr>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Door Orientation</td
              >
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <Select
                  :disabled="
                    !ability.can('update', 'order_column-door_orientation')
                  "
                  v-model="state.selectedLineItem.door_orientation"
                  class="text-md"
                  :options="[
                    { value: 'Facing Cab', label: 'Facing Cab' },
                    { value: 'Opposite of Cab', label: 'Opposite of Cab' }
                  ]"
                  optionLabel="label"
                  optionValue="value"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="mt-2">
        <label class="text-md text-700 dark:text-100">Size</label>
        <Select
          :disabled="!ability.can('update', 'order_column-productText')"
          icon="pi pi-plus"
          v-model="state.selectedLineItem.container_size"
          class="w-full mt-1"
          optionLabel="label"
          optionValue="value"
          :options="inventoryService.sizes"
        />
      </div>

      <div class="mt-2">
        <label class="text-md text-700 dark:text-100">Condition</label>
        <Select
          :disabled="!ability.can('update', 'order_column-productText')"
          optionLabel="label"
          optionValue="value"
          :options="inventoryService.conditions"
          v-model="state.selectedLineItem.condition"
          class="w-full mt-1"
          id="condition"
          type="text"
        />
      </div>
    </div>
    <div class="col-span-12 mt-2 border-t border"></div>

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
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  disabled
                  mode="currency"
                  :disabled="
                    !ability.can('update', 'order_column-container_cost')
                  "
                  :placeholder="state.selectedLineItem.inventory?.total_cost"
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
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Shipping Cost</td
              >
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
                  type="text"
                  class="flex-1"
                ></InputNumber>
              </td>
            </tr>
            <tr
              v-if="
                customerOrder.type === 'PURCHASE' ||
                customerOrder.type === 'RENT_TO_OWN'
              "
            >
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Shipping Price</td
              >
            </tr>
            <tr
              v-if="
                customerOrder.type === 'PURCHASE' ||
                customerOrder.type === 'RENT_TO_OWN'
              "
              style="height: 2rem"
            >
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  :disabled="
                    !ability.can('update', 'order_column-shipping_revenue')
                  "
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
            <tr
              v-if="
                customerOrder.type === 'PURCHASE' ||
                customerOrder.type === 'RENT_TO_OWN'
              "
            >
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Container price</td
              >
            </tr>
            <tr
              v-if="
                customerOrder.type === 'PURCHASE' ||
                customerOrder.type === 'RENT_TO_OWN'
              "
              style="height: 2rem"
            >
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  mode="currency"
                  :disabled="
                    !ability.can('update', 'order_column-container_revenue')
                  "
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
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Container color</td
              >
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <Select
                  placeholder="Container color"
                  optionLabel="name"
                  optionValue="code"
                  :options="state.container_colors"
                  v-model="state.container_color"
                  id="container_color"
                  type="text"
                />
              </td>
            </tr>
            <tr v-if="customerOrder.type === 'RENT'">
              <td colspan="2" class="text-md text-700 dark:text-100">
                Monthly price<br />
                <strong
                  >*Note: Monthly price change affects rent periods with no
                  payments made</strong
                >
              </td>
            </tr>
            <tr v-if="customerOrder.type === 'RENT'" style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  mode="currency"
                  currency="USD"
                  v-model="state.selectedLineItem.monthly_owed"
                  id="line_item_line_item_revenue"
                  type="text"
                  class="flex-1"
                >
                </InputNumber>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="col-span-12 mt-2 border-t border"></div>

    <p class="ml-2 text-xl font-semibold text-900 dark:text-0">Logistics</p>
    <div class="grid grid-cols-3 grid-cols-12 gap-2 gap-4 ml-1">
      <div>
        <table class="p-datatable-sm">
          <tbody>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Potential Date</td
              >
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <DatePicker
                  :disabled="
                    !ability.can('update', 'order_column-potential_date')
                  "
                  v-model="state.selectedLineItem.potential_date"
                  id="potential_date"
                  class="text-md"
                  dateFormat="mm/dd/y"
                />
              </td>
            </tr>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Set Date</td
              >
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <DatePicker
                  :disabled="!ability.can('update', 'order_column-set_date')"
                  v-model="state.selectedLineItem.scheduled_date"
                  id="scheduled_date"
                  class="text-md"
                  dateFormat="mm/dd/y"
                />
              </td>
            </tr>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100">
                Potential Dollar per Mile
              </td>
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  mode="currency"
                  :disabled="
                    !ability.can(
                      'update',
                      'order_column-potential_doller_per_mile'
                    )
                  "
                  v-model="state.selectedLineItem.potential_dollar_per_mile"
                  id="potential_doller_per_mile"
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
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Coming from</td
              >
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <InputText
                  disabled
                  mode="currency"
                  v-model="state.selectedLineItem.location"
                  id="location"
                  type="text"
                  class="flex-1"
                ></InputText>
              </td>
            </tr>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Potential Miles</td
              >
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <InputNumber
                  mode="decimal"
                  :disabled="
                    !ability.can('update', 'order_column-potential_miles')
                  "
                  v-model="state.selectedLineItem.potential_miles"
                  id="potential_miles"
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
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Welcome Call</td
              >
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <Select
                  :disabled="
                    !ability.can('update', 'order_column-welcome_call')
                  "
                  v-model="state.selectedLineItem.welcome_call"
                  class="text-md"
                  :options="[
                    { value: 'YES', label: 'Yes' },
                    { value: 'NO', label: 'No' },
                    { value: 'IN PROGRESS', label: 'In Progress' }
                  ]"
                  optionLabel="label"
                  optionValue="value"
                />
              </td>
            </tr>
            <tr>
              <td colspan="2" class="text-md text-700 dark:text-100"
                >Good To Go</td
              >
            </tr>
            <tr style="height: 2rem">
              <td class="text-sm text-900 dark:text-0">
                <Select
                  :disabled="!ability.can('update', 'order_column-good_to_go')"
                  v-model="state.selectedLineItem.good_to_go"
                  class="text-md"
                  :options="[
                    { value: 'YES', label: 'Yes' },
                    { value: 'NO', label: 'No' },
                    { value: 'IN PROGRESS', label: 'In Progress' }
                  ]"
                  optionLabel="label"
                  optionValue="value"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="grid grid-cols-12 gap-4 mt-4 ml-1 grid-nogutter p-fluid">
      <div class="col-span-3 mt-4 text-xl text-900 dark:text-0"
        >Container Release</div
      >
      <div
        v-if="
          ability.can('read', 'order_column-container_release') &&
          state.selectedLineItem?.inventory
        "
        class="col-span-3 mt-4 text-xl"
      >
        {{ containerReleaseAndNumber }}
      </div>
      <div
        v-if="ability.can('read', 'order_column-container_release')"
        class="col-span-3"
      >
        <Button
          @click="state.attachContainerDialog = true"
          :disabled="!ability.can('attach', 'container')"
          class="p-button-raised"
          :label="state.selectedLineItem?.inventory ? 'Update' : 'Attach'"
        />
      </div>
      <div
        v-if="
          ability.can('read', 'order_column-container_release') &&
          state.selectedLineItem?.inventory
        "
        class="col-span-3"
      >
        <Button
          :disabled="!ability.can('attach', 'container')"
          @click="detachContainer($event)"
          :loading="state.detachContainerLoading"
          class="ml-2 p-button-raised"
          label="Detatch"
        />
      </div>
      <div
        v-if="ability.can('read', 'order_column-container_release')"
        class="col-span-3 ml-2"
      >
        <Button
          v-if="
            state.selectedLineItem?.inventory?.container_release_number &&
            customerStore.order.is_pickup
          "
          :disabled="
            !ability.can('attach', 'container') ||
            !state.selectedLineItem?.inventory
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
    <div
      class="grid grid-cols-12 gap-4 mt-4 ml-1 grid-nogutter p-fluid"
      v-if="!customerStore.order.is_pickup"
    >
      <div class="col-span-3 mt-2 text-xl text-900 dark:text-0">Driver</div>
      <div
        v-if="
          state.selectedLineItem?.driver_name &&
          ability.can('read', 'order_column-release_sent')
        "
        class="col-span-3 text-xl"
      >
        {{ state.selectedLineItem?.driver_name || "None" }}
      </div>
      <div
        v-if="ability.can('read', 'order_column-release_sent')"
        class="col-span-3"
      >
        <Button
          @click="state.attachDriverDialog = true"
          :disabled="
            !ability.can('attach', 'driver') ||
            !state.selectedLineItem?.inventory_id ||
            customerStore.order.is_pickup
          "
          class="p-button-secondary"
          :label="
            state.selectedLineItem?.driver_name
              ? 'Re attach driver'
              : 'Attach driver'
          "
        />
      </div>
      <div
        v-if="ability.can('read', 'order_column-release_sent')"
        class="col-span-2"
      >
        <Button
          v-if="state.selectedLineItem?.driver_name"
          :disabled="
            !ability.can('attach', 'driver') || customerStore.order.is_pickup
          "
          @click="detachDriver"
          :loading="state.detachLoading"
          class="ml-4 mr-8 p-button-raised"
          label="Detatch driver"
        />
      </div>
    </div>
    <div
      class="grid grid-cols-12 gap-4 mt-4 ml-1 grid-nogutter p-fluid"
      v-if="
        state.selectedLineItem.inventory != null &&
        ability.can('create', 'container-location')
      "
    >
      <div class="col-span-3 mt-2 text-xl text-900 dark:text-0"
        >Container location</div
      >
      <div
        v-if="
          state.selectedLineItem.inventory_address == undefined ||
          state.selectedLineItem.inventory_address.length == 0
        "
        class="col-span-6 ml-2"
      >
        <Button
          @click="attachInventoryLocation"
          :loading="state.pickupEmailLoading"
          class="ml-2 mr-2 p-button-raised p-button-primary"
          label="Add inventory location"
        />
      </div>
      <div
        v-if="
          state.selectedLineItem.inventory_address &&
          state.selectedLineItem.inventory_address.length > 0
        "
        class="col-span-6 ml-2"
      >
        {{ state.selectedLineItem.inventory_address[0]?.full_address_computed }}
        <Button
          @click="attachInventoryLocation"
          :loading="state.pickupEmailLoading"
          icon="pi pi-pencil text-sm"
          class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
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
  import { onMounted, computed, inject } from "vue"
  import { useRouter } from "vue-router"
  import AccountApi from "@/api/account"

  const accountApi = new AccountApi()

  const $route = inject("$route")

  const driverStore = useDrivers()
  const driversService = new DriversService()
  const driverApi = new DriverApi()
  const router = useRouter()

  const driversList = computed(() => {
    return driverStore.drivers
      .map((d) => {
        return { label: d.company_name, value: d.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const containerReleaseAndNumber = computed(() => {
    const inventory = state.selectedLineItem?.inventory
    if (inventory?.container_release_number && inventory?.container_number) {
      return `${inventory?.container_release_number} | ${inventory?.container_number}`
    } else {
      return inventory?.container_release_number
    }
  })
  const openSelectContainer = (id) => {
    const currentParams = { ...router.params }
    currentParams.id = id.slice(0, 4)
    router.push({ name: "inventory_with_id", params: currentParams })
  }

  onMounted(async () => {
    let { data } = await driverApi.getDrivers()
    const drivers = data.value.map((l) => driversService.dtoDriver(l))
    driverStore.setDrivers(drivers)
    data = await accountApi.getAccount()
    const cms_attributes = data?.data?.value?.cms_attributes
    state.container_colors =
      cms_attributes?.container_colors != undefined
        ? cms_attributes.container_colors.map((el) => {
            return { name: el, code: el }
          })
        : []

    state.container_color = state.selectedLineItem?.inventory?.container_color
  })

  const {
    toggleEdit,
    saveLineItem,
    detachDriver,
    detachContainer,
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
    detachContainer: {
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
        attachContainerDialog: false,
        attachDriverDialog: false,
        originalLineItems: {},
        isLoading: false,
        selectedLineItem: {},
        selectedTypes: null,
        pickupEmailLoading: false,
        detachDriverLoading: false,
        detachContainerLoading: false,
        showAttachInventoryLocationDialog: false,
        container_colors: [],
        container_color: ""
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

  const attachInventoryLocation = () => {
    state.showAttachInventoryLocationDialog = true
  }
</script>
