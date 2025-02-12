<template>
  <div class="grid grid-cols-12 col-span-12 gap-4" style="max-width: 80vw">
    <div
      :class="{
        'col-span-3': state.hasRelatedContainers,
        'col-span-0': !state.hasRelatedContainers
      }"
      v-show="state.hasRelatedContainers"
    >
      <RelatedReleaseContainers
        :releaseNumber="state.containerReleaseNumber"
        @hasRelatedContainers="hasRelatedContainers"
      >
      </RelatedReleaseContainers>
    </div>
    <div
      :class="{
        'col-span-9': state.hasRelatedContainers,
        'col-span-12': !state.hasRelatedContainers
      }"
    >
      <div>
        <div>
          <div class="grid grid-cols-12 col-span-1 gap-4 formgrid p-fluid">
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label
                for="container_release"
                class="font-medium text-900 dark:text-0"
                :class="{
                  'p-error': v$.container.container_release_number.$invalid
                }"
                >Release #*</label
              >
              <InputText
                mode="decimal"
                :useGrouping="false"
                v-on:blur="updadeContainerReleaseNumber"
                v-model="state.container.container_release_number"
                id="container_release"
                class="p-component p-inputtext-fluid"
                :class="{
                  'p-invalid': v$.container.container_release_number.$invalid
                }"
                type="text"
              />
              <small
                v-if="
                  v$.container.container_release_number.$invalid ||
                  v$.container.container_release_number.$pending.$response
                "
                class="p-error"
                >{{
                  v$.container.container_release_number.required.$message.replace(
                    "Value",
                    "Release"
                  )
                }}</small
              >
            </div>

            <div class="col-span-12 mb-4 field md:col-span-4">
              <label
                for="container_number"
                class="font-medium text-900 dark:text-0"
                >Container #</label
              >
              <InputText
                :useGrouping="false"
                class="p-component p-inputtext-fluid"
                v-model="state.container.container_number"
                id="container_number"
                type="text"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label
                for="cost"
                class="font-medium text-900 dark:text-0"
                :class="{ 'p-error': v$.container.total_cost.$invalid }"
              >
                Cost</label
              >
              <InputNumber
                mode="currency"
                currency="USD"
                locale="en-US"
                class="p-component p-inputtext-fluid"
                v-model="state.container.total_cost"
                :class="{ 'p-invalid': v$.container.total_cost.$invalid }"
                id="cost"
                type="text"
              />
            </div>
            <div
              class="col-span-12 mb-4 field md:col-span-4"
              v-if="!isAttaching"
            >
              <label
                for="container_status"
                class="font-medium text-900 dark:text-0"
                >Container status</label
              >
              <Select
                placeholder="Container status"
                optionLabel="name"
                optionValue="code"
                class="p-component p-inputtext-fluid"
                :options="state.container_statuses"
                v-model="state.container.status"
                id="payment_type"
                type="text"
              />
            </div>

            <div class="col-span-12 mb-4 border border-t opacity-50"></div>
            <div
              class="col-span-12 mb-4 text-xl font-medium text-900 dark:text-0"
              >Coming from</div
            >
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label for="vendor" class="font-medium text-900 dark:text-0"
                >Vendor</label
              >
              <Select
                @click="checkVendors()"
                class="p-component p-inputtext-fluid"
                v-model="state.container.vendor_id"
                :editable="true"
                :options="vendorList"
                :class="{ 'p-invalid': v$.container.vendor_id.$invalid }"
                optionLabel="label"
                optionValue="value"
                placeholder="Select Vendor"
              />
            </div>
            <div
              v-if="!containerProp.id"
              class="col-span-12 mb-4 field md:col-span-4"
            >
              <label for="vendor" class="font-medium text-900 dark:text-0"
                >City</label
              >
              <Select
                class="p-component p-inputtext-fluid"
                placeholder="Select City"
                v-model="state.selectedCity"
                optionLabel="label"
                optionValue="value"
                :options="mappedDepotCities"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label for="vendor" class="font-medium text-900 dark:text-0"
                >Depot</label
              >
              <Select
                v-model="state.container.depot_id"
                :editable="true"
                :options="mappedDepots"
                :class="{ 'p-invalid': v$.container.depot_id.$invalid }"
                optionLabel="label"
                optionValue="value"
                placeholder="Select Depot"
                class="p-component p-inputtext-fluid"
              />
            </div>

            <div class="col-span-12 mb-4 border border-t opacity-50"></div>
            <div
              class="col-span-12 mb-4 text-xl font-medium text-900 dark:text-0"
              >Product</div
            >
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label
                for="container_number"
                class="font-medium text-900 dark:text-0"
                >Product</label
              >
              <Select
                placeholder="Product"
                optionLabel="label"
                optionValue="value"
                :options="state.products"
                :class="{ 'p-invalid': v$.container.product_id.$invalid }"
                v-model="state.container.product_id"
                id="condition"
                class="p-component p-inputtext-fluid"
                type="text"
              />
            </div>
            <div
              v-if="!isAttaching && !containerProp?.id"
              class="col-span-12 mb-4 field md:col-span-4"
            >
              <label for="vendor" class="font-medium text-900 dark:text-0"
                >Quantity</label
              >
              <InputNumber
                v-model="state.quantity"
                class="p-component p-inputtext-fluid"
              ></InputNumber>
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label
                for="container_color"
                class="font-medium text-900 dark:text-0"
                >Container color</label
              >
              <!-- v-validate="
              state.cmsAttributes.id === 1 &&
              state.container_color?.length > 0 &&
              state.product_id?.includes('One-Trip')
                ? 'required'
                : ''
            " -->
              <Select
                placeholder="Container color"
                optionLabel="name"
                optionValue="code"
                :options="state.container_colors"
                v-model="state.container.container_color"
                id="payment_type"
                type="text"
                class="p-component p-inputtext-fluid"
              />
            </div>

            <div
              class="col-span-12 mb-4 text-xl font-medium text-900 dark:text-0"
            >
              Purchase type
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label
                for="container_number"
                class="font-medium text-900 dark:text-0"
                >Purchase type</label
              >
              <Select
                placeholder="Purchase type"
                optionLabel="label"
                optionValue="value"
                :options="inventoryService.purchase_types"
                v-model="state.container.purchase_type"
                class="p-component p-inputtext-fluid"
                id="condition"
                type="text"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label
                for="iinvoice_number"
                class="font-medium text-900 dark:text-0"
                >Invoice number</label
              >
              <InputText
                :useGrouping="false"
                v-model="state.container.invoice_number"
                class="p-component p-inputtext-fluid"
                id="invoice_number"
                type="text"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label for="invoiced_at" class="font-medium text-900 dark:text-0"
                >Invoiced date</label
              >
              <DatePicker
                v-model="state.container.invoiced_at"
                class="p-component p-inputtext-fluid"
                :manualInput="false"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label for="pickup_at" class="font-medium text-900 dark:text-0"
                >Pickup at</label
              >
              <DatePicker
                v-model="state.container.pickup_at"
                :manualInput="false"
                class="p-component p-inputtext-fluid"
                showIcon
                fluid
                iconDisplay="input"
                style="max-width: 210px"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label for="payment_type" class="font-medium text-900 dark:text-0"
                >Payment type</label
              >
              <Select
                placeholder="Payment type"
                optionLabel="label"
                optionValue="value"
                :options="inventoryService.payment_types"
                class="p-component p-inputtext-fluid"
                v-model="state.container.payment_type"
                id="payment_type"
                type="text"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label for="paid_at" class="font-medium text-900 dark:text-0"
                >Paid On</label
              >
              <DatePicker
                v-model="state.container.paid_at"
                :manualInput="false"
                class="p-component p-inputtext-fluid"
                showIcon
                fluid
                iconDisplay="input"
                style="max-width: 210px"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label
                for="iinvoice_number"
                class="font-medium text-900 dark:text-0"
                >Description</label
              >
              <Textarea
                :useGrouping="false"
                v-model="state.container.description"
                class="p-component p-inputtext-fluid"
                id="invoice_number"
                type="text"
              />
            </div>
            <div class="col-span-12 mb-4 field md:col-span-4">
              <label for="vendor" class="font-medium text-900 dark:text-0"
                >Revenue</label
              >
              <InputNumber
                v-model="state.container.revenue"
                class="p-component p-inputtext-fluid"
              ></InputNumber>
            </div>
          </div>

          <div class="col-span-12 mb-4 border border-t opacity-50"></div>
          <!-- <div class="col-span-6 mb-4 field">
        <label for="notes" class="font-medium text-900 dark:text-0">Notes</label>
        <Textarea
          v-model="state.container.notes"
          id="notes"
          :autoResize="true"
          ::rows="5"
        ></Textarea>
      </div> -->
          <!-- <div class="col-span-12 mb-4 border border-t opacity-50"></div> -->
          <Carousel
            :v-if="state.container?.image_urls?.length > 0"
            :value="state.container.image_urls"
            :numVisible="3"
            :numScroll="1"
            :circular="true"
            :autoplayInterval="3000"
            :responsiveOptions="responsiveOptions"
          >
            <template #item="slotProps">
              <div
                class="border-1 surface-border border-round m-2 text-center py-5"
              >
                <img
                  :src="slotProps.data.image_url"
                  :alt="'Image ' + slotProps.index"
                  style="width: 300px"
                  class="w-full h-12rem shadow-2 object-cover"
                />
                <Button
                  type="button"
                  icon="pi pi-trash text-sm"
                  @click="deleteImage(slotProps.index, $event)"
                  class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
                ></Button>
              </div>
            </template>
          </Carousel>
          <p :v-if="state.container?.image_urls?.length == 0"
            >No images uploaded.</p
          >

          <div class="card">
            <Toast />
            <FileUpload
              name="demo[]"
              :customUpload="true"
              @select="onSelect"
              @uploader="onUpload"
              :multiple="true"
              accept="image/*"
              :maxFileSize="1000000"
            >
              <template #empty>
                <span>Drag and drop files to here to upload.</span>
              </template>
            </FileUpload>
          </div>
          <p :v-if="state.container_images_on_update.length > 0"
            >Images uploaded.</p
          >

          <Carousel
            :v-if="state.container_images_on_update.length > 0"
            :value="state.container_images_on_update"
            :numVisible="3"
            :numScroll="1"
            :circular="true"
            :autoplayInterval="3000"
            :responsiveOptions="responsiveOptions"
          >
            <template #item="slotProps">
              <div
                class="border-1 surface-border border-round m-2 text-center py-5"
              >
                <img
                  :src="slotProps.data.image_url"
                  :alt="'Image ' + slotProps.index"
                  style="width: 300px"
                  class="w-full h-12rem shadow-2 object-cover"
                />
              </div>
            </template>
          </Carousel>
        </div>
        <Button
          :label="buttonLabel"
          @click="createUpdateContainer()"
          :loading="state.loading"
          icon="pi pi-file"
          class="w-auto"
        ></Button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, defineEmits } from "vue"
  import { watchOnce } from "@vueuse/core"
  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"
  import VendorsService from "@/service/Vendors"
  import VendorsApi from "@/api/vendors"
  import DepotApi from "@/api/depot"
  import DepotService from "@/service/Depot"
  import PricingService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import AccountApi from "@/api/account"
  import RelatedReleaseContainers from "@/components/inventory/RelatedReleaseContainers.vue"
  import { noAuthHTTP } from "@/composables/useHttp"
  import { useAxios } from "@vueuse/integrations/useAxios"

  import { useVendors } from "@/store/modules/vendors"
  import { useDepots } from "@/store/modules/depots"
  import InventoryService from "@/service/Inventory"
  import InventoryApi from "@/api/inventory"
  import { useToast } from "primevue/usetoast"
  import { useInventory } from "@/store/modules/inventory"
  import Dropdown from "primevue/dropdown"

  const vendorService = new VendorsService()
  const vendorApi = new VendorsApi()
  const depotApi = new DepotApi()
  const depotService = new DepotService()
  const inventoryService = new InventoryService()
  const inventoryApi = new InventoryApi()
  const accountApi = new AccountApi()

  const vendorStore = useVendors()
  const depotStore = useDepots()
  const inventoryStore = useInventory()
  const pricingService = new PricingService()
  const pricingApi = new PricingApi()

  const stateService = new StateService()
  const toast = useToast()
  const { containerProp, isAttaching, resetFunction, shouldSwap, status } =
    defineProps({
      containerProp: {
        type: Object,
        default: {}
      },
      isAttaching: {
        type: Boolean,
        default: () => {}
      },
      resetFunction: {
        type: Function,
        default: () => {}
      },
      shouldSwap: {
        type: Boolean,
        default: false
      },
      status: {
        type: String,
        default: ""
      }
    })

  const deleteImage = (index) => {
    state.container?.image_urls?.splice(index, 1)
  }

  const onSelect = (event) => {
    // Rename files as they're selected
    event.files.forEach((file, index) => {
      const uuid = crypto.randomUUID()
      const extension = file.name.split(".").pop()

      // Create a new File object with the modified name
      const newFile = new File([file], `${uuid}.${extension}`, {
        type: file.type
      })
      // Replace the original file with renamed file
      event.files[index] = newFile
    })
  }

  const onUpload = async (event) => {
    const formData = new FormData()
    event.files.forEach((file) => {
      formData.append("files", file)
    })

    try {
      const requestConfig = {
        method: "POST",
        headers: {
          "Content-Type": "multipart/form-data"
        }
      }
      if (formData) {
        requestConfig.data = formData
      }
      const response = await useAxios(
        `/public/api/upload`,
        requestConfig,
        noAuthHTTP
      )

      const files = response.data.value.files
      files.forEach((file) => {
        state.container_images_on_update.push({ image_url: file.url })
      })

      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Files uploaded successfully",
        life: 3000
      })
    } catch (error) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Upload failed",
        life: 3000
      })
    }
  }

  const buttonLabel = computed(() => {
    if (isAttaching) {
      return "Attach"
    }
    return containerProp?.id ? "Update" : "Create"
  })

  const emit = defineEmits(["hide", "containerAttached"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const swapOldContainer = (updatedContainer) => {
    let store
    const storeString = `${updatedContainer.status.toLowerCase()}Inventory`
    store = inventoryStore[storeString]

    const index = cloneDeep(store)
      .map((u) => u.id)
      .indexOf(updatedContainer.id)
    let clonedContainers = cloneDeep(store)
    clonedContainers[index] = inventoryService.dtoInventory(updatedContainer)

    const setterName = `set${updatedContainer.status}Inventory`
    inventoryStore[setterName](clonedContainers)
  }

  onMounted(async () => {
    state.statesList = stateService.getStates()
    resetContainer()
    checkVendors()

    if (depotStore.depots?.length === 0) {
      state.loading = true
      const { data } = await depotApi.getDepots()
      const depots = data.value.map((depot) => depotService.dtoDepot(depot))
      depotStore.setDepots(depots)
      state.loading = false
    }

    let products = await pricingApi.getContainerPricing()
    products = products.data.value.map((el) => {
      return {
        label: el.title,
        value: el.id
      }
    })
    const uniqueProducts = Array.from(
      new Set(products.map((m) => m.label))
    ).map((text) => {
      return products.find((p) => p.label === text)
    })

    uniqueProducts.sort((a, b) => a.label.localeCompare(b.label))
    state.products = uniqueProducts

    let selectedProduct = products.find(
      (p) => p.value == state.container.product_id
    )
    if (selectedProduct) {
      selectedProduct = uniqueProducts.find(
        (p) => p.label === selectedProduct.label
      )
      state.container.product_id = selectedProduct.value
    }

    const { data, error } = await accountApi.getAccount()

    const cms_attributes = data.value.cms_attributes
    console.log(cms_attributes)
    state.container_colors =
      cms_attributes.container_colors != undefined
        ? cms_attributes.container_colors.map((el) => {
            return { name: el, code: el }
          })
        : []

    state.cmsAttributes = cms_attributes
    const statuseKeys = Object.keys(state.cmsAttributes.inventory_status_list)
    state.container_statuses = statuseKeys
      .filter((e) => {
        return state.cmsAttributes.inventory_status_list[e]
      })
      .map((e) => {
        return { name: e, code: e }
      })
  })
  const capitalizeFirst = (s) => s && s[0].toUpperCase() + s.slice(1)

  const emptyContainer = {
    type: inventoryService.defaultContainerType,
    container_number: null,
    container_release_number: null,
    vendor_id: "",
    depot_id: "",
    total_cost: null,
    container_size: "",
    product_id: "",
    condition: "",
    days_in_yard: 0,
    rental_periods_count: 0,
    door_type: [],
    height_type: [],
    container_color: null,
    image_urls: [],
    description: "",
    revenue: 0
  }

  const state = reactive({
    loading: false,
    quantity: 1,
    containerReleaseNumber: "",
    container: cloneDeep(emptyContainer),
    selectedCity: null,
    originalContainer: null,
    hasRelatedContainers: false,
    selectedCategory: { name: "Rental", code: "rental" },
    categorys: [
      { name: "Rental", code: "rental" },
      { name: "Rent to Own", code: "rto" },
      { name: "Sale", code: "purchase" },
      { name: "All", code: "all" }
    ],
    displayTypes: [],
    container_colors: [],
    container_statuses: [],
    cmsAttributes: null,
    container_images_on_update: []
  })
  const hasRelatedContainers = (status) => {
    state.hasRelatedContainers = status
  }
  const rules = computed(() => ({
    container: {
      container_release_number: { required, $lazy: true },
      total_cost: { required, $lazy: true },
      vendor_id: { required, $lazy: true },
      depot_id: { required, $lazy: true },
      product_id: { required, $lazy: true }
      //container_size: { required, $lazy: true },
      // type: { required, $lazy: true },
      //condition: { required, $lazy: true },
    }
  }))

  const v$ = useVuelidate(rules, state)

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
        (vendor) =>
          vendor.type == null || vendor.type.type == "SHIPPING_CONTAINER"
      )
      .map((v) => {
        return { label: v.name, value: v.id }
      })
      .sort((a, b) => a?.label?.localeCompare(b.label))
  })

  const mappedDepotCities = computed(() => {
    return depotStore.depots
      .map((depot) => {
        return {
          label: depot.city,
          value: depot.city
        }
      })
      .filter((depot, index, self) => {
        return self.findIndex((t) => t.value === depot.value) === index
      })
      .sort((a, b) => {
        const labelA = a.label || ""
        const labelB = b.label || ""
        labelA.localeCompare(labelB)
      })
  })

  const mappedDepots = computed(() => {
    if (containerProp?.id) {
      return depotStore.depots
        .map((depot) => {
          return {
            label: depot.name,
            value: depot.id
          }
        })
        .sort((a, b) => a.label.localeCompare(b.label))
    }
    return depotStore.depots
      .filter((d) => d.city === state.selectedCity)
      .map((depot) => {
        return {
          label: depot.name,
          value: depot.id
        }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const resetContainer = () => {
    let container = null
    if ($isObjectPopulated(containerProp)) {
      container = cloneDeep(containerProp)
    } else {
      container = emptyContainer
    }
    state.originalContainer = cloneDeep(container)
    state.container = cloneDeep(container)
    if (state.container.pickup_at) {
      state.container.pickup_at = new Date(state.container.pickup_at)
    }
    if (state.container.paid_at) {
      state.container.paid_at = new Date(state.container.paid_at)
    }

    if (state.container.invoiced_at) {
      state.container.invoiced_at = new Date(state.container.invoiced_at)
    }

    state.container.product_id = state.container.product?.id

    for (const key in container.type) {
      if (container.type.hasOwnProperty(key)) {
        const value = container.type[key]
        if (value === true) {
          let label = ""
          if (key == "high_cube") {
            label = "High Cube"
          } else if (key == "standard") {
            label = "Standard"
          } else if (key == "double_door") {
            label = "Double Door"
          }
          state.displayTypes.push({ value: key, label: label })
        }
      }
    }

    v$.value.$reset()
  }

  const createUpdateContainer = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    const obj = state.products.find(
      (obj) => obj["value"] == state.container.product_id
    )

    if (
      obj?.label?.includes("One-Trip") &&
      state.container.container_color == null &&
      state.container_colors.length > 0
    ) {
      toast.add({
        severity: "warn",
        summary: "Container color is mandatory",
        detail: "Container Color is mandatory for One-Trip containers",
        group: "br",
        life: 5000
      })
      return
    }

    state.loading = true
    console.log(state.container)
    if (!state.container.id && state.container.container_number != null) {
      //lets check if the container number is used
      let urlStr = `searchBy=CONTAINER_NUMBER&searchValue=${state.container.container_number.trim()}&searchStatus=All`
      const { error, data } = await inventoryApi.searchInventory(urlStr)
      if (error.value) {
        data.value = []
      }
      const returnedContainer = inventoryService
        .removeOtherInventory(
          "CONTAINER_NUMBER",
          state.container.container_number.trim(),
          data.value
        )
        .map((i) => inventoryService.orderToInventory(i))
        .flat(1)
        .filter((v, i, a) => a.findIndex((t) => t.id === v.id) === i)
        .map((container) => container.container_number)

      const inventory = returnedContainer.filter(
        (container_number) =>
          container_number.toLowerCase() ===
          state.container.container_number.trim().toLowerCase()
      )
      if (inventory.length !== 0) {
        toast.add({
          severity: "warn",
          summary: "Error",
          detail: "Sorry container number is already used",
          group: "br",
          life: 5000
        })
        state.loading = false
        return
      }
    }
    if (state.container.id) {
      let requestData = $removeUnusedProps(
        state.container,
        state.originalContainer
      )

      const displayTypes = state.displayTypes.map((obj) => obj["value"])
      console.log(
        cloneDeep(state.originalContainer.type),
        cloneDeep(displayTypes)
      )
      requestData.type = pricingService.convertDisplayAttributesToAttributes(
        cloneDeep(state.originalContainer.type),
        cloneDeep(displayTypes)
      )
      delete requestData.displayTypes

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "Container Unchanged",
          detail: "Container Unchanged",
          group: "br",
          life: 5000
        })
        return
      }
      if (
        state.container?.image_urls &&
        state.container?.image_urls?.length > 0
      ) {
        requestData.image_urls = [
          ...state.container.image_urls,
          ...state.container_images_on_update
        ]
      } else {
        requestData.image_urls = state.container_images_on_update
      }
      const { data, error } = await inventoryApi.updateInventory(
        state.container.id,
        requestData
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Container Updated",
          detail: "Successfully updated container",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating container",
          group: "br",
          life: 5000
        })
      }

      if (shouldSwap) {
        await inventoryService.swapInventory(data.value.id, status, "Edit")
      } else {
        swapOldContainer(data.value)
      }
      await resetFunction()
    } else {
      const displayTypes = state.displayTypes.map((obj) => obj["value"])

      state.container.type =
        pricingService.convertDisplayAttributesToAttributes(
          cloneDeep(state.container.type),
          cloneDeep(displayTypes)
        )
      if (isAttaching) {
        state.container.status = "Attached"
      }
      state.container.quantity = state.quantity
      if (state.container.image_urls && state.container.image_urls.length > 0) {
        state.container.image_urls = [
          ...state.container.image_urls,
          ...state.container_images_on_update
        ]
      } else {
        state.container.image_urls = state.container_images_on_update
      }

      const { data, error } = await inventoryApi.createInventory(
        state.container
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Container Saved",
          detail: "Successfully saved container",
          group: "br",
          life: 5000
        })
      } else if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail:
            error?.value?.response?.data?.detail || "Error saving container",
          group: "br",
          life: 5000
        })
      }

      if (isAttaching) {
        state.loading = true
        emit("containerAttached", data.value[0])
      }
      if (state.container.quantity <= 1) {
        if (shouldSwap) {
          await inventoryService.swapInventory(
            data.value[0].id,
            status,
            "Create"
          )
        }

        state.container = cloneDeep(emptyContainer)
      } else {
        await resetFunction()
      }
      // resetContainer();
    }
    state.loading = false
    emit("hide")
  }

  const updadeContainerReleaseNumber = () => {
    state.containerReleaseNumber = state.container.container_release_number
  }
</script>

<style></style>
