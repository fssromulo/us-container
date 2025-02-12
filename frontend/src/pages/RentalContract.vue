<template>
  <div v-if="loading && !contract_limit_reached" class="spinner-overlay">
    <div class="spinner"></div>
  </div>
  <div v-if="contract_limit_reached"> Contract limit reached. </div>
</template>

<script setup>
  import { inject, onMounted, ref } from "vue"
  import CustomerApi from "@/api/customers"

  const loading = ref(false)
  const contract_limit_reached = ref(false)
  const $route = inject("$route")

  const customerApi = new CustomerApi()

  onMounted(async () => {
    const orderId = $route.currentRoute.value.params.orderId
    loading.value = true
    const { data, error } = await customerApi.sendeRentalContract(orderId)
    loading.value = false
    window.location.href = data.value["sign_page_url"]
  })
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
