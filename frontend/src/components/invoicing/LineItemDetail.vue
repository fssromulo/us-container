<template>
  <div v-if="state.lineItems.length > 0">
    <div class="flex items-center justify-between w-full">
      <ConfirmPopup></ConfirmPopup>
      <div class="grid grid-cols-12 gap-4">
        <div class="col-span-6">
          <Button
            type="button"
            icon="pi pi-pencil text-sm"
            @click="toggleEdit"
            class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
          ></Button>
        </div>
        <div class="col-span-6">
          <Button
            v-if="state.lineItems.length > 1"
            type="button"
            :loading="state.isDeleting"
            :disabled="!$ability.can('delete', 'order_column-line_item')"
            icon="pi pi-trash text-sm"
            @click="deleteLineItem($event)"
            class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
          ></Button>
        </div>
      </div>
    </div>

    <Divider />
    <div v-if="!state.isEditing">
      <div class="col-span-12">
        <section class="flex flex-col w-full">
          <span class="mb-1 ml-1 text-xl text-900 dark:text-0">Product</span>
          <table class="p-datatable-sm">
            <tbody>
              <tr style="height: 1rem">
                <td class="text-xl text-700 dark:text-100">Title</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem?.title }}
                </td>
              </tr>
              <tr style="height: 1rem">
                <td class="text-xl text-700 dark:text-100">Delivery from</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem?.location }}
                </td>
              </tr>
              <tr
                v-if="state.selectedLineItem?.potential_date"
                style="height: 1.5rem"
              >
                <td class="text-xl text-700 dark:text-100">Potential Date</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ dfs(state.selectedLineItem?.potential_date) }}
                </td>
              </tr>
              <tr
                v-if="
                  $ability.can('read', 'order_column-potential_driver_id') &&
                  state.selectedLineItem?.potential_driver
                "
                style="height: 1.5rem"
              >
                <td class="text-xl text-700 dark:text-100">Potential Driver</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem?.potential_driver.company_name }}
                </td>
              </tr>
              <tr style="height: 1.5rem">
                <td class="text-xl text-700 dark:text-100">Welcome Call</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem?.welcome_call }}
                </td>
              </tr>
              <tr style="height: 1.5rem">
                <td class="text-xl text-700 dark:text-100">Good To Go</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem?.good_to_go }}
                </td>
              </tr>
              <tr class="mb-2" style="height: 1.5rem">
                <td class="text-xl text-700 dark:text-100">Door Orientation</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem.door_orientation }}
                </td>
              </tr>
              <tr>
                <td><Divider /></td>
                <td><Divider /></td>
              </tr>
              <tr>
                <td
                  ><div class="mt-4 text-xl text-900 dark:text-0"
                    >Price & Cost</div
                  ></td
                >
              </tr>

              <tr
                v-if="$ability.can('read', 'order_column-container_cost')"
                style="height: 1.5rem"
              >
                <td class="text-xl text-700 dark:text-100">Cost</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ $fc(state.selectedLineItem?.inventory?.total_cost) }}
                </td>
              </tr>
              <tr
                v-if="$ability.can('read', 'order_column-shipping_cost')"
                style="height: 1.5rem"
              >
                <td class="text-xl text-700 dark:text-100">Shipping Cost</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ $fc(state.selectedLineItem.shipping_cost) }}
                </td>
              </tr>
              <tr
                v-if="
                  customerStore.order.type === 'PURCHASE' ||
                  customerStore.order.type === 'PURCHASE_ACCESSORY' ||
                  customerStore.order.type === 'RENT_TO_OWN'
                "
                style="height: 1.5rem"
              >
                <td class="text-xl text-700 dark:text-100">Price</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ $fc(state.selectedLineItem.revenue) }}
                </td>
              </tr>
              <tr
                v-if="customerStore.order.type === 'RENT'"
                style="height: 1.5rem"
              >
                <td class="text-xl text-700 dark:text-100">Monthly Price</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ $fc(state.selectedLineItem.monthly_owed) }}
                </td>
              </tr>
              <tr style="height: 1.5rem">
                <td class="text-xl text-700 dark:text-100">Shipping Price</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ shippingPriceMessage }}
                </td>
              </tr>
              <tr>
                <td><Divider /></td>
                <td><Divider /></td>
              </tr>
              <tr
                v-for="(history, index) in state.selectedLineItem
                  ?.rental_history"
                :key="index"
              >
                <td class="text-xl text-700 dark:text-100"
                  >Previously Attached
                </td>
                <td class="text-xl text-900 dark:text-0">
                  <Tag
                    :value="
                      history.inventory.container_number +
                      ` : ` +
                      history.inventory.container_release_number
                    "
                    @click="openSelectContainer(history.inventory.id)"
                  ></Tag>
                </td>
              </tr>
              <tr style="height: 1.5rem; max-width: 0px">
                <td class="text-xl text-700 dark:text-100">Container</td>
                <td
                  v-if="$ability.can('read', 'order_column-container_release')"
                  class="text-xl text-900 dark:text-0"
                >
                  {{ container }}
                </td>
              </tr>
              <tr style="height: 1.5rem" v-if="!customerStore.order.is_pickup">
                <td class="text-xl text-700 dark:text-100">Driver</td>
                <td
                  v-if="$ability.can('read', 'order_column-release_sent')"
                  class="text-xl text-900 dark:text-0"
                >
                  {{ state.selectedLineItem?.driver_name || "None" }}
                </td>
                <td v-else class="text-sm text-900 dark:text-0">
                  {{ state.selectedLineItem?.driver_name || "" }}
                </td>
              </tr>
              <tr>
                <td class="text-xl text-700 dark:text-100">Container color</td>
                <td class="text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem.inventory?.container_color }}
                </td>
              </tr>
              <tr
                v-if="
                  $ability.can('create', 'container-location') &&
                  state.selectedLineItem.inventory != null &&
                  !state.isEditing
                "
              >
                <td class="text-base text-xl text-700 dark:text-100"
                  >Container location</td
                >
                <td>
                  {{
                    state.selectedLineItem.inventory_address == undefined
                      ? ""
                      : state.selectedLineItem.inventory_address[0]
                          ?.full_address_computed
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>
      <div class="col-span-12" v-if="canSeeLogisticsBtns">
        <section class="flex flex-col w-full">
          <LogisticsButton
            :orderId="customerStore?.order?.id"
            :lineItem="state.selectedLineItem"
          ></LogisticsButton>
        </section>
      </div>
      <!-- <div class="col-span-12">
      <section class="flex flex-col w-full">
        <table class="p-datatable-sm">
          <tr
            style="height: 1.5rem"
            v-if="customerStore.order.type === 'RENT'"
          >
            <td class="text-xl text-700 dark:text-100">Returned</td>
            <td class="text-xl text-700 dark:text-100">
              {{ dfl(state.selectedLineItem.returned_at) }}
            </td>
          </tr>
        </table>
      </section>
    </div> -->
    </div>

    <div v-else>
      <LineItemEdit
        :state="state"
        :toggleEdit="toggleEdit"
        :saveLineItem="saveLineItem"
        :detachDriver="detachDriver"
        :detachContainer="detachContainer"
        :sendPickupEmail="sendPickupEmail"
        :ability="$ability"
        :customerStore="customerStore"
        :customerOrder="customerStore.order"
        :inventoryService="inventoryService"
        :isNotInvoiced="isNotInvoiced"
      />
    </div>
    <Paginator
      @page="onPage"
      :rows="1"
      :totalRecords="state.lineItems.length"
      template="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
      currentPageReportTemplate="{first} of {totalRecords}"
    ></Paginator>
    <Dialog
      v-model:visible="state.attachDriverDialog"
      dismissableMask
      closeOnEscape
      :breakpoints="{
        '2000px': '70vw',
        '1400px': '65vw',
        '1200px': '75vw',
        '992px': '85vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
      :modal="true"
    >
      <template #header>
        <div class="flex items-stretch">
          <div class="flex">
            <p class="text-3xl">Attach Driver</p>
          </div>
        </div>
      </template>
      <AttachDriver
        @onUpdate="updateOrder()"
        :close="() => (state.attachDriverDialog = false)"
        :lineItem="state.selectedLineItem"
      />
    </Dialog>

    <Dialog
      v-model:visible="state.attachContainerDialog"
      dismissableMask
      closeOnEscape
      :modal="true"
      :breakpoints="{
        '2000px': '80vw',
        '1400px': '80vw',
        '1200px': '80vw',
        '992px': '85vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
    >
      <template #header>
        <div class="flex items-stretch">
          <div class="flex">
            <p class="text-3xl">Attach Container</p>
          </div>
        </div>
      </template>
      <AttachContainer
        @onUpdate="updateOrder"
        :close="() => (state.attachContainerDialog = false)"
        :lineItem="state.selectedLineItem"
      />
    </Dialog>

    <Dialog
      v-model:visible="state.showAttachInventoryLocationDialog"
      dismissableMask
      closeOnEscape
      :modal="true"
      :breakpoints="{
        '2000px': '80vw',
        '1400px': '80vw',
        '1200px': '80vw',
        '992px': '85vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
    >
      <template #header>
        <div class="flex items-stretch">
          <div class="flex">
            <p class="text-3xl">Attach Container Location</p>
          </div>
        </div>
      </template>
      <div class="flex items-stretch">
        <div class="flex">
          <AddContainerLocation
            v-if="
              state.selectedLineItem.inventory_address == undefined ||
              state.selectedLineItem.inventory_address.length == 0
            "
            :line_item_id="state.selectedLineItem?.id"
            :inventory_id="state.selectedLineItem?.inventory?.id"
            :close="() => (state.showAttachInventoryLocationDialog = false)"
            :resetFunction="resetOrder"
          />

          <AddContainerLocation
            v-if="
              state.selectedLineItem.inventory_address &&
              state.selectedLineItem.inventory_address.length > 0
            "
            :line_item_id="state.selectedLineItem?.id"
            :inventory_id="state.selectedLineItem?.inventory?.id"
            :state="state.selectedLineItem.inventory_address[0].address"
            :isUpdate="true"
            :address_id="state.selectedLineItem.inventory_address[0].address.id"
            :close="() => (state.showAttachInventoryLocationDialog = false)"
            :resetFunction="resetOrder"
          />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, onMounted, inject, computed, watch } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import isEqual from "lodash.isequal"
  import LineItemApi from "@/api/lineItem"
  import { useToast } from "primevue/usetoast"
  import AttachContainer from "@/components/inventory/AttachContainer"
  import AddContainerLocation from "@/components/inventory/AddContainerLocation"
  import AttachDriver from "@/components/drivers/AttachDriver"
  import InventorysService from "../../service/Inventory"
  import InventorysApi from "../../api/inventory"
  import PricingService from "../../service/Pricing"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import CustomerApi from "@/api/customers"
  import LineItemEdit from "@/components/invoicing/LineItemEdit.vue"
  import { dfs, convertDateForPost } from "@/service/DateFormat"
  import Divider from "primevue/divider"
  import { useConfirm } from "primevue/useconfirm"
  import LogisticsButton from "@/components/invoicing/Logistics/LogisticsButton.vue"
  import { useUsers } from "@/store/modules/users"
  import { useRouter } from "vue-router"

  const inventoryService = new InventorysService()
  const inventoryApi = new InventorysApi()
  const pricingService = new PricingService()
  const toast = useToast()
  const lineItemApi = new LineItemApi()
  const customerStore = useCustomerOrder()
  const customerApi = new CustomerApi()
  const confirm = useConfirm()
  const $isObjectPopulated = inject("$isObjectPopulated")
  const $fc = inject("$formatCurrency")
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $ability = inject("$ability")
  const userStore = useUsers()
  const router = useRouter()

  const isNotInvoiced = computed(() => {
    return customerStore.order?.status !== "Invoiced"
  })

  const emit = defineEmits(["onUpdate"])

  const props = defineProps({
    swapCustomerOrder: {
      type: Function,
      required: false,
      default: () => {}
    }
  })

  onMounted(() => {
    resetLineItem()
  })
  const openSelectContainer = (id) => {
    const currentParams = { ...router.params }
    currentParams.id = id.slice(0, 4)
    router.push({ name: "inventory_with_id", params: currentParams })
  }

  const container = computed(() => {
    const container_number =
      state?.selectedLineItem?.inventory?.container_number
    const container_release_number =
      state?.selectedLineItem?.inventory?.container_release_number

    if (
      container_number !== undefined &&
      container_number !== "" &&
      container_release_number !== undefined &&
      container_release_number !== ""
    ) {
      return container_number + " | " + container_release_number
    } else if (container_number !== undefined && container_number !== "") {
      return container_number
    } else {
      return container_release_number
    }
  })

  const shippingPriceMessage = computed(() => {
    return customerStore.order.type === "PURCHASE" ||
      customerStore.order.type === "RENT_TO_OWN"
      ? $fc(state.selectedLineItem.shipping_revenue)
      : "*See first rent period (under schedule)"
  })

  const canSeeLogisticsBtns = computed(() => {
    return userStore.cms?.account_name === "USA Containers"
  })
  const deleteLineItem = (event) => {
    confirm.require({
      target: event.currentTarget,
      message: "Do you want to delete this line item ?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        state.isDeleting = true
        const { error } = await lineItemApi.deleteLineItem(
          state.selectedLineItem.id
        )
        if (error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Error deleting line item",
            group: "br",
            life: 2000
          })
          state.isDeleting = false
          return
        }
        await updateOrder()
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Line item deleted",
          group: "br",
          life: 2000
        })
        state.isDeleting = false
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Rejected",
          detail: "You have rejected",
          life: 2000
        })
      }
    })
  }
  const detachRentalContainer = async () => {
    state.isLoading = true
    let updateData = {
      lineItems: [
        {
          id: state.selectedLineItem.id,
          inventory_id: null,
          product_cost: 0
        }
      ],
      move_out_date: state.rental_move_out_date,
      inventoryIdsToMakeAvailable: [state.selectedLineItem.inventory_id]
    }
    const { data, error } = await lineItemApi.updateLineItemExtra(updateData)

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
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Detached container",
        group: "br",
        life: 2000
      })
      await updateOrder()
      state.isLoading = false
      state.move_out_container = false
    }
  }
  const detachContainer = async (event) => {
    state.detachContainerLoading = true
    confirm.require({
      target: event.target,
      message:
        customerStore.order.type == "RENT"
          ? 'Detaching is for unmoved orders. If you want to detach a box because customer is in return process, use the "Move out" button instead.'
          : `Do you want to detach this container ?`,
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        state.detachContainerLoading = true

        let updateData = {
          lineItems: [
            {
              id: state.selectedLineItem.id,
              inventory_id: null,
              product_cost: 0
            }
          ],
          inventoryIdsToMakeAvailable: [state.selectedLineItem.inventory_id]
        }
        const { data, error } = await lineItemApi.updateLineItemExtra(
          updateData
        )

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
          detail: "Detached container",
          group: "br",
          life: 2000
        })
        state.move_out_container = false
        await updateOrder()
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Canceled",
          detail: "Container detach canceled",
          life: 2000
        })
        state.detachContainerLoading = false
      }
    })

    state.detachContainerLoading = false
  }

  const detachDriver = async () => {
    state.detachDriverLoading = true
    //
    let updateDate = [
      {
        id: state.selectedLineItem.id,
        driver_id: null,
        shipping_cost: 0
      }
    ]
    const { data, error } = await lineItemApi.updateLineItem(updateDate)

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error detaching driver",
        group: "br",
        life: 2000
      })
      state.isLoading = false
      return
    }
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Detached driver",
      group: "br",
      life: 2000
    })
    await updateOrder()

    state.detachDriverLoading = false
  }

  const updateOrder = async () => {
    const { data } = await customerApi.getOrderByDisplayId(
      customerStore.order.display_order_id
    )
    customerStore.setOrder(null)
    customerStore.setOrder(data.value)
  }

  const sendPickupEmail = async () => {
    state.pickupEmailLoading = true

    const { data, error } = await lineItemApi.sendPickupEmail(
      state.selectedLineItem.id
    )

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error sending pickup email",
        group: "br",
        life: 2000
      })
      state.isLoading = false
      return
    }
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Pickup email sent",
      group: "br",
      life: 2000
    })
    state.selectedLineItem.pickup_email_sent = true
    state.pickupEmailLoading = false
  }

  const lineItemDto = (lineItem) => {
    lineItem.inventory_id = lineItem.inventory?.id
    lineItem.driver_id = lineItem.driver?.id
    lineItem.potential_driver_id = lineItem.potential_driver?.company_name
    lineItem.container_release_number =
      lineItem.inventory?.container_release_number
    lineItem.driver_name = lineItem.driver?.company_name
    lineItem.potential_driver_name = lineItem.potential_driver?.company_name
    // lineItem.scheduled_date = dfs(lineItem.scheduled_date);
    // lineItem.potential_date = dfs(lineItem.potential_date);

    const displayAttributes = pricingService.convertAttributesToDisplay(
      lineItem.attributes
    )

    lineItem.displayAttributes = displayAttributes

    delete lineItem.driver
    delete lineItem.potential_driver
    delete lineItem.deliveries
    delete lineItem.note
    return lineItem
  }

  const resetOrder = async (lineItem) => {
    state.selectedLineItem = lineItem
  }

  const resetLineItem = () => {
    state.lineItems = cloneDeep(customerStore.order)
      .line_items.filter(
        (e) =>
          e.product_type == null ||
          (e.product_type && e.product_type !== "CONTAINER_ACCESSORY")
      )
      .map((lineItem) => {
        return lineItemDto(lineItem)
      })
    state.originalLineItems = cloneDeep(state.lineItems)

    state.isLoading = false
    state.isEditing = false
    state.attachContainerDialog = false
    state.attachDriverDialog = false
    state.detachDriverLoading = false
    state.detachContainerLoading = false
    state.selectedLineItem = state.lineItems[0] || {}
  }

  const onPage = (event) => {
    state.selectedLineItem = state.lineItems[event.page] || {}
  }

  const change_rental_period = async () => {
    const { error, data } = await customerApi.updateRentPeriodPrice(
      customerStore.order.id,
      state.new_rental_period_price
    )

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Updated rent price",
        group: "br",
        life: 5000
      })
      resetOrder(true)
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to update rent price",
        group: "br",
        life: 5000
      })
    }
  }

  const saveLineItem = async () => {
    let updatedContainerColor = false
    if (state.container_color) {
      const { inventory_data, inventory_error } =
        await inventoryApi.updateInventory(
          state.selectedLineItem.inventory.id,
          { container_color: state.container_color }
        )
      toast.add({
        severity: "success",
        summary: "Success",
        detail: `Container color was successfully updated`,
        group: "br",
        life: 2000
      })
      updatedContainerColor = true
    }
    if (isEqual(state.lineItems, state.originalLineItems)) {
      toast.add({
        severity: "warn",
        summary: "Warn",
        detail: "Line items unchanged",
        group: "br",
        life: 2000
      })
      if (updatedContainerColor) {
        state.isEditing = false
        updateOrder()
      }
      return
    }
    const updateData = [] // Array to store update data

    // for in loop with index example in js
    state.lineItems.forEach((lineItem, i) => {
      const requestData = $removeUnusedProps(
        lineItem,
        state.originalLineItems[i]
      )
      if (!$isObjectPopulated(requestData)) {
        return
      }

      if (requestData.potential_date != undefined) {
        requestData.potential_date = convertDateForPost(
          requestData.potential_date
        )
      }

      if (requestData.scheduled_date != undefined) {
        requestData.scheduled_date = convertDateForPost(
          requestData.scheduled_date
        )
      }

      if (requestData.revenue || requestData.shipping_revenue) {
        const originalLineItem = state.originalLineItems[i]

        if (
          originalLineItem.revenue > requestData.revenue &&
          !$ability.can("read", "decrease_container_revenue")
        ) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "You do not have permission to decrease revenue",
            group: "br",
            life: 5000
          })
          return
        }

        if (
          originalLineItem.shipping_revenue > requestData.shipping_revenue &&
          !$ability.can("read", "decrease_container_revenue")
        ) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "You do not have permission to decrease revenue",
            group: "br",
            life: 5000
          })
          return
        }
      }

      delete requestData.driver_name
      delete requestData.potential_driver_name
      delete requestData.container_release_number

      requestData.attributes =
        pricingService.convertDisplayAttributesToAttributes(
          lineItem.attributes,
          lineItem.displayAttributes
        )
      delete requestData.displayAttributes

      state.isLoading = true
      requestData.id = lineItem.id
      updateData.push(requestData)
    })

    // Wait for all update promises to complete
    lineItemApi
      .updateLineItem(updateData)
      .then((responses) => {
        // all line items have been updated successfully
        toast.add({
          severity: "success",
          summary: "Success",
          detail: `${updateData.length} line item(s) were successfully updated`,
          group: "br",
          life: 2000
        })
        updateOrder()
        props.swapCustomerOrder(customerStore.order.id)
      })
      .catch((error) => {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "There was an error updating one or more of these line items",
          group: "br",
          life: 2000
        })
        console.error(error)
      })
  }

  const toggleEdit = () => {
    state.isEditing = !state.isEditing
  }
  let currentDate = new Date()
  let year = currentDate.getFullYear()
  let month = String(currentDate.getMonth() + 1).padStart(2, "0") // Months are zero-based
  let day = String(currentDate.getDate()).padStart(2, "0")

  const state = reactive({
    lineItems: {},
    isDeleting: false,
    attachContainerDialog: false,
    attachDriverDialog: false,
    originalLineItems: {},
    isEditing: false,
    isLoading: false,
    selectedLineItem: {},
    selectedTypes: null,
    pickupEmailLoading: false,
    detachDriverLoading: false,
    detachContainerLoading: false,
    showAttachInventoryLocationDialog: false,
    rental_move_out_date: `${day}/${month}/${year}`,
    move_out_container: false
  })

  watch(
    () => customerStore.order,
    (newVal) => {
      resetLineItem()
    },
    { immediate: true, deep: true }
  )
</script>

<style scoped>
  .padTableCol {
    padding: 20px;
  }
</style>
