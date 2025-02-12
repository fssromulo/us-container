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
            v-if="state.lineItemsTotal > 1"
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
          <span class="mb-1 ml-1 text-base text-xl text-900 dark:text-0"
            >Product</span
          >
          <table class="p-datatable-sm">
            <tbody>
              <tr style="height: 1rem">
                <td class="text-base text-xl text-700 dark:text-100">Title</td>
                <td class="text-base text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem.title }}
                </td>
              </tr>
              <tr style="height: 1rem">
                <td class="text-base text-xl text-700 dark:text-100"
                  >Product Link</td
                >
                <td class="text-base text-xl text-900 dark:text-0">
                  <a
                    :href="
                      state.selectedLineItem?.accessory_line_item[0]
                        ?.other_product?.product_link
                    "
                    target="_blank"
                    >Click here</a
                  >
                </td>
              </tr>

              <tr style="height: 1rem">
                <td class="text-base text-xl text-700 dark:text-100"
                  >Tracking No.</td
                >
                <td class="text-base text-xl text-900 dark:text-0">
                  {{ state.selectedLineItem?.other_inventory?.tracking_number }}
                </td>
              </tr>
              -
              <tr style="height: 1rem">
                <td class="text-base text-xl text-700 dark:text-100"
                  >Is Delivered ?
                </td>
                <td class="text-base text-xl text-900 dark:text-0">
                  {{
                    dfc(state.selectedLineItem?.delivery_date?.toISOString()) ==
                    "Invalid DateTime"
                      ? "No"
                      : "Yes"
                  }}
                </td>
              </tr>
              <tr style="height: 1rem">
                <td class="text-base text-xl text-700 dark:text-100"
                  >Delivered On
                </td>
                <td class="text-base text-xl text-900 dark:text-0">
                  {{
                    dfc(state.selectedLineItem?.delivery_date?.toISOString()) ==
                    "Invalid DateTime"
                      ? "Not Delivered"
                      : dfc(
                          state.selectedLineItem?.delivery_date?.toISOString()
                        )
                  }}
                </td>
              </tr>
              <tr>
                <td><Divider /></td>
                <td><Divider /></td>
              </tr>
              <tr
                ><td>
                  <div class="mt-4 text-xl text-900 dark:text-0"
                    >Price & Cost</div
                  ></td
                ></tr
              >
              <tr
                v-if="$ability.can('read', 'order_column-container_cost')"
                style="height: 1.5rem"
              >
                <td class="text-base text-xl text-700 dark:text-100"
                  >Convenience fee</td
                >
                <td class="text-base text-xl text-900 dark:text-0">
                  {{ $fc(state.selectedLineItem?.fee) }}
                </td>
              </tr>
              <tr
                v-if="$ability.can('read', 'order_column-shipping_cost')"
                style="height: 1.5rem"
              >
                <td class="text-base text-xl text-700 dark:text-100">Price</td>
                <td class="text-base text-xl text-900 dark:text-0">
                  {{ $fc(state.selectedLineItem?.calculated_total_revenue) }}
                </td>
              </tr>
              <tr
                v-if="
                  customerStore?.order?.status == 'Completed' ||
                  dfc(state.selectedLineItem?.delivery_date?.toISOString()) !=
                    'Invalid DateTime'
                "
                style="height: 1.5rem"
              >
                <td class="text-base text-xl text-700 dark:text-100"
                  >Commission</td
                >
                <td class="text-base text-xl text-900 dark:text-0">
                  {{
                    $fc(state.selectedLineItem?.calculated_accessory_commission)
                  }}
                </td>
              </tr>

              <tr>
                <td><Divider /></td>
                <td><Divider /></td>
              </tr>
              <tr style="height: 1.5rem; max-width: 0px">
                <td class="text-base text-xl text-700 dark:text-100">Vendor</td>
                <td
                  v-if="$ability.can('read', 'order_column-container_release')"
                  class="text-base text-xl text-900 dark:text-0"
                >
                  {{ state.selectedLineItem?.other_inventory?.vendor?.name }}
                </td>
              </tr>
              <!-- <tr style="height: 1.5rem" v-if="!customerStore.order.is_pickup">
            <td class="text-base text-xl text-700 dark:text-100">Driver</td>
            <td
              v-if="$ability.can('read', 'order_column-release_sent')"
              class="text-xl text-900 dark:text-0"
            >
              {{ state.selectedLineItem?.driver_name || "None" }}
            </td>
            <td v-else class="text-sm text-900 dark:text-0">
              {{ state.selectedLineItem?.driver_name || "" }}
            </td>
          </tr> -->
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
    </div>

    <div v-else>
      <AccessoryItemEdit
        :state="state"
        :toggleEdit="toggleEdit"
        :saveLineItem="saveLineItem"
        :detachDriver="detachDriver"
        :detachAccessory="detachAccessory"
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
      v-model:visible="state.attachAccessoryDialog"
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
            <p class="text-3xl">Attach Accessory</p>
          </div>
        </div>
      </template>
      <AttachAccessory
        @AttachAccessory="updateOrder"
        :close="() => (state.attachAccessoryDialog = false)"
        :lineItem="state.selectedLineItem"
        :displayOrderId="customerStore.order.display_order_id"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, onMounted, inject, computed, watch } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import isEqual from "lodash.isequal"

  import LineItemApi from "@/api/lineItem"
  import { useToast } from "primevue/usetoast"
  import AttachAccessory from "@/components/inventory/AttachAccessory"
  import InventorysService from "../../service/Inventory"
  import InventorysApi from "../../api/inventory"
  import PricingService from "../../service/Pricing"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import CustomerApi from "@/api/customers"
  import AccessoryItemEdit from "@/components/invoicing/AccessoryItemEdit.vue"
  import { dfs, dfc } from "@/service/DateFormat"
  import Divider from "primevue/divider"
  import { useConfirm } from "primevue/useconfirm"
  import LogisticsButton from "@/components/invoicing/Logistics/LogisticsButton.vue"
  import { useUsers } from "@/store/modules/users"

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

  const isNotInvoiced = computed(() => {
    return customerStore.order?.status !== "Invoiced"
  })

  const emit = defineEmits(["onUpdate"])

  const props = defineProps({})

  onMounted(() => {
    resetLineItem()
  })

  const accessory = computed(() => {
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

  const detachAccessory = async () => {
    state.detachAccessoryLoading = true
    const { data, error } = await inventoryApi.detachOtherInventory(
      state.selectedLineItem.other_inventory?.id
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
    await updateOrder()

    state.detachAccessoryLoading = false
  }

  const detachDriver = async () => {
    state.detachDriverLoading = true
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

  const resetLineItem = () => {
    state.lineItems = cloneDeep(customerStore.order)
      .line_items.filter(
        (e) => e.product_type && e.product_type === "CONTAINER_ACCESSORY"
      )
      .map((lineItem) => {
        return lineItemDto(lineItem)
      })
    state.lineItemsTotal = customerStore.order.line_items.length
    state.originalLineItems = cloneDeep(state.lineItems)

    state.isLoading = false
    state.isEditing = false
    state.attachAccessoryDialog = false
    state.detachDriverLoading = false
    state.detachAccessoryLoading = false
    state.selectedLineItem = state.lineItems[0]
    if (state.selectedLineItem?.delivery_date) {
      state.selectedLineItem.delivery_date = new Date(
        state.selectedLineItem?.delivery_date
      )
    }
  }

  const onPage = (event) => {
    state.selectedLineItem = state.lineItems[event.page]
    if (state.selectedLineItem?.delivery_date) {
      state.selectedLineItem.delivery_date = new Date(
        state.selectedLineItem?.delivery_date
      )
    }
  }

  const saveLineItem = async () => {
    if (isEqual(state.lineItems, state.originalLineItems)) {
      toast.add({
        severity: "warn",
        summary: "Warn",
        detail: "Line items unchanged",
        group: "br",
        life: 2000
      })
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

  const state = reactive({
    lineItems: {},
    isDeleting: false,
    attachAccessoryDialog: false,
    originalLineItems: {},
    isEditing: false,
    isLoading: false,
    selectedLineItem: {},
    selectedTypes: null,
    pickupEmailLoading: false,
    detachDriverLoading: false,
    detachAccessoryLoading: false,
    lineItemsTotal: 0
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
