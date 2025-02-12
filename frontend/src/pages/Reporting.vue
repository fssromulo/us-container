<template>
  <div>
    <div
      class="grid grid-cols-12 gap-4 formgrid p-fluid"
      v-if="state.currentPage === ''"
    >
      <div
        class="p-4 col-span-12 xs:col-10 md:col-span-5 xl:col-span-2"
        :class="{ 'xl:col-offset-1': idx == 0 || !(idx % 5) }"
        v-for="(name, idx) in filteredComponents"
        :key="idx"
      >
        <div class="p-4 bg-0 dark:bg-900 shadow rounded-border">
          <a
            v-ripple
            class="flex px-6 py-4 transition-colors cursor-pointer md:px-2 items-center hover:bg-100 dark:hover:bg-700 rounded-border duration-150 p-ripple"
            :class="{
              'bg-primary text-primary-contrast hover:bg-primary hover:text-primary-contrast':
                state.currentPage === name,
              'text-700 dark:text-100': state.currentPage !== name
            }"
            @click="setPage(name)"
          >
            <span class="text-lg font-medium md:text-2xl">{{ name }}</span>
          </a>
        </div>
      </div>
    </div>
    <div class="flex ml-2 justify-content-left" v-else>
      <a
        v-ripple
        class="flex px-6 py-4 cursor-pointer md:px-2 items-center"
        @click="setPage()"
      >
        <span class="text-lg font-medium md:text-2xl"
          ><i class="pi pi-arrow-left"></i>&nbsp; Back</span
        >
      </a>
      <p class="flex px-6 py-4 cursor-pointer md:px-2 md:text-2xl items-center">
        {{ state.currentPage }}
      </p>
    </div>
    <ReportingSearches v-if="state.currentPage === 'Quotes Searches'" />
    <ContainerSalesByState
      v-if="state.currentPage === 'Container Sales By State'"
    />
    <ContainerConditionByState
      v-if="state.currentPage === 'Container Condition By State'"
    />
    <ContainerConditionByStatePercentages
      v-if="state.currentPage === 'Container Condition By State %'"
    />
    <AverageProfitPerContainer
      v-if="state.currentPage === 'Average Profit Per Container'"
    />
    <QuotedRevenue
      v-if="state.currentPage === '# of Orders & Quoted Revenue'"
    />
    <TopZipCodes v-if="state.currentPage === 'Top Zip Codes'" />
    <OrderByPaymentTypes v-if="state.currentPage === 'Order by Payment Type'" />
    <AgentRanking v-if="state.currentPage === 'Agent Ranking'" />
    <ManagerRanking v-if="state.currentPage === 'Manager Ranking'" />
    <DeliveryEfficiency v-if="state.currentPage === 'Delivery Efficiency'" />
    <DepositReport v-if="state.currentPage === 'Deposit Report'" />
    <FeeReport v-if="state.currentPage === 'Fee Report'" />
    <SalesTaxReport v-if="state.currentPage === 'Sales Tax Report'" />
    <Rankings v-if="state.currentPage === 'Rankings'" />
    <VendorInventory v-if="state.currentPage === 'Vendor Inventory'" />

    <UsersWithoutSales v-if="state.currentPage === 'Users Without Sales'" />
    <NotesRankings v-if="state.currentPage === 'Notes Rankings'" />
  </div>
</template>

<script setup>
  import ReportingSearches from "@/components/reporting/ReportingSearches.vue"
  import ContainerSalesByState from "@/components/reporting/ContainerSalesByState.vue"
  import ContainerConditionByState from "@/components/reporting/ContainerConditionByState.vue"
  import ContainerConditionByStatePercentages from "@/components/reporting/ContainerConditionByStatePercentages.vue"
  import AverageProfitPerContainer from "@/components/reporting/AverageProfitPerContainer.vue"
  import QuotedRevenue from "@/components/reporting/QuotedRevenue.vue"
  import TopZipCodes from "@/components/reporting/TopZipCodes.vue"
  import OrderByPaymentTypes from "@/components/reporting/OrderByPaymentTypes.vue"
  import AgentRanking from "@/components/reporting/AgentRanking.vue"
  import ManagerRanking from "@/components/reporting/ManagerRanking.vue"
  import DeliveryEfficiency from "@/components/reporting/DeliveryEfficiency.vue"
  import DepositReport from "@/components/reporting/DepositReport.vue"
  import FeeReport from "@/components/reporting/FeeReport.vue"
  import SalesTaxReport from "@/components/reporting/SalesTaxReport.vue"
  import VendorInventory from "@/components/reporting/VendorInventory.vue"
  import UsersWithoutSales from "@/components/reporting/UsersWithoutSales.vue"
  import NotesRankings from "@/components/reporting/NotesRankings.vue"
  import Rankings from "@/components/reporting/Rankings.vue"
  import { useRouter } from "vue-router"
  import { useUsers } from "@/store/modules/users"
  import UsersService from "@/service/User"
  import UserApi from "@/api/user"

  import { computed, inject, reactive, onMounted, ref } from "vue"
  const $route = inject("$route")
  const usersService = new UsersService()
  const userApi = new UserApi()
  const usersStore = useUsers()

  const filteredComponents = computed(() => {
    if (usersStore.currentUser.role_name == "admin") {
      return state.componentList
    }
    return component === "Quotes Searches"
  })

  const home = ref({
    icon: "pi pi-home",
    route: "/introduction"
  })
  const items = ref([
    { label: "Components" },
    { label: "Form" },
    { label: "InputText", route: "/inputtext" }
  ])
  const setPageFromQueryParam = () => {
    if ($route.currentRoute.value.query.hasOwnProperty("report")) {
      let routePage = $route.currentRoute.value.query["report"]
      state.currentPage = routePage
      state.active = state.componentList.indexOf(routePage) || -1
    } else {
      state.currentPage = ""
      state.active = -1
    }
  }
  const setPage = (componentName = "") => {
    state.active = state.componentList.indexOf(componentName)
    state.currentPage = componentName
  }

  const state = reactive({
    active: -1,
    currentPage: "",
    componentList: [
      "Quotes Searches",
      "Container Sales By State",
      "Container Condition By State",
      "Container Condition By State %",
      "Average Profit Per Container",
      "# of Orders & Quoted Revenue",
      "Top Zip Codes",
      "Order by Payment Type",
      "Agent Ranking",
      "Manager Ranking",
      "Delivery Efficiency",
      "Deposit Report",
      "Fee Report",
      "Sales Tax Report",
      "Users Without Sales",
      "Vendor Inventory",
      "Rankings"
    ]
  })

  onMounted(async () => {
    setPageFromQueryParam()
    if (usersStore.users.length === 0) {
      const { data } = await userApi.getUsers()
      usersStore.setUsers(data.value.map((u) => usersService.dtoUser(u)))
    }
    if (usersStore.cms?.feature_flags?.notes_reminder) {
      state.componentList.push("Notes Rankings")
    }
  })
</script>
