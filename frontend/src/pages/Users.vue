<template>
  <div>
    <ul
      class="flex p-2 m-0 overflow-x-auto list-none select-none bg-0 dark:bg-900"
    >
      <template :key="idx" v-for="(name, idx) in filteredComponentList">
        <li class="pr-4">
          <a
            v-ripple
            :style="[state.active === idx ? { color: 'white !important' } : '']"
            class="flex items-center px-6 py-4 transition-colors duration-150 cursor-pointer hover:bg-100 dark:hover:bg-700 rounded-border p-ripple"
            :class="{
              'p-button p-component p-button-secondary': state.active === idx,
              'text-700 dark:text-100': state.active !== idx
            }"
            @click="state.active = idx"
          >
            <span class="text-2xl font-medium">{{ name }}</span>
          </a>
        </li>
        <li class="flex items-center">
          <div style="width: 1px; height: 50%" class="border border-r"></div>
        </li>
      </template>
    </ul>
    <users-table v-if="state.active === 0" class="mt-6"></users-table>
    <team-members v-if="state.active === 1" class="mt-6"></team-members>
    <Roles v-if="state.active === 2" class="mt-6"></Roles>
  </div>
</template>

<script setup>
  import UsersTable from "@/components/users/UsersTable.vue"
  import TeamMembers from "@/components/users/TeamMembers.vue"
  import Roles from "@/components/users/Roles.vue"

  import { computed, inject, reactive } from "vue"

  const $ability = inject("$ability")

  const state = reactive({
    active: 0
  })

  const filteredComponentList = computed(() => {
    return ["Users", "Team Members", "Roles"].filter((name) => {
      return $ability.can("read", "navigation-users")
    })
  })
</script>

<style></style>
