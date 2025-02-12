<template>
  <div v-if="props.isBiWeeklyPicker" class="flex flex-col h-full">
    <div class="flex items-center justify-center shrink-0">
      <p class="ml-4 text-2xl" v-if="state.currentDateRange">
        {{ dfm(state.currentDateRange[0]) }} -
        {{ dfm(state.currentDateRange[1]) }}
      </p>
    </div>
    <div class="flex items-center justify-center shrink-0">
      <Paginator
        @page="selectPage"
        v-model:first="state.page"
        :rows="1"
        :totalRecords="state.datesList.length"
      ></Paginator>
    </div>
  </div>
  <div v-if="props.isMonthPicker" class="flex flex-col h-full">
    <div class="flex items-center justify-center shrink-0">
      <label class="text-2xl" for="range">Select month</label>
    </div>
    <div class="flex items-center justify-center shrink-0">
      <label class="text-2xl" for="range">{{
        state.monthDate &&
        $DateTime.fromJSDate(state.monthDate).toFormat("MMMM")
      }}</label>
    </div>
    <div class="flex items-center justify-center shrink-0 mt-4">
      <DatePicker
        class="ml-4 w-full p-input-large"
        inputId="range"
        v-model="state.monthDate"
        view="month"
        :placeholder="month"
        :minDate="state.minDate"
      />
    </div>
  </div>
</template>

<script setup>
  import { reactive, watch, onMounted, inject } from "vue"
  import CustomerOrderService from "@/service/Customers.js"
  import { useToast } from "primevue/usetoast"
  import { dfm } from "@/service/DateFormat"
  const toast = useToast()
  const emit = defineEmits(["selectedDates"])
  const $DateTime = inject("$DateTime")
  const customerOrderService = new CustomerOrderService()

  const props = defineProps(["isMonthPicker", "isBiWeeklyPicker"])
  const month = $DateTime.local().monthLong

  const calculateBiWeeklyPayPeriods = () => {
    const april = $DateTime.fromObject({ year: 2023, month: 4, day: 1 })
    state.minDate = april.toJSDate()
    const startOfThisMonth = april.startOf("month")

    let months = []
    for (let i = 0; i < 24; i++) {
      const start = startOfThisMonth.plus({ months: i })
      const end = start.endOf("month") // Calculate the end of the month dynamically
      months.push([start, end])
    }

    let payPeriods = []
    months.forEach((month) => {
      let start = month[0]
      let end = month[1]
      const midPointDate = start.plus({ days: 14 })
      payPeriods.push([start, midPointDate])
      payPeriods.push([midPointDate.plus({ day: 1 }), end])
    })

    state.datesList = payPeriods
  }

  const selectPage = (e) => {
    state.page = e.page
    state.currentDateRange = state.datesList[e.page]
    emit(
      "selectedDates",
      state.currentDateRange[0].toFormat("M/d/yy"),
      state.currentDateRange[1].toFormat("M/d/yy")
    )
  }

  // const payPeriodDateRangesList = createPayPeriodDateRangesList();
  onMounted(() => {
    if (props.isBiWeeklyPicker) {
      calculateBiWeeklyPayPeriods()
    }
    if (props.isMonthPicker) {
      state.monthDate = $DateTime.local().toJSDate()
    }
  })

  const state = reactive({
    start_date: null,
    end_date: null,
    dateRange: null,
    datesList: [],
    currentDateRange: null,
    monthDate: null,
    minDate: null,
    page: 0
  })

  watch(
    () => state.monthDate,
    (newVal) => {
      if (newVal) {
        state.start_date = $DateTime.fromJSDate(newVal).startOf("month")
        state.end_date = $DateTime.fromJSDate(newVal).endOf("month")
        if (state.start_date && state.end_date) {
          state.start_date = state.start_date.toFormat("M/d/yy")
          state.end_date = state.end_date.toFormat("M/d/yy")
        }
        emit("selectedDates", state.start_date, state.end_date)
      }
    }
  )

  watch(
    () => state.datesList,
    (newVal) => {
      if (newVal) {
        // const today = $DateTime.local().plus({ days: 13 });
        const today = $DateTime.local()
        let currentPayPeriod = newVal.findIndex((payPeriod) => {
          const start = payPeriod[0]
          const end = payPeriod[1]
          return today >= start && today <= end
        })
        if (currentPayPeriod == -1) {
          // Current pay period falls outside the range of any given period
          currentPayPeriod = newVal.findIndex((payPeriod) => {
            const end = payPeriod[1]
            return today <= end
          })
          currentPayPeriod -= 1
        }
        selectPage({ page: currentPayPeriod })
      }
    }
  )

  watch(
    () => state.page,
    (newVal) => {
      if (newVal) {
        console.log(newVal)
      }
    }
  )
</script>
