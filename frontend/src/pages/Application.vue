<template>
  <div>
    <CreditApplication></CreditApplication>
  </div>
</template>

<script setup>
  // && $ability.can('read', 'inventory-depots')
  import { reactive, inject } from "vue"
  import CreditApplication from "@/components/applications/CreditApplication.vue"
</script>

<style></style>
