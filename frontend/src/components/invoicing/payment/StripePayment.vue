<template>
  <div class="flex flex-col flex-auto">
    <div class="flex flex-col flex-auto">
      <div class="flex justify-center mt-4">
        <div class="" style="max-width: 800px">
          <form id="payment-form">
            <div id="payment-element">
              <!-- Stripe will create form elements here -->
            </div>
            <div class="flex flex-wrap justify-center mt-8 field-checkbox">
              <Button
                :label="payButton"
                style="max-width: 200px"
                type="submit"
                @click="handleSubmit"
                :loading="state.loading"
                v-if="state.stripeLoaded"
                class="p-button-primary p-button-rounded p-button-lg"
              ></Button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <Dialog
      v-model:visible="state.customerPaidDialog"
      :dismissableMask="true"
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Thank you for your payment!"
      :modal="true"
      class="p-fluid"
      @after-hide="afterHide"
      :breakpoints="{
        '2000px': '45vw',
        '1400px': '55vw',
        '1200px': '65vw',
        '992px': '75vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
    >
      <div class="ml-1 mr-1">{{ state.paymentMessage }}</div>
    </Dialog>
  </div>
</template>

<script setup>
  import { ref, onMounted, inject, reactive, computed } from "vue"
  import { useToast } from "primevue/usetoast"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"

  const toast = useToast()
  const customerApi = new CustomerApi()
  const customerOrderStore = useCustomerOrder()

  const $fc = inject("$formatCurrency")

  const props = defineProps({
    clientSecret: {
      type: String,
      default: ""
    },
    publicKey: {
      type: String,
      default: ""
    },
    orderToken: {
      type: String,
      default: ""
    },
    amountToPay: {
      default: 0.0
    },
    accountId: {
      default: 0
    },
    paymentIntentId: {
      type: String,
      default: ""
    }
  })

  const state = reactive({
    stripeLoaded: false,
    loading: false,
    status_retrieved: false,
    paymentMessage: "",
    customerPaidDialog: false
  })
  const token = ref(null)
  const stripe = ref(null)
  const elements = ref(null)
  const payButton = computed(() => {
    return !state.loading ? `Pay ${$fc(props.amountToPay)}` : "Please wait ..."
  })
  onMounted(() => {
    token.value = props.orderToken // Use to identify the payment
    stripe.value = Stripe(props.publicKey)
    const options = {
      clientSecret: props.clientSecret
    }

    elements.value = stripe.value.elements(options)
    const paymentElement = elements.value.create("payment")
    paymentElement.mount("#payment-element")
    state.stripeLoaded = true
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    state.loading = true

    let { error } = await stripe.value.confirmPayment({
      elements: elements.value,
      redirect: "if_required"
    })
    if (error === undefined) {
      let timesChecked = 0
      let paymentCompleted = false
      while (!state.status_retrieved && timesChecked <= 10) {
        await new Promise((resolve) => setTimeout(resolve, 5000))
        timesChecked++
        const { data } = await customerApi.checkTransactionStatus({
          orderToken: props.orderToken,
          clientSecret: props.paymentIntentId,
          accountId: props.accountId
        })
        if (data.value) {
          state.status_retrieved = true
          state.loading = false
          paymentCompleted = true
          handlePostPaymentPublic(data.value.balance)
        }
      }
      if (!paymentCompleted) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Failed to confirm your payment, refresh the browser",
          group: "br",
          life: 2000
        })
        state.loading = false
      }
    } else {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to process your payment.",
        group: "br",
        life: 2000
      })
      state.loading = false
    }
  }
  const handlePostPaymentPublic = (balance) => {
    if (Number(balance).toFixed(2) > 0) {
      state.paymentMessage = `We have received your payment. Your remaining balance is ${$fc(
        Number(balance)
      )}. Please pay the remaining balance to complete your order.`
    } else {
      state.paymentMessage = customerOrderStore.publicCms.afterPaymentMessage
    }
    state.customerPaidDialog = true
    setTimeout(() => {
      state.customerPaidDialog = false
      window.location.reload()
    }, 10000)
  }
</script>
