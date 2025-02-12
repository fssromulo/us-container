<template>
  <div class="grid grid-cols-12 gap-2">
    <div class="col-span-12 md:col-span-7">
      <div class="grid grid-cols-12 gap-4 p-fluid">
        <div
          v-if="$isObjectPopulated(accessoryPriceProp)"
          class="col-span-12 mb-2 text-2xl"
        >
          {{ state.accessory.title }}
        </div>
        <div class="col-span-12 mb-4 field md:col-span-6">
          <label for="description" class="font-medium text-900 dark:text-0"
            >Product Category</label
          >
          <Select
            placeholder="Select Category"
            :options="state.productTypes"
            v-model="state.accessory.product_category_id"
            class="p-component p-inputtext-fluid"
            id="condition"
            type="text"
            optionLabel="label"
            optionValue="value"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-6">
          <label for="description" class="font-medium text-900 dark:text-0"
            >Product Name</label
          >
          <InputText
            placeholder="Accessory Name"
            v-model="state.accessory.name"
            class="p-inputtext p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 border border-t opacity-50"></div>
        <div class="col-span-12 mb-4 field md:col-span-6">
          <label for="description" class="font-medium text-900 dark:text-0"
            >Product Price</label
          >
          <InputNumber
            mode="currency"
            currency="USD"
            placeholder="Price"
            class="w-full"
            v-model="state.accessory.price"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-6">
          <label for="description" class="font-medium text-900 dark:text-0"
            >Shiping Time (ex. 10 - 15 days)</label
          >
          <InputText
            placeholder="Shipping time"
            v-model="state.accessory.shipping_time"
            class="p-inputtext p-component p-inputtext-fluid"
            id="monthly_price"
            type="text"
          />
        </div>
        <div class="col-span-12 text-xl font-medium text-900 dark:text-0"
          >Product Link</div
        >
        <div class="col-span-12 mb-2 field md:col-span-12">
          <Textarea
            placeholder="Product Link"
            v-model="state.accessory.product_link"
            class="p-inputtext p-component p-inputtext-fluid"
            id="monthly_price"
            :autoResize="true"
            ::rows="1"
          ></Textarea>
        </div>
      </div>
      <div class="grid grid-cols-12 gap-4 my-8 mt-1 mb-2">
        <span class="col-span-2 font-medium text-900 dark:text-0">{{
          state.accessory.in_stock ? "In Stock" : "Out Of Stock"
        }}</span>
        <ToggleSwitch class="col-span-6" v-model="state.accessory.in_stock" />
      </div>
      <div class="col-span-6 mb-4 field">
        <label for="description" class="font-medium text-900 dark:text-0"
          >Description</label
        >
        <Textarea
          v-model="state.accessory.description"
          id="description"
          :autoResize="true"
          class="p-inputtext p-component p-inputtext-fluid"
          ::rows="5"
        ></Textarea>
      </div>
      <div class="col-span-12 mb-4 border border-t opacity-50"></div>
    </div>
    <div class="col-span-12 md:col-span-5">
      <FileUpload
        v-if="!productImage || productImage == null || state.changeProduceImage"
        name="demo"
        url="/api/upload"
        @upload="onTemplatedUpload($event)"
        :multiple="false"
        accept="image/*"
        :maxFileSize="1000000"
        @select="onSelectedFile"
      >
        <template
          #header="{ chooseCallback, uploadCallback, clearCallback, files }"
        >
          <div class="flex flex-wrap items-center justify-between flex-1 gap-4">
            <div class="flex gap-2">
              <Button
                @click="chooseCallback()"
                icon="pi pi-image"
                rounded
                outlined
                severity="secondary"
              ></Button>
              <!-- <Button @click="uploadEvent(uploadCallback)" icon="pi pi-cloud-upload" rounded outlined severity="success" :disabled="!file" />
                        <Button @click="clearCallback()" icon="pi pi-times" rounded outlined severity="danger" :disabled="!file" /> -->
            </div>
            <ProgressBar
              :value="totalSizePercent"
              :showValue="false"
              class="w-full h-1 md:w-20rem md:ml-auto"
            >
              <span class="whitespace-nowrap">{{ totalSize }}B / 1Mb</span>
            </ProgressBar>
          </div>
        </template>
        <template
          #content="{
            files,
            uploadedFiles,
            removeUploadedFileCallback,
            removeFileCallback
          }"
        >
          <div class="flex flex-col gap-8 pt-4">
            <div v-if="file">
              <h5>Selected File</h5>
              <div
                class="flex flex-col items-center gap-4 p-8 border rounded-border border-surface"
              >
                <div>
                  <img
                    role="presentation"
                    :alt="file.name"
                    :src="file.objectURL"
                    width="100"
                    height="50"
                  />
                </div>
                <span
                  class="overflow-hidden font-semibold text-ellipsis max-w-60 whitespace-nowrap"
                  >{{ file.name }}</span
                >
                <div>{{ formatSize(file.size) }}</div>
                <Badge value="Pending" severity="warn" />
                <Button
                  icon="pi pi-times"
                  @click="onRemoveFile(removeFileCallback)"
                  outlined
                  rounded
                  severity="danger"
                />
              </div>
            </div>

            <div v-if="uploadedFile">
              <h5>Uploaded File</h5>
              <div
                class="flex flex-col items-center gap-4 p-8 border rounded-border border-surface"
              >
                <div>
                  <img
                    role="presentation"
                    :alt="uploadedFile.name"
                    :src="uploadedFile.objectURL"
                    width="100"
                    height="50"
                  />
                </div>
                <span
                  class="overflow-hidden font-semibold text-ellipsis max-w-60 whitespace-nowrap"
                  >{{ uploadedFile.name }}</span
                >
                <div>{{ formatSize(uploadedFile.size) }}</div>
                <Badge value="Completed" class="mt-4" severity="success" />
              </div>
            </div>
          </div>
        </template>
        <template #empty>
          <div class="flex flex-col items-center justify-center">
            <i
              class="pi pi-cloud-upload !border-2 !rounded-full !p-8 !text-4xl !text-muted-color"
            />
            <p class="mt-6 mb-0">Drag and drop a file here to upload.</p>
          </div>
        </template>
      </FileUpload>
      <div v-else class="flex flex-wrap item-center">
        <label for="description" class="w-full font-medium text-900 dark:text-0"
          >Product Image</label
        >
        <img :src="productImage" class="m-5" style="max-width: 100px" />
      </div>
      <Button
        v-if="
          state.accessory.id &&
          productImage &&
          productImage != null &&
          !state.changeProduceImage
        "
        icon="pi pi-trash text-sm"
        class="mr-5"
        :disabled="state.loading"
        @click="deleteAccessoryImage"
      ></Button>

      <Button
        v-if="state.accessory.id && productImage && productImage != null"
        :label="state.changeProduceImage ? 'Cancel' : 'Update Image'"
        @click="state.changeProduceImage = !state.changeProduceImage"
        icon="pi pi-file"
        class="w-2/3"
        :disabled="state.loading"
      ></Button>
    </div>
    <div class="col-span-12">
      <Button
        :label="
          $isObjectPopulated(accessoryPriceProp)
            ? 'Update Accessory'
            : 'Create Accessory'
        "
        @click="createUpdateAccessory"
        icon="pi pi-file"
        class="w-full"
        :loading="state.loading"
      ></Button>
    </div>
  </div>
</template>

<script setup>
  import {
    reactive,
    computed,
    onMounted,
    inject,
    defineEmits,
    ref,
    watch
  } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"

  import PricingService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import InventoryService from "@/service/Inventory"

  import { useToast } from "primevue/usetoast"
  import { useContainerPrices } from "@/store/modules/pricing"
  import { usePrimeVue } from "primevue/config"
  import UploadApi from "@/api/upload.js" // Import the UploadApi class

  const toast = useToast()

  const pricingService = new PricingService()
  const pricingApi = new PricingApi()
  const pricingStore = useContainerPrices()
  const inventoryService = new InventoryService()
  const uploadApi = new UploadApi()

  const stateService = new StateService()

  const $primevue = usePrimeVue()
  const totalSize = ref(0)
  const totalSizePercent = ref(0)
  const file = ref(null)
  const uploadedFile = ref(null)
  const files = ref([])

  const { accessoryPriceProp } = defineProps({
    accessoryPriceProp: {
      type: Object,
      default: () => ({})
    }
  })

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const swapOldAccessory = (updatedAccessory) => {
    const index = cloneDeep(pricingStore.accessoryPrices)
      .map((u) => u.id)
      .indexOf(updatedAccessory.id)
    let clonedAccessories = cloneDeep(pricingStore.accessoryPrices)
    clonedAccessories[index] =
      pricingService.dtoProductPricing(updatedAccessory)
    pricingStore.setAccessoryPrices(clonedAccessories)
  }

  const loadAccessoryImage = async () => {
    if (state.accessory.id && state.accessory.file_upload.length > 0) {
      const { data } = await uploadApi.getPresignedGetUrl(
        state.accessory.file_upload[0].filename,
        state.accessory.file_upload[0].folder_type,
        state.accessory.account_id,
        null,
        state.accessory.id
      )
      state.accessory.image_link = data.value
    } else {
      state.accessory.image_link = null
    }
  }
  onMounted(async () => {
    state.statesList = stateService.getStates()
    resetAccessory()
    await loadAccessoryImage()
  })

  const emptyAccessory = {
    in_stock: false,
    shipping_time: "",
    product_link: "",
    product_category_id: pricingStore.productCategories[0]?.id,
    price: "",
    description: "",
    name: ""
  }

  const state = reactive({
    loading: false,
    changeProduceImage: false,
    accessory: cloneDeep(emptyAccessory),
    originalAccessory: null,
    isRental: false,
    productTypes: pricingStore.productCategories.map((category) => {
      return {
        label: category.name,
        value: category.id
      }
    })
  })
  const productImage = computed(() => {
    return state.accessory.image_link
  })
  const rules = computed(() => ({
    accessory: {
      name: { required, $lazy: true },
      price: { required, $lazy: true },
      product_link: { required, $lazy: true },
      shipping_time: { required, $lazy: true },
      product_category_id: { required, $lazy: true }
    }
  }))

  const v$ = useVuelidate(rules, state)

  const resetAccessory = () => {
    let accessory = null
    if ($isObjectPopulated(accessoryPriceProp)) {
      accessory = cloneDeep(accessoryPriceProp)
    } else {
      accessory = emptyAccessory
    }
    state.originalAccessory = cloneDeep(accessory)
    state.accessory = cloneDeep(accessory)

    v$.value.$reset()
  }

  const createUpdateAccessory = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      toast.add({
        severity: "warn",
        summary: "Error",
        detail: "All fields are required",
        group: "br",
        life: 5000
      })
      return
    }
    state.loading = true
    try {
      if (state.accessory.id) {
        await updateAccessory()
      } else {
        await createAccessory()
      }
      state.loading = false
      emit("hide")
    } catch (e) {
      console.log(e)
      state.loading = false
      toast.add({
        severity: "warn",
        summary: "Error",
        detail: "Error saving accessory",
        group: "br",
        life: 5000
      })
      return
    }
  }

  const createAccessory = async () => {
    const newProduct = await pricingApi.createProduct(state.accessory)
    if (file.value != null && newProduct.data.value) {
      await uploadFile(
        newProduct.data.value.id,
        newProduct.data.value.account_id
      )
    }
    const { data } = await pricingApi.getProduct()
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Accessory Saved",
        detail: "Successfully saved accessory",
        group: "br",
        life: 5000
      })
    }
    const prices = data.value.map((p) => pricingService.dtoProductPricing(p))
    pricingStore.setAccessoryPrices(prices)
    resetAccessory()
    await loadAccessoryImage()
  }
  const updateAccessory = async () => {
    if (file.value != null) {
      if (state.accessory.file_upload.length > 0) {
        await updateFile(
          state.accessory.id,
          state.accessory.account_id,
          state.accessory.file_upload[0].id
        )
      } else {
        await uploadFile(state.accessory.id, state.accessory.account_id)
      }
    }
    let requestData = $removeUnusedProps(
      cloneDeep(state.accessory),
      cloneDeep(state.originalAccessory)
    )

    if (!$isObjectPopulated(requestData)) {
      toast.add({
        severity: "warn",
        summary: "Accessory Unchanged",
        detail: "Accessory Unchanged",
        group: "br",
        life: 5000
      })
      return
    }

    const { data, error } = await pricingApi.updateProduct(
      state.accessory.id,
      requestData
    )
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Accessory Price Updated",
        detail: "Successfully updated accessory",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error updating accessory price",
        group: "br",
        life: 5000
      })
    }
    swapOldAccessory(data.value)
  }

  const deleteAccessoryImage = async () => {
    state.loading = true
    await uploadApi.deleteExistingFile(
      state.accessory.file_upload[0].id,
      state.accessory.account_id
    )
    const { data, error } = await pricingApi.getProduct()
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Accessory Image Updated",
        detail: "Successfully updated accessory",
        group: "br",
        life: 5000
      })
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error deleting accessory image",
        group: "br",
        life: 5000
      })
    }
    const prices = data.value.map((p) => pricingService.dtoProductPricing(p))
    pricingStore.setAccessoryPrices(prices)
    resetAccessory()
    state.loading = false
  }
  //TODO file upload

  const onRemoveFile = (removeFileCallback) => {
    removeFileCallback()
    file.value = null
    totalSize.value = 0
    files.value = []
    totalSizePercent.value = 0
  }

  const onSelectedFile = (event) => {
    file.value = event.files[0]
    files.value = [file.value]
    totalSize.value = parseInt(formatSize(file.value.size))
  }

  const uploadFile = async (productId, accountId) => {
    await uploadApi.sendToS3(
      file.value.name,
      file.value,
      file.value.type,
      "product_image",
      accountId,
      null,
      productId
    )
  }

  const updateFile = async (productId, accountId, existingId) => {
    await uploadApi.sendUpdateToS3(
      file.value.name,
      file.value,
      file.value.type,
      "product_image",
      accountId,
      null,
      productId,
      existingId
    )
  }

  const onTemplatedUpload = () => {
    uploadedFile.value = file.value
    file.value = null
    toast.add({
      severity: "info",
      summary: "Success",
      detail: "File Uploaded",
      life: 3000
    })
  }

  const formatSize = (bytes) => {
    const k = 1024
    const dm = 3
    const sizes = $primevue.config.locale.fileSizeTypes

    if (bytes === 0) {
      return `0 ${sizes[0]}`
    }

    const i = Math.floor(Math.log(bytes) / Math.log(k))
    const formattedSize = parseFloat((bytes / Math.pow(k, i)).toFixed(dm))

    return `${formattedSize} ${sizes[i]}`
  }

  watch(
    () => state.changeProduceImage,
    async (newVal, oldVal) => {
      if (newVal == false) {
        file.value = null
      }
    }
  )
</script>

<style></style>
