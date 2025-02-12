<template>
  <div class="grid grid-cols-12 card">
    <div class="col-span-12 field xs:col-10 md:col-span-12 xl:col-span-12">
      <label for="range"> Select date range</label>
      <DatePicker
        v-model="dates"
        selectionMode="range"
        :manualInput="false"
        style="margin-left: 10px"
      />
      <label for="user" style="margin-left: 10px"> Select user </label>
      <Select
        :options="users"
        v-model="state.selectedUser"
        optionLabel="name"
        placeholder="ALL"
        style="margin-left: 10px"
      />
    </div>
    <Chart type="bar" :data="chartData" :options="chartOptions" class="chart" />
    <div class="card">
      <DataTable :value="postalCodes" tableStyle="min-width: 50rem">
        <Column field="postal_code" header="postal_code"></Column>
        <Column field="unique_clicks" header="unique clicks"></Column>
        <Column field="occurrences" header="clicks"></Column>
        <Column field="users" header="users"></Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
  import QuoteSearchesApi from "@/api/search_quotes"
  import { reactive, watch, onMounted, computed, ref } from "vue"
  import { useUsers } from "@/store/modules/users"
  import UsersService from "@/service/User"
  import UserApi from "@/api/user"

  const usersService = new UsersService()
  const userApi = new UserApi()

  const userStore = useUsers()
  const quoteSearchesApi = new QuoteSearchesApi()
  const dates = ref([new Date(2024, 1, 1), new Date()])
  const postalCodes = ref()
  const users = ref()

  const state = reactive({
    date1: null,
    date2: null,
    selectedUser: "ALL"
  })

  const getUsers = async () => {
    const { data } = await userApi.getUsers()
    const mappedUsers = data.value.map((d) => usersService.dtoUser(d))
    userStore.setUsers(mappedUsers)
  }
  const home = ref({
    icon: "pi pi-home"
  })
  const search = async () => {
    const timezoneOffsetMinutes = new Date().getTimezoneOffset()
    state.date1 -= timezoneOffsetMinutes * 60
    state.date2 -= timezoneOffsetMinutes * 60

    let zone = "UTC"
    const { data, error } = await quoteSearchesApi.getQuoteSearches(
      state.date1,
      state.date2,
      zone,
      state.selectedUser.code
    )
    let values = data._rawValue.map((o) => {
      o["unique_clicks"] = o["users"].length
      o["users"] = o["users"].join(", ")
      return o
    })
    postalCodes.value = values

    const postalCodesList = values.map((obj) => obj.postal_code)
    const occurencesList = values.map((obj) => obj.occurrences)
    chartData.value = setChartData(postalCodesList, occurencesList)
  }

  watch(
    () => state.selectedUser,
    async (newValue, oldValue) => {
      await search()
    }
  )

  watch(
    () => dates.value,
    async (newValue, oldValue) => {
      state.date1 = newValue[0].getTime() / 1000
      if (newValue[1] === null) {
        return
      }
      state.date2 = newValue[1].getTime() / 1000

      await search()
    }
  )

  onMounted(async () => {
    const { data, error } = await quoteSearchesApi.getQuoteSearches(
      undefined,
      undefined,
      null,
      "ALL"
    )

    let values = data._rawValue.map((o) => {
      o["unique_clicks"] = o["users"].length
      o["users"] = o["users"].join(", ")
      return o
    })
    postalCodes.value = values
    const postalCodesList = values.map((obj) => obj.postal_code)
    const occurencesList = values.map((obj) => obj.occurrences)

    chartData.value = setChartData(postalCodesList, occurencesList)
    chartOptions.value = setChartOptions()

    await getUsers()

    const users_list = [{ name: "All", code: "ALL" }]
    users.value = users_list.concat(
      userStore.users
        .map((user) => {
          return {
            name: user.first_name + " " + user.last_name,
            code: user.id
          }
        })
        .sort((a, b) => {
          return a["name"].localeCompare(b["name"])
        })
    )
  })

  const chartData = ref()
  const chartOptions = ref()

  const setChartData = (postalCodesList, occurencesList) => {
    return {
      labels: postalCodesList,
      datasets: [
        {
          label: "Clicks",
          data: occurencesList,
          backgroundColor: "rgba(255, 159, 64, 0.2)",
          borderColor: "rgb(255, 159, 64)",
          borderWidth: 1
        }
      ]
    }
  }
  const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement)
    const textColor = documentStyle.getPropertyValue("--text-color")
    const textColorSecondary = documentStyle.getPropertyValue(
      "--text-color-secondary"
    )
    const surfaceBorder = documentStyle.getPropertyValue("--border")

    return {
      plugins: {
        legend: {
          labels: {
            color: textColor
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: textColorSecondary
          },
          grid: {
            color: surfaceBorder
          }
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: textColorSecondary
          },
          grid: {
            color: surfaceBorder
          }
        }
      }
    }
  }
</script>

<style scoped>
  .chart {
    width: 800px;
  }
</style>
