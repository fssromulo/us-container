<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="col-span-12 mb-4 field md:col-span-4">
          <label
            for="container_release"
            class="font-medium text-900 dark:text-0"
            >Product Title</label
          >
          <InputText
            :disabled="true"
            mode="decimal"
            :useGrouping="false"
            v-model="lineItem.other_product_name"
            id="container_release"
            type="text"
          />
        </div>

        <div class="col-span-12 mb-4 field md:col-span-4">
          <label for="container_number" class="font-medium text-900 dark:text-0"
            >Quantity</label
          >
          <InputNumber
            :disabled="true"
            v-model="state.other_inventory.quantity"
          ></InputNumber>
        </div>

        <div class="col-span-12 mb-4 border-t opacity-50 border"></div>
        <div class="col-span-12 mb-4 text-xl font-medium text-900 dark:text-0"
          >Shipped By</div
        >
        <div class="col-span-12 mb-4 field md:col-span-4">
          <label for="vendor" class="font-medium text-900 dark:text-0"
            >Vendor</label
          >
          <Select
            @click="checkVendors()"
            v-model="state.other_inventory.vendor_id"
            :editable="true"
            :options="vendorList"
            optionLabel="label"
            optionValue="value"
            placeholder="Select Vendor"
          />
        </div>

        <div class="col-span-12 mb-4 field md:col-span-4">
          <label for="description" class="font-medium text-900 dark:text-0"
            >Product</label
          >
          <Select
            placeholder="Select Product"
            :options="state.products"
            v-model="state.other_inventory.product_id"
            id="condition"
            type="text"
            optionLabel="label"
            optionValue="value"
          />
        </div>

        <div
          v-if="!containerProp.id"
          class="col-span-12 mb-4 field md:col-span-4"
        >
          <label for="vendor" class="font-medium text-900 dark:text-0"
            >Tracking Number</label
          >
          <InputText
            class="w-full"
            placeholder="Add Tracking Number"
            v-model="state.other_inventory.tracking_number"
          />
        </div>
        <div
          v-if="!containerProp.id"
          class="col-span-12 mb-4 field md:col-span-4"
        >
          <label for="vendor" class="font-medium text-900 dark:text-0"
            >Delivery Timeframe (5 days)</label
          >
          <InputText
            class="w-full"
            placeholder="5 days"
            v-model="state.other_inventory.delivered"
          />
        </div>

        <div class="col-span-12 mb-4 field md:col-span-4">
          <label for="surcharge_fee" class="font-medium text-900 dark:text-0"
            >Product Unit Price</label
          >
          <InputNumber
            mode="currency"
            currency="USD"
            locale="en-US"
            v-model="lineItem.revenue"
            :disabled="true"
            id="cost"
            type="text"
          />
        </div>

        <div class="col-span-12 mb-4 field md:col-span-4">
          <label for="surcharge_fee" class="font-medium text-900 dark:text-0"
            >Product Unit Cost</label
          >
          <InputNumber
            mode="currency"
            currency="USD"
            locale="en-US"
            :disabled="true"
            v-model="lineItem.product_cost"
            id="cost"
            type="text"
          />
        </div>
      </div>

      <div class="col-span-12 mb-4 border-t opacity-50 border"></div>
      <!-- <div class="col-span-6 mb-4 field">
          <label for="notes" class="font-medium text-900 dark:text-0">Notes</label>
          <Textarea
            v-model="state.container.notes"
            id="notes"
            :autoResize="true"
            ::rows="5"
          ></Textarea>
        </div> -->
      <!-- <div class="col-span-12 mb-4 border-t opacity-50 border"></div> -->
    </div>
    <Button
      :label="buttonLabel"
      @click="createAttachAccessory()"
      :loading="state.loading"
      icon="pi pi-file"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, defineEmits } from "vue"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"
  import VendorsService from "@/service/Vendors"
  import VendorsApi from "@/api/vendors"
  import DepotApi from "@/api/depot"
  import DepotService from "@/service/Depot"
  import PricingService from "@/service/Pricing"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"

  import { useVendors } from "@/store/modules/vendors"
  import { useDepots } from "@/store/modules/depots"
  import InventoryService from "@/service/Inventory"
  import InventoryApi from "@/api/inventory"
  import { useToast } from "primevue/usetoast"
  import { useInventory } from "@/store/modules/inventory"
  import Dropdown from "primevue/dropdown"
  import PricingApi from "@/api/pricing"

  const vendorService = new VendorsService()
  const vendorApi = new VendorsApi()
  const depotApi = new DepotApi()
  const depotService = new DepotService()
  const inventoryService = new InventoryService()
  const inventoryApi = new InventoryApi()
  const pricingService = new PricingService()
  const customerApi = new CustomerApi()
  const customerStore = useCustomerOrder()
  const pricingApi = new PricingApi()

  const vendorStore = useVendors()
  const depotStore = useDepots()
  const inventoryStore = useInventory()

  const stateService = new StateService()
  const toast = useToast()
  const { containerProp, isAttaching, lineItem, displayOrderId } = defineProps({
    displayOrderId: {
      type: String,
      default: ""
    },
    lineItem: {
      type: Object,
      default: () => ({})
    },
    containerProp: {
      type: Object,
      default: () => ({})
    },
    isAttaching: {
      type: Boolean,
      default: () => {}
    }
  })

  const buttonLabel = computed(() => {
    return lineItem?.other_inventory?.id ? "Update" : "Create"
  })

  const emit = defineEmits(["hide", "containerAttached"])

  onMounted(async () => {
    state.statesList = stateService.getStates()
    checkVendors()

    if (depotStore.depots?.length === 0) {
      state.loading = true
      const { data } = await depotApi.getDepots()
      const depots = data.value.map((depot) => depotService.dtoDepot(depot))
      depotStore.setDepots(depots)
      state.loading = false
    }

    const { data } = await pricingApi.getProduct()
    state.products = data.value.map((p) => {
      return {
        label: p.name,
        value: p.id
      }
    })
  })

  const state = reactive({
    loading: false,
    quantity: 1,
    selectedCity: null,
    selectedCategory: { name: "Rental", code: "rental" },
    categorys: [
      { name: "Rental", code: "rental" },
      { name: "Rent to Own", code: "rto" },
      { name: "Sale", code: "purchase" }
    ],
    other_inventory: cloneDeep({
      delivered: lineItem.other_inventory?.delivered || "",
      quantity: 1,
      tracking_number: lineItem.other_inventory?.tracking_number || "",
      invoice_number: "",
      product_id: null,
      vendor_id: lineItem.other_inventory?.vendor?.id || "",
      line_item_id: lineItem.id,
      cost: lineItem.product_cost,
      price: lineItem.revenue
    })
  })

  const checkVendors = async () => {
    if (vendorStore.vendors?.length === 0) {
      state.loading = true
      const { data } = await vendorApi.getVendors()
      const vendors = data.value.map((l) => vendorService.dtoVendor(l))
      vendorStore.setVendors(vendors)
      state.loading = false
    }
  }

  const vendorList = computed(() => {
    return vendorStore?.vendors
      ?.filter(
        (vendor) => vendor.type != null && vendor.type.type == "ACCESSORIES"
      )
      .map((v) => {
        return { label: v.name, value: v.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const createAttachAccessory = async () => {
    state.loading = true
    if (lineItem?.other_inventory?.id) {
      const { data, error } = await inventoryApi.updateOtherInventory(
        lineItem?.other_inventory?.id,
        state.other_inventory
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Inventory updated",
          detail: "Successfully updated accessory inventory",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating accessory inventory",
          group: "br",
          life: 5000
        })
      }
    } else {
      const { data, error } = await inventoryApi.createOtherInventory(
        state.other_inventory
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Inventory created",
          detail: "Successfully created accessory inventory",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error creating accessory inventory",
          group: "br",
          life: 5000
        })
      }
    }
    await updateOrder()
    state.loading = false
    emit("hide")
  }
  const updateOrder = async () => {
    const { data } = await customerApi.getOrderByDisplayId(displayOrderId)
    customerStore.setOrder(null)
    customerStore.setOrder(data.value)
  }
</script>

<style></style>
