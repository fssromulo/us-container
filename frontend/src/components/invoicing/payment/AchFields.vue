<template>
  <div class="flex flex-col flex-auto">
    <div class="flex justify-center mt-4">
      <div
        class="flex flex-wrap justify-center mt-2 mb-6"
        style="max-width: 900px"
      >
        <div class="w-full mb-5">
          <div>
            <label for="bank_name" class="font-medium text-900 dark:text-0"
              >Bank Name</label
            >
            <InputText
              class="p-inputtext p-component p-inputtext-fluid"
              v-model="state.bank_name"
              id="bank_name"
              type="text"
              @input="handleInputChange"
            />
          </div>
          <div class="grid w-full gap-2 sm:grid-cols-1 md:grid-cols-2">
            <div>
              <label
                for="account_number"
                class="font-medium text-900 dark:text-0"
                >Account number</label
              >
              <InputText
                class="p-inputtext p-component p-inputtext-fluid"
                v-model="state.account_number"
                id="account_number"
                type="text"
                @input="handleInputChange"
              />
            </div>
            <div>
              <label
                for="routing_number"
                class="font-medium text-900 dark:text-0"
                >Routing number</label
              >
              <InputText
                class="p-inputtext p-component p-inputtext-fluid"
                v-model="state.routing_number"
                id="routing_number"
                type="text"
                @input="handleInputChange"
              />
            </div>
          </div>
          <div class="col-span-12 mb-4 field md:col-span-12">
            <label>Billing information </label>
          </div>
          <div class="grid w-full gap-2 sm:grid-cols-1 md:grid-cols-2">
            <div>
              <label
                for="routing_number"
                class="font-medium text-900 dark:text-0"
                >First Name</label
              >
              <InputText
                class="p-inputtext p-component p-inputtext-fluid"
                v-model="state.billing_first_name"
                id="routing_number"
                type="text"
                @input="handleInputChange"
              />
            </div>

            <div>
              <label
                for="routing_number"
                class="font-medium text-900 dark:text-0"
                >Last Name</label
              >
              <InputText
                class="p-inputtext p-component p-inputtext-fluid"
                v-model="state.billing_last_name"
                id="routing_number"
                type="text"
                @input="handleInputChange"
              />
            </div>
          </div>
          <div class="col-span-12 mb-4 field md:col-span-6">
            <label for="routing_number" class="font-medium text-900 dark:text-0"
              >Address
            </label>
            <InputText
              class="p-inputtext p-component p-inputtext-fluid"
              v-model="state.billing_address"
              id="routing_number"
              type="text"
              @input="handleInputChange"
            />
          </div>

          <div class="col-span-12 mb-4 field md:col-span-6">
            <label for="routing_number" class="font-medium text-900 dark:text-0"
              >City
            </label>
            <InputText
              class="p-inputtext p-component p-inputtext-fluid"
              v-model="state.billing_city"
              id="routing_number"
              type="text"
              @input="handleInputChange"
            />
          </div>
          <div class="grid w-full gap-2 sm:grid-cols-1 md:grid-cols-2">
            <div>
              <label
                for="routing_number"
                class="font-medium text-900 dark:text-0"
                >{{ stateProvinceText }}
              </label>
              <InputText
                class="p-inputtext p-component p-inputtext-fluid"
                v-model="state.billing_state"
                id="routing_number"
                type="text"
                @input="handleInputChange"
              />
            </div>

            <div>
              <label
                for="routing_number"
                class="font-medium text-900 dark:text-0"
                >{{ postalZipText }}
              </label>
              <InputText
                class="p-inputtext p-component p-inputtext-fluid"
                v-model="state.billing_zip"
                id="routing_number"
                type="text"
                @input="handleInputChange"
              />
            </div>
          </div>
        </div>
        <Button
          v-if="
            !isPayMode &&
            !isUpdateAch &&
            $ability.can('update', 'rental_payments')
          "
          :label="`Add ACH`"
          :loading="state.loading"
          style="max-width: 200px"
          @click="addACH"
          class="p-button-primary p-button-rounded p-button-lg"
        ></Button>

        <Button
          v-if="
            !isPayMode &&
            isUpdateAch &&
            $ability.can('update', 'rental_payments')
          "
          :label="`Remove ACH`"
          :loading="state.loading_remove_ach"
          style="max-width: 200px"
          @click="removeACH"
          class="p-button-primary p-button-rounded p-button-lg"
        ></Button>
        <Button
          v-if="
            !isPayMode &&
            isUpdateAch &&
            $ability.can('update', 'rental_payments')
          "
          :label="`Update ACH`"
          :loading="state.loading_update_ach"
          style="max-width: 200px; margin-left: 50px"
          @click="updateACH"
          class="p-button-primary p-button-rounded p-button-lg"
        ></Button>

        <Button
          v-if="
            isPayMode &&
            !isUpdateAch &&
            $ability.can('update', 'rental_payments')
          "
          :label="`Save ACH`"
          :loading="state.loading"
          style="max-width: 200px; margin-left: 50px"
          @click="addACHPublic"
          class="p-button-primary p-button-rounded p-button-lg"
        ></Button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, defineEmits, inject, computed } from "vue"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import { useUsers } from "@/store/modules/users"
  const userStore = useUsers()

  const $ability = inject("$ability")

  const toast = useToast()

  const customerApi = new CustomerApi()
  const customerOrderStore = useCustomerOrder()

  const emit = defineEmits(["bankAccountInfo"])
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

  const handleInputChange = () => {
    emit(
      "bankAccountInfo",
      state.bank_name,
      state.account_number,
      state.routing_number
    )
  }

  const props = defineProps({
    isUpdateAch: {
      type: Boolean,
      default: false
    },
    isPayMode: {
      type: Boolean,
      default: false
    },
    refreshFunction: {
      type: Function,
      default: () => {}
    }
  })

  onMounted(async () => {
    if (customerOrderStore.order) {
      const customerProfileId = customerOrderStore.order.customer_profile_id
      const { data, error } = await customerApi.getCustomerProfile(
        customerProfileId
      )
      for (var i = 0; i < data?.value?.profile?.paymentProfiles.length; i++) {
        if (
          data?.value?.profile?.paymentProfiles[i].payment.bankAccount ==
          undefined
        ) {
          continue
        }

        if (data?.value?.profile?.paymentProfiles[i].payment) {
          state.bank_name =
            data?.value?.profile?.paymentProfiles[i].billTo.firstName +
            " " +
            data?.value?.profile?.paymentProfiles[i].billTo.lastName
          state.account_number =
            data.value.profile.paymentProfiles[
              i
            ].payment.bankAccount.accountNumber
          state.routing_number =
            data.value.profile.paymentProfiles[
              i
            ].payment.bankAccount.routingNumber
        }

        state.billing_first_name =
          data?.value?.profile?.paymentProfiles[i].billTo.firstName
        state.billing_last_name =
          data?.value?.profile?.paymentProfiles[i].billTo.lastName
        state.billing_address =
          data?.value?.profile?.paymentProfiles[i].billTo.address
        state.billing_city =
          data?.value?.profile?.paymentProfiles[i].billTo.city
        state.billing_state =
          data?.value?.profile?.paymentProfiles[i].billTo.state
        state.billing_zip = data?.value?.profile?.paymentProfiles[i].billTo.zip
      }
    }
  })

  const state = reactive({
    bank_name: "",
    account_number: "",
    routing_number: "",
    loading: false,
    billing_first_name: "",
    billing_last_name: "",
    billing_address: "",
    billing_city: "",
    billing_state: "",
    billing_zip: "",
    loading_remove_ach: false,
    loading_update_ach: false
  })

  const updateACH = async () => {
    state.loading_update_ach = true
    let creditCardObj = {
      first_name: state.billing_first_name,
      last_name: state.billing_last_name,
      zip: state.billing_zip,
      avs_street: state.billing_address,
      city: state.billing_city,
      state: state.billing_state,
      order_id: customerOrderStore.order.id,
      bank_name: state.bank_name,
      account_number: state.account_number,
      routing_number: state.routing_number
    }

    const { error } = await customerApi.updateACH(creditCardObj)
    state.loading_update_ach = false

    if (!error.value) {
      const { data, isLoading, error } = await customerApi.getOrderByDisplayId(
        customerOrderStore.order.display_order_id
      )
      customerOrderStore.setOrder(data.value)
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Added ACH on File.",
        group: "br",
        life: 2000
      })
    } else {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to Add ACH on File.",
        group: "br",
        life: 2000
      })
    }
  }

  const removeACH = async () => {
    state.loading_remove_ach = true
    await customerApi.removeCustomerPaymentProfile(
      customerOrderStore.order.id,
      "ACH"
    )
    /*await customerApi.updateOrder(customerOrderStore.order.id, {
    customer_profile_id: null,
    is_autopay: false,
  });*/
    const { data, isLoading, error } = await customerApi.getOrderByDisplayId(
      customerOrderStore.order.display_order_id
    )
    customerOrderStore.setOrder(data.value)
    state.customerRemoveCardOnFile = false
    state.loading_remove_ach = false

    await props.refreshFunction()
  }

  const addACH = async () => {
    state.loading = true
    let creditCardObj = {
      first_name: state.billing_first_name,
      last_name: state.billing_last_name,
      zip: state.billing_zip,
      avs_street: state.billing_address,
      city: state.billing_city,
      state: state.billing_state,
      order_id: customerOrderStore.order.id,
      bank_name: state.bank_name,
      account_number: state.account_number,
      routing_number: state.routing_number
    }

    const { error } = await customerApi.addACH(creditCardObj)
    state.loading = false

    if (!error.value) {
      const { data, isLoading, error } = await customerApi.getOrderByDisplayId(
        customerOrderStore.order.display_order_id
      )
      customerOrderStore.setOrder(data.value)
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Added ACH on File.",
        group: "br",
        life: 2000
      })

      await props.refreshFunction()
    } else {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to Add ACH on File.",
        group: "br",
        life: 2000
      })
    }
  }

  const addACHPublic = async () => {
    state.loading = true
    let creditCardObj = {
      first_name: customerOrderStore.publicOrder.customer.first_name,
      last_name: customerOrderStore.publicOrder.customer.last_name,
      zip: customerOrderStore.publicOrder.address.zip,
      avs_street: customerOrderStore.publicOrder.address.street_address,
      city: customerOrderStore.publicOrder.address.city,
      state: customerOrderStore.publicOrder.address.state,
      order_id: customerOrderStore.publicOrder.id,
      bank_name: state.bank_name,
      account_number: state.account_number,
      routing_number: state.routing_number
    }

    const { error } = await customerApi.addACH(creditCardObj)
    state.loading = false

    if (!error.value) {
      const { data, isLoading, error } = await customerApi.getOrderByDisplayId(
        customerOrderStore.publicOrder.display_order_id
      )
      customerOrderStore.setPublicOrder(data.value)
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Added ACH on File.",
        group: "br",
        life: 2000
      })
    } else {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to Add ACH on File.",
        group: "br",
        life: 2000
      })
    }
  }
</script>
