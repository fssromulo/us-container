<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Name</label
          >
          <InputText
            placeholder="Name"
            v-model="state.depot.name"
            :class="{ 'p-invalid': v$.depot.name.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="state" class="font-medium text-900 dark:text-0">{{
            stateProvinceText
          }}</label>
          <Select
            v-model="state.depot.state"
            :placeholder="stateProvinceText"
            :class="{ 'p-invalid': v$.depot.state.$invalid }"
            class="p-component p-inputtext-fluid"
            :options="
              getAccountCountry == 'Canada'
                ? stateService.getProvinces()
                : state.statesList
            "
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0">City</label>
          <InputText
            placeholder="City"
            v-model="state.depot.city"
            class="p-component p-inputtext-fluid"
            :class="{ 'p-invalid': v$.depot.city.$invalid }"
            id="city"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0"
            >Address</label
          >
          <InputText
            placeholder="Address"
            v-model="state.depot.street_address"
            class="p-component p-inputtext-fluid"
            :class="{ 'p-invalid': v$.depot.street_address.$invalid }"
            id="street_address"
            type="text"
            maxlength="60"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0">{{
            postalZipText
          }}</label>
          <InputText
            :useGrouping="false"
            :placeholder="postalZipText"
            class="p-component p-inputtext-fluid"
            v-model="state.depot.zip"
            :class="{ 'p-invalid': v$.depot.zip.$invalid }"
            id="zip"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Primary phone</label
          >
          <InputMask
            mode="decimal"
            :useGrouping="false"
            mask="(999) 999-9999"
            placeholder="(999) 999-9999"
            v-model="state.depot.primary_phone"
            class="p-component p-inputtext-fluid"
            :class="{ 'p-invalid': v$.depot.primary_phone.$invalid }"
            id="primary_phone"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Secondary phone</label
          >
          <InputMask
            mode="decimal"
            :useGrouping="false"
            mask="(999) 999-9999"
            placeholder="(999) 999-9999"
            class="p-component p-inputtext-fluid"
            v-model="state.depot.secondary_phone"
            id="secondary_phone"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0"
            >Primary Email</label
          >
          <InputText
            placeholder="Primary Email"
            v-model="state.depot.primary_email"
            class="p-component p-inputtext-fluid"
            :class="{ 'p-invalid': v$.depot.primary_email.$invalid }"
            id="primary_email"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="zip" class="font-medium text-900 dark:text-0"
            >Secondary Email</label
          >
          <InputText
            placeholder="Secondary Email"
            v-model="state.depot.secondary_email"
            class="p-component p-inputtext-fluid"
            id="secondary_email"
            type="text"
          />
        </div>
      </div>
    </div>
    <Button
      :label="$isObjectPopulated(depotProp) ? 'Update Depot' : 'Create Depot'"
      @click="createUpdateDepot"
      icon="pi pi-file"
      class="w-auto"
      :loading="state.loading"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"

  import DepotsService from "@/service/Depot"
  import DepotApi from "@/api/depot"
  import InventoryService from "@/service/Inventory"

  import { useToast } from "primevue/usetoast"
  import { useDepots } from "@/store/modules/depots"
  import { useUsers } from "@/store/modules/users"
  const userStore = useUsers()

  const toast = useToast()

  const depotApi = new DepotApi()
  const depotService = new DepotsService()
  const depotStore = useDepots()
  const inventoryService = new InventoryService()

  const stateService = new StateService()

  const { depotProp } = defineProps({
    depotProp: {
      type: Object,
      default: () => ({})
    }
  })

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const swapOldDepot = (updatedDepot) => {
    const index = cloneDeep(depotStore.depots)
      .map((u) => u.id)
      .indexOf(updatedDepot.id)
    let clonedDepots = cloneDeep(depotStore.depots)
    clonedDepots[index] = depotService.dtoDepot(updatedDepot)
    depotStore.setDepots(clonedDepots)
  }

  onMounted(async () => {
    state.statesList = stateService.getStates()
    resetDepot()
  })

  const emptyDepot = {
    name: "",
    city: "",
    state: "",
    zip: "",
    street_address: "",
    primary_phone: "",
    secondary_phone: "",
    primary_email: "",
    secondary_email: ""
  }

  const state = reactive({
    loading: false,
    depot: cloneDeep(emptyDepot),
    statesList: [],
    originalDepot: null
  })

  const rules = computed(() => ({
    depot: {
      name: { required, $lazy: true },
      city: { required, $lazy: true },
      state: { required, $lazy: true },
      zip: { required, $lazy: true },
      street_address: { required, $lazy: true },
      primary_phone: { required, $lazy: true },
      primary_email: { required, $lazy: true }
    }
  }))

  const v$ = useVuelidate(rules, state)
  const postalZipText = computed(() => {
    return userStore.cms?.account_country &&
      userStore.cms?.account_country == "Canada"
      ? "Postal Code"
      : "Zip"
  })
  const stateProvinceText = computed(() => {
    return userStore.cms?.account_country &&
      userStore.cms?.account_country == "Canada"
      ? "Province"
      : "State"
  })
  const getAccountCountry = computed(() => {
    let account_country = userStore.cms.account_country
    return account_country
  })
  const resetDepot = () => {
    let depot = null
    if (depotProp) {
      depot = depotService.dtoDepot(depotProp)
    } else {
      depot = emptyDepot
    }
    state.originalDepot = cloneDeep(depot)
    state.depot = cloneDeep(depot)
    v$.value.$reset()
  }

  const createUpdateDepot = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    state.loading = true

    if (state.depot.id) {
      let requestData = $removeUnusedProps(state.depot, state.originalDepot)

      if (requestData.primary_phone) {
        requestData.primary_phone = requestData.primary_phone.replace(
          /[^0-9]/g,
          ""
        )
      }

      if (requestData.secondary_phone) {
        requestData.secondary_phone = requestData.secondary_phone.replace(
          /[^0-9]/g,
          ""
        )
      }

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "Depot Unchanged",
          detail: "Depot Unchanged",
          group: "br",
          life: 5000
        })
        state.loading = false
        return
      }

      const { data, error } = await depotApi.updateDepot(
        state.depot.id,
        requestData
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Depot Updated",
          detail: "Successfully updated depot",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating depot",
          group: "br",
          life: 5000
        })
      }
      swapOldDepot(data.value)
      state.loading = false
    } else {
      const { data } = await depotApi.createDepot(state.depot)

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Depot Saved",
          detail: "Successfully saved depot",
          group: "br",
          life: 5000
        })
      }
      let updatedDepots = cloneDeep(depotStore.depots)
      updatedDepots.unshift(depotService.dtoDepot(data.value))
      depotStore.setDepots(updatedDepots)
      resetDepot()
    }
    state.loading = false
    emit("hide")
  }
</script>

<style></style>
