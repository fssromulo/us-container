<template>
  <div class="container">
    <h3 class="text-center">Clear cache</h3>
    <div class="p-buttonset" style="margin-top: 5px">
      <Button label="Clear cache" icon="pi pi-trash" @click="clearCache" />
    </div>
  </div>
</template>

<script setup>
  import Cache from "@/api/cache.js"
  import { useToast } from "primevue/usetoast"

  const cache = new Cache()
  const toast = useToast()

  const clearCache = async () => {
    const { data, error } = await cache.clear()
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Clearing cache failed.",
        detail: error.message,
        life: 3000,
        group: "br"
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Cache cleared successfully.",
        life: 3000,
        group: "br"
      })
    }
  }
</script>
