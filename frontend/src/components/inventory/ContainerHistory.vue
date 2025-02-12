<template v-if="state.order">
  <div style="max-width: 95vw">
    <div class="grid grid-cols-3 grid-cols-12 gap-4 gap-20 mt-2">
      <!-- Column 1 -->
      <div class="col-span-1">
        <div class="mb-2 text-xl font-medium border-b text-900 dark:text-0">
          {{ props.container.product?.title }} (ID:
          {{ props.container.id.substring(0, 4) }})
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Created On: {{ dfm(props.container.created_at) }}
        </div>
        <div
          v-if="props.container.invoiced_at"
          class="mb-2 text-xl font-medium text-600 dark:text-200"
        >
          Invoiced Date: {{ dfm(props.container.invoiced_at) }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Pickup Date: {{ dfm(props.container.pickup_at) }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Days In Yard: {{ calculateDaysInYard() }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Days Rented: {{ calculateDaysRented() }}
        </div>
      </div>

      <!-- Column 2 -->
      <div class="col-span-1">
        <div class="mt-8 mb-2 text-xl font-medium text-600 dark:text-200">
          Container #: {{ props.container.container_number }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Container Release: {{ props.container.container_release_number }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Status: {{ props.container.status }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Payment Type: {{ props.container.payment_type }}
        </div>
      </div>

      <!-- Column 3 -->
      <div class="col-span-1 mt-8">
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Paid On: {{ dfm(props.container.paid_at) }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Purchased For: {{ $fc(props.container.total_cost) }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Rental revenue: {{ $fc(state.calculateRentalIncome) }}
        </div>
        <div class="mb-2 text-xl font-medium text-600 dark:text-200">
          Invoice #: {{ props.container.invoice_number }}
        </div>
      </div>
    </div>

    <DataTable
      v-if="!state.loading"
      ref="dt"
      :value="state.mappedHistory"
      :style="`width: ${tableWidth}`"
      scrollHeight="60vh"
      dataKey="id"
      :paginator="true"
      scrollDirection="both"
      :rows="25"
      :filters="state.filters"
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      :rowsPerPageOptions="[10, 25, 50]"
      currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Container History"
      responsiveLayout="scroll"
    >
      <Column
        field="line_item.order.display_order_id"
        header="Order Id"
        style="width: 120px"
      >
        <template #body="slotProps">
          <Button
            class="p-button-rounded"
            @click="openOrder(slotProps.data.line_item.order.display_order_id)"
            >{{ slotProps.data.line_item.order.display_order_id }}</Button
          >
        </template>
      </Column>
      <Column
        v-for="(col, i) in state.columns"
        :key="col.order_id + col.line_item_id + i.toString()"
        :field="col.field"
        :header="col.display"
        :sortable="col.sortable"
        :style="col.style"
      ></Column>
    </DataTable>
  </div>

  <Dialog
    v-model:visible="state.orderDetailDialog"
    :style="{ height: '100vh' }"
    :breakpoints="{
      '2000px': '45vw',
      '1400px': '55vw',
      '1200px': '65vw',
      '992px': '75vw',
      '600px': '100vw',
      '480px': '100vw',
      '320px': '100vw'
    }"
    closeOnEscape
    :dismissableMask="true"
    keepInViewPort
    modal=""
    :draggable="false"
  >
    <template #header>
      <div class="flex align-items">
        <div class="flex">
          <p :class="smAndSmaller ? 'text-xl' : 'text-3xl'">
            Invoice - {{ state.customerOrder.display_order_id }}
          </p>
        </div>
      </div>
    </template>
    <CustomerOrderDetail :customerOrderProp="state.customerOrder" />
  </Dialog>
</template>

<script setup>
  import { ref, reactive, onMounted, computed, inject } from "vue"
  import { dfm } from "@/service/DateFormat"
  import CustomerService from "@/service/Customers"
  import CustomerOrderDetail from "@/components/invoicing/CustomerOrderDetail.vue"
  import CustomerApi from "@/api/customers"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  const $DateTime = inject("$DateTime")
  const $fc = inject("$formatCurrency")
  const customerApi = new CustomerApi()

  const customerService = new CustomerService()
  const customersStore = useCustomerOrder()

  const props = defineProps({
    container: {
      type: Object,
      default: {}
    }
  })

  const calculateDaysDifference = (start, end, end_is_short) => {
    let endDateTime
    if (!end_is_short) {
      endDateTime = $DateTime.fromISO(end, { setZone: true })
    } else {
      const [month, day, year] = end.split("/")
      const fullYear = "20" + year
      const endDate = `${fullYear}-${month}-${day}T00:00:00.000Z`
      endDateTime = $DateTime.fromISO(endDate)
    }

    const startDateTime = $DateTime.fromISO(start, { setZone: true })

    const diff = startDateTime.diff(endDateTime, "days").toObject().days

    return Math.abs(Number(diff).toFixed(0))
  }

  const openOrder = async (orderId) => {
    state.individualOrderLoading = orderId
    await getOrderByDisplayId(orderId)
    state.individualOrderLoading = null
    state.orderDetailDialog = true
  }
  const getOrderByDisplayId = async (id) => {
    const { data, isLoading, error } = await customerApi.getOrderByDisplayId(id)

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading order",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.customerOrder = data.value
      customersStore.setOrder(data.value)
    }
  }

  const calculateDaysRented = (history) => {
    const daysRented = props.container.rental_history.reduce((acc, curr) => {
      if (
        curr.line_item?.order?.calculated_paid_thru == null ||
        curr.line_item?.order?.calculated_paid_thru == "NOT APPLICABLE"
      )
        return 0
      let daysRented = calculateDaysDifference(
        curr.rent_started_at,
        curr.line_item?.order?.calculated_paid_thru,
        true
      )
      return daysRented
    }, 0)
    return daysRented
  }

  const calculateDaysInYard = (history) => {
    const daysRented = props.container.rental_history.reduce((acc, curr) => {
      if (
        curr.line_item?.order?.calculated_paid_thru == null ||
        curr.line_item?.order?.calculated_paid_thru == "NOT APPLICABLE"
      )
        return 0
      let daysRented = calculateDaysDifference(
        curr.rent_started_at,
        curr.line_item?.order?.calculated_paid_thru,
        true
      )
      return daysRented
    }, 0)
    let ownershipStartedAt = props.container.pickup_at
    if (ownershipStartedAt == undefined) {
      ownershipStartedAt = props.container.created_at
    }
    const totalDaysOwned = calculateDaysDifference(
      ownershipStartedAt,
      $DateTime.now().toISO(),
      false
    )
    return Math.abs(totalDaysOwned - daysRented)
  }

  const calculateRentalIncome = async (history) => {
    if (props.container) {
      const display_order_id = history.line_item.order.display_order_id

      const data_request = {
        display_order_id: display_order_id,
        start_date: history.rent_started_at,
        end_date: history.rent_ended_at
      }

      const { data, error } = await customerApi.transactions_rent_periods(
        data_request
      )
      state.calculateRentalIncome = data.value
      return data.value
    } else {
      return 0
    }
  }

  const calculateTotalRentalRevenue = computed(() => {
    if (props.container && props.container.rental_history.length > 0)
      return state.mappedHistory == null
        ? 0
        : state.mappedHistory.reduce((acc, curr) => {
            return acc + curr.rental_revenue
          }, 0)
    return 0
  })

  const fetchRentalIncome = async (history) => {
    const income = await calculateRentalIncome(history)
    history.rental_revenue = income
    history.display_rental_revenue = $fc(income)
    state.mappedHistory.push(history)
  }

  const mappedHistory = async () => {
    state.mappedHistory = []
    if (props.container && props.container.rental_history) {
      const map = props.container.rental_history.map((r) => {
        return {
          ...r,
          order_created_at: dfm(r.line_item?.order.created_at),
          display_rent_started_at: dfm(r.rent_started_at),
          display_rent_ended_at:
            r.rent_ended_at != null ? dfm(r.rent_ended_at) : "Still Ongoing",
          rental_revenue: 0,
          display_rental_revenue: 0,
          display_monthly_owed: $fc(r.line_item?.monthly_owed),
          days_rented: calculateDaysDifference(
            r.rent_started_at,
            r.rent_ended_at == null
              ? new Date().toISOString()
              : r.rent_ended_at,
            false
          )
        }
      })

      const promises = []

      map.forEach(async (el) => {
        promises.push(fetchRentalIncome(el))
      })
      await Promise.allSettled(promises)
    }
  }

  const state = reactive({
    showEditNote: false,
    mappedHistory: [],
    isLoading: false,
    orderDetailDialog: false,
    customerOrder: null,
    calculateRentalIncome: 0,
    note: {
      title: "",
      content: ""
    },
    columns: [
      {
        field: "display_rent_started_at",
        display: "Rent Started",
        sortable: true,
        style: "max-width: 160px"
      },
      {
        field: "display_rent_ended_at",
        display: "Rent Ended",
        sortable: true,
        style: "max-width: 160px"
      },
      {
        field: "days_rented",
        display: "Days rented",
        sortable: true,
        style: "max-width: 100px"
      },
      {
        field: "display_monthly_owed",
        display: "Monthly Price",
        sortable: true,
        style: "max-width: 100px"
      },
      {
        field: "display_rental_revenue",
        display: "Rental Revenue",
        sortable: true,
        style: "max-width: 100px"
      }
    ]
  })

  onMounted(async () => {
    await mappedHistory()
  })
</script>
