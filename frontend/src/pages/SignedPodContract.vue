<template>
  <div v-if="loading" class="spinner-overlay">
    <div class="spinner"></div>
  </div>
  <div
    class="ml-6 justify-content-center"
    style="max-width: 80vw"
    v-else-if="pod_signed"
  >
    <PodContract
      :orderId="$route.currentRoute.value.params.orderId"
      :selectedSchema="state.applicationSchemas[0].content"
      :selectedSchemaId="state.applicationSchemas[0].id"
      :podSigned="pod_signed"
      :oldSignedDate="dfc(customerOrderStore.publicOrder?.signed_at)"
      :contractResponse="
        customerOrderStore.publicOrder?.application_response[0]
      "
    />
  </div>
  <div v-else> Contract is not signed. </div>
</template>

<script setup>
  import { inject, onMounted, ref, computed, reactive } from "vue"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import AccountApi from "@/api/account"
  import { dfc } from "@/service/DateFormat.js"

  import PodContract from "@/components/applications/PodContract.vue"
  import { useToast } from "primevue/usetoast"
  const accountApi = new AccountApi()

  const toast = useToast()
  const state = reactive({
    applicationSchemas: []
  })
  const loading = ref(false)
  const contract_limit_reached = ref(false)
  const $route = inject("$route")
  const customerOrderStore = useCustomerOrder()

  const customerApi = new CustomerApi()
  const pod_signed = computed(() => {
    return customerOrderStore.publicOrder?.signed_at ? true : false
  })
  onMounted(async () => {
    const orderId = $route.currentRoute.value.params.orderId
    loading.value = true
    const { data } = await customerApi.getOrderByIdPublic(orderId)

    if (data.value == undefined) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Order does not exist or it was deleted.",
        group: "br",
        life: 5000
      })
      loading.value = false
      return
    }
    customerOrderStore.setPublicOrder(data.value)
    // const res = await accountApi.getPublicAccount(
    //     customerOrderStore.publicOrder.account_id
    // );
    // customerOrderStore.setPublicCms(res.data.value);
    await fetchSchema()
    loading.value = false
  })

  const fetchSchema = async () => {
    const result = await customerApi.getApplicationSchemasByName(
      "POD",
      customerOrderStore.publicOrder.id
    )
    if (result.data.value) {
      state.applicationSchemas = result.data.value
    }
  }
</script>

<style scoped>
  .spinner-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .spinner {
    width: 50px;
    height: 50px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
