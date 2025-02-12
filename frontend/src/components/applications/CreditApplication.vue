<template>
  <div>
    <div class="grid grid-cols-1 gap-4">
      <FormKit
        v-if="props.selectedSchema"
        type="form"
        :key="formKey"
        :actions="false"
        id="application-form"
        class="col-span-12"
        ref="myApplication"
        #default="{ state: { valid } }"
        v-model="fileData"
        @submit="submitHandler"
      >
        <div class="grid grid-cols-12 gap-4">
          <FormKitSchema
            v-if="props.selectedSchema"
            :schema="props.selectedSchema"
            :library="library"
            :data="fileData"
          />
        </div>
      </FormKit>
    </div>
    <div class="grid grid-cols-12 gap-4">
      <div class="col-span-12 text-center">
        <hr class="my-4" />

        <Button
          label="Submit Application"
          class="px-4 py-2 text-lg text-white bg-green-500 rounded-full hover:bg-green-600"
          @click="submitForm"
          :loading="state.loading"
          v-styleclass="{
            selector: '#popover-cart',
            leaveToClass: 'hidden',
            leaveActiveClass: 'animate-fadeout'
          }"
        ></Button>
      </div>
    </div>

    <Dialog
      v-model:visible="state.applicationSubmitedSuccessfully"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ width: '50rem' }"
      header="Application submitted successfully"
      :modal="true"
      class="p-fluid"
    >
      &#x2713; You have successfully submitted your application. &#x2713; <br />
      Please watch out for further communication from us within 1-2 business
      days. <br />
      For any questions, please email rentals@usacontainers.co.
    </Dialog>
  </div>
</template>

<script setup>
  import { ref, reactive, inject, markRaw, computed } from "vue"
  import CustomerApi from "@/api/customers"
  import UploadApi from "@/api/upload.js" // Import the UploadApi class
  import FileUploader from "./FileUploader.js"

  const fileData = reactive({})

  const LabelFileLinkComp = {
    props: ["label1", "link", "label2", "label3", "name"],
    template: `
    <div>
      <label> {{ label1 }} <a :href="link"> {{ label2 }} </a> {{label3}}</label>
      <br />
      <FormKit
        type="file"
        multiple="false"
        :name="name"
        maxFileSize="1000000"
        accept=".jpg,.png,.pdf"
        validation="required"
      />
    </div>
  `
  }
  const myApplication = ref(null)
  // Assign the custom component a library
  // <FileUpload mode="basic" name="{{name}}" accept="image/*" :maxFileSize="1000000" />

  const library = markRaw({
    LabelFileLinkComp: LabelFileLinkComp
  })

  const formKey = computed(() => JSON.stringify(props.selectedSchema))

  const $route = inject("$route")
  const uploadApi = new UploadApi()

  import { useToast } from "primevue/usetoast"
  import isObjectPopulated from "../../utils/isObjectPopulated"
  const toast = useToast()

  const customerApi = new CustomerApi()
  function submitForm() {
    // retrieve the core node (several ways to do this):
    const node = myApplication.value.node
    // submit the form!
    node.submit()
  }

  const submitHandler = async (data) => {
    state.loading = true
    //doing this to avoid validation failed
    // data['same_as_billing'] = true

    // filter out any properties that have arrays
    let filteredData = Object.fromEntries(
      Object.entries(data).filter(([k, v]) => !Array.isArray(v))
    )
    delete filteredData?.slots

    // filter the opposite of the above
    let files = Object.fromEntries(
      Object.entries(fileData).filter(([k, v]) => Array.isArray(v))
    )

    const app = {
      response_content: JSON.stringify(filteredData),
      order_id: props.orderId,
      schema_id: props.selectedSchemaId
    }

    let uploadPromises = []

    // loop through the file data and upload each file
    for (const [key, value] of Object.entries(files)) {
      console.log(`${key}: ${value}`)
      if (value.length === 0) {
        continue
      }
      const fileData = files[key][0]

      if (!fileData.file) {
        continue
      }

      if (fileData.file.size > 4 * 1024 * 1024) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "File size too large, must be less than 4mb",
          life: 3000,
          group: "br"
        })
        continue
      }

      const folderType = key
      const contentType = fileData.file.type
      const orderId = $route.currentRoute.value.params.orderId

      uploadPromises.push(
        uploadApi.sendToS3(
          fileData.name,
          fileData.file,
          contentType,
          folderType,
          "2",
          orderId,
          null
        )
      )
    }

    try {
      await Promise.all(uploadPromises)
    } catch (e) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Cannot upload images.",
        life: 3000,
        group: "br"
      })
      return
    }

    await customerApi.createCustomerApplication(app)

    toast.add({
      severity: "success",
      summary: "Success",
      group: "br",
      detail: "Application Submitted!",
      life: 3000
    })
    state.applicationSubmitedSuccessfully = true

    state.loading = false
    setTimeout(function () {
      window.location.reload()
    }, 3000)
  }

  const props = defineProps({
    orderId: {
      type: String,
      required: true
    },
    selectedSchema: {
      type: Array,
      required: true,
      default: []
    },
    selectedSchemaId: {
      type: String,
      required: true,
      default: ""
    }
  })

  const state = reactive({
    loading: false,
    valid: false,
    applicationSubmitedSuccessfully: false
  })
</script>
<style scoped>
  input[type="file"] {
    display: none !important;
  }

  #dl_front {
    border: 1px solid #ccc;
    display: inline-block;
    padding: 6px 12px;
    cursor: pointer;
  }
  /* selector by  */
</style>
