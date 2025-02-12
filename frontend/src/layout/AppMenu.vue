<template>
  <div class="flex flex-col h-full side-nav">
    <div class="flex items-center justify-center shrink-0" style="height: 60px">
      <img
        :src="$logoPath"
        alt="Image"
        :height="userStore.cms?.logo_settings?.logo_width || 50"
      />
    </div>

    <div class="mt-4">
      <div v-if="filteredModel.length > 1" class="p-0">
        <template v-for="(item, i) of filteredModel" :key="item.label || i">
          <app-menu-item
            :item="item"
            :index="i"
            @closed="emit('closed')"
          ></app-menu-item>
        </template>
      </div>
    </div>
    <div class="flex justify-center p-4 mt-auto border border-t">
      <a
        v-ripple
        class="inline-flex items-center justify-center text-white transition-colors duration-150 bg-pink-500 border-2 border-pink-600 rounded-full cursor-pointer hover:bg-pink-600 text-600 dark:text-200 p-ripple"
        style="width: 40px; height: 40px"
        @click="logOut()"
      >
        <i @click="logOut()" class="text-xl pi pi-sign-out"></i>
      </a>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed, watch, inject, defineEmits } from "vue"
  import AppMenuItem from "./AppMenuItem.vue"
  import { useAuth0 } from "@auth0/auth0-vue"
  import { useUsers } from "../store/modules/users"
  import UsersService from "../service/User"
  const $ability = inject("$ability")
  const $isPublic = inject("$isPublic")
  const $logoPath = inject("$logoPath")

  const userStore = useUsers()
  const usersService = new UsersService()
  const emit = defineEmits(["closed"])
  const { logout } = useAuth0()

  const filteredModel = computed(() => {
    return model.value.filter((item) => {
      switch (item.label) {
        case "Quote":
          return $ability.can("read", "navigation-quotes") || $isPublic
        case "Orders":
          return $ability.can("read", "navigation-orders")
        case "Inventory":
          return $ability.can("read", "navigation-inventory")
        case "Reports":
          return $ability.can("read", "navigation-reports") && false
        case "Pricing":
          return $ability.can("read", "navigation-products")
        case "Drivers":
          return $ability.can("attach", "driver")
        case "Commission":
          return (
            $ability.can("read", "navigation-personal_commissions") &&
            userStore.cms?.feature_flags?.commmissions_enabled
          )
        case "Handbook":
          return (
            $ability.can("read", "navigation-agent_guide") &&
            userStore.cms?.feature_flags?.commmissions_enabled
          )
        case "Users":
          return $ability.can("read", "navigation-users")
        case "Settings":
          return true
        case "Reporting":
          return $ability.can("read", "reports")
        case "Deliveries":
          return (
            $ability.can("read", "own_driver_account") ||
            $ability.can("read", "deliveries")
          )
        default:
          break
      }
    })
  })

  const model = computed(() => {
    // if (!userStore.cms) {
    //   return [];
    // }
    return [
      {
        label: "Quote",
        icon: "pi pi-fw pi-send",
        to: "/quotes"
      },
      {
        label: "Orders",
        icon: "pi pi-fw pi-file",
        to: "/invoices"
      },
      {
        label: "Inventory",
        icon: "pi pi-fw pi-box",
        to: "/inventory"
      },
      {
        label: "Reports",
        icon: "pi pi-fw pi-chart-line",
        to: "/reports"
      },
      {
        label: "Pricing",
        icon: "pi pi-fw pi-money-bill",
        to: "/pricing"
      },
      {
        label: "Drivers",
        icon: "pi pi-fw pi-truck",
        to: "/drivers"
      },
      {
        label: "Commission",
        icon: "pi pi-fw pi-dollar",
        to: "/commission"
      },
      {
        label: "Reporting",
        icon: "pi pi-fw pi-chart-line",
        to: "/reporting"
      },
      {
        label: "Handbook",
        icon: "pi pi-fw pi-compass",
        redirect: userStore.cms?.agent_guide_link
      },
      {
        label: "Users",
        icon: "pi pi-fw pi-users",
        to: "/users"
      },
      {
        label: "Deliveries",
        icon: "pi pi-fw pi-truck",
        to: "/deliveries"
      },
      {
        label: "Settings",
        icon: "pi pi-fw pi-cog",
        to: "/settings"
      }
    ]
  })

  const logOut = async () => {
    userStore.$reset()
    localStorage.clear()
    await logout({
      returnTo: window.location.origin
    })
  }

  watch(
    () => userStore.darkMode,
    async (isDark) => {
      if (isDark) {
        document.documentElement.classList.add("app-dark")
      } else {
        document.documentElement.classList.remove("app-dark")
      }
    }
  )
</script>

<style lang="scss" scoped>
  .side-nav {
    z-index: 999;
  }
</style>
