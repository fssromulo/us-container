<template>
  <div class="" v-if="application || photoUploads">
    <div class="mt-2">
      <p class="text-3xl text-center">Application</p>
    </div>

    <div>
      <p class="text-2xl text-center">
        {{ state.mappedPhotos.length ? "Photos" : "No photos" }}
      </p>
    </div>

    <div class="grid grid-cols-12 gap-4 mt-2 ml-2">
      <table
        class="col-span-6"
        style="display: inline-block; margin-bottom: 1rem"
      >
        <tbody>
          <tr
            v-for="(key, value, index) in Object.entries(application).slice(
              0,
              Math.ceil(Object.keys(application).length / 2)
            )"
            style="height: 2rem"
          >
            <td class="text-xl text-700 dark:text-100">
              {{ convertFromSnakeCase(key[0]) }}
            </td>
            <td
              style="min-width: 14rem"
              class="ml-12 text-xl text-900 dark:text-0"
            >
              {{ key[1] }}
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Bottom table for the second half of keys -->
      <table class="col-span-6" style="display: inline-block">
        <tbody>
          <tr
            v-for="(key, value, index) in Object.entries(application).slice(
              Math.ceil(Object.keys(application).length / 2)
            )"
            style="height: 2rem"
          >
            <td class="text-xl text-700 dark:text-100">
              {{ convertFromSnakeCase(key[0]) }}
            </td>
            <td
              style="min-width: 14rem"
              class="ml-12 text-xl text-900 dark:text-0"
            >
              {{ key[1] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
      v-if="
        !applicationAcceptedRejected &&
        $ability.can('update', 'rental_approve_reject_application')
      "
      class="grid justify-center grid-cols-12 gap-4 mt-2 d-flex"
    >
      <div class="field">
        <Button
          class="p-button-rounded p-button-success p-button-lg"
          label="Approve"
          :loading="state.loadingAccepted"
          @click="acceptApplication(true)"
        />
      </div>
      <div class="ml-8 field">
        <Button
          class="p-button-rounded p-button-warning p-button-lg"
          label="Decline"
          :loading="state.loadingDeclined"
          @click="acceptApplication(false)"
        />
      </div>
    </div>

    <div v-if="applicationAccepted" class="grid grid-cols-12 gap-2 mt-2">
      <div
        class="col-span-7 col-start-1 field"
        v-if="$ability.can('update', 'rental_authorization_form')"
      >
        <div class="flex flex-col items-center">
          <Button
            class="m-2 p-button-rounded p-button-info p-button-lg"
            label="Send Authorization Form"
            :loading="state.authFormLoading['0'] || false"
            @click="sendAuthorizationForm()"
            v-if="usersStore.cms?.rent_options.is_have_authorization_form"
          />
          <Button
            class="m-2 p-button-rounded p-button-info p-button-lg"
            label="Send Authorization Form With Photo Upload"
            :loading="state.authFormLoading['1'] || false"
            @click="sendAuthorizationForm(true)"
            v-if="
              usersStore.integrations['esignatures.io']?.template_id
                ?.authorization_w_upload
            "
          />
        </div>
      </div>
      <div
        class="col-span-4 field"
        v-if="$ability.can('update', 'rental_main_contract')"
      >
        <Button
          class="p-button-rounded p-button-info p-button-lg"
          :label="sendMainContractTitle"
          :loading="state.mainContractLoading"
          @click="sendMainContract()"
        />
      </div>
      <Message
        @close="state.copiedLink = null"
        class="col-span-4"
        v-if="state.copiedLink"
        severity="info"
        >Link copied! Here it is {{ state.copiedLink }}</Message
      >
    </div>
    <div v-else class="mt-2 text-xl text-center">
      {{ applicationAcceptedRejectedMessage }}
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, computed, watch, ref, inject } from "vue"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import UploadApi from "@/api/upload.js" // Import the UploadApi class
  import { useToast } from "primevue/usetoast"
  import { dfl } from "@/service/DateFormat.js"
  import ContractApi from "@/api/contract.js"
  import { useUsers } from "@/store/modules/users"
  const $ability = inject("$ability")

  const props = defineProps({
    response: { type: Object, default: {} }
  })

  const toast = useToast()

  const uploadApi = new UploadApi()
  const customerStore = useCustomerOrder()
  const customerApi = new CustomerApi()
  const contractApi = new ContractApi()
  const usersStore = useUsers()

  const applicationAcceptedRejected = computed(() => {
    return props.response.date_rejected || props.response.date_accepted
  })

  const applicationRejected = computed(() => {
    return props.response.date_rejected
  })

  const applicationAccepted = computed(() => {
    return props.response.date_accepted
  })

  const applicationAcceptedRejectedMessage = computed(() => {
    if (props.response.date_rejected) {
      return `Application was rejected on ${dfl(props.response.date_rejected)}`
    }
    if (props.response.date_accepted) {
      return `Application was accepted on ${dfl(props.response.date_accepted)}`
    }
  })

  const sendMainContractTitle = computed(() => {
    if (customerStore.order?.type === "RENT") {
      return "Send Rental Contract"
    }
    if (customerStore.order?.type === "RENT_TO_OWN") {
      return "Send RTO Contract"
    }
    if (customerStore.order?.type === "PURCHASE") {
      return "Send Sales Contract"
    }
  })

  const application = computed(() => {
    // sort keys by first word
    let sortedObject = {}

    if (props.response?.response_content) {
      const sortedKeys = Object.keys(props.response?.response_content).sort(
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

  const photoUploads = computed(() => {
    if (customerStore.order?.file_upload) {
      return Array.isArray(customerStore.order?.file_upload)
        ? customerStore.order?.file_upload
        : [customerStore.order?.file_upload]
    }
    return []
  })

  const state = reactive({
    loadingAccepted: false,
    loadingDeclined: false,
    authFormLoading: [],
    mainContractLoading: false,
    cmsId: null,
    mappedPhotos: [],
    updateKey: 0,
    copiedLink: null
  })

  const setPhotos = async () => {
    if (customerStore.order?.file_upload && !state.mappedPhotos.length) {
      const uploads = Array.isArray(customerStore.order?.file_upload)
        ? customerStore.order?.file_upload
        : [customerStore.order?.file_upload]

      const promises = uploads.map((u) => {
        return uploadApi.getPresignedGetUrl(
          u.filename,
          u.folder_type,
          customerStore.order.account_id,
          customerStore.order.id,
          null
        )
      })
      Promise.all(promises).then((values) => {
        state.mappedPhotos = values.map((v, i) => {
          return {
            ...uploads[i],
            presigned_url: v.data.value
          }
        })
      })
    }
  }

  if (!state.mappedPhotos.length && customerStore.order?.file_upload) {
    setPhotos()
  }

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

  const convertFromSnakeCase = (k) => {
    if (typeof k === "object") {
      return
    }
    k = k.replace(/_/g, " ")
    k = k.replace(/\w\S*/g, function (txt) {
      if (["hq", "ein"].includes(txt)) return txt.toUpperCase()
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    })
    return k
  }

  const sendAuthorizationForm = async (form_with_upload = false) => {
    if (form_with_upload) state.authFormLoading[1] = true
    else state.authFormLoading[0] = true

    const response = await contractApi.sendAuthorizationForm(
      customerStore.order.id,
      form_with_upload
    )
    if (response.error.message) {
      toast.add({
        severity: "error",
        summary: "Error Sending Authorization Form",
        detail: response.error.message,
        life: 3000,
        group: "br"
      })
    } else {
      const sign_page_url = response.data._value.sign_page_url
      copyLinkToClipboard(sign_page_url)
      toast.add({
        severity: "success",
        summary: "Authorization Form Sent!",
        detail: "Customer has been emailed the authorization form",
        life: 3000,
        group: "br"
      })
    }
    if (form_with_upload) state.authFormLoading[1] = false
    else state.authFormLoading[0] = false
  }

  const copyLinkToClipboard = (sign_page_url) => {
    navigator.clipboard.writeText(sign_page_url).then(
      () => {
        state.copiedLink = sign_page_url
      },
      () => {}
    )
  }

  const sendMainContract = async () => {
    state.mainContractLoading = true
    const response = await contractApi.sendMainContract(customerStore.order.id)
    if (response.error.value) {
      toast.add({
        severity: "error",
        summary: "Error Sending Main Contract",
        detail: response.error.message,
        life: 3000,
        group: "br"
      })
    } else {
      if (response.data._value.sign_page_url) {
        const sign_page_url = response.data._value.sign_page_url
        copyLinkToClipboard(sign_page_url)
      }
      toast.add({
        severity: "success",
        summary: "Main Contract Sent!",
        detail: "Customer has been emailed the main contract",
        life: 3000,
        group: "br"
      })
    }
    state.mainContractLoading = false
  }

  const acceptApplication = async (accepted) => {
    state.loadingAccepted = accepted
    state.loadingDeclined = !accepted

    const requestBody = {
      accepted: accepted,
      order_id: customerStore.order.id,
      schema_id: props.response?.customer_application_schema.id
    }
    let updateOrderResposne
    const creditResponse = await customerApi.updateCreditApplication(
      props.response?.id,
      requestBody
    )

    if (creditResponse.error.value) {
      toast.add({
        severity: "error",
        summary: `Error ${accepted ? "Accepting" : "Declining"} Application`,
        detail: creditResponse.error.value.response.data.detail,
        life: 7000,
        group: "br"
      })
      state.loadingAccepted = false
      state.loadingDeclined = false
      return
    } else {
      toast.add({
        severity: "success",
        summary: `Application ${accepted ? "Accepted!" : "Declined :("} `,
        detail: "",
        life: 3000,
        group: "br"
      })

      if (accepted) {
        updateOrderResposne = await customerApi.updateOrder(
          customerStore.order.id,
          { status: "Approved" }
        )
      }

      if (updateOrderResposne?.data?.value) {
        customerStore.setOrder(updateOrderResposne.data.value)
      } else {
        customerStore.setOrder(creditResponse.data.value)
      }
    }
    state.loadingAccepted = false
    state.loadingDeclined = false
  }

  onMounted(async () => {
    await setPhotos()
  })

  watch(
    () => photoUploads.value,
    async () => {
      await setPhotos()
    }
  )

  watch(
    () => customerStore.order,
    async (newVal, oldVal) => {
      state.mappedPhotos = []
      setPhotos()
    }
  )
</script>
