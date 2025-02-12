<template>
  <div>
    <ul
      class="flex p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900"
      v-if="!smAndSmaller"
    >
      <template :key="idx" v-for="(name, idx) in filteredComponentList">
        <li class="pr-4">
          <a
            v-ripple
            class="flex items-center px-6 py-4 duration-150 cursor-pointer p-button p-component hover:bg-100 dark:hover:bg-700 rounded-border p-ripple"
            :class="{
              'p-button-primary': state.active === idx,
              'p-button-secondary': state.active !== idx
            }"
            @click="state.active = idx"
          >
            <span class="text-2xl font-medium" style="color: #f5f9ff">{{
              name
            }}</span>
          </a>
        </li>
        <li class="flex items-center">
          <div style="width: 1px; height: 50%" class="border border-r"></div>
        </li>
      </template>
    </ul>
    <div>
      <Select
        v-if="smAndSmaller"
        class="m-8"
        style="width: 80vw"
        scrollHeight="330px"
        v-model="state.active"
        :options="[
          ...filteredComponentList.map((e, index) => {
            return { value: index, label: e }
          })
        ]"
        :placeholder="`Select an option`"
        optionLabel="label"
        optionValue="value"
      />
    </div>
    <RankingsReport
      v-if="state.active === filteredComponentList.indexOf('Rankings Report')"
    ></RankingsReport>
    <CommissionsReport
      v-if="
        state.active === filteredComponentList.indexOf('Commissions Report')
      "
    ></CommissionsReport>
    <CommissionsAgentsReport
      v-if="
        state.active ===
        filteredComponentList.indexOf('Individual Commission Report')
      "
    ></CommissionsAgentsReport>
    <Rankings
      :showManagingAgentOnly="true"
      v-if="
        state.active === filteredComponentList.indexOf('Rankings as Managers')
      "
    ></Rankings>
    <Rankings
      v-if="state.active === filteredComponentList.indexOf('Rankings All')"
    ></Rankings>
    <CommissionHighlight
      v-if="
        state.active === filteredComponentList.indexOf('Commission Highlight')
      "
    />
    <CommissionHighlight
      v-if="state.active === filteredComponentList.indexOf('Team Highlight')"
      :isTeamCommission="true"
    />
    <TeamHighlightReport
      v-if="
        state.active === filteredComponentList.indexOf('Team Highlight Report')
      "
      :isTeamCommission="true"
    />
    <CommissionsTeamIndividualReport
      v-if="
        state.active === filteredComponentList.indexOf('Team Commission Report')
      "
      :non-dialog-page="true"
    />
    <CommissionIndividual
      :teamCommission="false"
      v-if="
        state.active === filteredComponentList.indexOf('Individual Commission')
      "
    ></CommissionIndividual>
    <CommissionIndividual
      :teamCommission="true"
      v-if="state.active === filteredComponentList.indexOf('Team Commission')"
    ></CommissionIndividual>
  </div>
</template>

<script setup>
  import { reactive, inject, computed } from "vue"

  import Rankings from "@/components/rankings/Rankings.vue"
  import CommissionHighlight from "@/components/rankings/CommissionHighlight.vue"
  import CommissionIndividual from "@/components/rankings/CommissionIndividual.vue"
  import RankingsReport from "../components/rankings/RankingsReport.vue"
  import CommissionsReport from "../components/rankings/CommissionsReport.vue"
  import TeamHighlightReport from "../components/rankings/TeamHighlightReport.vue"
  import CommissionsAgentsReport from "../components/rankings/CommissionsAgentsReport.vue"
  import { useUsers } from "../store/modules/users"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import CommissionsTeamIndividualReport from "../components/rankings/CommissionsTeamIndividualReport.vue"

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")
  const userStore = useUsers()
  const $ability = inject("$ability")

  const filteredComponentList = computed(() => {
    const componentList = [
      "Rankings Report",
      "Commissions Report",
      "Individual Commission Report",
      "Team Commission",
      "Team Highlight",
      "Commission Highlight",
      "Rankings All",
      "Rankings as Managers",
      "Team Highlight Report",
      "Team Commission Report"
    ]
    return componentList.filter((name) => {
      if (name == "Commissions Report") {
        return $ability.can("read", "personal_commission_highlight")
      }
      if (name === "Commission Highlight") {
        return $ability.can("read", "personal_commission_highlight")
      }
      if (name === "Team Highlight") {
        return $ability.can("read", "personal_commission_highlight")
      }
      if (name === "Team Highlight Report") {
        return $ability.can("read", "personal_commission_highlight")
      }
      if (name === "Team Commission") {
        return (
          userStore.currentUser?.team_lead?.length > 0 ||
          $ability.can("read", "view_team_commission")
        )
      }

      if (name === "Team Commission Report") {
        return (
          userStore.currentUser?.team_lead?.length > 0 ||
          $ability.can("read", "view_team_commission")
        )
      }
      if (name === "Individual Commission Report") {
        return $ability.can("read", "navigation-personal_commissions")
      }
      if (name === "Rankings as Managers") {
        return $ability.can("read", "rankings")
      }
      if (name === "Rankings All") {
        return $ability.can("read", "rankings")
      }
      if (name === "Rankings Report") {
        return true
      }
      return true
    })
  })

  const state = reactive({
    active: 0
  })
</script>

<style></style>
