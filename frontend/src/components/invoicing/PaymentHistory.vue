<template>
  <div v-if="!isRental" style="margin-left: 30px">
    <div class="mt-4">
      <p class="text-2xl">
        Transactions

        <Button
          v-if="state.transactionTypes.length > 0"
          type="button"
          icon="pi pi-pencil text-sm"
          @click="editToggle"
          class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
          :loading="state.savingTransactions"
        >
        </Button>
      </p>
    </div>
    <div class="mt-4" :style="other_transactions_style">
      <DataTable
        :value="state.transactionTypes"
        editMode="cell"
        onCell
        :loading="state.savingTransactions"
      >
        <template #loading> Loading.. </template>
        <Column
          field="transaction_effective_date"
          header="Date"
          style="width: 200px"
        >
          <template v-if="!state.editingTransactions" #body="{ data, field }">
            {{ parseDate(data[field]) }}
          </template>

          <template v-else #body="{ data, field }">
            <DatePicker
              v-if="data['payment_type'] != 'CREDIT CARD'"
              style="width: 120px"
              v-model="data[field]"
            />
            <span v-else> {{ parseDate(data[field]) }}</span>
          </template>
        </Column>
        <Column field="payment_type" header="Type"></Column>
        <Column field="notes" header="Notes">
          <template v-if="!state.editingTransactions" #body="{ data, field }">
            {{ data[field] }}
          </template>

          <template v-else #body="{ data, field }">
            <InputText
              v-if="data['payment_type'] != 'CREDIT CARD'"
              v-model="data[field]"
            />
            <span v-else> {{ data[field] }}</span>
          </template>
        </Column>
        <Column field="amount" header="Amount">
          <template v-if="!state.editingTransactions" #body="{ data, field }">
            {{ data[field] }}
          </template>

          <template v-else #body="{ data, field }">
            <InputText
              v-if="data['payment_type'] != 'CREDIT CARD'"
              v-model="data[field]"
              style="width: 80px"
            />
            <span v-else> {{ data[field] }}</span>
          </template>
        </Column>

        <Column
          field="id"
          v-if="!state.editingTransactions"
          header="Delete Transaction"
        >
          <template #body="slotProps">
            <Button
              type="button"
              icon="pi pi-trash text-sm"
              v-if="slotProps.data['payment_type'] != 'CREDIT CARD'"
              :loading="state.deletingTransactionsLoading === slotProps.data.id"
              @click="deleteTransaction(slotProps.data, $event)"
              class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
            ></Button>
          </template>
        </Column>

        <Column v-if="state.editingTransactions">
          <template #body="{ data, field }">
            <Button
              class="p-button-rounded"
              v-if="data['payment_type'] != 'CREDIT CARD'"
              :disabled="state.savingTransactions"
              :loading="state.savingTransactions"
              @click="update(data)"
            >
              Save
            </Button>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
  import { reactive, computed, ref, inject, onMounted, watch } from "vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import {
    dfa,
    dfc,
    formatISODate,
    convertDateForPost
  } from "@/service/DateFormat.js"
  import CustomerApi from "@/api/customers"
  import cloneDeep from "lodash.clonedeep"

  const $removeUnusedProps = inject("$removeUnusedProps")
  const customerApi = new CustomerApi()
  const $fc = inject("$formatCurrency")
  const toast = useToast()
  const customerStore = useCustomerOrder()

  const parseDate = (date) => {
    if (date == "") {
      return ""
    }
    const jsDate = convertDateForPost(new Date(date))
    return formatISODate(jsDate.toISOString())
  }

  const editToggle = () => {
    state.editingTransactions = !state.editingTransactions
  }

  const props = defineProps({
    resetFunction: {
      type: Function,
      default: () => {}
    }
  })

  const reloadTable = () => {}

  const update = async (data) => {
    state.savingTransactions = true

    const id = data.id
    let data_to_patch = cloneDeep(data)
    console.log(data_to_patch)
    console.log(state.originalTransactionTypes.find((el) => el.id === id))
    data_to_patch = $removeUnusedProps(
      data_to_patch,
      state.originalTransactionTypes.find((el) => el.id === id)
    )

    const { result_data, error } = await customerApi.editTransactionType(
      id,
      data_to_patch
    )

    if (error?.value != null) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error updating transaction type",
        group: "br",
        life: 2000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Successfully updated transaction type",
        group: "br",
        life: 2000
      })

      state.editingTransactions = false
    }
    state.savingTransactions = false
  }

  const state = reactive({
    editingTransactions: false,
    savingTransactions: false,
    transactionTypes: [],
    originalTransactionTypes: [],
    deletingTransactionsLoading: -1
  })

  const deleteTransaction = async (data, event) => {
    state.deletingTransactionsLoading = data.id

    const { result_data, error } = await customerApi.removeTransaction(data.id)

    if (error?.value != null) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error deleting transaction.",
        group: "br",
        life: 2000
      })
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Successfully deleting transaction.",
        group: "br",
        life: 2000
      })

      await props.resetFunction()

      state.transactionTypes = transactionTypes()
    }
    state.deletingTransactionsLoading = -1
  }

  const isRental = computed(() => {
    return customerStore.order?.type === "RENT"
  })

  const other_transactions_style = computed(() => {
    return state.editingTransactions ? "" : ""
  })

  const historyTransactions = computed(() => {
    return customerStore.order?.credit_card
      .sort((a, b) => {
        return new Date(b.created_at) - new Date(a.created_at)
      })
      .map((c) => {
        const authorizeProviderMessage =
          c.response_from_gateway?.transactionResponse?.messages
        const stripeProviderMessage = c.response_from_gateway?.metadata
          ? c.response_from_gateway
          : {}
        let approved = false
        let message = ""
        let amount = 0
        let approved_note, account_number
        if (authorizeProviderMessage?.length) {
          approved = authorizeProviderMessage[0].code === "1"
          amount =
            c?.response_from_gateway?.payment_amount ||
            c.response_from_gateway?.auth_amount
          approved_note =
            c.response_from_gateway?.result_code === "A" || approved
              ? "approved"
              : "declined"
          account_number =
            c.response_from_gateway?.transactionResponse?.accountNumber
        } else if (Object.keys(stripeProviderMessage)?.length > 0) {
          approved = stripeProviderMessage.status == "succeeded"
          amount = stripeProviderMessage.amount / 100
          approved_note = approved ? "approved" : "declined"
          account_number = "XXXX"
        } else if (c.response_from_gateway.retref != undefined) {
          approved = c.response_from_gateway.respstat == "A"
          amount = c.response_from_gateway.payment_amount
          approved_note = approved ? "approved" : "declined"
          account_number = c.response_from_gateway.account.slice(-4)
        }
        return {
          amount: $fc(amount),
          payment_type: "CREDIT CARD",
          created_at: `${dfa(c.created_at)}`,
          notes: ` ${c.card_type} | ${c.merchant_name} | ${approved_note} | ${account_number}`
          //result: c.response_from_gateway?.result || message,
          //errorMessage: c.response_from_gateway?.errorMessage,
        }
      })
  })

  const resetTransactions = () => {
    const transactions = transactionTypes()
    const clonedTransactions = cloneDeep(transactions)
    state.originalTransactionTypes = clonedTransactions
    state.transactionTypes = cloneDeep(clonedTransactions)
  }

  onMounted(() => {
    resetTransactions()
  })

  const transactionTypes = () => {
    if (state.savingTransactions === false) {
      let transactions = cloneDeep(customerStore.order?.transaction_type_order)
        .sort((a, b) => {
          return new Date(b.created_at) - new Date(a.created_at)
        })
        .map((transaction) => {
          transaction.created_at = formatISODate(transaction.created_at)
          return transaction
        })
      transactions = transactions.filter((el) => {
        return el.credit_card_object == null
      })
      return [...transactions, cloneDeep(...historyTransactions.value)]
    } else {
      return []
    }
  }
</script>

<style scoped>
  .scrollable-container {
    max-width: 500px; /* Set the maximum height of the container */
    overflow-x: auto; /* Enable vertical scrolling if the content overflows */
    /* Optionally, you can add other styles as needed */
  }
</style>
