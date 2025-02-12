<template>
  <div class="grid ml-2 p-fluid" v-if="props.rentPeriodId || props.orderId">
    <div class="col-span-12 mb-4 field">
      <DataTable
        :value="state.transactions"
        :loading="state.loadingTransaction"
      >
        <Column
          class="col-span-3"
          v-for="column in columns"
          :key="column.field"
          :field="column.field"
          :header="column.header"
        >
          <template #body="{ data, field }">
            <div v-if="!isInEditMode(data.id)">
              <span v-if="field !== 'amount'">{{ data[field] }}</span>
              <span v-if="field === 'amount' && data[field] > 0">{{
                $fc(data[field])
              }}</span>
            </div>
            <DatePicker
              v-else-if="field === 'transaction_effective_date'"
              v-model="data[field]"
            />
            <Select
              v-else-if="field === 'payment_type'"
              :options="paymentOptions"
              v-model="data[field]"
              placeholder="Select a payment type"
              optionLabel="label"
              optionValue="value"
              style="width: 100px"
            />
            <InputText v-else-if="field === 'notes'" v-model="data[field]" />
            <InputText
              v-else-if="field === 'amount'"
              v-model="data[field]"
              disabled
            />
          </template>
        </Column>
        <Column>
          <template #body="{ data }">
            <Button
              icon="pi pi-pencil"
              @click="editToggle(data.id)"
              :loading="state.savingTransactions"
            />
          </template>
        </Column>
        <Column>
          <template #body="{ data }">
            <Button
              v-if="isInEditMode(data.id)"
              @click="update(data)"
              :disabled="state.savingTransactions"
              :loading="state.savingTransactions"
            >
              Save
            </Button>
          </template>
        </Column>

        <ConfirmPopup id="confirmPopup"></ConfirmPopup>
        <Column>
          <template #body="{ data, field }">
            <Button
              id="confirmButton"
              @click="deleteTransaction($event, data)"
              :disabled="state.deletingTransactions"
              :loading="state.deletingTransactions"
            >
              <i class="pi pi-trash"></i>
            </Button>
          </template>
        </Column>
        <Column v-if="isRental">
          <template #body="{ data }">
            <Button @click="openReceipt(data)">Receipt</Button>
          </template>
        </Column>
        <template #empty>No transactions found.</template>
      </DataTable>
    </div>

    <Dialog
      v-model:visible="state.openReceiptDialog"
      closeOnEscape
      :modal="false"
      :breakpoints="orderDialogBreakpoints"
      :dismissableMask="true"
      keepInViewPort
    >
      <Receipt :transaction_id="state.transactionIdReceipt" />
    </Dialog>

    <Dialog
      v-model:visible="state.deleteTransactionDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Custom note"
      :modal="true"
      class="p-fluid"
    >
      <Textarea
        v-model="state.deleteTransactionNote"
        :autoResize="true"
        rows="4"
        placeholder="Delete transaction note"
      />
      <Button
        @click="deleteTransactionFunction(state.deleteTransactionTransactionId)"
        >Submit</Button
      >
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, watch } from "vue"
  import { useToast } from "primevue/usetoast"
  import { useConfirm } from "primevue/useconfirm"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import Receipt from "@/pages/Receipt.vue"
  import CustomerApi from "@/api/customers"
  import PaymentMethodsApi from "@/api/payment_methods"
  import {
    convertDateForPost,
    dfc_without_zone,
    dfa
  } from "@/service/DateFormat.js"
  import cloneDeep from "lodash.clonedeep"

  const toast = useToast()
  const confirm = useConfirm()
  const customerStore = useCustomerOrder()
  const customerApi = new CustomerApi()
  const paymentMethodsApi = new PaymentMethodsApi()

  const $removeUnusedProps = inject("$removeUnusedProps")
  const $fc = inject("$formatCurrency")

  const props = defineProps({
    orderId: String,
    rentPeriodId: {
      type: String,
      default: null
    },
    resetFunction: {
      type: Function
    }
  })

  const state = reactive({
    transactionsRentPeriod: [],
    originalTransactionsRentPeriod: [],
    transactionsOrder: [],
    originalTransactionsOrder: [],
    transactions: [],
    transactionsEditMode: {},
    transactionIdReceipt: null,
    openReceiptDialog: false,
    savingTransactions: false,
    deletingTransactions: false,
    deleteTransactionDialog: false,
    deleteTransactionNote: "",
    deleteTransactionTransactionId: null,
    loadingTransaction: false
  })

  let paymentOptions = []

  const columns = [
    { field: "transaction_effective_date", header: "Transaction Date" },
    { field: "payment_type", header: "Payment Type" },
    { field: "notes", header: "Notes" },
    { field: "amount", header: "Amount" },
    { field: "credit_card_object", header: "Account Info" }
  ]

  const orderDialogBreakpoints = computed(() => ({
    "2000px": "80vw",
    "1400px": "80vw",
    "1200px": "75vw",
    "992px": "95vw",
    "600px": "100vw",
    "480px": "100vw",
    "320px": "100vw"
  }))

  const isRental = computed(() => customerStore.order?.type === "RENT")

  const isInEditMode = (id) => {
    return state.transactionsEditMode[id]
  }

  const calculateOrderTransactionType = () => {
    const transactions = [...customerStore.order.transaction_type_order]
      .filter((tx) => !tx.credit_card_object)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

    const mappedTransactions = mapTransactionTypes(transactions, null)
    return mappedTransactions.concat(historyTransactions.value)
  }

  const historyTransactions = computed(() => {
    if (customerStore.order && customerStore.order.credit_card) {
      return customerStore.order.credit_card
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .map((c) => {
          const response = c.response_from_gateway
          let approved = false,
            note = "",
            amount = 0,
            accountNumber = ""

          // Simplifying transaction status checks
          if (response) {
            if (response.transactionResponse?.messages?.length) {
              approved = response.transactionResponse.messages[0].code === "1"
              amount = response.payment_amount || response.auth_amount
              note =
                response.result_code === "A" || approved
                  ? "approved"
                  : "declined"
              accountNumber = response.transactionResponse.accountNumber
            } else if (response.metadata) {
              approved = response.status === "succeeded"
              amount = response.amount / 100
              note = approved ? "approved" : "declined"
              accountNumber = "XXXX"
            } else if (response.retref) {
              approved = response.respstat === "A"
              amount = response.payment_amount
              note = approved ? "approved" : "declined"
              accountNumber = response.account.slice(-4)
            }
          }

          return {
            amount,
            payment_type: "CREDIT CARD",
            transaction_effective_date: `${dfa(c.created_at)}`,
            notes: `${c.card_type} | ${c.merchant_name} | ${note} | ${accountNumber}`
          }
        })
    }
    return []
  })

  const mapTransactionTypes = (transactions, totalAmount = null) => {
    return transactions.map((tx) => {
      return {
        id: tx.id,
        transaction_effective_date: dfc_without_zone(
          tx.transaction_effective_date
        ),
        payment_type: tx.payment_type,
        notes: tx.notes,
        amount: totalAmount || tx.amount
      }
    })
  }

  const refresh = async () => {
    try {
      state.loadingTransaction = true
      const { data } = await customerApi.getOrderByDisplayId(
        customerStore.order.display_order_id
      )
      const order = data.value

      if (isRental.value && props.rentPeriodId) {
        const rentPeriod =
          order.rent_periods?.find((obj) => obj.id === props.rentPeriodId)
            ?.transaction_type_rent_period || []

        const moddedTransactions = await Promise.all(
          rentPeriod.map(async (transaction) => {
            const amountResponse = await customerApi.getGroupedTransactions(
              transaction.id
            )
            const totalAmount = amountResponse.data.value.reduce(
              (acc, curr) => acc + curr.amount,
              0
            )
            return mapTransactionTypes([transaction], totalAmount)
          })
        )

        const flattenedTransactions = moddedTransactions.flat()

        state.transactionsRentPeriod = [...flattenedTransactions]
        state.originalTransactionsRentPeriod = cloneDeep(flattenedTransactions)
        state.transactionsEditMode = flattenedTransactions.reduce(
          (acc, item) => {
            acc[item.id] = false
            return acc
          },
          {}
        )
      }

      if (!isRental.value || !props.rentPeriodId) {
        state.transactionsOrder = [...calculateOrderTransactionType()]
        state.originalTransactionsOrder = cloneDeep(state.transactionsOrder)
        state.transactionsEditMode = state.transactionsOrder.reduce(
          (acc, item) => {
            acc[item.id] = false
            return acc
          },
          {}
        )
      }

      state.transactions = []
      state.transactions = isRental.value
        ? [...state.transactionsRentPeriod]
        : [...state.transactionsOrder]
    } catch (error) {
      console.error("Refresh Error:", error)
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Unable to refresh transactions."
      })
    } finally {
      state.loadingTransaction = false
    }
  }

  const editToggle = (transactionId) => {
    state.transactionsEditMode[transactionId] =
      !state.transactionsEditMode[transactionId]
  }

  const deleteTransactionFunction = async (transactionId) => {
    try {
      const { error } = await customerApi.removeTransaction(transactionId)
      if (error?.value) {
        toast.add({
          severity: "error",
          group: "br",
          summary: "Error",
          detail: "Error deleting transaction."
        })
      } else {
        toast.add({
          severity: "success",
          group: "br",
          summary: "Success",
          detail: "Successfully deleted transaction."
        })

        const { data: noteData } = await customerApi.getOrderById(props.orderId)
        const lastNote = noteData.value.note.slice(-1)[0] || {}

        const requestData = {
          title: state.deleteTransactionNote,
          content: `${lastNote?.content} ${state.deleteTransactionNote}`,
          order_id: customerStore.order.id
        }
        if (lastNote.id) {
          await customerApi.updateNote(lastNote.id, requestData)
        } else {
          await customerApi.saveNote(requestData)
        }
        state.deleteTransactionDialog = false
        await props.resetFunction(true)
      }
    } catch (error) {
      console.error("Delete Transaction Error:", error)
      toast.add({
        severity: "error",
        group: "br",
        summary: "Error",
        detail: "Could not submit delete note."
      })
    } finally {
      state.deletingTransactions = false
    }
  }

  const deleteTransaction = (event, data) => {
    console.log(event)
    state.deletingTransactions = true
    confirm.require({
      target: event.currentTarget,
      message: "Do you want to remove this transaction?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger",
      accept: () => {
        state.deleteTransactionDialog = true
        state.deleteTransactionTransactionId = data.id
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Canceled",
          detail: "Transaction removal canceled."
        })
        state.deletingTransactions = false
      }
    })
  }

  const update = async (data) => {
    state.savingTransactions = true
    const id = data.id
    try {
      let dataToPatch = cloneDeep(data)

      const originalTransactionList = isRental.value
        ? state.originalTransactionsRentPeriod
        : state.originalTransactionsOrder
      dataToPatch = $removeUnusedProps(
        dataToPatch,
        originalTransactionList.find((el) => el.id === id)
      )

      const { error } = await customerApi.editTransactionType(id, dataToPatch)
      if (error?.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating transaction type."
        })
      } else {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Successfully updated transaction type."
        })
      }
    } catch (error) {
      console.error("Update Transaction Error:", error)
      toast.add({
        severity: "error",
        summary: "Update Failed",
        detail: "Could not update transaction."
      })
    } finally {
      state.savingTransactions = false

      if (isRental.value) {
        await props.resetFunction(true)
      } else {
        await props.resetFunction()
      }
      editToggle(id)
    }
  }

  const openReceipt = (data) => {
    state.transactionIdReceipt = data.id
    state.openReceiptDialog = true
  }

  onMounted(async () => {
    await refresh()
    const paymentData = await paymentMethodsApi.getAllPaymentMethods()
    paymentOptions = paymentData.data.value.map((el) => ({
      label: el.display_name,
      value: el.name
    }))
  })

  watch(
    () => customerStore.order,
    async () => {
      console.log("order changed")
      await refresh()
    }
  )

  watch(
    () => props.rentPeriodId,
    async () => {
      await refresh()
    }
  )
</script>
