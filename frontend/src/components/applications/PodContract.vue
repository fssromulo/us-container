<template>
  <div v-if="props.contractResponse == null && props.podSigned">
    <div class="flex flex-col items-center">
      We emailed it to you on {{ props.oldSignedDate }}. Please check your
      email. If you do not have a copy emailed to you, please email us at
      cod@usacontainers.co and ask for a copy of the contract
    </div>
  </div>
  <div v-else-if="isObjectPopulated(updatedSchema)">
    <div class="flex flex-col items-end" v-if="props.podSigned">
      <Button @click="print" class="p-button-sm p-button-rounded">Print</Button>
    </div>
    <div class="grid ml-5 mr-5" id="generatedContract">
      <FormKit
        type="form"
        :actions="false"
        id="application-form"
        ref="myApplication"
        #default="{ state: { valid } }"
        v-model="fileData"
        @submit="submitHandler"
      >
        <div class="grid">
          <FormKitSchema :schema="updatedSchema" :data="fileData" />
        </div>
      </FormKit>

      <div
        v-html="
          props.podSigned
            ? props.contractResponse?.response_content?.contract
            : props.podContract.contract
        "
        class="mt-4 col-12"
      ></div>
      <div class="text-center col-12">
        <hr />
        <Button
          label="Terms Read, Understood and Accepted Place My Order"
          class="mt-3 row p-button-secondary p-button-lg"
          v-if="!props.podSigned"
          @click="submitForm"
          :loading="state.loading"
          style="max-width: 320px"
        ></Button>
        <div v-else class="flex flex-col items-center">
          <strong style="font-size: 30px"
            >Contract Signed On {{ computedDate }}</strong
          >
          <p style="font-family: 'Brush Script MT', cursive; font-size: 26px">{{
            state.printedName
          }}</p>
        </div>
      </div>
    </div>

    <Dialog
      v-model:visible="state.applicationSubmitedSuccessfully"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Contract signed successfully"
      :modal="true"
      class="p-fluid"
    >
      &#x2713; You have successfully signed the POD Contract. &#x2713; <br />
      Please watch out for further communication from us. <br />
      For any questions, please email cod@usacontainers.co.
    </Dialog>
  </div>
</template>

<script setup>
  import {
    ref,
    reactive,
    inject,
    markRaw,
    watch,
    computed,
    onMounted
  } from "vue"
  import CustomerApi from "@/api/customers"
  import UploadApi from "@/api/upload.js" // Import the UploadApi class
  import FileUploader from "./FileUploader.js"
  import rentalApplicationSchema from "./rentalApplicationSchema.json"
  import { usePaperizer } from "paperizer"

  const fileData = reactive({})
  const callback = () => {
    // console.log("Printing");
  }
  const myApplication = ref(null)
  // <FileUpload mode="basic" name="{{name}}" accept="image/*" :maxFileSize="1000000" />
  const { paperize } = usePaperizer(
    "generatedContract",
    { styles: ["https://cdn.tailwindcss.com"] },
    callback
  )
  const computedDate = computed(() => {
    const date = new Date(props.oldSignedDate)
    return date.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric"
    })
  })

  const $route = inject("$route")
  styles: ["/style/rental_statement_style.css"]
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
  const print = () => {
    paperize()
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
    filteredData.date = props.podContractFields.date
    filteredData.to = props.podContractFields.fullname
    filteredData.address = props.podContractFields.address
    filteredData.invoice = props.podContractFields.invoice
    filteredData.qty = props.podContractFields.qty_size
    filteredData.price = props.podContractFields.invoice_price
    filteredData.contract = props.podContract.contract

    console.log(filteredData)
    const isValid = Object.values(filteredData).every((value) => {
      console.log(value)
      return value !== "" && value !== null && value !== undefined
    })
    if (!isValid) {
      toast.add({
        severity: "error",
        summary: "Error",
        group: "br",
        detail: "All fields on this contract are required!",
        life: 3000
      })
      state.loading = false
      return
    }

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
    }

    console.log("Creating application for customer")
    await customerApi.publicSignPodContract(props.orderId, app)
    console.log("Customer application created")
    toast.add({
      severity: "success",
      summary: "Success",
      group: "br",
      detail: "Contract Signed Submitted!",
      life: 3000
    })
    state.applicationSubmitedSuccessfully = true

    state.loading = false
    setTimeout(function () {
      window.location.reload()
    }, 3000)
  }

  const props = defineProps({
    oldSignedDate: {
      type: String,
      default: ""
    },
    contractSignedOn: {
      type: String,
      default: ""
    },
    contractResponse: {
      type: Object,
      default: {}
    },
    podContractFields: {
      type: Object,
      default: {}
    },
    podContract: {
      type: Object,
      default: {}
    },
    podSigned: {
      type: Boolean,
      default: false
    },
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
    applicationSubmitedSuccessfully: false,
    printedName: ""
  })

  const updatedSchema = computed(() => {
    let updatedSchema = props.selectedSchema.map((f) => {
      if (props.podSigned) {
        if (f.value == "to_holder") {
          f.children[0] = "To: " + props.contractResponse?.response_content?.to
        }
        if (f.value == "address_holder") {
          f.children[0] =
            "Delivery Address: " +
            props.contractResponse?.response_content?.address
        }
        if (f.value == "invoice_number_holder") {
          f.children[0] =
            "USA Container Invoice: " +
            props.contractResponse?.response_content?.invoice
        }
        if (f.value == "container_holder") {
          f.attrs["style"] = "margin-bottom: 2rem;"
          f.children[0] =
            "Container Size & Qty: " +
            props.contractResponse?.response_content?.qty
        }
        if (f.value == "invoice_price_holder") {
          f.children[0] =
            "Invoice Price: " + props.contractResponse?.response_content?.price
        }
        if (f.value == "date_holder") {
          f.children[0] =
            "Date: " + props.contractResponse?.response_content?.date
        }
        // Prefill fields and disable them
        if (f.value == "confirmation_address_street") {
          f.attrs["style"] = "font-weight: bold;"
          f.children[0] =
            "Confirm Delivery Address (Street Address): " +
            props.contractResponse?.response_content
              ?.confirmation_address_street
        }
        if (f.value == "confirmation_address_city_state_zipcode") {
          f.attrs["style"] = "font-weight: bold;"
          f.children[0] =
            "Confirm Delivery Address (City, State, Zip Code): " +
            props.contractResponse?.response_content
              ?.confirmation_address_city_state_zipcode
        }
        if (f.value == "printed_name") {
          f.attrs["style"] = "font-weight: bold;"
          f.children[0] =
            "Printed Name: " +
            props.contractResponse?.response_content?.printed_name
          state.printedName =
            props.contractResponse?.response_content?.printed_name
        }
        if (f.value == "printed_phone_number") {
          f.attrs["style"] = "font-weight: bold;"
          f.children[0] =
            "Phone Number: " +
            props.contractResponse?.response_content?.phone_number
        }
        if (f.value == "printed_email_address") {
          f.attrs["style"] = "font-weight: bold;"
          f.children[0] =
            "E-Mail Address: " +
            props.contractResponse?.response_content?.email_address
        }
        if (f.value == "printed_date") {
          f.attrs["style"] = "font-weight: bold;"
          f.children[0] =
            "Date: " + props.contractResponse?.response_content?.date
        }
        if (f.value == "auth_rep_signature") {
          f.children[0] = ""
        }
      } else {
        if (f.value == "to_holder") {
          f.children[0] = "To : " + props.podContractFields.fullname
        }
        if (f.value == "address_holder") {
          f.children[0] = "Delivery Address: " + props.podContractFields.address
        }
        if (f.value == "invoice_number_holder") {
          f.children[0] =
            "USA Container Invoice: " + props.podContractFields.invoice
        }
        if (f.value == "container_holder") {
          f.children[0] =
            "Container Size & Qty: " + props.podContractFields.qty_size
        }
        if (f.value == "invoice_price_holder") {
          f.children[0] =
            "Invoice Price: " + props.podContractFields.invoice_price
        }

        if (f.value == "date_holder") {
          f.children[0] = "Date: " + props.podContractFields.date
        }
        const date = new Date(props.podContractFields.date)
        // Prefill fields
        if (f.value == "printed_name") {
          f.children[0].value = "" + props.podContractFields.customer?.full_name
        }
        if (f.value == "printed_phone_number") {
          f.children[0].value = "" + props.podContractFields.customer?.phone
        }
        if (f.value == "printed_email_address") {
          f.children[0].value = "" + props.podContractFields.customer?.email
        }
        if (f.value == "printed_date") {
          f.children[0].value = date.toLocaleDateString()
        }
      }
      return f
    })
    return updatedSchema
  })
  onMounted(() => {})
</script>
<style scoped>
  /* write me a class to style file upload component */

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
