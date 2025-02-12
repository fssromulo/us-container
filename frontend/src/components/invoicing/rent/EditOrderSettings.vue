<template>
  <div>
    <section class="flex flex-col w-full">
      <div class="col-span-12 mt-4 border border-t"></div>
      <table v-if="state.order">
        <tr
          v-if="creditCardFeeToggleEnabled"
          class="text-base text-xl text-900 dark:text-0"
        >
          <td class="text-base text-xl text-700 dark:text-100"
            >Allow External Payment</td
          >
          <td
            v-if="!state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            {{ state.order.allow_external_payments ? "Yes" : "No" }}
          </td>

          <td
            v-if="state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            <ToggleSwitch
              v-model="state.order.allow_external_payments"
              type="text"
            />
          </td>
        </tr>
        <tr v-if="creditCardFeeToggleEnabled" class="col-span-12">
          <td class="text-base text-xl text-700 dark:text-100"
            >Credit card fee enabled</td
          >
          <td
            v-if="!state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            {{ state.order.credit_card_fee ? "Yes" : "No" }}
          </td>
          <td
            v-if="state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            <ToggleSwitch
              id="credit_card_fees"
              v-model="state.order.credit_card_fee"
              type="text"
            />
          </td>
        </tr>
        <tr v-if="state.order.type === 'RENT'" style="height: 2rem">
          <td class="text-base text-xl text-700 dark:text-100">Is Auto Pay</td>
          <td
            v-if="!state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            {{ state.order.is_autopay ? "Yes" : "No" }}
          </td>

          <td
            v-if="state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            <ToggleSwitch
              v-model="state.order.is_autopay"
              type="text"
              :disabled="state.order.customer_profile_id === null"
            />
            <Button
              v-show="state.order.customer_profile_id === null"
              v-tooltip="
                'The customer needs to have a card on file in order to begin autopay'
              "
              icon="pi pi-info-circle"
              class="text-red-600 bg-transparent border-0"
            />
          </td>
        </tr>
        <tr
          v-if="state.order.payment_type && state.order.type === 'RENT'"
          style="height: 2rem"
        >
          <td class="text-base text-xl text-700 dark:text-100"
            >Apply Late Fee</td
          >
          <td
            v-if="!state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            {{ state.order.is_late_fee_applied ? "Yes" : "No" }}
          </td>

          <td
            v-if="state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            <ToggleSwitch
              v-model="state.order.is_late_fee_applied"
              type="text"
            />
            <Button
              v-show="state.order.customer_profile_id === null"
              v-tooltip="'Toggle late fee charge ON or OFF'"
              icon="pi pi-info-circle"
              class="text-red-600 bg-transparent border-0"
            />
          </td>
        </tr>

        <tr v-for="(application, index) in applications" :key="index">
          <td class="text-base text-xl text-700 dark:text-100"
            >{{ application.label }} Application override</td
          >
          <td
            v-if="state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            <ToggleSwitch
              v-model="
                state.order.applications_overridden[index_of(application.type)]
                  .overridden
              "
            />
          </td>
          <td
            v-if="!state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            {{
              state.order.applications_overridden[index_of(application.type)]
                ?.overridden
                ? "Yes"
                : "No"
            }}
          </td>
        </tr>
      </table>
    </section>
    <div class="grid grid-cols-12 gap-4 mt-8 text-right">
      <div class="col-span-4 col-start-5">
        <Button
          v-if="state.isEditing"
          @click="toggleEdit"
          label="Cancel"
          class="p-button-raised p-button-secondary"
        />
      </div>
      <div class="col-span-4">
        <Button
          v-if="state.isEditing"
          @click="saveOrder"
          :loading="state.isLoading"
          class="p-button-raised"
          label="Save"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted, defineEmits, computed, inject } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import { useUsers } from "@/store/modules/users"

  import CustomerService from "@/service/Customers"

  import CustomerApi from "@/api/customers"
  import isEqual from "lodash.isequal"
  import { useCustomerOrder } from "@/store/modules/customerOrder"

  import { useToast } from "primevue/usetoast"
  import { ref, watch } from "vue"
  const $removeUnusedProps = inject("$removeUnusedProps")

  const emit = defineEmits(["hide"])

  const toast = useToast()
  const usersStore = useUsers()

  const customerApi = new CustomerApi()
  const customerStore = useCustomerOrder()

  const userStore = useUsers()
  const customerService = new CustomerService()

  const currentDate = new Date()

  const props = defineProps({
    order: {},
    saveOrder: {}
  })

  const isLastDayOfMonth = () => {
    const currentDay = currentDate.getDate()
    const lastDayOfMonth = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth() + 1,
      0
    ).getDate()

    return currentDay === lastDayOfMonth
  }

  const creditCardFeeToggleEnabled = computed(() => {
    return usersStore.cms?.credit_card_fees.enable_toggle_credit_card_fees
  })

  const index_of = (name) => {
    const index = state.order.applications_overridden.findIndex(
      (obj) => obj.name == name
    )
    return index
  }
  const applications = computed(() => {
    if (state.order.applications_overridden == null) {
      state.order.applications_overridden = []
    }
    return Object.keys(usersStore.cms?.applications || [])
      .map((key) => {
        if (
          !state.order.applications_overridden.some((obj) => obj.name == key)
        ) {
          state.order.applications_overridden.push({
            name: key,
            overridden: false
          })
        }
        return {
          type: key,
          label: key
            .replace(/_/g, " ")
            .replace(/\b\w/g, (char) => char.toUpperCase()),
          value: usersStore.cms?.applications[key]
        }
      })
      .filter(
        (e) =>
          e.value == true &&
          (e.type == "credit_card" ||
            e.type == customerStore.order.type.toLowerCase())
      )
  })

  const resetOrder = () => {
    let order = customerService.orderDto()
    state.originalOrder = cloneDeep(order)
    state.order = cloneDeep(order)
    state.order.customer_application_schema_id =
      state.order?.customer_application_schema?.id || null
  }

  const close = () => {
    state.isLoading = false
    state.isEditing = false
    state.addContainerNumberDialog = false
    state.discountApplied = false
    state.addPayment = null
  }

  onMounted(async () => {
    resetOrder()
    state.isRborTaxChanged = false
  })

  const toggleEdit = async () => {
    state.isEditing = !state.isEditing
  }

  const saveOrder = async () => {
    let isOrderSame =
      isEqual(state.order, state.originalOrder) && !state.addPayment
    const requestData = $removeUnusedProps(state.order, state.originalOrder)
    if (isOrderSame) {
      toast.add({
        severity: "warn",
        summary: "Warn",
        detail: "Order unchanged",
        group: "br",
        life: 2000
      })
      state.isLoading = false
      return
    }

    state.isLoading = true
    let isWorking = false

    if (!isOrderSame) {
      let isAddPayment = state.addPayment != null
      if (isAddPayment) {
        let newBalance
        if (state.originalOrder.calculated_remaining_order_balance !== 0) {
          newBalance =
            state.originalOrder.calculated_remaining_order_balance -
            state.addPayment
          if (newBalance < 0) {
            newBalance = 0
          }
        } else {
          newBalance = state.originalOrder.total_price - state.addPayment
        }
        requestData["remaining_balance"] = newBalance
        delete requestData["calculated_remaining_order_balance"]
        let tType = {
          payment_type:
            state.order.payment_type == null
              ? "Echeck"
              : state.order.payment_type,
          order_id: state.originalOrder.id,
          notes: state.notes,
          amount: state.addPayment
        }
        const { data, error } = await customerApi.addTransactionType(tType)
        if (error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Cannot save transaction type.",
            life: 3000,
            group: "br"
          })
        }
      }
      try {
        delete requestData["fees"]
        const response = await customerApi.updateOrder(
          state.order.id,
          requestData
        )
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Order updated",
          group: "br",
          life: 2000
        })
        customerStore.setOrder(null)
        customerStore.setOrder(response.data)
        // await props.saveOrder();
      } finally {
        if (!isWorking) {
          close()
        }
      }
    } else {
      close()
    }
    state.isLoading = false
    emit("hide")
  }

  const state = reactive({
    order: {},
    orderUser: null,
    quickSearchOrder: [],
    originalOrder: {},
    loadingUsers: false,
    addPayment: null,
    isEditing: true,
    isLoading: false,
    addContainerNumberDialog: false,
    discountApplied: false,
    addedMiscCosts: [], // to-be-added misc costs that will be sent in a post request to the api
    addedFees: [], // to-be-added fees that will be sent in a post request to the api
    toastConfirmAction: null, // The action that will be tied to the yes button on the showtoast function
    toastCancelAction: null, // The action that will be tied to the no button on the showtoast function
    showToast: false, // bool that allows for the confirmation toast popup to be displayed
    costTypeOptions: ref([]), // This is the state object that actually holds and stores the cost_type options and then is used by miscCostOptionsList to populate the dropdown list
    isEditRb: true, // This will toggle the editing fields from being disabled or enabled for the remaining balance and tax fields. you cannot edit both fields at the same time
    isRborTaxChanged: false,
    notes: "",
    application_schemas: []
  })

  watch(
    () => customerStore.order,
    () => {
      resetOrder()
    },
    { immediate: true, deep: true }
  )

  watch(
    () => state.isEditing,
    () => {
      resetOrder()
    }
  )
</script>

<style scoped>
  .p-datepicker-current-day {
    background-color: blue !important;
  }
</style>
