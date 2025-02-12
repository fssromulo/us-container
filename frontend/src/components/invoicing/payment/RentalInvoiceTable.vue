<template>
  <div class="flex-col">
    <div class="flex justify-center" v-if="!verticalTable">
      <DataTable v-if="state.tableData.length > 0" :value="state.tableData">
        <Column
          v-for="(column, index) in state.visibleColumns"
          :key="index"
          :field="column.field"
          :header="column.header"
        >
        </Column>
      </DataTable>
    </div>

    <div v-else v-for="(item, i) in state.tableData" :key="i">
      <Divider class="mb-4" />
      <div class="mt-2"></div>
      <table class="justify-center ml-12">
        <tbody>
          <tr v-for="(column, index) in state.visibleColumns" :key="index">
            <td>{{ column.header }}</td>
            <td>{{ item[column.field] }} </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="flex justify-center">
      <DataTable
        :value="state.orderSummaryItemsDict"
        showHeaders="false"
        style="min-width: 350px"
      >
        <template #header>
          <div class="font-bold">Order Summary</div>
        </template>
        <Column field="name"></Column>
        <Column field="value"></Column>
        <template #footer>
          <div class="flex justify-left">
            <div class="font-bold">Amount Due:</div>
            <div class="font-bold ml-3">{{
              $fc(selectedRentPeriod.calculated_rent_period_total_balance)
            }}</div>
          </div>
        </template>
      </DataTable>
    </div>
  </div>
  <!-- Closing div for class="flex-col" -->
</template>

<script setup>
  import CustomerApi from "@/api/customers"

  import { reactive, onMounted, inject, computed } from "vue"
  const $fc = inject("$formatCurrency")
  const customerApi = new CustomerApi()

  const props = defineProps({
    order: {
      type: Object,
      default: null
    },
    rentPeriodId: {
      type: String,
      default: null
    },
    verticalTable: {
      type: Boolean,
      default: null
    }
  })

  const state = reactive({
    tableData: [],
    orderSummaryItemsDict: [],
    late_fee_header: "",
    visibleColumns: []
  })

  const selectedRentPeriod = computed(() => {
    return props.order.rent_periods.find(
      (rentPeriod) => rentPeriod.id === props.rentPeriodId
    )
  })

  onMounted(async () => {
    const { data, error } =
      await customerApi.generate_web_rental_order_table_data(
        props.order.id,
        props.rentPeriodId
      )
    const columns_data = Object.values(data.value.columns_data[2][0])
    const table_data = data.value.columns_data[1]
    const subtotals = data.value.subtotals
    state.visibleColumns = columns_data
    state.tableData = table_data.map((el, key) => {
      let data = {}
      columns_data.forEach((column, index) => {
        data[column.field] = el["item_" + index]
      })
      return data
    })
    state.orderSummaryItemsDict = subtotals.map((el, key) => {
      return {
        name: el.name,
        value: el.value
      }
    })
    state.late_fee_header = data.value.late_fee_header
  })
</script>
