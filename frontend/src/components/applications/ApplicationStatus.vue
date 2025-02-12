<template>
  <div class="pb-8 mt-4" v-if="application">
    <div v-if="props.manualApplication == false" class="mt-2">
      <p class="text-2xl font-semibold">Application & Contract Status</p>
    </div>
    <div
      v-if="props.manualApplication == false"
      class="mt-4 mb-4 overflow-x-auto bg-white rounded-lg shadow-md ring-1 ring-black ring-opacity-5"
    >
      <DataTable :value="contractAndApplicationHistory" class="w-full">
        <Column field="name" header="Application Name" />
        <Column field="date" header="Date" />
        <Column field="event" header="Event" />
      </DataTable>
    </div>
    <div
      v-if="
        $ability.can('update', 'rental_application_photo') &&
        props.manualApplication == true
      "
      class="mt-4"
    >
      <h3 class="mb-1 text-xl font-bold mr-">Upload Offline Application</h3>
      <FormKit
        type="form"
        :actions="false"
        id="application-form"
        ref="myApplication"
        v-model="fileData"
        @submit="submitHandler"
        class="space-y-6"
      >
        <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
          <FormKitSchema :schema="state.schema" :data="fileData" />
        </div>
      </FormKit>
      <div class="flex justify-center">
        <Button
          label="Submit Photo"
          class="p-button-rounded p-button-success p-button-lg"
          @click="submitForm"
          :loading="state.loading"
        ></Button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, computed, ref, inject } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import { dfl } from "@/service/DateFormat.js"
  import UploadApi from "@/api/upload.js" // Import the UploadApi class
  import basicFileUpload from "./basicFileUpload.json"
  import { useUsers } from "@/store/modules/users"
  const $ability = inject("$ability")

  const uploadApi = new UploadApi()

  const selectedFiles = ref([])
  const file = ref()
  const fileData = reactive({})

  const toast = useToast()
  const customerStore = useCustomerOrder()

  const userStore = useUsers()

  const props = defineProps({
    response: { type: Object, default: {} },
    resetFunction: {
      type: Function,
      default: () => {}
    },
    manualApplication: {
      type: Boolean,
      default: false
    },
    allResponses: {
      type: Array,
      default: []
    }
  })

  const submitHandler = async (data) => {
    state.loading = true
    let accountId = userStore?.cms?.account_id

    console.log(userStore?.cms)
    let filteredData = Object.fromEntries(
      Object.entries(data).filter(([k, v]) => !Array.isArray(v))
    )
    delete filteredData?.slots

    // filter the opposite of the above
    let files = Object.fromEntries(
      Object.entries(fileData).filter(([k, v]) => Array.isArray(v))
    )

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
      const orderId = customerStore.order.id

      uploadPromises.push(
        uploadApi.sendToS3(
          fileData.name,
          fileData.file,
          contentType,
          folderType,
          accountId,
          orderId,
          null,
          callback
        )
      )
    }

    try {
      await Promise.all(uploadPromises)
      state.loading = false
    } catch (e) {
      console.log(e)
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
  }

  const callback = () => {
    state.loading = false
    props.resetFunction()
  }

  const myApplication = ref(null)

  function submitForm() {
    // retrieve the core node (several ways to do this):
    const node = myApplication.value.node
    // submit the form!
    node.submit()
  }

  const application = computed(() => {
    // sort keys by first word
    let sortedObject = {}

    if (props.response?.response_content) {
      const sortedKeys = Object.keys(props.response.response_content).sort(
        (a, b) => {
          return a.split(" ")[0].localeCompare(b.split(" ")[0])
        }
      )
      sortedKeys.forEach((k) => {
        sortedObject[k] = props.response?.response_content[k]
      })
    }
    // put first name and last name keys at front of object
    if (sortedObject["first name"]) {
      const firstName = sortedObject["first name"]
      delete sortedObject["first name"]
      sortedObject["first name"] = firstName
    }

    return sortedObject
  })

  const contractAndApplicationHistory = computed(() => {
    let applicationStatuses = []
    let orderContacts = []
    if (props.allResponses.length > 0) {
      props.allResponses.forEach((res) => {
        applicationStatuses.push({
          date: dfl(res?.created_at),
          event: "Application Submitted",
          name: res?.customer_application_schema.full_schema_name
        })
        if (res?.date_accepted) {
          applicationStatuses.push({
            date: dfl(res?.date_accepted),
            event: "Application Accepted",
            name: res?.customer_application_schema.full_schema_name
          })
        }
        if (res?.date_rejected) {
          applicationStatuses.push({
            date: dfl(res?.date_rejected),
            event: "Application Rejected",
            name: res?.customer_application_schema.full_schema_name
          })
        }
      })
    }
    if (customerStore.order?.order_contract?.length) {
      orderContacts = customerStore.order?.order_contract.map((c) => {
        return {
          date: dfl(c.created_at),
          event: convertToSpacedAndCapitalized(c.status),
          name: ""
        }
      })
    }

    return [...applicationStatuses, ...orderContacts]
  })

  const convertToSpacedAndCapitalized = (inputString) => {
    // Split the string into an array of words
    const words = inputString.split("-")

    // Capitalize the first letter of each word and join them with a space
    const result = words
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")

    return result
  }

  const state = reactive({
    loadingAccepted: false,
    loadingDeclined: false,
    cmsId: null,
    updateKey: 0,
    schema: basicFileUpload
  })

  const responsiveOptions = ref([
    {
      breakpoint: "1199px",
      numVisible: 1,
      numScroll: 1
    },
    {
      breakpoint: "991px",
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: "767px",
      numVisible: 1,
      numScroll: 1
    }
  ])
</script>

<style>
  .formkit-wrapper label {
    text-align: right;
    clear: both;
    float: left;
    margin-right: 15px;
  }
</style>
