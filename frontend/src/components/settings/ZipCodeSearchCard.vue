<template>
  <div class="">
    <h3 class="">{{ postalZipText }} Delete Section</h3>
  </div>
  <div class="mb-4 field col-span-4">
    <label for="zipcode" class="font-medium text-900 dark:text-0"
      >{{ postalZipText }} Search</label
    >
    <div class="input-container">
      <span class="p-input-icon-left">
        <i class="pi pi-search" />
        <InputText v-model="zipcode" placeholder="Search" />
      </span>
      <div class="p-buttonset" style="margin-top: 5px">
        <Button label="Delete" icon="pi pi-trash" @click="deleteZipcode" />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed, reactive, onMounted } from "vue";
  import ZipCodeLookup from "@/api/zipCodeLookup.js";
  import { useCustomerOrder } from "@/store/modules/customerOrder";
  import { useUsers } from "@/store/modules/users";
  import { useToast } from "primevue/usetoast";

  const userStore = useUsers();
  const toast = useToast();

  const zipCodeLookup = new ZipCodeLookup();

    const zipcode = ref("")
    const postalZipText = computed(() => {
      return userStore.cms?.account_country &&
        userStore.cms?.account_country == "Canada"
        ? "Postal Code"
        : "Zip Code"
    })

  const state = reactive({
    cms: null,
    loading: false,
    cmsId: null,
  });
  onMounted(async () => {
    state.id = userStore.cms.id;
    state.cms = userStore.cms;
  });

  const deleteZipcode = async () => {
    state.loading = true;
    const { data, error } = await zipCodeLookup.deleteZipCode(zipcode.value);
    if (error.value) {
      toast.add({
        severity: "error",
        summary: `Error Deleting ${postalZipText.value}`,
        detail: error.message,
        life: 3000,
        group: "br",
      });
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: `Deleting ${postalZipText.value} Deleted`,
        life: 3000,
        group: "br",
      });
      const cms_attributes = data.value.cms_attributes;
      userStore.setCms(cms_attributes);
      userStore.setIntegrations(data.value.integrations);
    }
  }
</script>