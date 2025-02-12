<template>
  <section class="flex flex-col w-full">
    <div v-if="verticalTable">
      <div
        v-if="!props.isRentToOwn"
        :key="i"
        v-for="(summaryItem, i) in summaryItemsDict"
      >
        <!-- <hr class="mb-1" /> -->
        <table>
          <tbody>
            <tr>
              <td :class="getClassSummaryColumnName(summaryItem)">
                {{ summaryItem.rowTitle }}:
              </td>
              <td :class="getClassSummaryColumnValue(summaryItem)">
                {{ summaryItem.rowContent }}
              </td>
            </tr></tbody
          >
        </table>
      </div>
      <!-- <hr class="mb-1" /> -->
      <table>
        <tbody>
          <tr class="mb-1" v-if="props.isRentToOwn">
            <td class="text-2xl text-700 dark:text-100"
              >Estimated Monthly Price:</td
            >
            <td class="text-2xl text-900 dark:text-0">
              {{ props.monthlyPrice }}
            </td>
          </tr>
          <tr v-if="!props.isRentToOwn" class="mb-1">
            <td class="text-2xl text-700 dark:text-100">{{ totalTitle }}:</td>
            <td class="text-2xl text-900 dark:text-0">
              {{ grandTotal }}
            </td>
          </tr></tbody
        >
      </table>
      <Divider class="mb-1" />
      <table
        v-if="props.remainingBalance && !props.isRentToOwn && !props.isRent"
      >
        <tbody>
          <tr>
            <td class="text-2xl text-700 dark:text-100">Remaining Balance</td>
            <td class="text-2xl text-900 dark:text-0">
              {{ $fc(props.remainingBalance) }}
            </td>
          </tr></tbody
        >
      </table>
      <table></table>
    </div>
    <div class="mt-2 mb-2" v-else>
      <DataTable :value="summaryItemsDict" :rowClass="getRowClass">
        <Column
          v-if="!props.isRentToOwn"
          field="rowTitle"
          header="Order Summary"
        ></Column>
        <Column v-if="!props.isRentToOwn" field="rowContent"></Column>
        <ColumnGroup :type="!props.remainingBalance ? 'footer' : undefined">
          <Row v-if="props.totalRtoPrice && props.estimatedSalesTax > 0">
            <Column class="text-2xl" footer="Sales Tax" />
            <Column class="text-2xl" :footer="$fc(props.estimatedSalesTax)" />
          </Row>
          <Row v-if="props.totalRtoPrice">
            <Column class="text-2xl" footer="Estimated Monthly Price" />
            <Column class="text-2xl" :footer="props.monthlyPrice" />
          </Row>
          <Row v-if="!props.isRentToOwn">
            <Column class="text-2xl" :footer="totalTitle" />
            <Column class="text-2xl" :footer="grandTotal" />
          </Row>
        </ColumnGroup>
        <ColumnGroup v-if="props.remainingBalance" type="footer">
          <Row v-if="props.remainingBalance !== sumGrandTotal && !props.isRent">
            <Column
              class="text-2xl"
              :footer="
                props.monthlyPrice ? 'Monthly Price' : 'Remaining Balance'
              "
            />
            <Column
              class="text-2xl"
              :footer="
                props.monthlyPrice
                  ? props.monthlyPrice
                  : $fc(props.remainingBalance)
              "
            />
          </Row>
          <Row>
            <Column class="text-2xl" :footer="totalTitle" />
            <Column class="text-2xl" :footer="grandTotal" />
          </Row>
        </ColumnGroup>
      </DataTable>
    </div>
  </section>
</template>

<script setup>
  import { computed, inject } from "vue"
  const $fc = inject("$formatCurrency")

  const props = defineProps({
    /**
     * This will have rowTitle and rowContent attributes
     */
    summaryItemsDict: {
      type: Object,
      default: () => ({})
    },
    downPayment: {
      type: Number,
      default: 0
    },
    sumGrandTotal: {
      type: Number,
      default: 0
    },
    couponDiscount: {
      type: Number,
      default: 0
    },
    isRentToOwn: {
      type: Boolean,
      default: false
    },
    isRent: {
      type: Boolean,
      default: false
    },
    verticalTable: {
      type: Boolean,
      default: false
    },
    remainingBalance: {
      type: Number
    },
    totalRtoPrice: {
      type: Number
    },
    monthlyPrice: {
      type: Number,
      default: 0
    },
    estimatedSalesTax: {
      type: Number
    },
    appliedCoupons: {
      type: Array
    }
  })

  const grandTotal = computed(() => {
    if (props.isRent) return props.downPayment
    return props.sumGrandTotal
  })

  const getRowClass = (data) => {
    if (!data.hasOwnProperty("isCoupon")) {
      return ""
    } else {
      return "text-green-500"
    }
  }

  const getClassSummaryColumnName = (data) => {
    if (!data.hasOwnProperty("isCoupon")) {
      return "text-2xl text-700 dark:text-100"
    }

    return "text-2xl text-green-500"
  }

  const getClassSummaryColumnValue = (data) => {
    if (!data.hasOwnProperty("isCoupon")) {
      return "text-2xl text-900 dark:text-0"
    }

    return "text-2xl text-green-500"
  }

  const totalTitle = computed(() => {
    if (props.isRent) {
      return "Amount Due"
    }
    return props.isRentToOwn ? "30 Day Price" : "Grand Total"
  })
</script>

<style scoped>
  .green-row {
    background-color: #c3e6cb;
  }
</style>
